import requests
from datetime import datetime

API_BASE = "http://ingestion-api:8000"

# but : interroger l'endpoint /plants de l'API pour récupérer la liste des id. 
def get_plants():
    try:
        response = requests.get(f"{API_BASE}/plants")
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

# but : récupérer la liste des capteurs pour une plante spécifiée via l'endpoint /sensors
def get_sensors(plant_id):
    try:
        response = requests.get(
            f"{API_BASE}/sensors",
            params={"plant_id": plant_id}
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

# but : obtenir les données enregistrées par un capteur spécifique sur une plage temporelle donnée via l'endpoint /data
def get_sensor_data(plant_id, sensor_id, start, end):
    try:
        params = {
            "plant_id": plant_id,
            "sensor_id": sensor_id,
            "start": start.isoformat(),
            "end": end.isoformat()
        }
        response = requests.get(f"{API_BASE}/data", params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception:
        return []
