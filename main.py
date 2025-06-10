import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
# Update these imports to match your file structure
from db.db_collections import DBCollections  # rename your old collections.py to db_collections.py
from db.connection import get_db_collection

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session and flashing messages

# MongoDB's collection for users
users_col = get_db_collection(DBCollections.users)

# ===================== Sensor Data from JSON =====================
# Map sensor IDs to their data files
SENSOR_FILES = {
    "original": "readings.json",
    "park-givaat-rambam": "sensor-park-givaat-rambam.json",
    "gan-hashlosha-park": "sensor-gan-hashlosha-park.json",
    "central-bus-station": "sensor-central-bus-station.json",
    "bgu-university": "sensor-bgu-university.json",
    "soroka-medical-center": "sensor-soroka-medical-center.json"
}

def get_latest_sensor_data(sensor_id="original"):
    try:
        # Get the filename for the sensor
        filename = SENSOR_FILES.get(sensor_id, "readings.json")
        
        # Get the latest entries from the sensor JSON file
        sensor_data = {}
        
        # Get data from the specified sensor file
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                if "data" in data and "readings_data" in data["data"] and data["data"]["readings_data"]:
                    latest_data = data["data"]["readings_data"][0]  # Get first item since newest data is now at the top
                    
                    # Handle numeric values properly (including 0)
                    humidity = latest_data.get("Humidity")
                    # Make sure we don't convert 0 to N/A
                    if humidity is not None:
                        humidity_value = humidity
                    else:
                        humidity_value = "N/A"
                    
                    # For new sensors, radiation is included in the same file
                    radiation_value = latest_data.get("Radiation", "N/A")
                        
                    sensor_data = {
                        "temperature": latest_data.get("Temperature", "N/A"),
                        "humidity": humidity_value,
                        "battery": latest_data.get("Battery Level", "N/A"),
                        "sample_time": latest_data.get("sample_time_utc", "N/A"),
                        "radiation": radiation_value
                    }
        except Exception as e:
            print(f"Error reading sensor data from {filename}: {str(e)}")
        
        # For the original sensor, get radiation from separate file
        if sensor_id == "original":
            try:
                radiation_value = get_radiation_value()
                sensor_data["radiation"] = radiation_value
            except Exception as e:
                print(f"Error getting radiation value: {str(e)}")
        
        return sensor_data
            
    except Exception as e:
        print(f"Error in get_latest_sensor_data: {str(e)}")
        return {
            "temperature": "N/A",
            "humidity": "N/A", 
            "battery": "N/A",
            "sample_time": "N/A",
            "radiation": "N/A"
        }

def get_historical_sensor_data(sensor_id="original"):
    try:
        # Get the filename for the sensor
        filename = SENSOR_FILES.get(sensor_id, "readings.json")
        
        # Get sensor data
        with open(filename, "r") as file:
            sensor_data = json.load(file)
            
        # Get radiation data (only for original sensor)
        radiation_data = {}
        if sensor_id == "original":
            try:
                with open("readings-radiation.json", "r") as file:
                    rad_json = json.load(file)
                    if "data" in rad_json and "readings_data" in rad_json["data"]:
                        # Create a dictionary with timestamps as keys for quick lookup
                        for reading in rad_json["data"]["readings_data"]:
                            if "sample_time_utc" in reading:
                                radiation_data[reading["sample_time_utc"]] = reading.get("Radiation", "N/A")
            except Exception as e:
                print(f"Error loading radiation data: {str(e)}")
        
        # Process sensor data and add radiation values
        if "data" in sensor_data and "readings_data" in sensor_data["data"]:
            historical_data = []
            
            for reading in sensor_data["data"]["readings_data"]:
                sample_time = reading.get("sample_time_utc", "N/A")
                
                # For new sensors, radiation is in the same file
                if sensor_id == "original":
                    radiation_value = radiation_data.get(sample_time, "N/A")
                else:
                    radiation_value = reading.get("Radiation", "N/A")
                
                entry = {
                    "temperature": reading.get("Temperature", "N/A"),
                    "humidity": reading.get("Humidity", "N/A"),
                    "battery": reading.get("Battery Level", "N/A"),
                    "sample_time": sample_time,
                    "radiation": radiation_value
                }
                historical_data.append(entry)
                
            return historical_data
        else:
            raise ValueError("Invalid JSON structure")
    except Exception as e:
        print(f"Error in get_historical_sensor_data: {str(e)}")
        raise RuntimeError("Failed to fetch historical data")

def get_latest_radiation_data():
    try:
        with open("readings-radiation.json", "r") as file:
            data = json.load(file)
            if "data" in data and "readings_data" in data["data"] and data["data"]["readings_data"]:
                latest_data = data["data"]["readings_data"][0]  # Get first item since newest data is now at the top
                return {
                    "radiation": latest_data.get("Radiation", "N/A"),
                    "sample_time": latest_data.get("sample_time_utc", "N/A"),
                }
            else:
                raise ValueError("Invalid radiation JSON structure")
    except Exception as e:
        print(f"Error in get_latest_radiation_data: {str(e)}")
        return {"radiation": "N/A", "sample_time": "N/A"}

def get_radiation_value():
    """Get just the radiation value from the top entry"""
    try:
        with open("readings-radiation.json", "r") as file:
            data = json.load(file)
            if "data" in data and "readings_data" in data["data"] and data["data"]["readings_data"]:
                radiation = data["data"]["readings_data"][0].get("Radiation", "N/A")
                # Try to convert to float if it's a string number
                if isinstance(radiation, str) and radiation != "N/A":
                    try:
                        return float(radiation)
                    except ValueError:
                        pass
                return radiation
            return "N/A"
    except Exception as e:
        print(f"Error reading radiation value: {str(e)}")
        return "N/A"

# ===================== Weather API =====================
import requests

def get_weather():
    api_key = "27b99d8bad72ab73a65e2b96ab43ec97"
    lat, lon = 31.25181, 34.7913
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=en"
        response = requests.get(url)
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"]
        }
    except Exception as e:
        print("Weather API error:", e)
        return {"error": "Failed to fetch weather data"}


# ===================== Require Login for Protected Routes =====================
@app.before_request
def require_login():
    """
    This function runs before every request.
    We allow certain routes without login:
      - static files
      - login
      - register
    Everything else is redirected to /login if not logged in.
    """
    allowed_routes = {'login', 'register', 'static'}  # 'static' is not an endpoint, but let's keep it open
    if request.endpoint not in allowed_routes and 'logged_in' not in session:
        return redirect(url_for('login'))

# ===================== Routes =====================

@app.route("/")
def index():
    # If user is not logged in, they'll be redirected by the before_request check
    return render_template("index.html")

@app.route("/shadow-history")
def shadow_history():
    # If user is not logged in, they'll be redirected by the before_request check
    return render_template("shadow-history.html")

@app.route("/get-sensor-data")
def get_sensor_data():
    # If user is not logged in, they'll be redirected by the before_request check
    try:
        sensor_id = request.args.get('sensor_id', 'original')
        data = get_latest_sensor_data(sensor_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sensor data: {str(e)}"}), 500

@app.route("/get-sensor-history")
def get_sensor_history():
    # If user is not logged in, they'll be redirected by the before_request check
    try:
        sensor_id = request.args.get('sensor_id', 'original')
        history = get_historical_sensor_data(sensor_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500

@app.route("/get-radiation-data")
def get_radiation_data():
    # If user is not logged in, they'll be redirected by the before_request check
    try:
        data = get_latest_radiation_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch radiation data: {str(e)}"}), 500

@app.route("/get-weather")
def get_weather_route():
    weather_data = get_weather()
    return jsonify(weather_data)

import csv
from flask import Response

@app.route("/export-csv")
def export_csv():
    try:
        # Get the historical data which already includes radiation values
        historical_data = get_historical_sensor_data()

        if not historical_data:
            return "No sensor data available", 404

        # Create CSV string
        def generate():
            header = ["Temperature", "Humidity", "Battery Level", "Radiation", "Sample Time"]
            yield ",".join(header) + "\n"
            for item in historical_data:
                line = [
                    str(item.get("temperature", "")),
                    str(item.get("humidity", "")),
                    str(item.get("battery", "")),
                    str(item.get("radiation", "")),
                    str(item.get("sample_time", ""))
                ]
                yield ",".join(line) + "\n"

        return Response(generate(), mimetype='text/csv',
                        headers={"Content-Disposition": "attachment;filename=sensor_data.csv"})

    except Exception as e:
        return f"Error generating CSV: {str(e)}", 500

# ===================== User Registration & Login =====================

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Allows new users to register. If user already exists, shows a warning.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user already exists
        existing_user = users_col.find_one({"email": username})
        if existing_user:
            flash("User already exists", "warning")
            return redirect(url_for("register"))

        # Insert new user
        users_col.insert_one({
            "email": username,
            "password": password  # Plain text (for demonstration only)
        })
        flash(f"Registration successful for user {username}", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Logs the user in by checking credentials. If success, sets session.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Attempt to find user with matching credentials
        user = users_col.find_one({"email": username, "password": password})
        if user:
            # Save user info in session
            session['logged_in'] = True
            session['username'] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    # If already logged in, no need to see login page
    if 'logged_in' in session:
        return redirect(url_for('index'))

    return render_template("login.html")

@app.route("/logout")
def logout():
    """
    Logs out the current user by clearing the session, then redirects to login.
    """
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ===================== Run App =====================
if __name__ == "__main__":
    app.run(debug=True)

