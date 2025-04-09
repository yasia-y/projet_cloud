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
    payload = generate_payload()
    response = client.post("/ingest", data=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "OK"

def test_ingest_invalid():
    response = client.post("/ingest", data="payload_invalid")
    assert response.status_code != 200

