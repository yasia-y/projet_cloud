import os
import logging
import psycopg2
import socket
import time
from fastapi import FastAPI, Request, HTTPException, Query
from parser import decode_sensor_data
from validator import validate_sensor_payload, convert_measurements

app = FastAPI()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/plant_monitoring")
TEMP_MIN = 10.0
TEMP_MAX = 35.0
HUM_MIN = 30.0
HUM_MAX = 80.0

def wait_for_db():
    """Attend la résolution DNS du nom de l'hôte de la base de données"""
    for attempt in range(10):
        try:
            socket.gethostbyname('db')
            logging.info("Résolution DNS réussie pour 'db'")
            return True
        except socket.gaierror:
            wait_time = 5 * (attempt + 1)
            logging.warning("Échec résolution DNS (tentative %d/10), nouvelle tentative dans %ds...", 
                          attempt+1, wait_time)
            time.sleep(wait_time)
    return False

def get_db_connection():
    """Établit une connexion à la base de données avec réessais"""
    for attempt in range(5):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            logging.info("Connexion à la base de données réussie")
            return conn
        except psycopg2.OperationalError as e:
            wait_time = 2 ** attempt
            logging.warning("Échec connexion DB (tentative %d/5), nouvelle tentative dans %ds...: %s", 
                          attempt+1, wait_time, str(e))
            time.sleep(wait_time)
    raise Exception("Échec de connexion à la base de données après 5 tentatives")

@app.post("/ingest")
async def ingest(request: Request):
    try:
        if not wait_for_db():
            raise HTTPException(status_code=500, detail="Erreur de résolution DNS")

        raw_payload = await request.body()
        logging.info("Payload reçu (taille: %d octets)", len(raw_payload))

        # Décodage et validation
        decoded_data = decode_sensor_data(raw_payload)
        transformed_data = {
            "plant_id": str(decoded_data.get("plant_id")),
            "temperature": convert_measurements(decoded_data["measures"]["temperature"]),
            "humidity": convert_measurements(decoded_data["measures"]["humidite"]),
            "timestamp": decoded_data["time"]
        }

        is_valid, errors = validate_sensor_payload(transformed_data)
        if not is_valid:
            logging.error("Données invalides: %s", errors)
            raise HTTPException(status_code=400, detail=errors)

        # Détection d'anomalies
        alerts = []
        if transformed_data["temperature"] > TEMP_MAX:
            alerts.append(f"Température élevée ({transformed_data['temperature']}°C)")
        if not HUM_MIN <= transformed_data["humidity"] <= HUM_MAX:
            alerts.append(f"Humidité anormale ({transformed_data['humidity']}%)")

        for alert in alerts:
            logging.warning("ALERTE - Plante %s: %s", transformed_data['plant_id'], alert)

        # Insertion en base de données
        try:
            conn = get_db_connection()
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sensor_data (plant_id, temperature, humidity, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        transformed_data["plant_id"],
                        transformed_data["temperature"],
                        transformed_data["humidity"],
                        transformed_data["timestamp"]
                    ))
            logging.info("Données insérées avec succès")

        except Exception as e:
            logging.error("Erreur d'insertion: %s", str(e))
            raise HTTPException(status_code=500, detail="Erreur de base de données")

        return {"status": "OK", "alerts": alerts}

    except HTTPException:
        raise
    except Exception as e:
        logging.error("Erreur non gérée: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/health")
async def health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
        return {"status": "OK", "database": "connecté"}
    except Exception:
        return {"status": "OK", "database": "non connecté"}

@app.get("/data")
def get_data(plant_id: str = Query(..., description="ID de la plante à interroger")):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT plant_id, temperature, humidity, timestamp
                    FROM sensor_data
                    WHERE plant_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 20
                """, (plant_id,))
                
                return {
                    "results": [
                        {
                            "plant_id": row[0],
                            "temperature": float(row[1]),
                            "humidity": float(row[2]),
                            "timestamp": row[3].isoformat()
                        } for row in cursor.fetchall()
                    ]
                }
                
    except Exception as e:
        logging.error("Erreur de lecture: %s", str(e))
        raise HTTPException(status_code=500, detail="Erreur de base de données")
