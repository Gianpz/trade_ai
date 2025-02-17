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
    # Creare le sequenze di input per il modello e fare la predizione
    # Ad esempio, prendiamo gli ultimi 60 giorni di dati per fare la previsione
    X = df[-60:].values.reshape(1, 60, len(df.columns))
    predictions = model.predict(X)
    return predictions

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
