import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
# Update these imports to match your file structure
from db.db_collections import DBCollections  # rename your old collections.py to db_collections.py
from db.connection import get_db_collection
# Import functions from main_sensor.py
from main_sensor import get_latest_sensor_data as get_sensor_data_live
from main_sensor import get_historical_sensor_data as get_historical_data_live
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for session and flashing messages

# MongoDB's collection for users
users_col = get_db_collection(DBCollections.users)

# ===================== Sensor Data from Live Source =====================
def get_latest_sensor_data():
    """
    Get the latest sensor data from the live data source instead of JSON file
    """
    try:
        # Call the function from main_sensor.py
        data = get_sensor_data_live()
        
        # Safety checks and default values
        if "error" in data:
            raise ValueError(data["error"])
            
        # Ensure numeric values have defaults and convert strings to numbers if needed
        if data["temperature"] == "N/A":
            data["temperature"] = 0
        elif isinstance(data["temperature"], str):
            try:
                data["temperature"] = float(data["temperature"])
            except ValueError:
                data["temperature"] = 0
                
        if data["humidity"] == "N/A":
            data["humidity"] = 0
        elif isinstance(data["humidity"], str):
            try:
                data["humidity"] = float(data["humidity"])
            except ValueError:
                data["humidity"] = 0
                
        if data["battery"] == "N/A":
            data["battery"] = 0
        elif isinstance(data["battery"], str):
            try:
                data["battery"] = float(data["battery"])
            except ValueError:
                data["battery"] = 0
                
        # Extra hardening - add uppercase variants for compatibility
        data["Temperature"] = data["temperature"]
        data["Humidity"] = data["humidity"]
        data["Battery Level"] = data["battery"]
        
        return data
    except Exception as e:
        print(f"Error in get_latest_sensor_data: {str(e)}")
        # Return a default data object instead of raising an exception
        return {
            "temperature": 20.0,
            "Temperature": 20.0,
            "humidity": 50.0,
            "Humidity": 50.0,
            "battery": 100.0,
            "Battery Level": 100.0,
            "sample_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "sample_time_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "error_info": f"Using default data. Error: {str(e)}"
        }

def get_historical_sensor_data():
    """
    Get historical sensor data from the live data source instead of JSON file
    """
    try:
        # Call the function from main_sensor.py
        data = get_historical_data_live()
        
        # Handle error case or empty data
        if isinstance(data, dict) and "error" in data:
            # Return dummy data instead of failing
            return generate_dummy_history_data()
            
        # Ensure data is an array
        if not isinstance(data, list):
            return generate_dummy_history_data()
            
        # Process each entry to ensure numeric values
        for entry in data:
            # Ensure temperature is a number
            if entry["temperature"] == "N/A":
                entry["temperature"] = 0
            elif isinstance(entry["temperature"], str):
                try:
                    entry["temperature"] = float(entry["temperature"])
                except ValueError:
                    entry["temperature"] = 0
                    
            # Ensure humidity is a number
            if entry["humidity"] == "N/A":
                entry["humidity"] = 0
            elif isinstance(entry["humidity"], str):
                try:
                    entry["humidity"] = float(entry["humidity"])
                except ValueError:
                    entry["humidity"] = 0
                    
            # Ensure battery is a number
            if entry["battery"] == "N/A":
                entry["battery"] = 0
            elif isinstance(entry["battery"], str):
                try:
                    entry["battery"] = float(entry["battery"])
                except ValueError:
                    entry["battery"] = 0
            
        return data
    except Exception as e:
        print(f"Error in get_historical_sensor_data: {str(e)}")
        return generate_dummy_history_data()

# Helper function to generate dummy history data
def generate_dummy_history_data():
    """Generate sample history data for demonstration when real data is unavailable"""
    now = datetime.utcnow()
    return [
        {
            "temperature": 22.5,
            "humidity": 45.0,
            "battery": 95.0,
            "sample_time": (now - timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        }
        for i in range(5)
    ]

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
        # Get historical data from live source
        readings = get_historical_sensor_data()
        
        if not readings:
            return "No sensor data available", 404

        # Create CSV string
        def generate():
            header = ["Temperature", "Humidity", "Battery", "Sample Time"]
            yield ",".join(header) + "\n"
            for row in readings:
                line = [
                    str(row.get("temperature", "")),
                    str(row.get("humidity", "")),
                    str(row.get("battery", "")),
                    str(row.get("sample_time", ""))
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

