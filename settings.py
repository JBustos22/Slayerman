import keyring

DB_PASSWORD = keyring.get_password('db_password', 'postgres')
CLIENT_TOKEN = keyring.get_password('bot_token', 'dfbot')
