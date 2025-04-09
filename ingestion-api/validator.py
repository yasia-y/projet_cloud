def validate_sensor_payload(data: dict) -> (bool, list):
    errors = []
    if "plant_id" not in data or not isinstance(data.get("plant_id"), str):
        errors.append("plant_id manquant ou invalide")
    if "temperature" not in data or not isinstance(data.get("temperature"), (int, float)):
        errors.append("temperature manquante ou invalide")
    if "humidity" not in data or not isinstance(data.get("humidity"), (int, float)):
        errors.append("humidity manquante ou invalide")
    if "timestamp" not in data:
        errors.append("timestamp manquant")
    return (len(errors) == 0, errors)
