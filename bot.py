from flask import Flask, request, jsonify

app = Flask(__name__)

# Variabile per memorizzare i dati ricevuti
market_data = {}

@app.route('/update', methods=['POST'])
def update_data():
    global market_data
    market_data = request.json  # Salva i dati ricevuti
    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(market_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)