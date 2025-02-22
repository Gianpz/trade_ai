from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/candele', methods=['POST'])
def receive_candles():
    data = request.get_json()
    print("Dati ricevuti:", data)  # Stampa i dati per debug
    # Qui puoi elaborare i dati, salvarli, ecc.
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
