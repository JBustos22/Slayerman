import os
import keyring
from sqlalchemy import create_engine

if 'DFBOT_ENVIRONMENT' in os.environ and os.environ['DFBOT_ENVIRONMENT'] == 'CONTAINER':
    CLIENT_TOKEN = os.environ['CLIENT_TOKEN']
    DB_USER = os.environ['POSTGRES_USER']
    DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
    DB_NAME = os.environ['POSTGRES_DB']
    DB_ADDRESS = os.environ['POSTGRES_ADDRESS']
else:
    CLIENT_TOKEN = keyring.get_password('bot_token', 'dfbot')
    DB_PASSWORD = keyring.get_password('db_password', 'postgres')
    DB_USER = 'postgres'
    DB_NAME = 'Defrag'
    DB_ADDRESS = 'localhost'


CONN_STRING = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:5432/{DB_NAME}"
db = create_engine(CONN_STRING)