# setup_db.py

from db.connection import get_db_collection
from db.db_collections import DBCollections

# If you only want "users" collection, remove sensor_data references

users_col = get_db_collection(DBCollections.users)

# Insert a test user
users_col.insert_one({
    "email": "test@example.com",
    "password": "1234"  # plaintext for testing
})

print("? Dummy user inserted.")
