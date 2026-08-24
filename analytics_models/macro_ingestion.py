import os
import pandas as pd
import requests
from sqlalchemy import create_engine

def ingest_macro_data():
    print("[*] Fetching macroeconomic data from Central Bank of Brazil (BCB SGS - IPCA)...")
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Failed to access BCB API: {response.status_code}")
        
    data = response.json()
    if not data:
        raise ValueError("No data returned by BCB API.")
        
    df = pd.DataFrame(data)
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y').dt.date
    df['valor'] = pd.to_numeric(df['valor'])
    
    df_clean = pd.DataFrame({
        'date': df['data'],
        'indicator_name': 'IPCA - Monthly (%)',
        'value': df['valor']
    })
    
    db_host = os.getenv("DB_HOST", "localhost")
    conn_str = f"postgresql://admin:adminpassword@{db_host}:5432/economics_gold"
    engine = create_engine(conn_str)
    
    print(f"[*] Inserting {len(df_clean)} records into gold_economic_indicators...")
    df_clean.to_sql('gold_economic_indicators', engine, if_exists='replace', index=False)
    print("[+] Macroeconomic data ingestion completed successfully.")

if __name__ == "__main__":
    ingest_macro_data()
