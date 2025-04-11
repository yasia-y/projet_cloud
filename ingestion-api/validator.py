import logging


def validate_sensor_payload(data: dict) -> (bool, list):
    errors = []
    if not data.get("plant_id") or not isinstance(data.get("plant_id"), str) or not data.get("plant_id").isdigit():
        errors.append("plant_id manquant ou invalide (doit être un nombre)")
    if data.get("temperature") is None or not isinstance(data.get("temperature"), (int, float)):
        errors.append("temperature manquante ou invalide")
    if data.get("humidity") is None or not isinstance(data.get("humidity"), (int, float)):
        errors.append("humidity manquante ou invalide")
    if not data.get("timestamp"):
        errors.append("timestamp manquant")
    logging.info(f"Validation result: {len(errors) == 0}, errors: {errors}")
    return (len(errors) == 0, errors)


def convert_measurements(measure: str) -> float:
    try:
        if measure is None:
            return None
        if "°C" in measure:
            return float(measure.replace("°C", "").strip())
        elif "°F" in measure:
            return (float(measure.replace("°F", "").strip()) - 32) * 5.0 / 9.0
        elif "%" in measure:
            return float(measure.replace("%", "").strip())
        else:
            return float(measure)
    except Exception as e:
        logging.error(f"Error converting measurement: {measure}, error: {e}")
        return None
