import base64
import msgpack


def decode_sensor_data(raw_payload: bytes) -> dict:
    try:
        # Décodage Base64
        payload_str = raw_payload.decode('utf-8')
        binary_data = base64.b64decode(payload_str)

        # Décodage MsgPack
        data = msgpack.unpackb(binary_data, raw=False)
        return data
    except Exception as e:
        raise ValueError(
            f"Erreur lors du décodage des données du capteur : {e}")
