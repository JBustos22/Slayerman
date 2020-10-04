import keyring

CLIENT_TOKEN = keyring.get_password('bot_token', 'dfbot')

DB_PASSWORD = keyring.get_password('db_password', 'postgres')
CONN_STRING = f"postgres://postgres:{DB_PASSWORD}@localhost:5432/Defrag"