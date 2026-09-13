import os
from sqlalchemy import create_engine, text

def initialize_database():
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'admin')
    password = os.getenv('DB_PASSWORD', 'adminpassword')
    dbname = os.getenv('DB_NAME', 'economics_gold')
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_engine(conn_str)
    
    print('[*] Initializing Gold layer schema and analytical tables...')
    with engine.begin() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS gold_economic_indicators (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                indicator_name VARCHAR(100) NOT NULL,
                value NUMERIC(18, 4) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS gold_bitcoin_metrics (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                close_price NUMERIC(18, 2) NOT NULL,
                volume NUMERIC(24, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
    print('[+] Gold layer tables successfully initialized.')

if __name__ == '__main__':
    initialize_database()
