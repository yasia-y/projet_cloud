from flask import Flask, jsonify, request

app = Flask(__name__)

# Données simulées
orders = [
    {"id": 1, "item": "Temperature", "quantity": "19°C"},
    {"id": 2, "item": "Humidite", "quantity": "28%"},
]


@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)


@app.route("/api/orders", methods=["POST"])
def add_order():
    data = request.json
    data["id"] = len(orders) + 1
    orders.append(data)
    return jsonify(data), 201


if __name__ == "__main__":
    app.run(debug=True, port=8000)
