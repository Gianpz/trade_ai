from flask import Flask, request, jsonify

app = Flask(__name__)

# Memorizza i dati per ogni simbolo
market_data = {}

@app.route('/update', methods=['POST'])
def update_data():
    global market_data
    data = request.json
    symbol = data["symbol"]
    market_data[symbol] = data["candles"]  # Salva le candele più recenti
    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(market_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
