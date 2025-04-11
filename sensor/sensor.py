# -*- coding: utf-8 -*-
import time
import requests
import base64
import msgpack
import os
import random

API_URL = os.getenv("SERVER_URL", "http://ingestion-api:8000/ingest")
SENSOR_ID = os.getenv("SENSOR_ID", "1")
PLANT_ID = os.getenv("PLANT_ID", "1")


def generate_payload(sensor_id, plant_id):
    # Générer des données aléatoires
    # Température entre 15°C et 35°C
    temperature = round(random.uniform(15, 35), 2)
    humidity = round(random.uniform(30, 90), 2)     # Humidité entre 30% et 90%
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ")  # Timestamp actuel

    # Construire le payload
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

    # Encoder en msgpack
    packed = msgpack.packb(data)

    # Encoder en base64
    encoded = base64.b64encode(packed).decode('utf-8')
    return encoded


if __name__ == "__main__":
    while True:
        payload = generate_payload(SENSOR_ID, PLANT_ID)
        try:
            response = requests.post(API_URL, data=payload)
            print(f"Sensor {SENSOR_ID} sent data: {response.status_code}")
        except Exception as e:
            print(f"Error sending data: {e}")
        # Attendre 10 secondes avant d'envoyer de nouvelles données
        time.sleep(10)
