from flask import Flask, jsonify, request
from tvDatafeed import TvDatafeed, Interval

app = Flask(__name__)
tv = TvDatafeed()

@app.route('/api/candele5', methods=['GET'])
def get_candles():
    symbol = request.args.get('symbol', default='XAUUSD', type=str)
    exchange = request.args.get('exchange', default='OANDA', type=str)
    timeframe = request.args.get('timeframe', default='5minute', type=str)
    
    # Mappa il timeframe dall'input a Interval
    interval_map = {
        '1minute': Interval.in_1_minute,
        '5minute': Interval.in_5_minute,
        '15minute': Interval.in_15_minute,
        '30minute': Interval.in_30_minute,
        '1hour': Interval.in_1_hour
    }
    interval = interval_map.get(timeframe, Interval.in_5_minute)
    
    try:
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=300)
        candles = [
            {
                "time": index.strftime('%Y-%m-%d %H:%M:%S'),
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume']
            }
            for index, row in data.iterrows()
        ]
        return jsonify({"symbol": "XAUUSD", "timeframe": timeframe, "candles": candles}), 300
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/candele15', methods=['GET'])
def get_candles():
    symbol = request.args.get('symbol', default='XAUUSD', type=str)
    exchange = request.args.get('exchange', default='OANDA', type=str)
    timeframe = request.args.get('timeframe', default='15minute', type=str)
    
    # Mappa il timeframe dall'input a Interval
    interval_map = {
        '1minute': Interval.in_1_minute,
        '5minute': Interval.in_5_minute,
        '15minute': Interval.in_15_minute,
        '30minute': Interval.in_30_minute,
        '1hour': Interval.in_1_hour
    }
    interval = interval_map.get(timeframe, Interval.in_15_minute)
    
    try:
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=200)
        candles = [
            {
                "time": index.strftime('%Y-%m-%d %H:%M:%S'),
                "open": row['open'],
                "high": row['high'],
                "low": row['low'],
                "close": row['close'],
                "volume": row['volume']
            }
            for index, row in data.iterrows()
        ]
        return jsonify({"symbol": "XAUUSD", "timeframe": timeframe, "candles": candles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
