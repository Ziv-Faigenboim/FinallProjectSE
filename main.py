import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Function to retrieve the latest sensor data
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

# Function to retrieve all historical sensor data
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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shadow-history")
def shadow_history():
    """
    Serve the Shadow History page.
    """
    return render_template("shadow-history.html")

from website import create_app

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


if __name__ == "__main__":
    app.run(debug=True)
