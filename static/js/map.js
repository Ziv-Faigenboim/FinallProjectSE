// Replace with your actual Mapbox token
mapboxgl.accessToken = 'pk.eyJ1IjoiZWxhZDc2MTAiLCJhIjoiY205andvMnN2MDZpaDJqc2JvaXhlbWR2bCJ9.BL95xjSj5yW4y3Rb_0_l1w';

// Global flag for view mode (false = 2D, true = 3D)
var is3D = false;

// Initialize the Mapbox map
var map = new mapboxgl.Map({
    container: 'map', // ID of the container element in HTML
    style: 'mapbox://styles/mapbox/streets-v11', // You can change this style as needed
    center: [34.7913, 31.2518], // [longitude, latitude] for Beer Sheva, Israel
    zoom: 13,
    pitch: 0,    // Start in 2D view (flat)
    bearing: 0   // No rotation initially
});

// Add navigation controls (zoom and rotation buttons)
map.addControl(new mapboxgl.NavigationControl());

// When the map loads, add the 3D buildings layer (initially hidden)
map.on('load', function () {
    // Find the first symbol layer to correctly position the 3D layer
    var layers = map.getStyle().layers;
    var labelLayerId;
    for (var i = 0; i < layers.length; i++) {
        if (layers[i].type === 'symbol' && layers[i].layout && layers[i].layout['text-field']) {
            labelLayerId = layers[i].id;
            break;
        }
    }
    map.addLayer({
        'id': '3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 15,
        'layout': {
            'visibility': 'none' // Start hidden in 2D mode
        },
        'paint': {
            'fill-extrusion-color': '#aaa',
            'fill-extrusion-height': [
                "interpolate", ["linear"], ["zoom"],
                15, 0,
                15.05, ["get", "height"]
            ],
            'fill-extrusion-base': [
                "interpolate", ["linear"], ["zoom"],
                15, 0,
                15.05, ["get", "min_height"]
            ],
            'fill-extrusion-opacity': 0.6
        }
    }, labelLayerId);
});

// Toggle between 2D and 3D views
function toggleView() {
    if (is3D) {
        // Switch to 2D view: flat map with no pitch or rotation
        map.easeTo({
            pitch: 0,
            bearing: 0,
            duration: 1000
        });
        if (map.getLayer('3d-buildings')) {
            map.setLayoutProperty('3d-buildings', 'visibility', 'none');
        }
        is3D = false;
    } else {
        // Switch to 3D view: pitched and rotated map for a 3D effect
        map.easeTo({
            pitch: 60,
            bearing: -17.6,
            duration: 1000
        });
        if (map.getLayer('3d-buildings')) {
            map.setLayoutProperty('3d-buildings', 'visibility', 'visible');
        }
        is3D = true;
    }
}
