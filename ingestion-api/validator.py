import logging

# permet juste de s'assurer que le dict de données reçu respecte certains critères de validité qu'on attend pour un enregistrement de capteur.

def validate_sensor_payload(data: dict) -> (bool, list):
    errors = []

    # Vérification plant_id : doit exister et être un entier
    if "plant_id" not in data or not isinstance(data["plant_id"], int):
        errors.append("plant_id manquant ou invalide (doit être un entier)")

    # Vérification température : doit être un nombre
    if "temperature" not in data or not isinstance(data["temperature"], (int, float)):
        errors.append("temperature manquante ou invalide")

    # Vérification humidité : doit être un nombre
    if "humidity" not in data or not isinstance(data["humidity"], (int, float)):
        errors.append("humidity manquante ou invalide")

    # Vérification timestamp : doit exister
    if "timestamp" not in data:
        errors.append("timestamp manquant")

    logging.info(f"Validation result: {len(errors) == 0}, errors: {errors}")
    return (len(errors) == 0, errors)

# permet de convertir une valeur de mesure sous forme str en float.

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

