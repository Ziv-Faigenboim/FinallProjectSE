import requests
import json
from datetime import datetime, timedelta

from db.collections import Collections
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
#////////////////
   #  reading_data=[{'Temperature': 20.495296,
   #  'Humidity': 0,
   #  'External Battery': 8.6482725,
   #  'Vibration SD': 0.006814902,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 479,
   #  'Strain': 2.4169922,
   #  'Leak': 0.4649414,
   #  'Generic MV': 457.03125,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T10:37:30.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.298916,
   #  'Humidity': 0,
   #  'External Battery': 8.679524,
   #  'Vibration SD': 0.006792996,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 481,
   #  'Strain': 2.8564453,
   #  'Leak': 0.46625978,
   #  'Generic MV': 457.69043,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T07:37:17.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.205Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 19.684597,
   #  'Humidity': 0,
   #  'External Battery': 8.6653185,
   #  'Vibration SD': 0.007144165,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.2958984,
   #  'Leak': 0.4649414,
   #  'Generic MV': 457.25098,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T17:37:30.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.207Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lng': 34.771616169581, 'lat': 31.2499921993526},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.233456,
   #  'Humidity': 0,
   #  'External Battery': 8.66816,
   #  'Vibration SD': 0.0064612655,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.515625,
   #  'Leak': 0.46560058,
   #  'Generic MV': 457.03125,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T12:37:53.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lng': 34.771616169581, 'lat': 31.2499921993526},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.495296,
   #  'Humidity': 0,
   #  'External Battery': 8.679524,
   #  'Vibration SD': 0.007231605,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.9550781,
   #  'Leak': 0.46625978,
   #  'Generic MV': 458.12988,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T08:37:06.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.205Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.98373,
   #  'Humidity': 0,
   #  'External Battery': 8.6482725,
   #  'Vibration SD': 0.011359292,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 2.1972656,
   #  'Leak': 0.4649414,
   #  'Generic MV': 457.4707,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T14:37:17.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lng': 34.771616169581, 'lat': 31.2499921993526},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.21835,
   #  'Humidity': 0,
   #  'External Battery': 8.671001,
   #  'Vibration SD': 0.009819803,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.2958984,
   #  'Leak': 0.46625978,
   #  'Generic MV': 458.12988,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T09:37:48.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.485226,
   #  'Humidity': 0,
   #  'External Battery': 8.6511135,
   #  'Vibration SD': 0.0062024915,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 479,
   #  'Strain': 2.1972656,
   #  'Leak': 0.46516114,
   #  'Generic MV': 457.4707,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T16:37:48.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.207Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.933376,
   #  'Humidity': 0,
   #  'External Battery': 8.656795,
   #  'Vibration SD': 0.0071467934,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.0761719,
   #  'Leak': 0.46538085,
   #  'Generic MV': 457.03125,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T15:37:06.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.651394,
   #  'Humidity': 0,
   #  'External Battery': 8.6596365,
   #  'Vibration SD': 0.0063843215,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 2.4169922,
   #  'Leak': 0.4649414,
   #  'Generic MV': 458.3496,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T11:37:12.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 19.830624,
   #  'Humidity': 0,
   #  'External Battery': 8.673841,
   #  'Vibration SD': 0.006307598,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.2958984,
   #  'Leak': 0.46604005,
   #  'Generic MV': 457.25098,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T13:37:35.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.206Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 21.003872,
   #  'Humidity': 0,
   #  'External Battery': 8.673841,
   #  'Vibration SD': 0.0067824516,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 481,
   #  'Strain': 3.0761719,
   #  'Leak': 0.46538085,
   #  'Generic MV': 460.54688,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T02:37:48.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.205Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lng': 34.771616169581, 'lat': 31.2499921993526},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 20.641323,
   #  'Humidity': 0,
   #  'External Battery': 8.66816,
   #  'Vibration SD': 0.006527126,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 2.1972656,
   #  'Leak': 0.46691895,
   #  'Generic MV': 457.91016,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T03:37:30.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.205Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'},
   # {'Temperature': 21.361385,
   #  'Humidity': 0,
   #  'External Battery': 8.6624775,
   #  'Vibration SD': 0.0058033573,
   #  'Battery Level': 100,
   #  'ANEMOMETER': 0,
   #  'EMF': 480,
   #  'Strain': 3.515625,
   #  'Leak': 0.46691895,
   #  'Generic MV': 458.3496,
   #  'Distance': 0,
   #  'sample_time_utc': '2024-12-24T01:37:06.000Z',
   #  'gw_read_time_utc': '2024-12-24T17:44:45.205Z',
   #  'reading_type': 'Periodic',
   #  'triggers': {},
   #  'business_unit_id': '6665581e2ea7990022f43138',
   #  'mac': 'D2:34:24:34:68:70',
   #  'device_name': 'G2.1 68:70',
   #  'fw_version': {'mcu': '2.8.48+011'},
   #  'location': {'lat': 31.2499921993526, 'lng': 34.771616169581},
   #  'unit_name': 'G2.1 68:70',
   #  'gw_id': '6DD4D29C-C96A-480E-A8F5-305E01DA3208',
   #  'gw_version': '3.3.0+110'}]
#////////////////

    email = "sce@atomation.net"
    password = "123456"

    mac_addresses = ["D2:34:24:34:68:70"]
    start_date = "2025-04-16T00:00:00.000Z"
    end_date = "2025-04-16T23:59:59.000Z"
    sensor_data_collection=get_db_collection(Collections.sensor_data)

    try:

        token = get_access_token(email, password)
        print("Access token retrieved successfully!")
        print(token)
        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        print("Sensor readings retrieved successfully!")
        print(json.dumps(sensor_readings, indent=2))
        sensor_data_collection.insert_one(sensor_readings)
        #//////////////remove
       # sensor_data_collection.delete_one({"sample_time_utc": "2024-12-24T08:37:06.000Z"})
        #///////////////remove

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
