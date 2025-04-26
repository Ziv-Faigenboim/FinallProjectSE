# connection.py

from pymongo import MongoClient
import certifi
from db.db_collections import DBCollections  # Updated import
import platform
import ssl
import os
import sys

DB_NAME = "SensorData"

# Connection string with proper SSL settings
CONNECTION_STRING = "mongodb+srv://zivfa:5GTeldGLrjgYmIyM@cluster0.orsmafk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def get_db_connection_options():
    """
    Returns multiple connection options to try, from most secure to least secure
    """
    options = [
        # Option 1: Standard TLS with CA verification
        {
            "tls": True,
            "tlsCAFile": certifi.where(),
            "serverSelectionTimeoutMS": 5000
        },
        # Option 2: TLS with insecure mode
        {
            "tls": True,
            "tlsAllowInvalidCertificates": True,
            "serverSelectionTimeoutMS": 5000
        },
        # Option 3: Direct connection
        {
            "directConnection": True,
            "serverSelectionTimeoutMS": 5000
        }
    ]
    
    # On Windows, sometimes SSL context needs to be created manually
    if platform.system() == 'Windows':
        try:
            # Create a custom SSL context
            ctx = ssl.create_default_context(cafile=certifi.where())
            ctx.check_hostname = False
            
            # Option 4: With custom SSL context
            options.append({
                "tls": True,
                "tlsInsecure": True,
                "serverSelectionTimeoutMS": 5000
            })
        except Exception as e:
            print(f"Warning: Could not create custom SSL context: {e}")
    
    return options

def get_db_collection(collection_name: DBCollections):
    """
    Tries multiple connection options to connect to MongoDB
    """
    connection_options = get_db_connection_options()
    last_error = None
    
    # Try each connection option
    for i, options in enumerate(connection_options):
        try:
            print(f"Trying MongoDB connection option {i+1}...")
            client = MongoClient(CONNECTION_STRING, **options)
            
            # Test connection with a small operation
            client.admin.command('ping')
            print(f"✓ MongoDB connection successful with option {i+1}")
            
            # Determine which database to use based on collection
            if collection_name == DBCollections.users:
                db = client["FinalProject"]
            else:
                db = client["SensorData"]
                
            return db[collection_name.value]
            
        except Exception as e:
            print(f"✗ Connection option {i+1} failed: {e}")
            last_error = e
    
    # If we got here, all connection attempts failed
    print(f"ERROR: All MongoDB connection attempts failed. Last error: {last_error}")
    print("Falling back to local data.")
    
    # Return None to indicate connection failure
    return None



