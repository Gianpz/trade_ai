from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
api_key = "cut6n69r01qrsirl2c80cut6n69r01qrsirl2c8g"

@app.route('/api/candele', methods=['GET'])
def get_candles():
    symbol = "OANDA:XAU_USD"
    timeframe = request.args.get('timeframe', default='15', type=str)
    to_time = int(datetime.now().timestamp())
    from_time = int((datetime.now() - timedelta(days7)).timestamp())
    url = f"https://finnhub.io/api/v1/forex/candle?symbol={symbol}&resolution={timeframe}&from={from_time}&to={to_time}&token={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        candles = [
            {
                "time": datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'),
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": v
            }
            for t, o, h, l, c, v in zip(data['t'], data['o'], data['h'], data['l'], data['c'], data['v'])
        ][-200:]  # Ultime 200 candele
        return jsonify({"symbol": "XAU/USD", "timeframe": timeframe, "candles": candles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
