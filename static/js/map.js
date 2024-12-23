// Initialize the map
const map = L.map('map').setView([31.25181, 34.7913], 13); // Center on Be'er Sheva

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Add a marker to the map
const marker = L.marker([31.25181, 34.7913]).addTo(map);

// Fetch and display current sensor data
function fetchCurrentData() {
  fetch('http://127.0.0.1:5000/get-sensor-data')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const container = document.getElementById('sensor-data-container');
      container.innerHTML = `
        <p><strong>Temperature:</strong> ${data.temperature} °C</p>
        <p><strong>Humidity:</strong> ${data.humidity} %</p>
        <p><strong>Battery Level:</strong> ${data.battery} %</p>
        <p><strong>Sample Time:</strong> ${data.sample_time}</p>
      `;
    })
    .catch((error) => {
      console.error('Error fetching sensor data:', error);
      const container = document.getElementById('sensor-data-container');
      container.innerHTML = `<p>Error fetching sensor data: ${error.message}</p>`;
    });
}

// Fetch and display historical data
function fetchHistoricalData() {
  fetch('http://127.0.0.1:5000/get-sensor-history')
    .then((response) => {
      console.log('Response received:', response);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log('Historical Data:', data);
      const historyContainer = document.getElementById('history-container');
      const historyList = document.getElementById('history-list');
      historyList.innerHTML = ''; // Clear existing history

      if (Array.isArray(data)) {
        data.forEach((reading) => {
          const listItem = document.createElement('li');
          listItem.innerHTML = `
            <p><strong>Temperature:</strong> ${reading.temperature} °C</p>
            <p><strong>Humidity:</strong> ${reading.humidity} %</p>
            <p><strong>Battery Level:</strong> ${reading.battery} %</p>
            <p><strong>Sample Time:</strong> ${reading.sample_time}</p>
            <hr>
          `;
          historyList.appendChild(listItem);
        });
        historyContainer.style.display = 'block';
      } else {
        console.error('Unexpected data format:', data);
        historyContainer.innerHTML = `<p>Error: Unexpected data format</p>`;
      }
    })
    .catch((error) => {
      console.error('Error fetching historical data:', error);
    });
}



// Add click listener to the marker
marker.on('click', fetchCurrentData);

// Add click listener to the history button
document.getElementById('history-button').addEventListener('click', fetchHistoricalData);
