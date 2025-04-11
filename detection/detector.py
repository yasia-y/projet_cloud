import psycopg2
import time
import logging
from datetime import datetime, timedelta

# Configuration de la BDD
DB_HOST = "db"
DB_PORT = 5432
DB_NAME = "ferme"
DB_USER = "admin"
DB_PASSWORD = "secret"

logging.basicConfig(level=logging.INFO)

def detect_anomalies():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # On ne regarde que les données des 2 dernières minutes
        since = datetime.utcnow() - timedelta(minutes=2)
        cursor.execute("""
            SELECT plant_id, temperature, humidity, timestamp
            FROM sensor_data
            WHERE timestamp > %s
        """, (since,))
        rows = cursor.fetchall()

        for r in rows:
            plant_id, temp, hum, ts = r
            anomalies = []
            if temp > 30:
                anomalies.append("🌡️ Température élevée")
            if hum < 40:
                anomalies.append("💧 Humidité faible")
            if anomalies:
                logging.warning(f"[{ts}] PLANTE {plant_id} : {', '.join(anomalies)}")
            else:
                logging.info(f"[{ts}] PLANTE {plant_id} OK.")
        
        conn.close()
    except Exception as e:
        logging.error(f"Erreur de détection : {e}")

if __name__ == "__main__":
    while True:
        detect_anomalies()
        time.sleep(10)

