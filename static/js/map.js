document.addEventListener('DOMContentLoaded', () => {
  // Handle sun icon movement
  const slider = document.getElementById('time-slider');
  const sunIcon = document.getElementById('sun-icon');

  slider.addEventListener('input', function () {
    const value = slider.value;
    const percent = (value / 23) * 100;
    sunIcon.style.left = percent + '%';
  });

  // Initialize map
  const map = L.map('map').setView([31.2498119452557, 34.7895184904266], 15);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);

  const marker = L.marker([31.2498119452557, 34.7895184904266]).addTo(map);

  async function fetchSensorData() {
    const response = await fetch('/get-sensor-data');
    const data = await response.json();
    return data;
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

  marker.on('click', async () => {
    try {
      const sensorData = await fetchSensorData();
      const temp = sensorData.temperature;
      const humidity = sensorData.humidity;
      const qualityObj = calculateShadowQuality(temp, humidity);

      // Update popup
      const popupContent = `
        <div>
          <strong>Shadow Quality</strong><br>
          ${createGradientMeter(qualityObj.value)}
        </div>
      `;
      marker.bindPopup(popupContent).openPopup();

      // Update sensor panel on the left
      const sensorPanel = document.getElementById('sensor-data-container');
      sensorPanel.innerHTML = `
        <h3>Live Sensor Readings</h3>
        <p><strong>Temperature:</strong> ${temp.toFixed(1)}°C</p>
        <p><strong>Humidity:</strong> ${humidity.toFixed(1)}%</p>
        <p><strong>Shadow Quality:</strong></p>
        ${createGradientMeter(qualityObj.value)}
      `;
    } catch (err) {
      console.error('Error fetching sensor data:', err);
    }
  });
});
