import json
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
# Update these imports to match your file structure
from db.db_collections import DBCollections  # rename your old collections.py to db_collections.py
from db.connection import get_db_collection

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

# MongoDB collection for users
users_col = get_db_collection(DBCollections.users)

# ========== Sensor Data from JSON (as you had before) ==========
def get_latest_sensor_data():
    try:
        with open("readings.json", "r") as file:
            data = json.load(file)
            if "data" in data and "readings_data" in data["data"]:
                latest_data = data["data"]["readings_data"][-1]
                return {
                    "temperature": latest_data.get("Temperature", "N/A"),
                    "humidity": latest_data.get("Humidity", "N/A"),
                    "battery": latest_data.get("Battery Level", "N/A"),
                    "sample_time": latest_data.get("sample_time_utc", "N/A"),
                }
            else:
                raise ValueError("Invalid JSON structure")
    except Exception as e:
        print(f"Error in get_latest_sensor_data: {str(e)}")
        raise RuntimeError("Failed to fetch sensor data")

def get_historical_sensor_data():
    try:
        with open("readings.json", "r") as file:
            data = json.load(file)
            if "data" in data and "readings_data" in data["data"]:
                historical_data = [
                    {
                        "temperature": reading.get("Temperature", "N/A"),
                        "humidity": reading.get("Humidity", "N/A"),
                        "battery": reading.get("Battery Level", "N/A"),
                        "sample_time": reading.get("sample_time_utc", "N/A"),
                    }
                    for reading in data["data"]["readings_data"]
                ]
                return historical_data
            else:
                raise ValueError("Invalid JSON structure")
    except Exception as e:
        print(f"Error in get_historical_sensor_data: {str(e)}")
        raise RuntimeError("Failed to fetch historical data")

# ========== Routes ==========

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shadow-history")
def shadow_history():
    """
    Serve the Shadow History page.
    """
    return render_template("shadow-history.html")

@app.route("/get-sensor-data")
def get_sensor_data():
    try:
        data = get_latest_sensor_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch sensor data: {str(e)}"}), 500

@app.route("/get-sensor-history")
def get_sensor_history():
    try:
        history = get_historical_sensor_data()
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500

# ========== MongoDB User Registration & Login ==========

@app.route("/register", methods=["GET", "POST"])
def register():
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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Attempt to find user with matching credentials
        user = users_col.find_one({"email": username, "password": password})
        if user:
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

# ========== Run App ==========

if __name__ == "__main__":
    app.run(debug=True)
