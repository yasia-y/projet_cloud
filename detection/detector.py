import time


def detect_anomalies(data: dict) -> list:
    anomalies = []
    temp = data.get("temperature")
    hum = data.get("humidity")
    if temp is not None:
        if temp < 0 or temp > 50:
            anomalies.append("Temperature out of range")
    if hum is not None:
        if hum < 0 or hum > 100:
            anomalies.append("Humidity out of range")
    return anomalies


# Exemple d'utilisation
if __name__ == "__main__":
    while True:
        sample_data = {"temperature": 60, "humidity": 50}
        result = detect_anomalies(sample_data)
        print("Anomalies détectées :", result)
        time.sleep(10)
