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
    start_date_br = "01/01/2015"
    end_date_br = datetime.now().strftime("%d/%m/%Y")
    start_date_iso = "2015-01-01"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # 1. IPCA (Series 433)
    print("[*] Fetching IPCA from Central Bank of Brazil (BCB SGS Series 433)...")
    try:
        url_ipca = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json&dataInicial={start_date_br}&dataFinal={end_date_br}"
        response = session.get(url_ipca, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce').dt.date
                df['value'] = pd.to_numeric(df['valor'], errors='coerce')
                df['indicator_name'] = "IPCA - Monthly (%)"
                clean_df = df.dropna(subset=['date', 'value'])[['date', 'indicator_name', 'value']]
                all_dfs.append(clean_df)
                print(f"[+] Successfully loaded {len(clean_df)} records for IPCA.")
    except Exception as e:
        print(f"[-] Error fetching IPCA: {e}")

    # 2. Selic Target Rate (Series 432) fetched via raw JSON without URL params, filtered locally
    print("[*] Fetching Selic Target Rate from Central Bank of Brazil (BCB SGS Series 432)...")
    try:
        url_selic = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json"
        response = session.get(url_selic, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce').dt.date
                df['value'] = pd.to_numeric(df['valor'], errors='coerce')
                df['indicator_name'] = "Selic Target Rate (% a.a.)"
                min_date = pd.to_datetime(start_date_iso).date()
                clean_df = df.dropna(subset=['date', 'value'])
                clean_df = clean_df[clean_df['date'] >= min_date][['date', 'indicator_name', 'value']]
                all_dfs.append(clean_df)
                print(f"[+] Successfully loaded {len(clean_df)} records for Selic Target Rate.")
        else:
            print(f"[-] Warning: Selic API returned status {response.status_code}")
    except Exception as e:
        print(f"[-] Error fetching Selic Target Rate: {e}")

    # 3. USD/BRL Exchange Rate via yfinance
    print("[*] Fetching USD/BRL Exchange Rate via yfinance...")
    try:
        usdcny = yf.download("USDBRL=X", start=start_date_iso, progress=False)
        if not usdcny.empty:
            usdcny = usdcny.reset_index()
            if isinstance(usdcny.columns, pd.MultiIndex): 
                usdcny.columns = [col[0] if col[0] != '' else col[1] for col in usdcny.columns]
            close_col = 'Close' if 'Close' in usdcny.columns else usdcny.columns[1]
            df_usd = pd.DataFrame({
                'date': pd.to_datetime(usdcny['Date'], errors='coerce').dt.date,
                'indicator_name': 'USD/BRL Exchange Rate (Purchase)',
                'value': pd.to_numeric(usdcny[close_col], errors='coerce')
            }).dropna(subset=['date', 'value'])
            all_dfs.append(df_usd)
            print(f"[+] Successfully loaded {len(df_usd)} records for USD/BRL Exchange Rate.")
    except Exception as e:
        print(f"[-] Error fetching USD/BRL via yfinance: {e}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True).drop_duplicates(subset=['date', 'indicator_name'])
        print(f"[*] Inserting total of {len(final_df)} macroeconomic records into gold_economic_indicators...")
        final_df.to_sql('gold_economic_indicators', engine, if_exists='replace', index=False)
        print("[+] Macroeconomic multi-indicator ingestion completed successfully with 0 errors.")
    else:
        raise ValueError("Critical error: No macroeconomic data retrieved from any source.")

if __name__ == "__main__":
    ingest_macro_data()
