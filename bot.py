from flask import Flask, jsonify, request
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/api/candele', methods=['GET'])
def get_candles():
    # Parametri opzionali dall'URL (es. simbolo e timeframe)
    symbol = request.args.get('symbol', default='XAUUSD', type=str)  # Default: Apple
    timeframe = request.args.get('timeframe', default='15m', type=str)  # Default: 1 giorno
    candle_count = 200  # Numero fisso di candele

    # Configura il periodo per ottenere le ultime 200 candele
    try:
        # Crea oggetto Ticker
        ticker = yf.Ticker(symbol)

        # Calcola il periodo necessario (dipende dal timeframe)
        if timeframe == '1m':
            period = f"{candle_count}min"
        elif timeframe == '5m':
            period = f"{candle_count * 5}min"
        elif timeframe == '15m':
            period = f"{candle_count * 15}min"
        elif timeframe == '1h':
            period = f"{candle_count}d"
        elif timeframe == '1d':
            period = f"{candle_count}d"
        else:
            return jsonify({"error": "Timeframe non supportato. Usa: 1m, 5m, 15m, 1h, 1d"}), 400

        # Scarica i dati
        df = ticker.history(period=period, interval=timeframe)

        # Verifica se ci sono dati
        if df.empty:
            return jsonify({"error": "Nessun dato disponibile per il simbolo specificato"}), 404

        # Limita a 200 candele (le più recenti)
        df = df.tail(candle_count)

        # Converte i dati in un formato JSON-friendly
        candles = [
            {
                "time": index.strftime('%Y-%m-%d %H:%M:%S'),
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close'],
                "volume": row['Volume']
            }
            for index, row in df.iterrows()
        ]

        # Risposta JSON
        response = {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Errore durante il recupero dei dati: {str(e)}"}), 500

@app.route('/')
def home():
    return jsonify({"message": "Benvenuto! Usa /api/candele?symbol=AAPL&timeframe=1d per ottenere i dati"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
