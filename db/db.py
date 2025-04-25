import psycopg

from . config import CONFIG
from pymongo import MongoClient

#-------------------- Mongodb Connection ---------------
MONGO_CONFIG = CONFIG["mongodb"]

uri = f"mongodb://{MONGO_CONFIG['user']}:{MONGO_CONFIG['password']}@{MONGO_CONFIG['host']}:{MONGO_CONFIG['port']}/{MONGO_CONFIG['database']}?authSource={MONGO_CONFIG['auth_source']}"
client = MongoClient(uri)

def get_mongo_db() -> MongoClient:

    return client

if __name__ == "__main__":
    db = get_mongo_db()
    print("Connected to MongoDB. Database:", db.name)

#-------------------- Postgres Connection ---------------
DB_CONFIG = CONFIG["postgres"]

def get_db_connection():
     return psycopg.connect(**DB_CONFIG)