import tensorflow as tf
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
import os
from datetime import datetime, timedelta

app = Flask(__name__)

#carica il modello
print("Caricamento modello...")
model = tf.keras.models.load_model("model_lstm.h5", custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
print("Modello caricato!")

# Funzione per creare sequenze
def create_sequences(df, sequence_length):
    sequences = []
    for i in range(len(df) - sequence_length):
        sequences.append(df.iloc[i:i + sequence_length].values)
    return np.array(sequences)

# Funzione per generare timestamp a partire dalla data di inizio
def generate_timestamps(start_date, num_predictions):
    timestamps = []
    for i in range(num_predictions):
        timestamps.append(int((start_date + timedelta(minutes=i * 5)).timestamp()))  # intervallo di 5 minuti per ogni candela
    return timestamps

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["file"]
        df = pd.read_csv(file)

        # Controlla se il DataFrame è vuoto
        if df.empty:
            return jsonify({"error": "DataFrame vuoto, impossibile creare sequenze"}), 400

        # Preprocessing
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(np.float32)
        df = df.dropna()

        # Creazione delle sequenze
        SEQUENCE_LENGTH = 50
        X = create_sequences(df, SEQUENCE_LENGTH)

        # Controlla se ci sono abbastanza dati
        if X.shape[0] == 0:
            return jsonify({"error": "Dati insufficienti per creare sequenze"}), 400

        # Predizione
        predictions = model.predict(X)

        # Genera i timestamp (a partire dall'ultima data del DataFrame)
        last_timestamp = pd.to_datetime(df.iloc[-1]["Close"]).timestamp()
        timestamps = generate_timestamps(datetime.fromtimestamp(last_timestamp), len(predictions))

        # Crea un DataFrame per le previsioni
        pred_df = pd.DataFrame(predictions, columns=["Open", "High", "Low", "Close", "Volume"])
        pred_df["Timestamp"] = timestamps

        # Esporta il risultato in un file CSV
        output_filename = "predictions.csv"
        pred_df = pred_df[['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
        pred_df.to_csv(output_filename, index=False)

        return jsonify({"message": f"Predizioni salvate in {output_filename}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
