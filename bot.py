from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import flask as Flask

# 🔹 Crea l'istanza Flask
app = Flask(__name__)

# 🔹 Messaggio di conferma che il server è attivo
@app.route('/')
def home():
    return "Bot is running!"

# 🔹 Funzione del bot (esempio)
def start(update, context):
    update.message.reply_text("Ciao! Sono attivo.")

# 🔹 Avvio del bot Telegram in un thread separato
def run_bot():
    tv = TvDatafeed()
    
    # Scarica lo storico delle candele a 5 minuti per XAU/USD da OANDA
    df = tv.get_hist(
        symbol="XAUUSD",
        exchange="OANDA",   # Puoi anche usare FXCM, FOREXCOM, SAXO
        interval=Interval.in_5_minute,  # Timeframe 5 minuti
        n_bars=500  # Ultime 500 candele (modifica come necessario)
    )
    
    # Mostra le prime righe dei dati
    print(df)
    
    if df is not None and not df.empty:
        file = "candele.csv"
        df.to_csv(file, index=False)


# 🔹 Avvio del bot in background
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)  # Render userà Gunicorn per avviarlo
# Connessione anonima (senza login)
