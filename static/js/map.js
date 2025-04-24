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

  map.addSource('mapbox-dem', {
    'type': 'raster-dem',
    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
    'tileSize': 512,
    'maxzoom': 14
  });

  map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });

  map.setFog({
    'range': [0.5, 10],
    'color': '#f8f8f8',
    'horizon-blend': 0.1
  });

  map.setLight({
    anchor: 'viewport',
    position: calculateSunPosition(12),
    color: '#ffffff',
    intensity: 0.8
  });

  map.addLayer({
    'id': '3d-buildings',
    'source': 'composite',
    'source-layer': 'building',
    'filter': ['==', 'extrude', 'true'],
    'type': 'fill-extrusion',
    'minzoom': 15,
    'layout': { 'visibility': 'none' },
    'paint': {
      'fill-extrusion-color': '#9E9E9E',
      'fill-extrusion-height': [
        'interpolate', ['linear'], ['zoom'], 15, 0, 15.05, ['get', 'height']
      ],
      'fill-extrusion-base': [
        'interpolate', ['linear'], ['zoom'], 15, 0, 15.05, ['get', 'min_height']
      ],
      'fill-extrusion-opacity': 0.9
    }
  }, labelLayerId);

  map.addLayer({
    'id': 'ground-shadow',
    'type': 'fill',
    'source': 'composite',
    'source-layer': 'building',
    'layout': { 'visibility': 'none' },
    'paint': {
      'fill-color': '#000000',
      'fill-opacity': 0.35,
      'fill-translate': calculateShadowTranslation(12)
    }
  }, '3d-buildings');

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

      const comfort = calculateComfortLevel(temp, humidity);

      const popupContent = `
        <div>
          <strong>Comfort Level</strong><br>
          <div class="gradient-meter">
            <div class="gradient-bar"></div>
            <div class="meter-indicator" style="left: ${comfort}%;"></div>
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
        <p><strong>Comfort Level:</strong></p>
        <div class="gradient-meter">
          <div class="gradient-bar"></div>
          <div class="meter-indicator" style="left: ${comfort}%;"></div>
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
    map.setLayoutProperty('3d-buildings', 'visibility', 'none');
    map.setLayoutProperty('ground-shadow', 'visibility', 'none');
    is3D = false;
  } else {
    map.easeTo({ pitch: 60, bearing: -17.6, duration: 1000 });
    map.setLayoutProperty('3d-buildings', 'visibility', 'visible');
    map.setLayoutProperty('ground-shadow', 'visibility', 'visible');
    is3D = true;
  }
}

// פונקציה פשוטה לחישוב מדד נוחות
function calculateComfortLevel(temp, humidity) {
  const comfort = 100 - Math.abs(22 - temp) * 2 - Math.abs(60 - humidity) * 0.5;
  return Math.max(0, Math.min(100, comfort));
}

function calculateSunPosition(hour) {
  if (hour < 6 || hour > 18) return [1, hour < 6 ? 0 : 180, -10];
  const dayProgress = (hour - 6) / 12;
  const azimuth = dayProgress * 180;
  const elevation = Math.sin(dayProgress * Math.PI) * 60;
  return [1, azimuth, elevation];
}

function calculateShadowTranslation(hour) {
  const xOffset = (hour - 12) * 2;
  return [xOffset, 10];
}

document.getElementById('time-slider').addEventListener('input', (event) => {
  const hour = parseInt(event.target.value);
  const sunPos = calculateSunPosition(hour);
  const shadowTrans = calculateShadowTranslation(hour);

  map.setLight({
    anchor: 'viewport',
    position: sunPos,
    color: '#ffffff',
    intensity: 0.8
  });

  if (map.getLayer('ground-shadow')) {
    map.setPaintProperty('ground-shadow', 'fill-translate', shadowTrans);
  }
});

