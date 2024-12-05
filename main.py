from flask import Flask, render_template
import folium

app = Flask(__name__)


@app.route('/')
def map():
    # Coordinates of Be'er Sheva
    map_center = [31.25181, 34.7913]

    # Create the map with a center and zoom level
    beer_sheva_map = folium.Map(location=map_center, zoom_start=13)

    # Save the map to an HTML file
    beer_sheva_map.save('templates/map.html')

    # Render the map in the browser
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)
