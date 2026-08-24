import os
import pandas as pd
import requests
from datetime import datetime
from sqlalchemy import create_engine

INDICATORS = {
    "IPCA - Monthly (%)": "433",
    "Selic Rate - Daily (% a.a.)": "11",
    "USD/BRL Exchange Rate (Purchase)": "10813"
}

def ingest_macro_data():
    db_host = os.getenv("DB_HOST", "localhost")
    conn_str = f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold"
    engine = create_engine(conn_str)
    
    all_dfs = []
    start_date = "01/01/2015"
    end_date = datetime.now().strftime("%d/%m/%Y")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    print("[*] Fetching comprehensive macroeconomic series from Central Bank of Brazil (BCB SGS)...")
    for name, series_id in INDICATORS.items():
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.date
                df['value'] = pd.to_numeric(df['valor'], errors='coerce')
                df['indicator_name'] = name
                all_dfs.append(df[['date', 'indicator_name', 'value']])
                print(f"[+] Loaded {len(df)} records for indicator: {name}")
            else:
                print(f"[-] Warning: Empty response for series {series_id} ({name})")
        else:
            print(f"[-] Warning: Failed to fetch series {series_id} for {name} (Status: {response.status_code})")
            
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True).dropna(subset=['value'])
        print(f"[*] Inserting total of {len(final_df)} macroeconomic records into gold_economic_indicators...")
        final_df.to_sql('gold_economic_indicators', engine, if_exists='replace', index=False)
        print("[+] Macroeconomic multi-indicator ingestion completed successfully.")
    else:
        raise ValueError("No macroeconomic data retrieved from BCB APIs.")

if __name__ == "__main__":
    ingest_macro_data()
