import requests
import json
import os
import traceback
from datetime import datetime, timedelta

from db.db_collections import DBCollections
from db.connection import get_db_collection

base_url = "https://atapi.atomation.net/api/v1/s2s/v1_0"
# File path for local sensor data backup
LOCAL_BACKUP_PATH = "data/sensor_backup.json"

def get_access_token(email, password):
    login_url = f"{base_url}/auth/login"
    login_payload = {"email": email, "password": password}
    login_headers = {
        "Content-Type": "application/json",
        "app_version": "1.8.5",
        "access_type": "5"
    }

    response = requests.post(login_url, headers=login_headers, data=json.dumps(login_payload))
    response.raise_for_status()
    return response.json()["data"]["token"]

def get_sensor_readings(token, mac_addresses, start_date, end_date):
    sensors_readings_url = f"{base_url}/sensors_readings"
    sensors_readings_payload = {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "mac": mac_addresses,
            "createdAt": True
        },
        "limit": {"page": 1, "page_size": 100}
    }
    sensors_readings_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(sensors_readings_url, headers=sensors_readings_headers, data=json.dumps(sensors_readings_payload))
    if response.status_code == 200:
        return response.json()

    raise Exception(f"Failed to retrieve sensors readings: {response.json()}")
    # response.raise_for_status()
    # return response.json()

def get_latest_sensor_data():
    """
    Fetch the most recent data for the sensor.
    """
    try:
        email = "sce@atomation.net"
        password = "123456"
        mac_addresses = ["E9:19:79:09:A1:AD"]
        start_date = datetime.utcnow().strftime("%Y-%m-%dT00:00:00.000Z")
        end_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59.000Z")

        token = get_access_token(email, password)
        readings = get_sensor_readings(token, mac_addresses, start_date, end_date)

        if "data" in readings and "readings_data" in readings["data"]:
            readings_data = readings["data"]["readings_data"]

            if readings_data:
                latest_reading = readings_data[0]
                return {
                    "temperature": latest_reading.get("Temperature", "N/A"),
                    "humidity": latest_reading.get("Humidity", "N/A"),
                    "battery": latest_reading.get("BatteryLevel", "N/A"),
                    "sample_time": latest_reading.get("SampleTime", "N/A"),
                }
            else:
                return {"error": "No readings available"}
        else:
            return {"error": "No data found"}
    except Exception as e:
        return {"error": str(e)}

def get_historical_sensor_data():
    """
    Fetch historical data for the sensor.
    """
    try:
        email = "sce@atomation.net"
        password = "123456"
        mac_addresses = ["E9:19:79:09:A1:AD"]
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000Z")
        end_date = datetime.utcnow().strftime("%Y-%m-%dT23:59:59.000Z")

        token = get_access_token(email, password)
        readings = get_sensor_readings(token, mac_addresses, start_date, end_date)

        if "data" in readings and "readings_data" in readings["data"]:
            history = readings["data"]["readings_data"]
            formatted_history = [
                {
                    "temperature": entry.get("Temperature", "N/A"),
                    "humidity": entry.get("Humidity", "N/A"),
                    "battery": entry.get("BatteryLevel", "N/A"),
                    "sample_time": entry.get("SampleTime", "N/A"),
                }
                for entry in history
            ]
            return formatted_history
        else:
            return {"error": "No historical data found"}
    except Exception as e:
        return {"error": str(e)}

def save_to_local_backup(data):
    """Save sensor readings to a local backup file"""
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load existing backup if available
        existing_data = []
        if os.path.exists(LOCAL_BACKUP_PATH):
            with open(LOCAL_BACKUP_PATH, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error reading backup file, creating new backup")
                    existing_data = []
        
        # Add new data (avoid duplicates based on sample_time_utc)
        if 'data' in data and 'readings_data' in data['data']:
            new_entries = 0
            existing_times = {entry.get('sample_time_utc') for entry in existing_data 
                             if 'sample_time_utc' in entry}
            
            for reading in data['data']['readings_data']:
                if reading.get('sample_time_utc') not in existing_times:
                    existing_data.append(reading)
                    new_entries += 1
            
            # Save updated data
            with open(LOCAL_BACKUP_PATH, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            print(f"Saved {new_entries} new readings to local backup ({len(existing_data)} total)")
        else:
            print("No readings data to backup")
    except Exception as e:
        print(f"Error saving to local backup: {e}")
        traceback.print_exc()

def main():
    email = "sce@atomation.net"
    password = "123456"

    mac_addresses = ["D2:34:24:34:68:70"]
    # Use current date for data collection
    current_date = datetime.utcnow().strftime("%Y-%m-%dT")
    start_date = f"{current_date}00:00:00.000Z"
    end_date = f"{current_date}23:59:59.000Z"
    
    # Get MongoDB collection
    sensor_data_collection = get_db_collection(DBCollections.sensor_data)
    mongodb_available = sensor_data_collection is not None

    try:
        # Get sensor data from API
        token = get_access_token(email, password)
        print("Access token retrieved successfully!")
        
        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        print("Sensor readings retrieved successfully!")
        
        # Save to local backup first for data safety
        save_to_local_backup(sensor_readings)
        
        # Try to save to MongoDB if available
        if mongodb_available:
            try:
                # Insert the full API response
                sensor_data_collection.insert_one(sensor_readings)
                print("Inserted full sensor readings response to MongoDB")
                
                # Insert individual readings
                for reading in sensor_readings['data']['readings_data']:
                    if sensor_data_collection.find_one({"sample_time_utc": reading["sample_time_utc"]}):
                        print(f"Skipping duplicate reading for {reading['sample_time_utc']}")
                        continue
                    sensor_data_collection.insert_one(reading)
                    print(f"Inserted reading for {reading['sample_time_utc']}")
            except Exception as mongo_error:
                print(f"MongoDB error: {mongo_error}")
                traceback.print_exc()
        else:
            print("MongoDB connection not available, data saved to local backup only")
            
        # Update readings.json for web application
        update_readings_json(sensor_readings)
        
    except Exception as e:
        print(f"Error in main process: {e}")
        traceback.print_exc()

def update_readings_json(sensor_readings=None):
    """Update readings.json file with latest sensor data"""
    try:
        readings_file_path = os.path.join('static', 'readings.json')
        os.makedirs('static', exist_ok=True)
        
        # If no data provided, try to load from local backup
        if sensor_readings is None:
            if os.path.exists(LOCAL_BACKUP_PATH):
                with open(LOCAL_BACKUP_PATH, 'r') as f:
                    backup_data = json.load(f)
                    
                # Format backup data to match expected structure
                if backup_data:
                    sensor_readings = {
                        "code": 200,
                        "message": "",
                        "data": {
                            "readings_data": backup_data[:100],  # Limit to last 100 readings
                            "pageCount": 1,
                            "totalCount": len(backup_data)
                        }
                    }
        
        # If we have sensor readings, write to readings.json
        if sensor_readings and "data" in sensor_readings and "readings_data" in sensor_readings["data"]:
            with open(readings_file_path, 'w') as f:
                json.dump(sensor_readings, f, indent=2)
            print(f"Updated {readings_file_path} with {len(sensor_readings['data']['readings_data'])} readings")
        else:
            print("No sensor data available to update readings.json")
            
    except Exception as e:
        print(f"Error updating readings.json: {e}")
        traceback.print_exc()

def authenticate_and_get_token(email, password, app_version='1.8.5', access_type=5):
    url = 'https://atapi.atomation.net/api/v1/s2s/v1_0/auth/login'

    headers = {
        'app_version': app_version,
        'access_type': str(access_type)
    }

    payload = {
        'email': email,
        'password': password
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        token = data['data']['token']
        expires_in = data['data']['expires_in']
        refresh_token = data['data']['refresh_token']
        print("Authentication successful.")
        print(f"Token: {token}")
        print(f"Expires in: {expires_in} seconds")
        print(f"Refresh Token: {refresh_token}")
        return token, refresh_token
    else:
        print(f"Authentication failed. Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        return None, None

if __name__ == "__main__":
    # If you want to test this script directly, uncomment below:
    # data = get_latest_sensor_data()
    # print(data)
    main()
    pass
