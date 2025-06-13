mapboxgl.accessToken = 'pk.eyJ1IjoiZWxhZDc2MTAiLCJhIjoiY205andvMnN2MDZpaDJqc2JvaXhlbWR2bCJ9.BL95xjSj5yW4y3Rb_0_l1w';

let is3D = false;
let sensorChart = null;
let landUseVisible = false;

// Global variable to track selected sensor (accessible from HTML)
let selectedSensorId = null;

// Sensor definitions with their locations and IDs (accessible from HTML)
const sensors = [
  {
    id: 'original',
    name: 'SCE College',
    coordinates: [34.7895184904266, 31.2498119452557]
  },
  {
    id: 'park-givaat-rambam',
    name: 'Givaat Rambam Park',
    coordinates: [34.7750, 31.2820]
  },
  {
    id: 'gan-hashlosha-park',
    name: 'Gan Hashlosha Park',
    coordinates: [34.7580, 31.2680]
  },
  {
    id: 'central-bus-station',
    name: 'Central Bus Station',
    coordinates: [34.7913, 31.2431]
  },
  {
    id: 'bgu-university',
    name: 'BGU University Campus',
    coordinates: [34.8094, 31.2622]
  },
  {
    id: 'soroka-medical-center',
    name: 'Soroka Medical Center',
    coordinates: [34.7982, 31.2580]
  }
];

const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v11', // Using light style for better shadow visibility
  center: [34.7913, 31.2518],
  zoom: 15,
  pitch: 0,
  bearing: 0
});

map.addControl(new mapboxgl.NavigationControl());

// Initialize sun position based on slider
let sunPosition = calculateSunPosition(12); // Default to noon

map.on('load', () => {
  const layers = map.getStyle().layers;
  let labelLayerId;
  for (let i = 0; i < layers.length; i++) {
    if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
      labelLayerId = layers[i].id;
      break;
    }
  }

  // Add terrain source for shadow casting surfaces
  map.addSource('mapbox-dem', {
    'type': 'raster-dem',
    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
    'tileSize': 512,
    'maxzoom': 14
  });

  // Add terrain for shadows to cast onto
  map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });

  // Set fog effect to enhance depth perception
  map.setFog({
    'range': [0.5, 10],
    'color': '#f8f8f8',
    'horizon-blend': 0.1
  });

  // Configure the light with shadows enabled
  map.setLight({
    anchor: 'viewport',
    position: sunPosition,
    color: '#ffffff',
    intensity: 0.8
  });

  // Add 3D building layer with fixed consistent color
  map.addLayer({
    'id': '3d-buildings',
    'source': 'composite',
    'source-layer': 'building',
    'filter': ['==', 'extrude', 'true'],
    'type': 'fill-extrusion',
    'minzoom': 15,
    'layout': {
      'visibility': 'none'
    },
    'paint': {
      // Fixed consistent color for buildings
      'fill-extrusion-color': '#9E9E9E', // Medium gray that won't change with lighting
      'fill-extrusion-height': [
        'interpolate',
        ['linear'],
        ['zoom'],
        15, 0,
        15.05, ['get', 'height']
      ],
      'fill-extrusion-base': [
        'interpolate',
        ['linear'],
        ['zoom'],
        15, 0,
        15.05, ['get', 'min_height']
      ],
      'fill-extrusion-opacity': 0.9,
      // Improved shadow receiving properties
      'fill-extrusion-ambient-occlusion-intensity': 0.7,
      'fill-extrusion-ambient-occlusion-radius': 15
    }
  }, labelLayerId);

  // Enhanced ground shadow layer with more pronounced shadows
  map.addLayer({
    'id': 'ground-shadow',
    'type': 'fill',
    'source': 'composite',
    'source-layer': 'building',
    'layout': {
      'visibility': 'none'
    },
    'paint': {
      'fill-color': '#000000',
      'fill-opacity': 0.35, // Increased opacity for more pronounced shadows
      'fill-translate': calculateShadowTranslation(12) // Default shadow position
    }
  }, '3d-buildings');

  // Add land use layers (standardized)
  addLandUseLayers();

  // Add sensor markers
  sensors.forEach(sensor => {
    const markerElement = document.createElement('div');
    markerElement.className = 'custom-marker';
    // Use a single, clearly visible color and larger size for all markers
    markerElement.style.backgroundColor = '#0074D9'; // Bright blue
    markerElement.style.width = '28px';
    markerElement.style.height = '28px';
    markerElement.style.borderRadius = '50%';
    markerElement.style.border = '4px solid white';
    markerElement.style.cursor = 'pointer';
    markerElement.style.boxShadow = '0 4px 8px rgba(0,0,0,0.4)';
    markerElement.style.zIndex = '1000';
    // Optionally, add a white plus icon for extra visibility
    markerElement.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" style="position:absolute;top:5px;left:5px;"><circle cx="9" cy="9" r="8" fill="none" stroke="white" stroke-width="2"/><line x1="9" y1="4" x2="9" y2="14" stroke="white" stroke-width="2"/><line x1="4" y1="9" x2="14" y2="9" stroke="white" stroke-width="2"/></svg>';

    const marker = new mapboxgl.Marker(markerElement)
      .setLngLat(sensor.coordinates)
      .addTo(map);

    markerElement.addEventListener('click', async () => {
      try {
        // Set selected sensor
        selectedSensorId = sensor.id;
        
        // If history is currently shown, refresh it for the new sensor
        const historyContainer = document.getElementById('history-container');
        if (historyContainer && historyContainer.style.display === 'block') {
          // Hide history to trigger a refresh
          historyContainer.style.display = 'none';
          // Reset the button text to show it can be clicked again
          const historyButton = document.getElementById('history-button');
          if (historyButton) {
            historyButton.textContent = 'Show History';
          }
        }
        
        // Fetch sensor data (which now includes radiation)
        const response = await fetch(`/get-sensor-data?sensor_id=${sensor.id}`);
        const data = await response.json();
      
        // Extract data from the response
        const temp = data.temperature !== undefined ? data.temperature : "N/A";
        const humidity = data.humidity !== undefined ? data.humidity : "N/A";
        const battery = data.battery !== undefined ? data.battery : "N/A";
        const radiation = data.radiation !== undefined ? data.radiation : "N/A";
        const time = data.sample_time || "N/A";
        
        // Calculate comfort level based on temperature, humidity, and radiation
        const comfort = calculateComfortLevel(temp, humidity, radiation);
        const comfortInfo = getComfortLevelInfo(comfort);

        // Calculate needle angle - semicircle from left (0%) to right (100%)
        // At 0%: needle points left, at 50%: needle points up, at 100%: needle points right
        const needleAngle = Math.PI - (comfort / 100) * Math.PI; // π to 0 radians
        const needleX = 60 * Math.cos(needleAngle);
        const needleY = -60 * Math.sin(needleAngle); // negative Y to point upward in SVG

        const popupContent = `
          <div style="text-align: center; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 10px 0; color: #333;">${sensor.name}</h4>
            <div style="position: relative; width: 200px; height: 120px; margin: 10px auto;">
              <svg width="200" height="120" viewBox="0 0 200 120">
                <!-- Background - light gray semicircle -->
                <path d="M 20 100 A 80 80 0 0 1 180 100" 
                      fill="#f5f5f5" 
                      stroke="none"/>
                
                <!-- Gradient arc (red-yellow-green) -->
                <defs>
                  <linearGradient id="comfortGradient${sensor.id}" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#ff0000"/>
                    <stop offset="50%" style="stop-color:#ffff00"/>
                    <stop offset="100%" style="stop-color:#00ff00"/>
                  </linearGradient>
                </defs>
                <path d="M 20 100 A 80 80 0 0 1 180 100" 
                      fill="none" 
                      stroke="url(#comfortGradient${sensor.id})" 
                      stroke-width="20" 
                      stroke-linecap="round"/>
                
                <!-- Needle -->
                <g transform="translate(100,100)">
                  <line x1="0" y1="0" 
                        x2="${needleX}" 
                        y2="${needleY}" 
                        stroke="#333" 
                        stroke-width="3" 
                        stroke-linecap="round"/>
                  <circle cx="0" cy="0" r="6" fill="#333"/>
                </g>
              </svg>
            </div>
            <div style="margin-top: 15px;">
              <div style="font-size: 20px; font-weight: bold; color: #333; margin-bottom: 5px;">
                ${comfortInfo.text}
              </div>
              <div style="font-size: 16px; color: #666;">
                Comfort Score: ${Math.round(comfort)}%
              </div>
            </div>
          </div>
        `;

        new mapboxgl.Popup()
          .setLngLat(sensor.coordinates)
          .setHTML(popupContent)
          .addTo(map);

        const container = document.getElementById('sensor-data-container');
        container.innerHTML = `
          <h3>Live Sensor Readings - ${sensor.name}</h3>
          <p><strong>Temperature:</strong> ${typeof temp === 'number' ? temp.toFixed(1) : temp}°C</p>
          <p><strong>Humidity:</strong> ${typeof humidity === 'number' ? humidity.toFixed(1) : humidity}%</p>
          <p><strong>Battery:</strong> ${battery}%</p>
          <p><strong>Radiation:</strong> ${typeof radiation === 'number' ? radiation.toFixed(2) : radiation}</p>
          <p><strong>Sample Time:</strong> ${time}</p>
          <p><strong>Comfort Level:</strong> ${comfortInfo.text}</p>
          <div style="margin-top: 15px; margin-bottom: 20px;">
            <div style="text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 5px;">
              ${comfortInfo.text}
            </div>
            <div style="text-align: center; font-size: 16px; color: #666; margin-bottom: 10px;">
              Comfort Score: ${Math.round(comfort)}%
            </div>
            <div class="gradient-meter">
              <div class="gradient-bar"></div>
              <div class="meter-indicator" style="left: ${comfort}%;"></div>
            </div>
          </div>
        `;
      } catch (err) {
        console.error('Error fetching sensor data:', err);
      }
    });
  });
});

// Add land use layers based on standardized categories
function addLandUseLayers() {
  try {
    // Use the correct Mapbox composite source which includes land use data
    // This data comes from OpenStreetMap and is available globally
    
    // Standardized land use colors based on international standards
    const landUseColors = {
      'residential': '#FFC72C',      // Yellow - Residential areas
      'commercial': '#FF6B6B',       // Red - Commercial and business
      'industrial': '#9B59B6',       // Purple - Industrial areas
      'park': '#4ECDC4',             // Teal - Parks and recreation
      'cemetery': '#95A5A6',         // Gray - Cemeteries
      'hospital': '#E74C3C',         // Dark red - Medical facilities
      'school': '#3498DB',           // Blue - Educational facilities
      'agriculture': '#2ECC71',      // Green - Agricultural land
      'grass': '#A8E6CF',            // Light green - Grassland
      'scrub': '#D5E8D4',            // Very light green - Scrubland
      'wood': '#228B22',             // Forest green - Wooded areas
      'water': '#5DADE2',            // Light blue - Water bodies
      'airport': '#BDC3C7',          // Light gray - Airport areas
      'parking': '#34495E',          // Dark gray - Parking lots
      'pitch': '#52C41A',            // Bright green - Sports fields
      'sand': '#F39C12',             // Orange - Sandy areas
      'rock': '#7F8C8D'              // Medium gray - Rocky areas
    };

    // Add fill layer for land use using the composite source
    map.addLayer({
      'id': 'land-use-fill',
      'type': 'fill',
      'source': 'composite',
      'source-layer': 'landuse',
      'minzoom': 6,
      'maxzoom': 24,
      'layout': {
        'visibility': 'none'
      },
      'paint': {
        'fill-color': [
          'match',
          ['get', 'class'],
          ['residential', 'suburb'], landUseColors.residential,
          ['commercial', 'retail'], landUseColors.commercial,
          ['industrial', 'construction'], landUseColors.industrial,
          ['park', 'recreation_ground', 'playground'], landUseColors.park,
          'cemetery', landUseColors.cemetery,
          ['hospital', 'clinic'], landUseColors.hospital,
          ['school', 'college', 'university'], landUseColors.school,
          ['agriculture', 'farmland', 'farmyard'], landUseColors.agriculture,
          ['grass', 'meadow'], landUseColors.grass,
          ['scrub', 'scrubland'], landUseColors.scrub,
          ['wood', 'forest'], landUseColors.wood,
          'airport', landUseColors.airport,
          'parking', landUseColors.parking,
          ['pitch', 'sports_pitch'], landUseColors.pitch,
          'sand', landUseColors.sand,
          'rock', landUseColors.rock,
          '#E0E0E0' // Default light gray for unclassified
        ],
        'fill-opacity': [
          'interpolate',
          ['linear'],
          ['zoom'],
          6, 0.3,
          10, 0.5,
          14, 0.7,
          18, 0.8
        ]
      }
    });

         // Add natural land cover layer for better coverage
     map.addLayer({
       'id': 'natural-land-use',
       'type': 'fill',
       'source': 'composite',
       'source-layer': 'natural_label',
       'minzoom': 6,
       'maxzoom': 24,
       'layout': {
         'visibility': 'none'
       },
       'paint': {
         'fill-color': [
           'match',
           ['get', 'class'],
           'wood', landUseColors.wood,
           'water', landUseColors.water,
           'grass', landUseColors.grass,
           'sand', landUseColors.sand,
           'rock', landUseColors.rock,
           '#D0D0D0'
         ],
         'fill-opacity': [
           'interpolate',
           ['linear'],
           ['zoom'],
           6, 0.3,
           10, 0.4,
           14, 0.6,
           18, 0.7
         ]
       }
     });

      // Add additional building-based land use for better zoom coverage
      map.addLayer({
        'id': 'building-land-use',
        'type': 'fill',
        'source': 'composite',
        'source-layer': 'building',
        'minzoom': 14,
        'maxzoom': 24,
        'layout': {
          'visibility': 'none'
        },
        'paint': {
          'fill-color': [
            'match',
            ['get', 'type'],
            ['house', 'apartments', 'residential'], landUseColors.residential,
            ['commercial', 'office', 'retail'], landUseColors.commercial,
            ['industrial', 'warehouse'], landUseColors.industrial,
            ['hospital', 'clinic'], landUseColors.hospital,
            ['school', 'university'], landUseColors.school,
            '#F0F0F0' // Light gray for general buildings
          ],
          'fill-opacity': 0.4
        }
      });

         // Add outline layer for better definition
     map.addLayer({
       'id': 'land-use-outline',
       'type': 'line',
       'source': 'composite',
       'source-layer': 'landuse',
       'minzoom': 12,
       'maxzoom': 24,
       'layout': {
         'visibility': 'none'
       },
       'paint': {
         'line-color': '#555555',
         'line-width': [
           'interpolate',
           ['linear'],
           ['zoom'],
           12, 0.3,
           16, 0.5,
           20, 0.8
         ],
         'line-opacity': 0.4
       }
     });

    console.log('Land use layers added successfully');
  } catch (error) {
    console.error('Error adding land use layers:', error);
  }
}

// Toggle land use layer visibility
function toggleLandUse() {
  landUseVisible = !landUseVisible;
  const button = document.querySelector('.land-use-button');
  const legend = document.getElementById('land-use-legend');
  
  if (landUseVisible) {
    // Show all land use related layers
    if (map.getLayer('land-use-fill')) {
      map.setLayoutProperty('land-use-fill', 'visibility', 'visible');
    }
    if (map.getLayer('land-use-outline')) {
      map.setLayoutProperty('land-use-outline', 'visibility', 'visible');
    }
    if (map.getLayer('natural-land-use')) {
      map.setLayoutProperty('natural-land-use', 'visibility', 'visible');
    }
    if (map.getLayer('building-land-use')) {
      map.setLayoutProperty('building-land-use', 'visibility', 'visible');
    }
    
    button.classList.add('active');
    button.textContent = 'Hide Land Use';
    if (legend) legend.style.display = 'block';
    console.log('Land use layers enabled');
  } else {
    // Hide all land use related layers
    if (map.getLayer('land-use-fill')) {
      map.setLayoutProperty('land-use-fill', 'visibility', 'none');
    }
    if (map.getLayer('land-use-outline')) {
      map.setLayoutProperty('land-use-outline', 'visibility', 'none');
    }
    if (map.getLayer('natural-land-use')) {
      map.setLayoutProperty('natural-land-use', 'visibility', 'none');
    }
    if (map.getLayer('building-land-use')) {
      map.setLayoutProperty('building-land-use', 'visibility', 'none');
    }
    
    button.classList.remove('active');
    button.textContent = 'Land Use';
    if (legend) legend.style.display = 'none';
    console.log('Land use layers disabled');
  }
}

function toggleView() {
  if (is3D) {
    map.easeTo({ pitch: 0, bearing: 0, duration: 1000 });
    if (map.getLayer('3d-buildings')) {
      map.setLayoutProperty('3d-buildings', 'visibility', 'none');
      map.setLayoutProperty('ground-shadow', 'visibility', 'none');
    }
    is3D = false;
  } else {
    map.easeTo({ pitch: 60, bearing: -17.6, duration: 1000 });
    if (map.getLayer('3d-buildings')) {
      map.setLayoutProperty('3d-buildings', 'visibility', 'visible');
      map.setLayoutProperty('ground-shadow', 'visibility', 'visible');
    }
    is3D = true;

    // Update shadows when switching to 3D
    updateShadows();
  }
}

// Improved sun position calculation based on realistic solar position
function calculateSunPosition(hour) {
  // If it's night time, position sun below horizon
  if (hour < 6 || hour > 18) {
    return [1, hour < 6 ? 0 : 180, -10];
  }

  // Calculate relative time through the day (0 at sunrise, 1 at sunset)
  const dayProgress = (hour - 6) / 12;

  // Calculate azimuth
  // Sunrise: 0° (East)
  // Solar noon: 90° (South)
  // Sunset: 180° (West)
  const azimuth = dayProgress * 180;

  // Calculate elevation (max 60° at solar noon)
  const elevation = 60 * Math.sin(Math.PI * dayProgress);

  return [1, azimuth, elevation];
}

// Improved shadow translation calculation for more realistic shadows
function calculateShadowTranslation(hour) {
  // If it's night time, no shadows
  if (hour < 6 || hour > 18) {
    return [0, 0];
  }

  // Calculate relative time through the day (0 at sunrise, 1 at sunset)
  const dayProgress = (hour - 6) / 12;

  // Calculate sun's azimuth (0° = East, 90° = South, 180° = West)
  const sunAzimuth = dayProgress * 180;

  // Convert to radians
  const azimuthRad = (sunAzimuth * Math.PI) / 180;

  // Calculate shadow length - longer at sunrise/sunset, shorter at noon
  const baseLength = 15;
  const extraLength = 25 * (1 - Math.sin(Math.PI * dayProgress));
  const shadowLength = baseLength + extraLength;

  // Calculate x and y translation
  // At sunrise (0°): shadows point left (-x)
  // At noon (90°): shadows point up (-y)
  // At sunset (180°): shadows point right (+x)
  const dx = -Math.cos(azimuthRad) * shadowLength;
  const dy = -Math.sin(azimuthRad) * shadowLength;

  return [dx, dy];
}

// Get sunlight color based on time of day (warmer at sunrise/sunset)
function getSunlightColor(hour) {
  // Night time - cooler blue light
  if (hour < 6 || hour > 18) {
    return '#102030'; // dark blue night light
  }
  // Dawn/dusk - orange/red light
  else if (hour < 7 || hour > 17) {
    return '#ff7b39'; // strong orange sunrise/sunset
  }
  // Early morning/late afternoon - warm light
  else if (hour < 9 || hour > 15) {
    return '#fff5e6'; // slightly warm light
  }
  // Midday - white light
  else {
    return '#ffffff'; // white daylight
  }
}

// Get light intensity based on time of day
function getSunlightIntensity(hour) {
  // Night time - very low intensity
  if (hour < 6 || hour > 18) {
    return 0.2; // low light at night
  }
  // Dawn/dusk - medium-low intensity
  else if (hour < 7 || hour > 17) {
    return 0.4; // dawn/dusk
  }
  // Early morning/late afternoon - medium intensity
  else if (hour < 8 || hour > 16) {
    return 0.6; // morning/evening
  }
  // Midday - highest intensity
  else {
    return 0.8; // bright midday
  }
}

// Update shadows based on current time slider position
function updateShadows() {
  const hour = parseInt(document.getElementById('time-slider').value);
  const isNightTime = hour < 6 || hour > 18;

  if (map.loaded()) {
    // Update the light source
    sunPosition = calculateSunPosition(hour);
    map.setLight({
      anchor: 'map',
      position: sunPosition,
      color: getSunlightColor(hour),
      intensity: getSunlightIntensity(hour)
    });

    // Update shadow handling
    if (map.getLayer('ground-shadow')) {
      if (isNightTime) {
        map.setPaintProperty('ground-shadow', 'fill-opacity', 0);
      } else {
        const shadowTranslation = calculateShadowTranslation(hour);
        map.setPaintProperty('ground-shadow', 'fill-translate', shadowTranslation);

        // Adjust shadow opacity based on time of day
        let shadowOpacity;
        if (hour >= 10 && hour <= 14) {
          shadowOpacity = 0.7; // stronger shadows at midday
        } else if (hour < 7 || hour > 17) {
          shadowOpacity = 0.5; // medium shadows at dawn/dusk
        } else {
          shadowOpacity = 0.6; // normal shadows during day
        }
        map.setPaintProperty('ground-shadow', 'fill-opacity', shadowOpacity);
      }
    }
  }
}

// Slider and time display logic
document.addEventListener('DOMContentLoaded', () => {
  const slider = document.getElementById('time-slider');
  const sunIcon = document.getElementById('sun-icon');
  const sliderContainer = document.getElementById('slider-container');
  const graphButton = document.getElementById('graph-button');
  const graphModal = document.getElementById('graph-modal');

  if (slider && sunIcon) {
    // Create time display element
    const timeDisplay = document.createElement('div');
    timeDisplay.id = 'time-display';
    timeDisplay.style.textAlign = 'center';
    timeDisplay.style.marginTop = '5px';
    timeDisplay.style.fontWeight = 'bold';
    timeDisplay.style.fontSize = '16px';

    // Add time display below the slider
    sliderContainer.appendChild(timeDisplay);

    // Update time display and sun position when slider changes
    slider.addEventListener('input', function() {
      const hour = parseInt(slider.value);
      const formattedHour = hour.toString().padStart(2, '0') + ':00';
      timeDisplay.textContent = formattedHour;

      // Update sun icon position
      const percent = (hour / 23) * 100;
      sunIcon.style.left = percent + '%';

      // Update shadows
      updateShadows();
    });

    // Initialize with default time
    const initialHour = parseInt(slider.value);
    const formattedInitialHour = initialHour.toString().padStart(2, '0') + ':00';
    timeDisplay.textContent = formattedInitialHour;

    // Position sun icon correctly on page load
    const initialPercent = (initialHour / 23) * 100;
    sunIcon.style.left = initialPercent + '%';

    // Create and position morning and evening time indicators
    const createTimeLabel = (id, text, leftPos) => {
      const label = document.createElement('div');
      label.id = id;
      label.textContent = text;
      label.style.position = 'absolute';
      label.style.bottom = '5px';
      label.style.left = leftPos;
      label.style.fontSize = '14px';
      label.style.fontWeight = 'bold';
      sliderContainer.appendChild(label);
    };
    
    createTimeLabel('morning-label', '6 AM', '10px');
    createTimeLabel('evening-label', '6 PM', 'calc(100% - 40px)');

    // Initialize shadows with default slider value
    setTimeout(() => {
      updateShadows();
    }, 1000); // Small delay to ensure map is fully loaded
    
    // Add graph button functionality
    if (graphButton) {
      graphButton.addEventListener('click', function() {
        // Show the modal
        graphModal.style.display = 'flex';
        
        // Fetch sensor history data for the graph
        fetchAndDisplayGraph();
      });
    }
  }
});

// Function to fetch sensor history and create a graph
function fetchAndDisplayGraph() {
  if (!selectedSensorId) {
    alert('Please select a sensor on the map first before viewing the graph.');
    return;
  }
  
  fetch(`/get-sensor-history?sensor_id=${selectedSensorId}`)
    .then(response => response.json())
    .then(data => {
      if (data.length === 0) {
        document.getElementById('modal-chart-container').innerHTML = '<p>No historical data available</p>';
        return;
      }
      
      // Process ALL data points (no grouping, no filtering)
      const allDataPoints = [];
      
      // Parse and sort all data by timestamp
      data.forEach(item => {
        const date = new Date(item.sample_time);
        allDataPoints.push({
          timestamp: date,
          temperature: item.temperature,
          humidity: item.humidity,
          radiation: item.radiation || 0
        });
      });
      
      // Sort by time of day (00:00 to 23:59) for proper chronological display
      allDataPoints.sort((a, b) => {
        const hourA = a.timestamp.getHours();
        const minuteA = a.timestamp.getMinutes();
        const hourB = b.timestamp.getHours();
        const minuteB = b.timestamp.getMinutes();
        
        // Convert to minutes since midnight for proper sorting
        const totalMinutesA = hourA * 60 + minuteA;
        const totalMinutesB = hourB * 60 + minuteB;
        
        return totalMinutesA - totalMinutesB;
      });
      
      // Extract arrays for chart
      const times = [];
      const temperatures = [];
      const humidities = [];
      const radiations = [];
      
      allDataPoints.forEach(point => {
        // Format time as HH:MM in 24-hour format
        const hours = String(point.timestamp.getHours()).padStart(2, '0');
        const minutes = String(point.timestamp.getMinutes()).padStart(2, '0');
        times.push(`${hours}:${minutes}`);
        temperatures.push(point.temperature);
        humidities.push(point.humidity);
        radiations.push(point.radiation);
      });
      
      // Get display date from first data point
      const displayDate = allDataPoints[0].timestamp.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
      
      console.log(`Displaying graph with ${allDataPoints.length} data points`);
      console.log(`Time range: ${times[0]} to ${times[times.length - 1]}`);
      
      // Find the selected sensor name
      const selectedSensor = sensors.find(s => s.id === selectedSensorId);
      const sensorName = selectedSensor ? selectedSensor.name : 'Unknown Sensor';
      
      // Create chart with ALL data points
      createSensorChart(times, temperatures, humidities, radiations, displayDate, sensorName);
    })
    .catch(error => {
      console.error('Error fetching sensor history for graph:', error);
      document.getElementById('modal-chart-container').innerHTML = '<p>Error loading graph data</p>';
    });
}

// Function to create chart with Chart.js
function createSensorChart(labels, temperatures, humidities, radiations, dateLabel, sensorName = '') {
  const ctx = document.getElementById('sensor-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (sensorChart) {
    sensorChart.destroy();
  }
  
  // Set chart title
  const titleText = sensorName ? `${sensorName} - Readings for ${dateLabel}` : `Sensor Readings for ${dateLabel}`;
  document.querySelector('.modal-title').textContent = titleText;
  
  // Create gradient for temperature
  const tempGradient = ctx.createLinearGradient(0, 0, 0, 400);
  tempGradient.addColorStop(0, 'rgba(255, 99, 132, 0.8)');
  tempGradient.addColorStop(1, 'rgba(255, 99, 132, 0.1)');
  
  // Create gradient for humidity
  const humidityGradient = ctx.createLinearGradient(0, 0, 0, 400);
  humidityGradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
  humidityGradient.addColorStop(1, 'rgba(54, 162, 235, 0.1)');
  
  // Create gradient for radiation
  const radiationGradient = ctx.createLinearGradient(0, 0, 0, 400);
  radiationGradient.addColorStop(0, 'rgba(255, 205, 86, 0.8)');
  radiationGradient.addColorStop(1, 'rgba(255, 205, 86, 0.1)');
  
  sensorChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Temperature (°C)',
          data: temperatures,
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: tempGradient,
          tension: 0.4,
          fill: true,
          pointRadius: 6,
          pointBackgroundColor: 'rgb(255, 99, 132)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          yAxisID: 'y'
        },
        {
          label: 'Humidity (%)',
          data: humidities,
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: humidityGradient,
          tension: 0.4,
          fill: true,
          pointRadius: 6,
          pointBackgroundColor: 'rgb(54, 162, 235)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          yAxisID: 'y'
        },
        {
          label: 'Radiation',
          data: radiations,
          borderColor: 'rgb(255, 205, 86)',
          backgroundColor: radiationGradient,
          tension: 0.4,
          fill: true,
          pointRadius: 6,
          pointBackgroundColor: 'rgb(255, 205, 86)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: false
        },
        legend: {
          position: 'top',
          labels: {
            font: {
              size: 14,
              weight: 'bold'
            },
            padding: 20
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleFont: {
            size: 16
          },
          bodyFont: {
            size: 14
          },
          padding: 12,
          cornerRadius: 6
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Time',
            font: {
              size: 14,
              weight: 'bold'
            },
            padding: 10
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            maxTicksLimit: 24,
            callback: function(value, index, values) {
              // Show hourly labels (00:00, 01:00, 02:00, etc.)
              if (index % Math.max(1, Math.floor(values.length / 24)) === 0) {
                const label = this.getLabelForValue(value);
                if (label && label.includes(':')) {
                  return label;
                }
              }
              return '';
            },
            font: {
              size: 12
            }
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Temperature (°C) / Humidity (%)',
            font: {
              size: 14,
              weight: 'bold'
            },
            padding: 10
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            font: {
              size: 12
            }
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Radiation',
            font: {
              size: 14,
              weight: 'bold'
            },
            padding: 10
          },
          grid: {
            drawOnChartArea: false,
            color: 'rgba(255, 205, 86, 0.2)'
          },
          ticks: {
            font: {
              size: 12
            }
          }
        }
      },
      elements: {
        line: {
          borderWidth: 3
        }
      }
    }
  });
}

// Calculate comfort level based on temperature, humidity, and radiation
function calculateComfortLevel(temp, humidity, radiation) {
  // Base comfort calculation based on ideal temperature of 22°C and humidity of 60%
  let comfort = 100 - Math.abs(22 - temp) * 2 - Math.abs(60 - humidity) * 0.5;
  
  // Include radiation in comfort calculation if available
  if (radiation && typeof radiation === 'number') {
    // Reduce comfort by 1 point for each unit of radiation above the safe threshold
    const safeRadiationThreshold = 0.5;
    if (radiation > safeRadiationThreshold) {
      comfort -= (radiation - safeRadiationThreshold) * 10;
    }
  }
  
  return Math.max(0, Math.min(100, comfort));
}

// Get comfort level text and category
function getComfortLevelInfo(comfortScore) {
  if (comfortScore >= 80) {
    return { text: "Very High Comfort", category: "very-high" };
  } else if (comfortScore >= 60) {
    return { text: "High Comfort", category: "high" };
  } else if (comfortScore >= 40) {
    return { text: "Medium Comfort", category: "medium" };
  } else if (comfortScore >= 20) {
    return { text: "Low Comfort", category: "low" };
  } else {
    return { text: "Very Low Comfort", category: "very-low" };
  }
}

