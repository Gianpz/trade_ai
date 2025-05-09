from tvDatafeed import TvDatafeed, Interval
from flask import Flask,request, jsonify

app = Flask(__name__)

# Connessione a TradingView
tv = TvDatafeed()

@app.route('/candles', methods=['GET'])
def get_candles():
    symbol = request.args.get('symbol', 'XAUUSD')  # Default: Oro
    timeframe = request.args.get('timeframe', '15m')  # Default: 15 minuti

    interval_map = {
        '1m': Interval.in_1_minute,
        '5m': Interval.in_5_minute,
        '15m': Interval.in_15_minute,
        '1h': Interval.in_1_hour,
        '1d': Interval.in_daily
    }

    if timeframe not in interval_map:
        return jsonify({'error': 'Timeframe non valido'}), 400

    try:
        data = tv.get_hist(symbol=symbol, exchange='OANDA', interval=interval_map[timeframe], n_bars=500)
        #candles = data[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_dict(orient='records')
        candles = [ { "time": index.strftime('%Y-%m-%d %H:%M:%S'), "open": row['open'], "high": row['high'], "low": row['low'], "close": row['close'], "volume": row['volume'] } for index, row in data.iterrows() ]
        return jsonify(candles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
