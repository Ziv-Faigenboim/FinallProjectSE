# GIS ShadeSpotter

A web-based Geographic Information System (GIS) application that visualizes environmental sensor data on an interactive map. The application tracks temperature, humidity, radiation levels, and battery status from multiple sensors across different locations, with advanced shadow analysis capabilities based on time of day.

## Overview

This project was developed as part of my final year coursework, focusing on real-time environmental monitoring and spatial data visualization. The application integrates sensor data from multiple locations, displays it on an interactive Mapbox map, and provides tools for analyzing comfort levels and shadow patterns throughout the day.

<img width="2560" height="1440" alt="ShadeSpotter 1" src="https://github.com/user-attachments/assets/8b0f305d-2e57-469b-8dd4-fcee673d93dc" />
<img width="2560" height="1440" alt="ShadeSpotter 2" src="https://github.com/user-attachments/assets/08024a5c-645b-4d47-92f2-64c623c75997" />

## Key Features

- **Interactive Map Visualization**: Real-time sensor data displayed on a Mapbox GL JS map with custom markers for each sensor location
- **Shadow Analysis**: Dynamic 3D shadow visualization that changes based on time of day, allowing users to see how shadows affect different locations
- **Multi-Sensor Support**: Monitor data from six different sensor locations simultaneously
- **Comfort Level Calculation**: Automated comfort scoring based on temperature, humidity, and radiation levels
- **Historical Data Analysis**: View historical sensor readings with filtering options and interactive charts
- **Land Use Visualization**: Toggleable land use layers showing residential, commercial, park, and other area classifications
- **Weather Integration**: Real-time weather data from OpenWeatherMap API
- **Data Export**: CSV export functionality for sensor readings

## Technology Stack

**Backend:**
- Python 3.11
- Flask 2.3.3
- MongoDB (via PyMongo) for data storage
- Requests library for API integration

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Mapbox GL JS for map rendering
- Chart.js for data visualization
- Responsive design with Flexbox

**APIs:**
- Mapbox Maps API
- Mapbox Geocoding API
- OpenWeatherMap API
- Atomation Sensor API

**Deployment:**
- Render.com
- Gunicorn WSGI server

## Project Structure

```
FInalProjectRender/
├── main.py                 # Flask application and routes
├── main_sensor.py          # Sensor data fetcher from API
├── radiation_sensor.py     # Radiation sensor data fetcher
├── db/                     # Database connection modules
│   ├── connection.py
│   └── db_collections.py
├── Templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   └── shadow-history.html
├── static/                 # Static assets
│   ├── js/
│   │   └── map.js         # Main map and sensor logic
│   ├── style.css          # Application styles
│   └── images/            # Shadow analysis images
└── requirements.txt        # Python dependencies
```

## Setup and Installation

### Prerequisites

- Python 3.11 or higher
- MongoDB (optional, for data storage)
- Mapbox account with API token
- OpenWeatherMap API key (optional, for weather data)

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd FInalProjectRender
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export SECRET_KEY="your-secret-key-here"
export OPENWEATHER_API_KEY="your-api-key-here"
export FLASK_DEBUG="0"
export PORT=5000
```

5. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **View Sensor Data**: Click on any sensor marker on the map to view current readings including temperature, humidity, battery level, and radiation
2. **Analyze Shadows**: Use the time slider at the bottom of the map to see how shadows change throughout the day
3. **Toggle 3D View**: Click the "Toggle 2D/3D" button to switch between flat and 3D building visualization
4. **View History**: Select a sensor and click "Show History" to see historical data with filtering options
5. **Generate Charts**: Click the "Graph" button to view interactive charts of sensor readings over time
6. **Export Data**: Use the "Download CSV" button to export sensor data

## API Endpoints

- `GET /` - Main application page
- `GET /get-sensor-data?sensor_id=<id>` - Get latest sensor readings
- `GET /get-sensor-history?sensor_id=<id>` - Get historical sensor data
- `GET /get-weather` - Get current weather data
- `GET /export-csv` - Export sensor data as CSV
- `GET /shadow-history` - Shadow analysis information page

## Data Sources

Sensor data is collected from the Atomation API and stored in JSON files. The application supports multiple sensor locations including:
- SCE College
- Givaat Rambam Park
- Gan Hashlosha Park
- Central Bus Station
- BGU University Campus
- Soroka Medical Center

## Comfort Level Algorithm

The comfort score is calculated using a weighted formula that considers:
- Temperature (50% weight): Optimal at 22°C
- Humidity (30% weight): Optimal at 60%
- Radiation (20% weight): Lower is better

The final score ranges from 0-100%, categorized as Excellent, Good, Moderate, Low, or Very Low comfort.


