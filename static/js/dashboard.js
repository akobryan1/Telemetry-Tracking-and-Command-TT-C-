// TT&C Dashboard JavaScript

// Auto-refresh interval (milliseconds)
const REFRESH_INTERVAL = 5000;
let refreshTimer = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('TT&C Dashboard initialized');
    
    // Initial data load
    updateStatus();
    loadPasses();
    updateCommandParams();
    
    // Start auto-refresh
    startAutoRefresh();
});

// Start automatic refresh
function startAutoRefresh() {
    refreshTimer = setInterval(() => {
        updateStatus();
    }, REFRESH_INTERVAL);
    
    document.getElementById('refresh-status').textContent = 'Enabled';
}

// Stop automatic refresh
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
    document.getElementById('refresh-status').textContent = 'Disabled';
}

// Update satellite and network status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.error) {
            console.error('API Error:', data.error);
            return;
        }
        
        // Update satellite info
        document.getElementById('sat-name').textContent = data.satellite.name;
        document.getElementById('sat-battery').textContent = `${data.satellite.battery_voltage} V`;
        document.getElementById('sat-temp').textContent = `${data.satellite.temperature} °C`;
        document.getElementById('sat-mode').textContent = data.satellite.mode;
        
        // Color code mode badge
        const modeBadge = document.getElementById('sat-mode');
        modeBadge.className = 'value mode-badge';
        if (data.satellite.mode === 'SAFE') {
            modeBadge.style.background = '#ffc107';
        } else if (data.satellite.mode === 'SCIENCE') {
            modeBadge.style.background = '#28a745';
        } else {
            modeBadge.style.background = '#17a2b8';
        }
        
        document.getElementById('sat-position').textContent = 
            `${data.satellite.position.latitude.toFixed(2)}°, ${data.satellite.position.longitude.toFixed(2)}°`;
        document.getElementById('sat-altitude').textContent = 
            `${data.satellite.position.altitude_km.toFixed(2)} km`;
        
        // Update network info
        document.getElementById('active-stations').textContent = data.network.active_stations.length;
        document.getElementById('total-stations').textContent = data.network.total_stations;
        
        // Update station list
        updateStationList(data.network.visibility);
        
        // Update telemetry (fetch separately for real-time data)
        updateTelemetry();
        
        // Update last update time
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleTimeString();
        
    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

// Update station visibility cards
function updateStationList(visibilityData) {
    const stationList = document.getElementById('station-list');
    stationList.innerHTML = '';
    
    for (const [stationName, data] of Object.entries(visibilityData)) {
        const card = document.createElement('div');
        card.className = `station-card ${data.is_visible ? 'visible' : ''}`;
        
        let statusHTML = data.is_visible
            ? `<div class="station-status">✓ VISIBLE</div>`
            : `<div class="station-status">• Not visible</div>`;
        
        let dataHTML = '';
        if (data.is_visible) {
            dataHTML = `
                <div class="station-data">
                    El: ${data.elevation}° | Az: ${data.azimuth}°<br>
                    Range: ${data.range_km.toFixed(1)} km
                </div>
            `;
        }
        
        card.innerHTML = `
            <div class="station-name">${stationName}</div>
            ${statusHTML}
            ${dataHTML}
        `;
        
        stationList.appendChild(card);
    }
}

// Update telemetry data
async function updateTelemetry() {
    try {
        const response = await fetch('/api/telemetry');
        const data = await response.json();
        
        if (data.error) {
            return;
        }
        
        document.getElementById('telem-battery').textContent = data.battery_voltage.toFixed(2);
        document.getElementById('telem-solar').textContent = data.solar_current.toFixed(2);
        document.getElementById('telem-temperature').textContent = data.temperature.toFixed(1);
        document.getElementById('telem-count').textContent = data.telemetry_id;
        
    } catch (error) {
        console.error('Failed to update telemetry:', error);
    }
}

// Load pass predictions
async function loadPasses() {
    try {
        const stationSelect = document.getElementById('station-select');
        const selectedStation = stationSelect.value;
        
        let url = '/api/passes?hours=12';
        if (selectedStation) {
            url += `&station=${selectedStation}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            console.error('API Error:', data.error);
            return;
        }
        
        const passesList = document.getElementById('passes-list');
        passesList.innerHTML = '';
        
        let passCount = 0;
        
        // Display passes for each station
        for (const [stationName, passes] of Object.entries(data.passes)) {
            passes.forEach((pass, index) => {
                passCount++;
                
                const passItem = document.createElement('div');
                passItem.className = 'pass-item';
                
                const aosTime = new Date(pass.aos).toLocaleString();
                const losTime = new Date(pass.los).toLocaleString();
                
                passItem.innerHTML = `
                    <div class="pass-header">
                        <span>${stationName} - Pass #${index + 1}</span>
                        <span>${pass.duration_min} min</span>
                    </div>
                    <div class="pass-details">
                        <div>AOS: ${aosTime}</div>
                        <div>LOS: ${losTime}</div>
                        <div>Max El: ${pass.max_elevation}°</div>
                        <div>AOS Az: ${pass.aos_azimuth}°</div>
                    </div>
                `;
                
                passesList.appendChild(passItem);
            });
        }
        
        if (passCount === 0) {
            passesList.innerHTML = '<p style="padding: 1rem; text-align: center; color: #666;">No passes predicted in the next 12 hours</p>';
        }
        
    } catch (error) {
        console.error('Failed to load passes:', error);
    }
}

// Update command parameter fields based on selected command
function updateCommandParams() {
    const commandType = document.getElementById('command-type').value;
    const paramsDiv = document.getElementById('command-params');
    
    paramsDiv.innerHTML = '';
    
    if (commandType === 'SET_MODE') {
        paramsDiv.innerHTML = `
            <label for="mode-param">Mode:</label>
            <select id="mode-param">
                <option value="NOMINAL">NOMINAL</option>
                <option value="SAFE">SAFE</option>
                <option value="SCIENCE">SCIENCE</option>
            </select>
        `;
    } else if (commandType === 'ADJUST_POWER') {
        paramsDiv.innerHTML = `
            <label for="power-param">Power Delta (V):</label>
            <input type="number" id="power-param" step="0.1" value="0.5" min="-5" max="5">
        `;
    }
    // Other command types don't need parameters
}

// Send command to satellite
async function sendCommand() {
    const commandType = document.getElementById('command-type').value;
    const commandData = {
        command_type: commandType
    };
    
    // Add parameters based on command type
    if (commandType === 'SET_MODE') {
        const modeParam = document.getElementById('mode-param');
        if (modeParam) {
            commandData.mode = modeParam.value;
        }
    } else if (commandType === 'ADJUST_POWER') {
        const powerParam = document.getElementById('power-param');
        if (powerParam) {
            commandData.power_delta = parseFloat(powerParam.value);
        }
    }
    
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(commandData)
        });
        
        const result = await response.json();
        
        // Add to command log
        const logEntry = document.createElement('div');
        logEntry.className = result.success ? 'log-entry' : 'log-entry error';
        
        const now = new Date().toLocaleTimeString();
        
        if (result.success) {
            logEntry.innerHTML = `
                <div class="time">${now}</div>
                <div class="command">CMD#${result.command_id}: ${commandType}</div>
                <div>Status: ${result.status}</div>
                <div>Station: ${result.uplink_station}</div>
                <div>${result.acknowledgment}</div>
            `;
        } else {
            logEntry.innerHTML = `
                <div class="time">${now}</div>
                <div class="command">FAILED: ${commandType}</div>
                <div>Error: ${result.error}</div>
            `;
        }
        
        const logContainer = document.getElementById('command-history');
        logContainer.insertBefore(logEntry, logContainer.firstChild);
        
        // Update status after command
        setTimeout(updateStatus, 500);
        
    } catch (error) {
        console.error('Failed to send command:', error);
        alert('Failed to send command: ' + error.message);
    }
}
