#db.py
import psycopg
from config import CONFIG

DB_CONFIG = CONFIG["postgres"]

def get_db_connection():
     return psycopg.connect(**DB_CONFIG)