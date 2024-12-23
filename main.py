# app.py
from flask import Flask, render_template, jsonify
from main_sensor import get_latest_sensor_data, get_historical_sensor_data

app = Flask(__name__)

@app.route("/")
def index():
    """
    Serve the main page that contains:
    - A left panel for sensor data
    - A Leaflet map on the right
    """
    return render_template("index.html")

@app.route("/get-sensor-data")
def get_sensor_data():
    """
    Fetch the latest sensor data and return it as JSON
    """
    try:
        data = get_latest_sensor_data()
        # Log the data being returned for debugging
        print(f"Current Data: {data}")
        return jsonify(data), 200
    except Exception as e:
        print(f"Error fetching current sensor data: {str(e)}")
        return jsonify({"error": f"Failed to fetch sensor data: {str(e)}"}), 500

@app.route("/get-sensor-history")
def get_sensor_history():
    """
    Fetch historical sensor data and return it as JSON
    """
    try:
        # Fetch historical data from your sensor or database
        history = get_historical_sensor_data()
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch historical data: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
