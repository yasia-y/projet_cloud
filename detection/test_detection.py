import pytest
from detector import detect_anomalies


def test_detect_anomalies_normal():
    data = {"temperature": 25, "humidity": 50}
    anomalies = detect_anomalies(data)
    assert anomalies == []


def test_detect_anomalies_temp_error():
    data = {"temperature": 60, "humidity": 50}
    anomalies = detect_anomalies(data)
    assert "Temperature out of range" in anomalies
