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

def fetch_data():
    tv = TvDatafeed()
    df = tv.get_hist(symbol="XAUUSD", exchange="OANDA", interval=Interval.in_15_minute, n_bars=2000)
    df = df.reset_index().rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'})
    print(df.tail())
    
def update_predictions():
    while True:
        df_raw = fetch_data()
        time.sleep(900)  # 15 minuti
update_predictions()

@app.route('/')
def home():
    return f"{predicted_candles}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render usa la porta 10000
