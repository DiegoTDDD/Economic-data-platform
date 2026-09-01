import os
import pandas as pd
import yfinance as yf
from sqlalchemy import create_engine

def ingest_bitcoin_data():
    print("[*] Downloading historical Bitcoin (BTC-USD) data...")

    # Download Bitcoin data
    btc = yf.download("BTC-USD", start="2020-01-01", progress=False)

    if btc.empty:
        raise ValueError("No data returned by yfinance for BTC-USD.")

    # Reset the index to turn 'Date' into a regular column
    btc = btc.reset_index()

    # Handle MultiIndex columns in case yfinance returns tuples
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = [col[0] if col[0] != '' else col[1] for col in btc.columns]

    # Rename and select only the essential columns
    # Depending on the version, the column may come as 'Close' or 'Adj Close'
    close_col = 'Close' if 'Close' in btc.columns else btc.columns[1]

    df_clean = pd.DataFrame({
        'date': pd.to_datetime(btc['Date']).dt.date,
        'close_price': btc[close_col],
        'volume': btc['Volume'] if 'Volume' in btc.columns else 0
    })

    # Drop null values
    df_clean = df_clean.dropna(subset=['close_price'])

    # Set up connection to the Gold database on Docker
    db_host = os.getenv("DB_HOST", "localhost")
    conn_str = f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold"
    engine = create_engine(conn_str)

    print(f"[*] Inserting {len(df_clean)} records into the gold_bitcoin_metrics table...")
    df_clean.to_sql('gold_bitcoin_metrics', engine, if_exists='replace', index=False)
    print("[+] Bitcoin ingestion completed successfully.")

if __name__ == "__main__":
    ingest_bitcoin_data()
