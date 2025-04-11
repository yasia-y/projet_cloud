import psycopg2
import time
import logging
import socket
from datetime import datetime, timedelta, timezone

# Configuration de la BDD
DB_HOST = "db"
DB_PORT = 5432
DB_NAME = "plant_monitoring"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def wait_for_dns_resolution():
    """Attend que le nom d'hôte soit résolu par le DNS Docker"""
    max_retries = 10
    for attempt in range(max_retries):
        try:
            socket.gethostbyname(DB_HOST)
            logging.info("Résolution DNS réussie pour %s", DB_HOST)
            return True
        except socket.gaierror:
            wait_time = 2 ** attempt  # Backoff exponentiel
            logging.warning("Échec résolution DNS (tentative %d/%d), nouvelle tentative dans %ds...", 
                          attempt+1, max_retries, wait_time)
            time.sleep(wait_time)
    return False

def detect_anomalies():
    """Détecte les anomalies dans les données capteurs"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5  # Timeout de connexion réduit
        )
        cursor = conn.cursor()

        since = datetime.now(timezone.utc) - timedelta(minutes=2)
        cursor.execute("""
            SELECT plant_id, temperature, humidity, timestamp 
            FROM sensor_data 
            WHERE timestamp > %s
        """, (since,))
        
        for plant_id, temp, hum, ts in cursor.fetchall():
            anomalies = []
            if temp > 30: anomalies.append("🌡️ Température élevée")
            if hum < 40: anomalies.append("💧 Humidité faible")
            
            log_msg = f"[{ts.isoformat()}] PLANTE {plant_id}"
            logging.warning(f"{log_msg} : {', '.join(anomalies)}") if anomalies else logging.info(f"{log_msg} OK")

    except psycopg2.OperationalError as e:
        logging.error("Erreur de connexion à PostgreSQL: %s", e)
        raise
    finally:
        if 'conn' in locals(): conn.close()

def main_loop():
    """Boucle principale avec gestion robuste des erreurs"""
    while True:
        try:
            if wait_for_dns_resolution():
                detect_anomalies()
                time.sleep(10)  # Intervalle normal
            else:
                logging.critical("Échec critique de résolution DNS après 10 tentatives")
                break
                
        except Exception as e:
            logging.error("Erreur critique: %s", e, exc_info=True)
            logging.info("Nouvelle tentative dans 30 secondes...")
            time.sleep(30)

if __name__ == "__main__":
    logging.info("Démarrage du service de détection d'anomalies")
    main_loop()
