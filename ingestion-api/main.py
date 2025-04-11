import os
import logging
import psycopg2
from fastapi import FastAPI, Request, HTTPException
from parser import decode_sensor_data
from validator import validate_sensor_payload, convert_measurements
from fastapi import Query

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Connexion à PostgreSQL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ferme"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    print("Database connection successful")
except Exception as e:
    print("Database connection error:", e)

# filepath: ingestion-api/main.py


@app.post("/ingest")
async def ingest(request: Request):
    try:
        raw_payload = await request.body()
        logging.info(f"Raw payload received: {raw_payload}")

        # Étape 1 : Décodage des données
        try:
            decoded_data = decode_sensor_data(raw_payload)
            logging.info(f"Decoded data: {decoded_data}")
        except Exception as e:
            logging.error(f"Error decoding payload: {e}")
            raise HTTPException(
                status_code=400, detail="Invalid payload encoding")

        # Vérifiez les champs requis
        if not decoded_data.get("plant_id") or not decoded_data.get("time") or \
           not decoded_data.get("measures", {}).get("temperature") or \
           not decoded_data.get("measures", {}).get("humidite"):
            logging.error(
                f"Missing required fields in decoded data: {decoded_data}")
            raise HTTPException(
                status_code=400, detail="Missing required fields in payload")

        # Étape 2 : Transformation des données
        transformed_data = {
            # Convertir en chaîne de caractères
            "plant_id": str(decoded_data.get("plant_id")),
            "temperature": convert_measurements(decoded_data.get("measures", {}).get("temperature")),
            "humidity": convert_measurements(decoded_data.get("measures", {}).get("humidite")),
            "timestamp": decoded_data.get("time"),
        }
        logging.info(f"Transformed data: {transformed_data}")

        # Étape 3 : Validation des données
        is_valid, errors = validate_sensor_payload(transformed_data)
        if not is_valid:
            logging.error(f"Validation errors: {errors}")
            raise HTTPException(status_code=400, detail=errors)

        # Étape 4 : Insertion dans la base de données
        try:
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
            logging.info(f"Data inserted successfully: {transformed_data}")
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
        cursor.execute("""
            SELECT plant_id, temperature, humidity, timestamp
            FROM sensor_data
            WHERE plant_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (plant_id,))
        rows = cursor.fetchall()

        results = [
            {
                "plant_id": r[0],
                "temperature": r[1],
                "humidity": r[2],
                "timestamp": r[3].isoformat()
            }
            for r in rows
        ]
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Test manuel du décodage

raw_payload = b"halzZW5zb3JfaWSmNzQ2MzEyrnNlbnNvcl92ZXJzaW9upUZSLXY4qHBsYW50X2lkzgAAAAGkdGltZbQyMDI1LTA0LTEwVDIwOjQ3OjQ2WqhtZWFzdXJlc4KrdGVtcGVyYXR1cmWlMTTCsEOoaHVtaWRpdGWjMTIl"
try:
    decoded_data = decode_sensor_data(raw_payload)
    print("Decoded data:", decoded_data)
except Exception as e:
    print("Error decoding payload:", e)

raw_payload = b"hKhwbGFudF9pZKlwbGFudGVfNDKrdGVtcGVyYXR1cmXLQDWAAAAAAACoaHVtaWRpdHnLQE4AAAAAAACpdGltZXN0YW1wszIwMjQtMDQtMDhUMTQ6MDA6MDA="
try:
    decoded_data = decode_sensor_data(raw_payload)
    print("Decoded data:", decoded_data)
except Exception as e:
    print("Error decoding payload:", e)


def validate_sensor_payload(data: dict) -> (bool, list):
    errors = []
    if not data.get("plant_id") or not isinstance(data.get("plant_id"), str):
        errors.append("plant_id manquant ou invalide")
    if data.get("temperature") is None or not isinstance(data.get("temperature"), (int, float)):
        errors.append("temperature manquante ou invalide")
    if data.get("humidity") is None or not isinstance(data.get("humidity"), (int, float)):
        errors.append("humidity manquante ou invalide")
    if not data.get("timestamp"):
        errors.append("timestamp manquant")
    logging.info(f"Validation result: {len(errors) == 0}, errors: {errors}")
    return (len(errors) == 0, errors)


# Example payload for testing
example_payload = {
    "sensor_id": "17629",
    "sensor_version": "FR-v8",
    "plant_id": "2",
    "time": "2025-04-11T07:51:34Z",
    "measures": {
        "temperature": "25°C",
        "humidite": "50%"
    }
}
