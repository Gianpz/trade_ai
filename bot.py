from flask import Flask
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed, Interval
import time
import re
import subprocess

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
