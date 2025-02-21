from flask import Flask
import subprocess

app = Flask(__name__)

# Avvia lo script all'avvio del server
subprocess.run(["python", "pred.py", "model_williams_20.40.h5"])

@app.route('/')
def home():
    return "🚀 Server Flask in esecuzione su Render!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render usa la porta 10000
