from pymongo import MongoClient

from db.collections import Collections

DB_NAME="SensorData"

CONNECTION_STRING = 'mongodb://localhost/FinalProject'


def get_db_collection(collection_name: Collections):
    client = MongoClient(CONNECTION_STRING)

    return client[DB_NAME][collection_name.value]
