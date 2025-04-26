import requests
import json
from datetime import datetime, timedelta

from db.db_collections import DBCollections

from db.connection import get_db_collection
base_url = "https://atapi.atomation.net/api/v1/s2s/v1_0"

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
            "sample_time_utc": True  # סינון לפי sample_time_utc במקום createdAt
        },
        "limit": {"page": 1, "page_size": 100}
    }
    sensors_readings_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print("🔎 Requesting data with filter:")
    print(json.dumps(sensors_readings_payload, indent=2))

    response = requests.post(
        sensors_readings_url,
        headers=sensors_readings_headers,
        data=json.dumps(sensors_readings_payload)
    )

    if response.status_code == 200:
        print("✅ Data fetched successfully!")
        return response.json()

    # הדפסה בולטת במקרה של כישלון
    print(f"❌ Failed to retrieve sensors readings! Status {response.status_code}")
    print(response.text)
    raise Exception(f"Failed to retrieve sensors readings: {response.json()}")


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

def main():
    "C4:45:5E:64:F9:3E"

    email = "pre_delivery@atomation.net"
    password = "123456"

    mac_addresses = ["C4:45:5E:64:F9:3E"]
    start_date = "2025-04-18T00:00:00.000Z"
    end_date = "2025-04-18T23:59:59.000Z"
    sensor_data_collection = get_db_collection(DBCollections.radiationsensor)

    print("Connected to collection:", sensor_data_collection.full_name)

    try:
        token = get_access_token(email, password)
        print("Access token retrieved successfully!")
        print(token)
        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        
        # Display full sensor data details
        if "data" in sensor_readings and "readings_data" in sensor_readings["data"]:
            readings_data = sensor_readings["data"]["readings_data"]
            print("\n===== RADIATION SENSOR DATA =====")
            for i, reading in enumerate(readings_data):
                print(f"\nReading #{i+1}:")
                print(json.dumps(reading, indent=2))
                
                # Display key metrics in a more readable format
                if reading:
                    print("\n--- Key Metrics ---")
                    print(f"Temperature: {reading.get('Temperature', 'N/A')} °C")
                    print(f"Humidity: {reading.get('Humidity', 'N/A')} %")
                    print(f"Battery Level: {reading.get('Battery Level', reading.get('BatteryLevel', 'N/A'))} %")
                    print(f"EMF: {reading.get('EMF', 'N/A')}")
                    print(f"Strain: {reading.get('Strain', 'N/A')}")
                    print(f"External Battery: {reading.get('External Battery', reading.get('ExternalBattery', 'N/A'))}")
                    print(f"Sample Time: {reading.get('sample_time_utc', 'N/A')}")
                    print("----------------------")
        else:
            print("No sensor data found in the response")
            
        # Save data to MongoDB as before
        sensor_data_collection.insert_one(sensor_readings)
        
        for reading in sensor_readings['data']['readings_data']:
            if sensor_data_collection.find_one({"sample_time_utc": reading["sample_time_utc"]}):
                print("Sensor reading already exists in database!")
                continue
            sensor_data_collection.insert_one(reading)
            print(f"Inserted sensor reading from {reading.get('sample_time_utc', 'unknown')} into database!")
        
        # Also print data from MongoDB to verify
        print("\n===== SAVED RADIATION SENSOR DATA FROM MONGODB =====")
        saved_readings = list(sensor_data_collection.find({}).limit(5))
        for i, doc in enumerate(saved_readings):
            if isinstance(doc, dict):
                print(f"\nDocument #{i+1} from MongoDB:")
                if "data" in doc and "readings_data" in doc["data"]:
                    # This is the complete response structure
                    print(f"Found {len(doc['data']['readings_data'])} readings")
                else:
                    # This is an individual reading
                    print(json.dumps({k: v for k, v in doc.items() if k != '_id'}, indent=2))

    except Exception as e:
        print(f"Error: {e}")

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
