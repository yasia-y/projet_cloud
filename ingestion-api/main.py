import base64
import msgpack
import os
import logging
import psycopg2
import socket
import time
from fastapi import FastAPI, Request, HTTPException, Query

from validator import validate_sensor_payload

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/plant_monitoring")
TEMP_MIN = 10.0
TEMP_MAX = 35.0
HUM_MIN = 30.0
HUM_MAX = 80.0
# according to les données sur internet of course

def wait_for_db():
    for attempt in range(10):
        try:
            socket.gethostbyname('db')
            logging.info("Résolution DNS réussie pour 'db'")
            return True
        except socket.gaierror:
            wait_time = 5 * (attempt + 1)
            logging.warning("DNS échec (tentative %d), retry dans %ds", attempt + 1, wait_time)
            time.sleep(wait_time)
    return False
# permet de faire une boucle de 10 tentatives et en cas d'échec de réessayer.


def get_db_connection():
    for attempt in range(5):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            logging.info("Connexion DB réussie")
            return conn
        except psycopg2.OperationalError as e:
            wait_time = 2 ** attempt
            logging.warning("Échec DB (tentative %d), retry dans %ds...: %s", attempt + 1, wait_time, str(e))
            time.sleep(wait_time)
    raise Exception("Connexion à la base échouée après 5 tentatives")

# endpoint /ingest permet de réceptionner, convertit et valide les données, génère des anomalies, enregistre les données dans la table "sensor_data".


@app.post("/ingest")
async def ingest(request: Request):
    try:
        if not wait_for_db():
            raise HTTPException(status_code=500, detail="DNS DB échoué")

        raw_payload = await request.body()
        logging.info("Payload reçu (%d octets)", len(raw_payload))

        decoded_data = msgpack.unpackb(base64.b64decode(raw_payload), raw=False)

        logging.info("Contenu reçu : %s", decoded_data)

        transformed_data = {
            "plant_id": int(decoded_data["plant_id"]),
            "temperature": float(decoded_data["temperature"]),
            "humidity": float(decoded_data["humidity"]),
            "timestamp": decoded_data["timestamp"]
        }

        is_valid, errors = validate_sensor_payload(transformed_data)
        if not is_valid:
            logging.error("Données invalides : %s", errors)
            raise HTTPException(status_code=400, detail=errors)

        alerts = []
        if transformed_data["temperature"] > TEMP_MAX:
            alerts.append(f"Température élevée ({transformed_data['temperature']}°C)")
        if not HUM_MIN <= transformed_data["humidity"] <= HUM_MAX:
            alerts.append(f"Humidité anormale ({transformed_data['humidity']}%)")

        for alert in alerts:
            logging.warning("🚨 Alerte plante %s : %s", transformed_data['plant_id'], alert)

        try:
            conn = get_db_connection()
            with conn:
                with conn.cursor() as cursor:
                    # Dans la fonction @app.post("/ingest")
                    cursor.execute("""
                        INSERT INTO sensor_data 
                        (sensor_id, sensor_version, plant_id, temperature, humidity, timestamp, anomaly)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        decoded_data["sensor_id"],
                        decoded_data["sensor_version"],
                        transformed_data["plant_id"],
                        transformed_data["temperature"],
                        transformed_data["humidity"],
                        transformed_data["timestamp"],
                        len(alerts) > 0  # True si au moins une alerte
                    ))

            logging.info("✅ Données insérées")
        except Exception as e:
            logging.error("Erreur insertion DB : %s", str(e))
            raise HTTPException(status_code=500, detail="Erreur base de données")

        return {"status": "OK", "alerts": alerts}

    except HTTPException:
        raise
    except Exception as e:
        logging.error("Erreur non gérée : %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur serveur interne")


# execute une requête pour récupérer et retourner la liste des identifiants de plantes distincts stockées dans la base

@app.get("/plants")
def get_plants():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT DISTINCT plant_id FROM sensor_data ORDER BY plant_id")
                return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logging.error("Erreur récupération plantes : %s", str(e))
        raise HTTPException(status_code=500, detail="Erreur base de données")

# prend en paramètre un identifiant de plante et retourne, pour cette plante, la liste des capteurs distincts (identifiant et version)
@app.get("/sensors")
def get_sensors(plant_id: int = Query(...)):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT sensor_id, sensor_version 
                    FROM sensor_data 
                    WHERE plant_id = %s
                    ORDER BY sensor_id
                """, (plant_id,))
                return [
                    {"sensor_id": row[0], "sensor_version": row[1]}
                    for row in cursor.fetchall()
                ]
    except Exception as e:
        logging.error("Erreur récupération capteurs : %s", str(e))
        raise HTTPException(status_code=500, detail="Erreur base de données")


# effectue un test pour vérifier si la connexion à la base est fonctionnelle et renvoie un indicateur de statut de la base

@app.get("/health")
async def health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return {"status": "OK", "database": "connecté"}
    except Exception:
        return {"status": "OK", "database": "non connecté"}

# permet de récuperer les données enregistrées pour une plante donnée, avec pour possibilité de filtrer parmi les capteurs et les dates.

@app.get("/data")
def get_data(
    plant_id: int = Query(..., description="ID de la plante"),
    sensor_id: str = Query(None, description="ID du capteur"),
    start: str = Query(None, description="Date de début (ISO)"),
    end: str = Query(None, description="Date de fin (ISO)")
):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Modification de la requête SQL
                base_query = """
                    SELECT 
                        plant_id, 
                        temperature, 
                        humidity, 
                        timestamp, 
                        anomaly,
                        cross_sensor_issue,
                        sensor_id
                    FROM sensor_data
                    WHERE plant_id = %s
                """
                params = [plant_id]
                
                if sensor_id:
                    base_query += " AND sensor_id = %s"
                    params.append(sensor_id)
                
                if start and end:
                    base_query += " AND timestamp BETWEEN %s AND %s"
                    params.extend([start, end])
                
                base_query += " ORDER BY timestamp DESC LIMIT 20"
                
                cursor.execute(base_query, tuple(params))
                
                return {
                    "results": [
                        {
                            "plant_id": row[0],
                            "temperature": float(row[1]),
                            "humidity": float(row[2]),
                            "timestamp": row[3].isoformat(),
                            "anomaly": bool(row[4]),
                            "cross_sensor_issue": bool(row[5]),
                            "sensor_id": row[6]
                        } 
                        for row in cursor.fetchall()
                    ]
                }
                
    except Exception as e:
        logging.error("Erreur de lecture DB : %s", str(e))
        raise HTTPException(status_code=500, detail="Erreur base de données")

