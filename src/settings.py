import os

CLIENT_TOKEN = os.environ['CLIENT_TOKEN']
DB_USER = os.environ['POSTGRES_USER']
DB_PASSWORD = os.environ['POSTGRES_PASSWORD']
DB_NAME = os.environ['POSTGRES_DB']
CONN_STRING = f"postgres://postgres:{DB_PASSWORD}@{DB_USER}:5432/{DB_NAME}"
