import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
# Update these imports to match your file structure
from db.db_collections import DBCollections  # rename your old collections.py to db_collections.py
from db.connection import get_db_collection
import os
import subprocess
import threading
from datetime import datetime, timedelta
import time
import traceback
from dotenv import load_dotenv

# Import updated functions from main_sensor
import main_sensor

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session and flashing messages

# Try to get database collections
users_col = get_db_collection(DBCollections.users)
sensor_data_col = get_db_collection(DBCollections.sensor_data)

# File path for sensor data cache 
READINGS_JSON_PATH = "static/readings.json"

# ===================== Auto-update readings.json with main_sensor data =====================
def update_readings_json():
    """
    Gets data directly from MongoDB sensor_data collection and saves it to readings.json.
    Falls back to local backup if MongoDB is unavailable.
    """
    try:
        # Check if we have a valid MongoDB connection
        if sensor_data_col is None:
            print("MongoDB connection is not available, using local backup or sample data")
            # Try to use main_sensor's update_readings_json with its local backup
            main_sensor.update_readings_json()
            
            # Check if readings.json was created by main_sensor
            if os.path.exists(READINGS_JSON_PATH):
                with open(READINGS_JSON_PATH, "r") as f:
                    data = json.load(f)
                    if data:
                        print(f"Successfully used local backup via main_sensor module")
                        return data
            
            # If not, generate sample data as last resort
            return generate_sample_data()
        
        print("Getting sensor data from MongoDB collection...")
        test_data = None
        
        try:
            # Try to query MongoDB
            test_data = sensor_data_col.find().sort("timestamp", -1).limit(100)
            test_data = list(test_data)
            
            if not test_data:
                print("No data found in MongoDB collection, trying local backup")
                main_sensor.update_readings_json()
                
                # Check if readings.json was created successfully
                if os.path.exists(READINGS_JSON_PATH):
                    with open(READINGS_JSON_PATH, "r") as f:
                        data = json.load(f)
                        if data:
                            return data
                
                # Last resort - generate sample data
                return generate_sample_data()
                    
            # Convert MongoDB ObjectId to string for JSON serialization
            for item in test_data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
                    
            # Write data to readings.json
            with open(READINGS_JSON_PATH, "w") as f:
                json.dump(test_data, f, indent=2)
                
            print(f"Updated {READINGS_JSON_PATH} with {len(test_data)} records from MongoDB")
            return test_data
            
        except Exception as e:
            print(f"Error getting data from MongoDB: {e}")
            traceback.print_exc()
            
            # Try to use main_sensor's update_readings_json with its local backup
            main_sensor.update_readings_json()
            
            # Check if readings.json was created by main_sensor
            if os.path.exists(READINGS_JSON_PATH):
                with open(READINGS_JSON_PATH, "r") as f:
                    data = json.load(f)
                    if data:
                        return data
            
            # Last resort - generate sample data
            return generate_sample_data()
    
    except Exception as e:
        print(f"Error updating readings.json: {e}")
        traceback.print_exc()
        return generate_sample_data()

def generate_sample_data():
    """Create sample data for the application to use when MongoDB is unavailable"""
    print("Creating guaranteed sample data...")
    sample_data = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Temperature": 22.5,
            "Humidity": 45,
            "CO": 0.2,
            "CH4": 0.1,
            "Distance": 150,
            "Gas": 25,
            "source": "sample_data"
        }
    ]
    
    # Ensure the static directory exists
    os.makedirs("static", exist_ok=True)
    
    # Write sample data to readings.json
    with open(READINGS_JSON_PATH, "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created {READINGS_JSON_PATH} with guaranteed sample data")
    return sample_data

# ===================== Sensor Data from JSON =====================
def get_latest_sensor_data():
    try:
        # Look for readings.json in the static folder
        with open(os.path.join('static', 'readings.json'), "r") as file:
            data = json.load(file)
            
            # Handle both formats (main_sensor.py format and MongoDB format)
            if "data" in data and "readings_data" in data["data"]:
                # main_sensor.py format
                latest_data = data["data"]["readings_data"][-1]
                return {
                    "temperature": latest_data.get("Temperature", "N/A"),
                    "humidity": latest_data.get("Humidity", "N/A"),
                    "battery": latest_data.get("Battery Level", "N/A"),
                    "sample_time": latest_data.get("sample_time_utc", "N/A"),
                }
            elif isinstance(data, list) and len(data) > 0:
                # MongoDB format or sample data format
                latest_data = data[0]  # Assuming data is sorted newest first
                return {
                    "temperature": latest_data.get("Temperature", "N/A"),
                    "humidity": latest_data.get("Humidity", "N/A"),
                    "battery": latest_data.get("Battery Level", "N/A"),
                    "sample_time": latest_data.get("sample_time_utc", latest_data.get("timestamp", "N/A")),
                }
            else:
                raise ValueError("Invalid JSON structure")
    except Exception as e:
        print(f"Error in get_latest_sensor_data: {str(e)}")
        traceback.print_exc()
        return {
            "temperature": "Error",
            "humidity": "Error",
            "battery": "Error",
            "sample_time": "Error loading data"
        }

def get_historical_sensor_data():
    try:
        # Look for readings.json in the static folder
        with open(os.path.join('static', 'readings.json'), "r") as file:
            data = json.load(file)
            
            # Handle both formats (main_sensor.py format and MongoDB format)
            if "data" in data and "readings_data" in data["data"]:
                # main_sensor.py format
                readings = data["data"]["readings_data"]
            elif isinstance(data, list):
                # MongoDB format or sample data format
                readings = data
            else:
                raise ValueError("Invalid JSON structure")
                
            historical_data = []
            for reading in readings:
                historical_data.append({
                    "temperature": reading.get("Temperature", "N/A"),
                    "humidity": reading.get("Humidity", "N/A"),
                    "battery": reading.get("Battery Level", "N/A"),
                    "sample_time": reading.get("sample_time_utc", reading.get("timestamp", "N/A")),
                })
            return historical_data
    except Exception as e:
        print(f"Error in get_historical_sensor_data: {str(e)}")
        traceback.print_exc()
        return [{"error": "Failed to fetch historical data"}]

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
        data = get_latest_sensor_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sensor data: {str(e)}"}), 500

@app.route("/get-sensor-history")
def get_sensor_history():
    # If user is not logged in, they'll be redirected by the before_request check
    try:
        history = get_historical_sensor_data()
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500

@app.route("/get-weather")
def get_weather_route():
    weather_data = get_weather()
    return jsonify(weather_data)

import csv
from flask import Response

@app.route("/export-csv")
def export_csv():
    try:
        # Look for readings.json in the static folder
        with open(os.path.join('static', 'readings.json'), "r") as file:
            data = json.load(file)
            readings = data.get("data", {}).get("readings_data", [])

        if not readings:
            return "No sensor data available", 404

        # Create CSV string
        def generate():
            header = ["Temperature", "Humidity", "Battery Level", "sample_time_utc"]
            yield ",".join(header) + "\n"
            for row in readings:
                line = [
                    str(row.get("Temperature", "")),
                    str(row.get("Humidity", "")),
                    str(row.get("Battery Level", "")),
                    str(row.get("sample_time_utc", ""))
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
    # Update readings.json with data from MongoDB at startup
    print("Initializing application...")
    update_readings_json()
    
    # Start a background thread to periodically update sensor data
    def background_task():
        while True:
            try:
                # Run main_sensor.py to collect new data
                print("Running main_sensor.py to collect fresh sensor data...")
                main_sensor.main()
                
                # Wait for 30 minutes before updating again
                time.sleep(1800)  # 30 minutes
            except Exception as e:
                print(f"Error in background task: {e}")
                traceback.print_exc()
                time.sleep(300)  # Wait 5 minutes before retrying if there's an error
    
    # Start the background thread
    sensor_thread = threading.Thread(target=background_task, daemon=True)
    sensor_thread.start()
    
    # Run the Flask app
    app.run(debug=True)

