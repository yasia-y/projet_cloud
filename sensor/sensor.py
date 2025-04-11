# -*- coding: utf-8 -*-
import time
import requests
import base64
import msgpack
import os
import random
from datetime import datetime

# Récupération des variables d'environnement
API_URL = os.getenv("SERVER_URL", "http://ingestion-api:8000/ingest")
SENSOR_ID = os.getenv("SENSOR_ID", "1")
PLANT_ID = os.getenv("PLANT_ID", "1")


def generate_fake_measurements():
    """
    Génère des mesures réalistes avec une faible probabilité d'anomalies.
    """
    # Valeurs normales
    temperature = round(random.normalvariate(25, 3), 2)  # Moyenne 25°C, écart-type 3
    humidity = round(random.normalvariate(60, 10), 2)    # Moyenne 60%, écart-type 10

    # Simulation d'anomalies (5 % de chance)
    if random.random() < 0.05:
        temperature += random.randint(5, 10)  # Surchauffe
    if random.random() < 0.05:
        humidity += random.randint(20, 30)    # Humidité trop élevée

    return temperature, humidity


def generate_payload(sensor_id, plant_id):
    """
    Génère le payload encodé pour le capteur.
    """
    temperature, humidity = generate_fake_measurements()
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Construction des données
    data = {
        "sensor_id": sensor_id,
        "sensor_version": "v1",
        "plant_id": plant_id,
        "time": timestamp,
        "measures": {
            "temperature": f"{temperature}°C",
            "humidite": f"{humidity}%"
        }
    }

    # Encodage msgpack puis base64
    packed = msgpack.packb(data)
    encoded = base64.b64encode(packed).decode("utf-8")
    return encoded


if __name__ == "__main__":
    print(f"🌱 Sensor {SENSOR_ID} for plant {PLANT_ID} started! Sending data to {API_URL}...")
    while True:
        payload = generate_payload(SENSOR_ID, PLANT_ID)
        try:
            response = requests.post(API_URL, data=payload)
            print(f"✅ Sensor {SENSOR_ID} sent data at {datetime.utcnow().isoformat()} | Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending data from sensor {SENSOR_ID}: {e}")
        time.sleep(10)

