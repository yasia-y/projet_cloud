import base64
import msgpack

def decode_sensor_data(raw_payload: bytes) -> dict:
    try:
        payload_str = raw_payload.decode('utf-8')
        binary_data = base64.b64decode(payload_str)
        data = msgpack.unpackb(binary_data, raw=False)
        return data
    except Exception as e:
        raise ValueError("Erreur lors du décodage des données du capteur") from e
