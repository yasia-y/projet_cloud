import os
import logging
import psycopg2
from fastapi import FastAPI, Request, HTTPException
from parser import decode_sensor_data
from validator import validate_sensor_payload
from fastapi import Query

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Connexion à PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

@app.post("/ingest")
async def ingest(request: Request):
    try:
        raw_payload = await request.body()
        decoded_data = decode_sensor_data(raw_payload)
        is_valid, errors = validate_sensor_payload(decoded_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=errors)

        # Insertion dans la base
        cursor.execute("""
            INSERT INTO sensor_data (plant_id, temperature, humidity, timestamp)
            VALUES (%s, %s, %s, %s)
        """, (
            decoded_data["plant_id"],
            decoded_data["temperature"],
            decoded_data["humidity"],
            decoded_data["timestamp"]
        ))
        conn.commit()

        logging.info(f"Données insérées : {decoded_data}")
        return {"status": "OK", "data": decoded_data}
    except Exception as e:
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

