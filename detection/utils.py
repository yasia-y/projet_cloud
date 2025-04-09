def calculate_average(values: list) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)

def clean_data(data: list) -> list:
    # Filtre simple : on élimine les valeurs None
    return [x for x in data if x is not None]
