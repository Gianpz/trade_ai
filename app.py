from flask import Flask, request, send_file
import pandas as pd
import numpy as np
import tensorflow as tf
from io import StringIO
import os

SEQUENCE_LENGTH = 50  # Il modello si aspetta sequenze di 50 timestep

app = Flask(__name__)

#carica il modello
print("Caricamento modello...")
model = tf.keras.models.load_model("model.h5", custom_objects={'mse': tf.keras.losses.MeanSquaredError()})
print("Modello caricato!")

@app.route("/predict", methods=["POST"])

def create_sequences(df, sequence_length):
    """ Crea sequenze della lunghezza richiesta dal modello """
    sequences = []
    
    for i in range(len(df) - sequence_length):
        sequences.append(df[i : i + sequence_length].values)  # Prende i dati in finestre di 50 righe
    
    return np.array(sequences)

def preprocess_data(csv_data):
    # Preprocessing dei dati storici delle candele (ad esempio, normalizzazione, creazione di sequenze)
    df = pd.read_csv(StringIO(csv_data))
    # Aggiungere il preprocessing desiderato (come normalizzazione e formattazione delle sequenze)
    return df

def predict_candles(df):
    print(df.dtypes)  # Controlla se ci sono colonne di tipo "object"
    print(df.head())  # Guarda il primo batch di dati
    global model  # Assumiamo che il modello sia già stato caricato

    try:
        # Seleziona solo colonne numeriche
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(np.float32)

        # Rimuove NaN
        df = df.dropna()

        # Creare sequenze di 50 timestep
        X = create_sequences(df, SEQUENCE_LENGTH)

        # Controlla se ci sono abbastanza dati
        if X.shape[0] == 0:
            raise ValueError("Non ci sono abbastanza dati per creare sequenze di 50 timestep!")

        print(f"Forma dell'input per il modello: {X.shape}")  # Dovrebbe essere (N, 50, 5)
        # Predizione del modello
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
