from tvDatafeed import TvDatafeed, Interval
import pandas as pd

# Connessione anonima (senza login)
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

