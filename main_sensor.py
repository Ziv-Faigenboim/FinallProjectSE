import requests
import json
base_url = "https://atapi.atomation.net/api/v1/s2s/v1_0"
def get_access_token(email, password):

    login_url = f"{base_url}/auth/login"

    login_payload = {
        "email": email,
        "password": password
    }

    login_headers = {
        "Content-Type": "application/json",
        "app_version": "1.8.5",
        "access_type": "5"
    }
    response = requests.post(login_url, headers=login_headers, data=json.dumps(login_payload))
    if response.status_code == 200:
        return response.json()["data"]["token"]
    else:
        raise Exception(f"Login failed: {response.json()}")
def get_sensor_readings(token, mac_addresses, start_date, end_date):

    sensors_readings_url = f"{base_url}/sensors_readings"
    sensors_readings_payload = {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "mac": mac_addresses,
            "createdAt": True
        },
        "limit": {
            "page": 1,
            "page_size": 100
        }
    }

    sensors_readings_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.post(sensors_readings_url, headers=sensors_readings_headers, data=json.dumps(sensors_readings_payload))
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve sensors readings: {response.json()}")

def main():

    email = "sce@atomation.net"
    password = "123456"

    mac_addresses = ["E9:19:79:09:A1:AD"]
    start_date = "2024-12-11T00:00:00.000Z"
    end_date = "2024-12-12T23:59:59.000Z"

    try:

        token = get_access_token(email, password)
        print("Access token retrieved successfully!")
        print(token)

        sensor_readings = get_sensor_readings(token, mac_addresses, start_date, end_date)
        print("Sensor readings retrieved successfully!")
        print(json.dumps(sensor_readings, indent=2))

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
    main()

   # authenticate_and_get_token("sce@atomation.net", "123456", app_version='1.8.5', access_type=5)