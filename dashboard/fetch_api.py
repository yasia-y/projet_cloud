# Functions to query the ingestion API and retrieve processed sensor data.
# Handle retries, timeouts, and data formatting.

import requests

API_URL = "http://ingestion-api:8000/data"

def get_data_for_plant(plant_id):
    try:
        response = requests.get(API_URL, params={"plant_id": plant_id})
        return response.json()
    except Exception as e:
        print(f"Erreur de récupération via API : {e}")
        return {}

