import time
import requests
import base64
import msgpack
import os
import random
from datetime import datetime, timezone

API_URL = os.getenv("SERVER_URL", "http://ingestion-api:8000/ingest")
SENSOR_ID = os.getenv("SENSOR_ID", "FR-001")
PLANT_ID = int(os.getenv("PLANT_ID", "1").replace("PLANT-", ""))
SENSOR_VERSION = os.getenv("SENSOR_VERSION", "FR-v8")

def generate_fake_measurements():
    temperature = round(random.normalvariate(25, 3), 2)
    humidity = round(random.normalvariate(60, 10), 2)

    if random.random() < 0.05:
        temperature += random.randint(5, 15)
    if random.random() < 0.05:
        humidity += random.randint(15, 25)

    return temperature, humidity

def generate_payload():
    temperature, humidity = generate_fake_measurements()
    return {
        "sensor_id": SENSOR_ID,
        "sensor_version": SENSOR_VERSION,
        "plant_id": PLANT_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": temperature,
        "humidity": humidity
    }

def encode_payload(payload):
    return base64.b64encode(msgpack.packb(payload)).decode('utf-8')

if __name__ == "__main__":
    print(f"🚀 Capteur {SENSOR_ID} (v{SENSOR_VERSION}) actif pour plante {PLANT_ID}")
    while True:
        try:
            payload = generate_payload()
            encoded = encode_payload(payload)
            response = requests.post(API_URL, data=encoded, headers={
                "Content-Type": "application/msgpack",
                "X-Sensor-Version": SENSOR_VERSION
            })
            print(f"📤 Données envoyées | Statut: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur d'envoi : {str(e)}")
        time.sleep(int(os.getenv("INTERVAL", "10")))

