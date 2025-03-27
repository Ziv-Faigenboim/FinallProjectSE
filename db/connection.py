# connection.py

from pymongo import MongoClient
from db.db_collections import DBCollections  # Updated import

DB_NAME = "FinalProject"
CONNECTION_STRING = 'mongodb://localhost:27017/'

def get_db_collection(collection_name: DBCollections):
    client = MongoClient(CONNECTION_STRING)
    return client[DB_NAME][collection_name.value]
