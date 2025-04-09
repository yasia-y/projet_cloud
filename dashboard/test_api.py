from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Données simulées
capteurs = [
    {"id": 1, "type_donnée": "Temperature", "valeur": "19", "unite":"°C" "timestamp": "2023-10-01T12:00:00"},
    {"id": 2, "type_donnée": "Humidite", "valeur": "28", "unite":"%", "timestamp": "2023-10-01T12:00:00"},
]


@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(capteurs)


@app.route("/api/orders", methods=["POST"])
def add_order():
    data = request.json
    data["id"] = len(capteurs) + 1
    capteurs.append(data)
    data["timestamp"] = datetime.now().isoformat()
    return jsonify(data), 201


if __name__ == "__main__":
    app.run(debug=True, port=8000)
