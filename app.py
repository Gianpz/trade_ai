from flask import Flask, request, send_file
import pandas as pd
import numpy as np
import tensorflow as tf
from io import StringIO
import os

# Carica il modello
model = tf.keras.models.load_model('model_lstm.h5', custom_objects={'mse': tf.keras.losses.MeanSquaredError()})

app = Flask(__name__)

def preprocess_data(csv_data):
    # Preprocessing dei dati storici delle candele (ad esempio, normalizzazione, creazione di sequenze)
    df = pd.read_csv(StringIO(csv_data))
    # Aggiungere il preprocessing desiderato (come normalizzazione e formattazione delle sequenze)
    return df

def predict_candles(df):
    global model  # Assumiamo che il modello sia già stato caricato
    print(df.dtypes)  # Controlla se ci sono colonne di tipo "object"
    print(df.head())  # Guarda il primo batch di dati

    try:
        # Seleziona solo le colonne numeriche e converte in float
        df = df.select_dtypes(include=[np.number]).astype(np.float32)

        # Rimuove righe con valori NaN
        df = df.dropna()

        # Verifica che il DataFrame non sia vuoto
        if df.empty:
            raise ValueError("Il DataFrame è vuoto dopo il preprocessing!")

        # Converte il DataFrame in array per TensorFlow
        X = np.array(df)

        # Esegui la predizione
        predictions = model.predict(X)

        return predictions

    except Exception as e:
        print(f"Errore in predict_candles: {e}")
        raise


def create_tradingview_file(predictions):
    # Creare un file CSV con le predizioni delle candele
    df = pd.DataFrame(predictions, columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"])
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "File not found", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    # Carica il CSV
    csv_data = file.read().decode('utf-8')
    
    # Preprocessing e predizione
    df = preprocess_data(csv_data)
    predictions = predict_candles(df)
    
    # Crea il file per TradingView
    tradingview_file = create_tradingview_file(predictions)
    
    # Restituisce il file CSV per TradingView
    return send_file(tradingview_file, mimetype='text/csv', as_attachment=True, download_name='predictions.csv')

if __name__ == '__main__':
    app.run(debug=True)
