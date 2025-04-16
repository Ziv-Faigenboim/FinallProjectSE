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

def main():
    sensor_data_collection = get_db_collection(DBCollections.sensor_data)
    print("Connected to collection:", sensor_data_collection.full_name)

    email = "sce@atomation.net"
    password = "123456"

    mac_addresses = ["D2:34:24:34:68:70"]
    start_date = "2025-04-16T00:00:00.000Z"
    end_date = "2025-04-16T23:59:59.000Z"
    sensor_data_collection = get_db_collection(DBCollections.sensor_data)


    try:

        token = get_access_token(email, password)
        print("Access token retrieved successfully!")
        print(token)
        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        print("Sensor readings retrieved successfully!")
        print(json.dumps(sensor_readings, indent=2))
        sensor_data_collection.insert_one(sensor_readings)

        for reading in sensor_readings['data']['readings_data']:
        #for reading in reading_data:
            if sensor_data_collection.find_one({"sample_time_utc": reading["sample_time_utc"]}):
                print("sensor readings data already exists!")

                continue
            sensor_data_collection.insert_one(reading)
            print("inserted sensor readings data!")

    except Exception as e:
        print(e)

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
