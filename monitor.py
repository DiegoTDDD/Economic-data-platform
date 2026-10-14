import os
import subprocess
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

def check_infrastructure():
    print('=== PLATFORM HEALTH MONITOR ===')

    # 1. Check active Docker container status
    print('[*] Checking active Docker containers...')
    result = subprocess.run(['docker', 'ps', '--format', '{{.Names}} - {{.Status}}'], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout if result.stdout else 'No active containers found.')
    else:
        print('[!] Error querying Docker.')

    # 2. Test connectivity with the PostgreSQL Gold layer
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'admin')
    password = os.environ['DB_PASSWORD']
    dbname = os.getenv('DB_NAME', 'economics_gold')
    print(f'[*] Testing PostgreSQL connection at {host}...')
    try:
        engine = create_engine(URL.create('postgresql+psycopg2', username=user, password=password, host=host, port=int(port), database=dbname))
        with engine.connect() as conn:
            print('[+] PostgreSQL Gold database RESPONDING successfully.')
    except Exception as e:
        print(f'[-] Database connection failed: {e}')

if __name__ == '__main__':
    check_infrastructure()
