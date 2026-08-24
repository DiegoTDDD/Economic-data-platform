import os
import pandas as pd
import requests
import yfinance as yf
from datetime import datetime
from sqlalchemy import create_engine

def ingest_macro_data():
    db_host = os.getenv("DB_HOST", "localhost")
    conn_str = f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold"
    engine = create_engine(conn_str)
    
    all_dfs = []
    start_date = "2015-01-01"
    start_date_br = "01/01/2015"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # 1. Ingest IPCA from BCB SGS (Series 433)
    print("[*] Fetching IPCA from Central Bank of Brazil (BCB SGS)...")
    try:
        url_ipca = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={start_date_br}"
        response = session.get(url_ipca, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.date
                df['value'] = pd.to_numeric(df['valor'], errors='coerce')
                df['indicator_name'] = "IPCA - Monthly (%)"
                filtered_df = df[['date', 'indicator_name', 'value']]
                all_dfs.append(filtered_df)
                print(f"[+] Loaded {len(filtered_df)} records for IPCA")
    except Exception as e:
        print(f"[-] Error fetching IPCA: {e}")

    # 2. Ingest Selic Rate from BCB SGS (Series 11) with date constraint to prevent 406 payload error
    print("[*] Fetching Selic Rate from Central Bank of Brazil (BCB SGS)...")
    try:
        url_selic = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json&dataInicial={start_date_br}"
        response = session.get(url_selic, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.date
                df['value'] = pd.to_numeric(df['valor'], errors='coerce')
                df['indicator_name'] = "Selic Rate - Daily (% a.a.)"
                filtered_df = df[['date', 'indicator_name', 'value']]
                all_dfs.append(filtered_df)
                print(f"[+] Loaded {len(filtered_df)} records for Selic Rate")
        else:
            print(f"[-] Warning: Selic API returned status {response.status_code}")
    except Exception as e:
        print(f"[-] Error fetching Selic Rate: {e}")

    # 3. Ingest USD/BRL Exchange Rate via yfinance (Robust & Reliable)
    print("[*] Fetching USD/BRL Exchange Rate via yfinance...")
    try:
        usdcny = yf.download("USDBRL=X", start=start_date, progress=False)
        if not usdcny.empty:
            usdcny = usdcny.reset_index()
            if isinstance(usdcny.columns, pd.MultiIndex): 
                usdcny.columns = [col[0] if col[0] != '' else col[1] for col in usdcny.columns]
            close_col = 'Close' if 'Close' in usdcny.columns else usdcny.columns[1]
            df_usd = pd.DataFrame({
                'date': pd.to_datetime(usdcny['Date']).dt.date,
                'indicator_name': 'USD/BRL Exchange Rate (Purchase)',
                'value': usdcny[close_col]
            }).dropna(subset=['value'])
            all_dfs.append(df_usd)
            print(f"[+] Loaded {len(df_usd)} records for USD/BRL Exchange Rate")
    except Exception as e:
        print(f"[-] Error fetching USD/BRL via yfinance: {e}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True).dropna(subset=['value'])
        print(f"[*] Inserting total of {len(final_df)} macroeconomic records into gold_economic_indicators...")
        final_df.to_sql('gold_economic_indicators', engine, if_exists='replace', index=False)
        print("[+] Macroeconomic multi-indicator ingestion completed successfully.")
    else:
        raise ValueError("No macroeconomic data retrieved from sources.")

if __name__ == "__main__":
    ingest_macro_data()
