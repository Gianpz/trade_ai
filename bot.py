from flask import Flask,jsonify
from tvDatafeed import TvDatafeed, Interval

app = Flask(__name__)

tv = TvDatafeed()

@app.route("/dati")
def get_dati():
    dati = tv.get_hist(symbol="XAUUSD", exchange="OANDA", interval=Interval.in_15_minute, n_bars=2000)
    return jsonify(dati.to_dict())

@app.route('/')
def home():
    return "vai su /dati"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render usa la porta 10000
