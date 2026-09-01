import os
import subprocess
import sys
from sqlalchemy import create_engine

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
    conn_str = f'postgresql://admin:adminpassword@{host}:5432/economics_gold'
    print(f'[*] Testing PostgreSQL connection at {host}...')
    try:
        engine = create_engine(conn_str)
        with engine.connect() as conn:
            print('[+] PostgreSQL Gold database RESPONDING successfully.')
    except Exception as e:
        print(f'[-] Database connection failed: {e}')

if __name__ == '__main__':
    check_infrastructure()
