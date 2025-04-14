import psycopg2
import time
import logging
import socket
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

# Seuils environnementaux
TEMP_MIN = 5.0  # Au lieu de 10.0
TEMP_MAX = 40.0  # Au lieu de 35.0

# Seuils d'écart entre capteurs
MAX_TEMP_DIFF = 1.5  # Au lieu de 2.0
MAX_HUM_DIFF = 3.0   # Au lieu de 5.0

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

# résoudre le nom de l'hôte jusqu'à 10 fois. retourne true dès que la résolution réussit

def wait_for_dns_resolution() -> bool:
    """Attend que le nom d'hôte soit résolu par le DNS Docker"""
    max_retries = 10
    for attempt in range(max_retries):
        try:
            socket.gethostbyname(DB_HOST)
            logging.info("Résolution DNS réussie pour %s", DB_HOST)
            return True
        except socket.gaierror:
            wait_time = 2 ** attempt
            logging.warning("Échec résolution DNS (tentative %d/%d), nouvelle tentative dans %ds...", 
                          attempt+1, max_retries, wait_time)
            time.sleep(wait_time)
    return False

# autre check
def get_db_connection():
    """Établit une connexion à la base de données avec réessais"""
    for attempt in range(5):
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                connect_timeout=5
            )
        except psycopg2.OperationalError as e:
            wait_time = 2 ** attempt
            logging.warning("Échec connexion DB (tentative %d/5): %s", attempt+1, str(e))
            time.sleep(wait_time)
    raise Exception("Échec de connexion à la base de données après 5 tentatives")

# requête SQL pour comparer les mesures de températures et humidités entre capteurs différents. identifie une anomalie et pour chaque anomalie détectée loggue un avertissement détaillant l'écart observé entre les capteurs.

def detect_cross_sensor_anomalies(cursor, plant_id: int):
    """Détecte les anomalies entre capteurs sur la même plante"""
    cursor.execute("""
        SELECT s1.sensor_id, s1.timestamp, s1.temperature, s2.temperature, 
               s1.humidity, s2.humidity
        FROM sensor_data s1
        JOIN sensor_data s2 
        ON s1.plant_id = s2.plant_id 
        AND s1.timestamp = s2.timestamp 
        WHERE s1.plant_id = %s
        AND s1.sensor_id != s2.sensor_id
        AND (
            ABS(s1.temperature - s2.temperature) > 2.0 OR 
            ABS(s1.humidity - s2.humidity) > 5.0
        )
    """, (plant_id,))
    
    for row in cursor.fetchall():
        sensor1, ts, temp1, temp2, hum1, hum2 = row
        anomalies = []
        if abs(temp1 - temp2) > 2.0:
            anomalies.append(f"Écart température anormal ({temp1}°C vs {temp2}°C)")
        if abs(hum1 - hum2) > 5.0:
            anomalies.append(f"Écart humidité anormal ({hum1}% vs {hum2}%)")
        
        logging.warning(
            f"[{ts.isoformat()}] PLANTE {plant_id} - Capteurs {sensor1} : {', '.join(anomalies)}"
        )

# récupère les mesures des capteurs enregistrées durant les 2 dernières minutes, vérifie si la temp et l'hum est en dehors des limites critiques, en cas d'anomalie logge un message d'avertissement et met à jour pour marquer la donnée comme anormale.

def detect_environment_anomalies(cursor):
    """Détecte les anomalies environnementales"""
    cursor.execute("""
        SELECT plant_id, sensor_id, timestamp, temperature, humidity
        FROM sensor_data
        WHERE timestamp > NOW() - INTERVAL '2 minutes'
    """)
    
    for plant_id, sensor_id, ts, temp, hum in cursor.fetchall():
        anomalies = []
        if temp > 35.0 or temp < 10.0:
            anomalies.append(f"Température critique ({temp}°C)")
        if hum > 85.0 or hum < 25.0:
            anomalies.append(f"Humidité critique ({hum}%)")
        
        if anomalies:
            logging.warning(
                f"[{ts.isoformat()}] PLANTE {plant_id} - Capteur {sensor_id} : {', '.join(anomalies)}"
            )
            # Marquer l'anomalie dans la BDD
            cursor.execute("""
                UPDATE sensor_data
                SET anomaly = TRUE
                WHERE plant_id = %s AND sensor_id = %s AND timestamp = %s
            """, (plant_id, sensor_id, ts))

# 

def detect_gradual_drift(cursor):
    """Détecte les dérives progressives sur les 30 dernières minutes"""
    cursor.execute("""
        WITH sensor_stats AS (
            SELECT sensor_id,
                   AVG(temperature) as avg_temp,
                   STDDEV(temperature) as std_temp,
                   AVG(humidity) as avg_hum,
                   STDDEV(humidity) as std_hum
            FROM sensor_data
            WHERE timestamp > NOW() - INTERVAL '30 minutes'
            GROUP BY sensor_id
        )
        SELECT s.plant_id, s.sensor_id, s.timestamp, s.temperature, s.humidity
        FROM sensor_data s
        JOIN sensor_stats st ON s.sensor_id = st.sensor_id
        WHERE s.timestamp > NOW() - INTERVAL '5 minutes'
        AND (
            ABS(s.temperature - st.avg_temp) > 3 * st.std_temp OR
            ABS(s.humidity - st.avg_hum) > 3 * st.std_hum
        )
    """)
    
    for plant_id, sensor_id, ts, temp, hum in cursor.fetchall():
        logging.warning(
            f"[{ts.isoformat()}] PLANTE {plant_id} - Capteur {sensor_id} : Dérive détectée "
            f"(Temp: {temp}°C, Hum: {hum}%)"
        )

# établit une connexion à la BDD

def detect_anomalies():
    """Détection complète des anomalies"""
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                # Détection multi-capteurs
                cursor.execute("SELECT DISTINCT plant_id FROM sensor_data")
                for (plant_id,) in cursor.fetchall():
                    detect_cross_sensor_anomalies(cursor, plant_id)
                
                # Détection environnementale
                detect_environment_anomalies(cursor)
                
                # Détection dérive progressive
                detect_gradual_drift(cursor)
                
        logging.info("Vérification des anomalies terminée")
        
    except Exception as e:
        logging.error("Erreur lors de la détection: %s", str(e), exc_info=True)
        raise

# lance une boucle infinie, et vérifie en continu réussit pour l'hôte de la base.
def main_loop():
    """Boucle principale avec gestion robuste des erreurs"""
    while True:
        try:
            if wait_for_dns_resolution():
                detect_anomalies()
                time.sleep(10)
            else:
                logging.critical("Échec critique de résolution DNS après 10 tentatives")
                break
                
        except Exception as e:
            logging.error("Erreur critique: %s", str(e), exc_info=True)
            logging.info("Nouvelle tentative dans 30 secondes...")
            time.sleep(30)

if __name__ == "__main__":
    logging.info("Démarrage du service de détection d'anomalies")
    main_loop()
