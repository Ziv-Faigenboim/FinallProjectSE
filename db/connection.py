# connection.py

from pymongo import MongoClient
from db.db_collections import DBCollections  # Updated import

DB_NAME = "SensorData"

CONNECTION_STRING = "mongodb://localhost:27017/"



def get_db_collection(collection_name: DBCollections):
    client = MongoClient(CONNECTION_STRING)

    # Different settings according to connection type
    if collection_name == DBCollections.users:
        db = client["FinalProject"]
    else:
        db = client["SensorData"]

    return db[collection_name.value]



