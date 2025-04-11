import os
import logging
import psycopg2
from fastapi import FastAPI, Request, HTTPException
from parser import decode_sensor_data
from validator import validate_sensor_payload, convert_measurements
from fastapi import Query

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Connexion à PostgreSQL via variable d'env
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@db:5432/ferme")

TEMP_MIN = 10.0  # Beaucoup de plantes meurent ou arrête de croître
TEMP_MAX = 35.0  # Au-delà, la photosynthèse est perturbée
HUM_MIN = 30.0  # Trop sec, stress hydrique
HUM_MAX = 80.0  # Risque de moisissures, champignons

@app.post("/ingest")
async def ingest(request: Request):
    try:
        raw_payload = await request.body()
        logging.info(f"Raw payload received: {raw_payload}")

        # Étape 1 : Décodage
        try:
            decoded_data = decode_sensor_data(raw_payload)
            logging.info(f"Decoded data: {decoded_data}")
        except Exception as e:
            logging.error(f"Error decoding payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload encoding")

        # Étape 2 : Transformation
        transformed_data = {
            "plant_id": str(decoded_data.get("plant_id")),
            "temperature": convert_measurements(decoded_data["measures"]["temperature"]),
            "humidity": convert_measurements(decoded_data["measures"]["humidite"]),
            "timestamp": decoded_data["time"]
        }
        logging.info(f"Transformed data: {transformed_data}")

        # Étape 3 : Validation
        is_valid, errors = validate_sensor_payload(transformed_data)
        if not is_valid:
            logging.error(f"Validation errors: {errors}")
            raise HTTPException(status_code=400, detail=errors)

        # Initialisation des alertes
        alerts = []

        # Vérification des alertes
        if transformed_data["temperature"] > TEMP_MAX:
            alerts.append(f"ALERTE 🔥: Température anormale ({transformed_data['temperature']}°C) pour la plante {transformed_data['plant_id']}")
        if not HUM_MIN <= transformed_data["humidity"] <= HUM_MAX:
            alerts.append(f"ALERTE 💧: Humidité anormale ({transformed_data['humidity']}%) pour la plante {transformed_data['plant_id']}")

        for alert in alerts:
            logging.warning(alert)

        # Étape 4 : Insertion en BDD
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_data (plant_id, temperature, humidity, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (
                transformed_data["plant_id"],
                transformed_data["temperature"],
                transformed_data["humidity"],
                transformed_data["timestamp"]
            ))
            conn.commit()
            cursor.close()
            conn.close()
            logging.info("Data inserted successfully.")
        except Exception as e:
            logging.error(f"Database insertion error: {e}")
            raise HTTPException(status_code=500, detail="Database error")

        return {"status": "OK", "data": transformed_data}
    except Exception as e:
        logging.error(f"Unhandled error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "API opérationnelle"}


@app.get("/data")
def get_data(plant_id: str = Query(..., description="ID de la plante à interroger")):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT plant_id, temperature, humidity, timestamp
            FROM sensor_data
            WHERE plant_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (plant_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "results": [
                {
                    "plant_id": r[0],
                    "temperature": r[1],
                    "humidity": r[2],
                    "timestamp": r[3].isoformat()
                } for r in rows
            ]
        }
    except Exception as e:
        logging.error(f"DB read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

