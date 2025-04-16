document.addEventListener('DOMContentLoaded', () => {
  // Replace with your actual token from Mapbox
  mapboxgl.accessToken = 'pk.eyJ1IjoiZWxhZDc2MTAiLCJhIjoiY205andvMnN2MDZpaDJqc2JvaXhlbWR2bCJ9.BL95xjSj5yW4y3Rb_0_l1w';

  // Create map with normal (2D) style
  let map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [34.7895184904266, 31.2498119452557],
    zoom: 15,
    pitch: 0,
    bearing: 0,
    antialias: true
  });

  // Add navigation controls (zoom buttons, etc.)
  map.addControl(new mapboxgl.NavigationControl(), 'top-right');

  // Time slider (sun icon movement)
  const slider = document.getElementById('time-slider');
  const sunIcon = document.getElementById('sun-icon');
  slider.addEventListener('input', function () {
    const value = slider.value;
    const percent = (value / 23) * 100;
    sunIcon.style.left = percent + '%';
  });

  // Marker for the sensor
  const marker = new mapboxgl.Marker()
    .setLngLat([34.7895184904266, 31.2498119452557])
    .addTo(map);

  // 3D Toggle
  let is3D = false;
  const toggleBtn = document.getElementById('toggle-3d');

  toggleBtn.addEventListener('click', () => {
    if (!is3D) {
      // Switch to a pitched/3D view
      map.easeTo({ pitch: 60, bearing: -17.6, duration: 1000 });
      add3DBuildings();
      toggleBtn.textContent = '2D Map';
      is3D = true;
    } else {
      // Return to flat 2D
      map.easeTo({ pitch: 0, bearing: 0, duration: 1000 });
      remove3DBuildings();
      toggleBtn.textContent = '3D Map';
      is3D = false;
    }
  });

  function add3DBuildings() {
    if (map.getLayer('3d-buildings')) return; // Already added
    map.addLayer({
      id: '3d-buildings',
      source: 'composite',
      'source-layer': 'building',
      filter: ['==', 'extrude', 'true'],
      type: 'fill-extrusion',
      minzoom: 15,
      paint: {
        'fill-extrusion-color': '#aaa',
        'fill-extrusion-height': ['get', 'height'],
        'fill-extrusion-base': ['get', 'min_height'],
        'fill-extrusion-opacity': 0.7
      }
    });
  }

  function remove3DBuildings() {
    if (map.getLayer('3d-buildings')) {
      map.removeLayer('3d-buildings');
    }
  }

  // ========== Sensor Data Logic ==========
  async function fetchSensorData() {
    const response = await fetch('/get-sensor-data');
    return await response.json();
  }

  function calculateShadowQuality(temp, humidity) {
    const shadowScore = Math.min(100, Math.max(0, (humidity * 0.6 + (30 - temp) * 2)));
    return { value: shadowScore };
  }

  function createGradientMeter(value) {
    return `
      <div class="gradient-meter">
        <div class="gradient-bar"></div>
        <div class="meter-indicator" style="left: ${value}%;"></div>
      </div>
    `;
  }

  marker.getElement().addEventListener('click', async () => {
    try {
      const sensorData = await fetchSensorData();
      const temp = sensorData.temperature;
      const humidity = sensorData.humidity;
      const battery = sensorData.battery;
      const time = sensorData.sample_time;
      const qualityObj = calculateShadowQuality(temp, humidity);

      // Show popup
      new mapboxgl.Popup()
        .setLngLat([34.7895184904266, 31.2498119452557])
        .setHTML(`
          <div>
            <strong>Shadow Quality</strong><br>
            ${createGradientMeter(qualityObj.value)}
          </div>
        `)
        .addTo(map);

      // Update sensor panel
      const sensorPanel = document.getElementById('sensor-data-container');
      sensorPanel.innerHTML = `
        <h3>Live Sensor Readings</h3>
        <p><strong>Temperature:</strong> ${temp.toFixed(1)}°C</p>
        <p><strong>Humidity:</strong> ${humidity.toFixed(1)}%</p>
        <p><strong>Battery:</strong> ${battery}%</p>
        <p><strong>Sample Time:</strong> ${time}</p>
        <p><strong>Shadow Quality:</strong></p>
        ${createGradientMeter(qualityObj.value)}
      `;
    } catch (err) {
      console.error('Error fetching sensor data:', err);
    }
  });
});
