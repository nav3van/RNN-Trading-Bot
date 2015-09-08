import os, sqlite3
from sys import exit

missing_auth_dir = '  neural-network-trading-bot/pyTrader/auth not found.\n' \
                   '    auth directory has been created'
missing_data_dir = '  neural-network-trading-bot/pyTrader/data not found.\n' \
                   '    data directory has been created'
missing_nonce_db = '  neural-network-trading-bot/pyTrader/auth/nonce.sqlite not found.\n' \
                   '    First db record must contain nonce value\n' \
                   '    expected by BTC-e API (0 if no prior trade\n' \
                   '    API requests have been made). Nonce has been\n' \
                   '    set to 1'
missing_credentials_json = '  neural-network-trading-bot/pyTrader/auth/api-credentials.json not found.\n' \
                           '    Credentials json format should be\n' \
                           '    {"api_secret": "your-account-secret", "api_key": "your-api-key"}'

missing_directory = []
missing_data = []

parent_dir = os.path.dirname(os.path.realpath('')) + '/'
nonce_file = 'auth/nonce.sqlite'
output_file = parent_dir + 'data/output.sqlite'

def notify_missing_directory():
    for directory in missing_directory:
        print(directory + '\n')

def notify_missing_data():
    for files in missing_data:
        print(files + '\n')

def check_data_files():
    if not os.path.exists('auth'):
        os.makedirs('auth')
        missing_directory.append(missing_auth_dir)
    else:
        print('Detected auth directory')

    if not os.path.exists(parent_dir + 'data'):
        os.makedirs(parent_dir + 'data')
        missing_directory.append(missing_data_dir)
    else:
        print('Detected data directory')

    if not os.path.isfile('auth/api-credentials.json'):
        with open('auth/api-credentials.json', 'w') as temp_api_cred:
            temp_api_cred.write('{"api_secret": "your-account-secret-goes-here", "api_key": "your-api-key-goes-here"}')
            temp_api_cred.close()
            missing_data.append(missing_credentials_json)
    else:
        print('Detected api-credentials.json')

    if not os.path.isfile('auth/nonce.sqlite'):
        new_nonce_db = sqlite3.connect('auth/nonce.sqlite')

        new_nonce_cursor = new_nonce_db.cursor()
        new_nonce_cursor.execute('CREATE TABLE IF NOT EXISTS nonce (current_nonce INTEGER)' )
        new_nonce_cursor.execute('INSERT INTO nonce (current_nonce) VALUES(1)')

        new_nonce_db.commit()
        new_nonce_db.close()
        missing_data.append(missing_nonce_db)
    else:
        print('Detected nonce.sqlite')

    if len(missing_directory) > 0 or len(missing_data) > 0:

        print('\n\n**************Missing Data Detected**************\n')

        if len(missing_directory) > 0:
            notify_missing_directory()

        if len(missing_data) > 0:
            notify_missing_data()

        print('*************************************************\n')

        if len(missing_data) > 0:
            exit(0)
    else:
        print('All required directories and files detected')
