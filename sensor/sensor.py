# -*- coding: utf-8 -*-
import time
import requests
import base64
import msgpack
import os

API_URL = os.getenv("SERVER_URL", "http://ingestion-api:8000/ingest")
SENSOR_ID = os.getenv("SENSOR_ID", "1")
PLANT_ID = os.getenv("PLANT_ID", "1")


def generate_payload(sensor_id, plant_id):
    data = {
        "sensor_id": sensor_id,
        "sensor_version": "v1",
        "plant_id": plant_id,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "measures": {
            "temperature": "25°C",  # Le symbole ° est encodé en UTF-8
            "humidite": "50%"
        }
    }
    packed = msgpack.packb(data)
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
        time.sleep(10)
