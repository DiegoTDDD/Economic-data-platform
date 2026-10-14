import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

def initialize_database():
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'admin')
    password = os.environ['DB_PASSWORD']
    dbname = os.getenv('DB_NAME', 'economics_gold')
    # URL.create escapes special characters in the password (@ : / # % ...)
    engine = create_engine(URL.create('postgresql+psycopg2', username=user, password=password, host=host, port=int(port), database=dbname))
    
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
