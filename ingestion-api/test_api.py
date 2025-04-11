from fastapi.testclient import TestClient
from main import app
import base64
import msgpack

client = TestClient(app)


def generate_payload():
    data = {
        "plant_id": "plante_42",
        "temperature": 21.5,
        "humidity": 60.0,
        "timestamp": "2024-04-08T14:00:00"
    }
    packed = msgpack.packb(data)
    encoded = base64.b64encode(packed).decode('utf-8')
    return encoded


def test_ingest_valid():
    payload = {
        "sensor_id": "17629",
        "sensor_version": "FR-v8",
        "plant_id": "2",
        "time": "2025-04-11T07:33:06Z",
        "measures": {"temperature": "25°C", "humidite": "50%"}
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_ingest_invalid():
    response = client.post("/ingest", data="payload_invalid")
    assert response.status_code != 200


def test_ingest_and_db_insertion():
    payload = {
        "sensor_id": "17629",
        "sensor_version": "FR-v8",
        "plant_id": "2",
        "time": "2025-04-11T07:33:06Z",
        "measures": {"temperature": "25°C", "humidite": "50%"}
    }
    response = client.post("/ingest", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

    # Verify the data in the database
    cursor.execute("SELECT * FROM sensor_data WHERE plant_id = %s", ("2",))
    result = cursor.fetchone()
    assert result is not None
    assert result[1] == "2"  # plant_id
    assert result[2] == 25.0  # temperature
    assert result[3] == 50.0  # humidity
