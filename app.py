import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import joblib
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import os
from datetime import datetime, timedelta

app = Flask(__name__)

#carica il modello
print("Caricamento modello...")
model = tf.keras.models.load_model("model.h5")
scaler = joblib.load('scaler.pkl')
print("Modello caricato!")

# Creazione dataset
def create_dataset(data, time_step=10):
    X = []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i+time_step), :])
    return np.array(X)

time_step = 10

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        # Caricamento dati e scaler
        #df = pd.read_csv(file, parse_dates=["Time"])
        df = pd.read_csv(file)
        print("file caricato!")
        df.set_index("Time", inplace=True)
        print("file set index!")
        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        scaled_data = scaler.transform(df[features])

        print(df.head())  # Mostra le prime righe
        print(df.columns)  # Mostra i nomi delle colonne

        # Controlla se il DataFrame è vuoto
        if df.empty:
            return jsonify({"error": "DataFrame vuoto, impossibile creare sequenze"}), 400

        X = create_dataset(scaled_data, time_step)
        # Previsioni sui dati esistenti
        predictions = model.predict(X)
        predictions = scaler.inverse_transform(np.hstack([predictions, np.zeros((predictions.shape[0], 1))]))[:, :-1]

        # Previsione candele future
        nu = 50
        future_predictions = np.zeros((nu, 4))
        last_sequence = X[-1]

        for i in range(nu):
            new_prediction = model.predict(last_sequence.reshape(1, time_step, X.shape[2]))
            future_predictions[i] = new_prediction[0]
            new_sequence = np.roll(last_sequence, -1, axis=0)
            new_sequence[-1] = np.append(new_prediction[0], [0])
            last_sequence = new_sequence

        # De-normalizzazione
        future_predictions = scaler.inverse_transform(np.hstack([future_predictions, np.zeros((nu, 1))]))[:, :-1]

        # Salvataggio delle previsioni future in un file CSV
        future_df = pd.DataFrame(future_predictions, columns=['Open', 'High', 'Low', 'Close'])
        future_df.to_csv('flask_resp.csv', index=False)
        print(f"Previsioni salvate in flask_resp.csv")

        return jsonify({"message": f"Predizioni salvate in flask_resp.csv"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
