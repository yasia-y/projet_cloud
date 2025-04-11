# -*- coding: utf-8 -*-
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
