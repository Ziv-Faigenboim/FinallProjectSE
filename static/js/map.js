mapboxgl.accessToken = 'pk.eyJ1IjoiZWxhZDc2MTAiLCJhIjoiY205andvMnN2MDZpaDJqc2JvaXhlbWR2bCJ9.BL95xjSj5yW4y3Rb_0_l1w';

let is3D = false;

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v11',
  center: [34.7913, 31.2518],
  zoom: 15,
  pitch: 0,
  bearing: 0
});

map.addControl(new mapboxgl.NavigationControl());

map.on('load', () => {
  const layers = map.getStyle().layers;
  let labelLayerId;
  for (let i = 0; i < layers.length; i++) {
    if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
      labelLayerId = layers[i].id;
      break;
    }
  }

  map.addLayer({
    id: '3d-buildings',
    source: 'composite',
    'source-layer': 'building',
    filter: ['==', 'extrude', 'true'],
    type: 'fill-extrusion',
    minzoom: 15,
    layout: { visibility: 'none' },
    paint: {
      'fill-extrusion-color': '#aaa',
      'fill-extrusion-height': [
        'interpolate', ['linear'], ['zoom'],
        15, 0,
        15.05, ['get', 'height']
      ],
      'fill-extrusion-base': [
        'interpolate', ['linear'], ['zoom'],
        15, 0,
        15.05, ['get', 'min_height']
      ],
      'fill-extrusion-opacity': 0.6
    }
  }, labelLayerId);

  // Add the sensor marker
  const marker = new mapboxgl.Marker()
    .setLngLat([34.7895184904266, 31.2498119452557])
    .addTo(map);

  marker.getElement().addEventListener('click', async () => {
    try {
      const response = await fetch('/get-sensor-data');
      const data = await response.json();
      const temp = data.temperature;
      const humidity = data.humidity;
      const battery = data.battery;
      const time = data.sample_time;
      const quality = Math.min(100, Math.max(0, (humidity * 0.6 + (30 - temp) * 2)));

      const popupContent = `
        <div>
          <strong>Shadow Quality</strong><br>
          <div class="gradient-meter">
            <div class="gradient-bar"></div>
            <div class="meter-indicator" style="left: ${quality}%;"></div>
          </div>
        </div>
      `;

      new mapboxgl.Popup()
        .setLngLat([34.7895184904266, 31.2498119452557])
        .setHTML(popupContent)
        .addTo(map);

      const container = document.getElementById('sensor-data-container');
      container.innerHTML = `
        <h3>Live Sensor Readings</h3>
        <p><strong>Temperature:</strong> ${temp.toFixed(1)}°C</p>
        <p><strong>Humidity:</strong> ${humidity.toFixed(1)}%</p>
        <p><strong>Battery:</strong> ${battery}%</p>
        <p><strong>Sample Time:</strong> ${time}</p>
        <p><strong>Shadow Quality:</strong></p>
        <div class="gradient-meter">
          <div class="gradient-bar"></div>
          <div class="meter-indicator" style="left: ${quality}%;"></div>
        </div>
      `;
    } catch (err) {
      console.error('Error fetching sensor data:', err);
    }
  });
});

function toggleView() {
  if (is3D) {
    map.easeTo({ pitch: 0, bearing: 0, duration: 1000 });
    if (map.getLayer('3d-buildings')) {
      map.setLayoutProperty('3d-buildings', 'visibility', 'none');
    }
    is3D = false;
  } else {
    map.easeTo({ pitch: 60, bearing: -17.6, duration: 1000 });
    if (map.getLayer('3d-buildings')) {
      map.setLayoutProperty('3d-buildings', 'visibility', 'visible');
    }
    is3D = true;
  }
}

// Sun slider logic
document.addEventListener('DOMContentLoaded', () => {
  const slider = document.getElementById('time-slider');
  const sunIcon = document.getElementById('sun-icon');
  if (slider && sunIcon) {
    slider.addEventListener('input', function () {
      const value = slider.value;
      const percent = (value / 23) * 100;
      sunIcon.style.left = percent + '%';
    });
  }
});