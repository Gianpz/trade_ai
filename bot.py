from flask import Flask
import argparse
import tensorflow as tf
from tensorflow.keras.models import load_model
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

mp = "model_williams_20_40.h5"
# Estrai informazioni dal nome del modello
model_filename = os.path.basename(mp)
match = re.match(r"model_([a-z]+)_(\d+)_(\d+)\.h5", model_filename)
if not match:
    raise ValueError("Il nome del modello deve essere nel formato 'model_{ind}_{num_candle}_{seq}.h5'")

ind, num_candle, seq_length = match.groups()
IND = ind
PRED_LENGTH = int(num_candle)
SEQ_LENGTH = int(seq_length)

# Deriva il percorso dello scaler
scaler_path = f"scaler_{IND}_{PRED_LENGTH}_{SEQ_LENGTH}.pkl"
if not os.path.exists(scaler_path):
    raise FileNotFoundError(f"Il file {scaler_path} non è stato trovato.")

tv = TvDatafeed()
scaler = joblib.load(scaler_path)

# Feature base
base_features = ['Open', 'High', 'Low', 'Close', 'Volume']

# Funzioni indicatori
def williams_r(df, period=args.w_len):
    high_max = df['High'].rolling(window=period).max()
    low_min = df['Low'].rolling(window=period).min()
    wr = -100 * (high_max - df['Close']) / (high_max - low_min)
    return wr

def atr(df, period=args.a_len):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    true_range = np.maximum(high_low, np.maximum(high_close, low_close))
    return true_range.rolling(window=period).mean()

def volume_profile(df, seq_start, seq_length, price_bins=50):
    seq_data = df.iloc[seq_start:seq_start + seq_length]
    prices = seq_data['Close']
    volumes = seq_data['Volume']
    hist, bin_edges = np.histogram(prices, bins=price_bins, weights=volumes)
    poc_idx = np.argmax(hist)
    poc = (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2
    return poc

def volume_profile_vector(df, seq_start, seq_length, price_bins=10):
    seq_data = df.iloc[seq_start:seq_start + seq_length]
    prices = seq_data['Close']
    volumes = seq_data['Volume']
    hist, _ = np.histogram(prices, bins=price_bins, weights=volumes, density=True)
    return hist / hist.sum()

def vwap(df):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    vwap_value = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
    return vwap_value

def fetch_and_process_data():
    df = tv.get_hist(symbol="XAUUSD", exchange="OANDA", interval=Interval.in_15_minute, n_bars=2000)
    df = df.reset_index().rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume', 'datetime': 'Date'})

    if IND == "williams":
        df['Williams_%R'] = williams_r(df)
        features = base_features + ['Williams_%R']
    elif IND == "atr":
        df['ATR'] = atr(df)
        features = base_features + ['ATR']
    elif IND == "vwap":
        df['VWAP'] = vwap(df)
        features = base_features + ['VWAP']
    elif IND == "poc":
        df['POC'] = 0.0
        for i in range(len(df) - SEQ_LENGTH):
            df.loc[i + SEQ_LENGTH, 'POC'] = volume_profile(df, i, SEQ_LENGTH)
        features = base_features + ['POC']
    elif IND == "vp":
        features = base_features

    df.dropna(inplace=True)
    df[features] = scaler.transform(df[features])
    return df, features

def create_sequences(data, seq_length, features):
    if IND == "vp":
        PRICE_BINS = 10
        X = []
        df_temp = pd.DataFrame(data, columns=features)
        for i in range(len(data) - seq_length):
            seq = data[i:i + seq_length]
            vp_hist = volume_profile_vector(df_temp, i, seq_length, PRICE_BINS)
            X.append(np.hstack([seq, np.repeat(vp_hist[np.newaxis, :], seq_length, axis=0)]))
        return np.array(X)
    else:
        X = []
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
        return np.array(X)

class Attention(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(Attention, self).__init__(**kwargs)
        self.W_q = tf.keras.layers.Dense(128)
        self.W_v = tf.keras.layers.Dense(128)
        self.V = tf.keras.layers.Dense(1)

    def call(self, inputs):
        query, value = inputs
        query_transformed = self.W_q(query)
        value_transformed = self.W_v(value)
        attention_scores = self.V(tf.tanh(query_transformed + value_transformed))
        attention_weights = tf.nn.softmax(attention_scores, axis=1)
        return value * attention_weights

    def get_config(self):
        return super().get_config()

model = load_model(args.model_path, custom_objects={'Attention': Attention}, compile=False)

def update_predictions():
    while True:
        df_raw, features = fetch_and_process_data()
        if len(df_raw) < SEQ_LENGTH + PRED_LENGTH:
            print(f"Non ci sono abbastanza dati ({len(df_raw)} righe) per SEQ_LENGTH={SEQ_LENGTH}.")
            time.sleep(60)
            continue

        data = df_raw[features].values
        X = create_sequences(data, SEQ_LENGTH, features)
        predictions = model.predict(X[-1].reshape(1, SEQ_LENGTH, X.shape[2]), verbose=0)
        predictions = scaler.inverse_transform(predictions.reshape(PRED_LENGTH, len(features)))
        predicted_candles = pd.DataFrame(predictions, columns=features)

        # Correzione del gap
        df_denorm = df_raw.copy()
        df_denorm[features] = scaler.inverse_transform(df_denorm[features])
        last_real_close = df_denorm['Close'].tail(1).values[0]
        first_pred_close = predicted_candles['Close'].iloc[0]
        shift = last_real_close - first_pred_close
        predicted_candles['Close'] = predicted_candles['Close'] + shift

        # Timestamp per le previsioni
        last_time = df_denorm['Date'].tail(1).iloc[0]
        time_pred = [last_time + timedelta(minutes=15 * i) for i in range(1, PRED_LENGTH + 1)]

        # Stampa l'output
        print(f"\nAggiornamento: {datetime.now().strftime('%H:%M:%S')}")
        print(f"Ultima candela reale (Close): {last_real_close:.2f}")
        print(f"Previsioni (Close) per le prossime {PRED_LENGTH} candele (SEQ_LENGTH={SEQ_LENGTH}):")
        for i, t in enumerate(time_pred):
            print(f"  {t.strftime('%Y-%m-%d %H:%M')} - Close: {predicted_candles['Close'].iloc[i]:.2f}")

        time.sleep(900)  # 15 minuti

update_predictions()

@app.route('/')
def home():
    return f"{predicted_candles}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render usa la porta 10000
