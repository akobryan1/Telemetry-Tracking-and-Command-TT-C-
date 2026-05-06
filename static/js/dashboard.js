// TT&C Dashboard JavaScript (Phase 7: Real-Time WebSocket Updates)

// WebSocket connection
let socket = null;
let isConnected = false;

// Auto-refresh interval (fallback for REST API if WebSocket fails)
const REFRESH_INTERVAL = 5000;
let refreshTimer = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('TT&C Dashboard initialized (Phase 7: WebSocket Mode)');
    
    // Phase 8: Load available satellites
    loadSatellites();
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Initial data load
    loadPasses();
    updateCommandParams();
});

// Initialize WebSocket connection
function initializeWebSocket() {
    try {
        // Connect to Socket.IO server
        socket = io({
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 10
        });
        
        // Connection established
        socket.on('connect', function() {
            console.log('✓ WebSocket connected');
            isConnected = true;
            updateConnectionStatus('Connected (Real-time)', 'connected');
            
            // Stop polling fallback if active
            stopAutoRefresh();
            
            // Request initial status
            socket.emit('request_status');
        });
        
        // Connection failed
        socket.on('connect_error', function(error) {
            console.error('✗ WebSocket connection error:', error);
            updateConnectionStatus('Connection Error - Using Polling', 'error');
            
            // Fallback to REST API polling
            if (!refreshTimer) {
                startAutoRefresh();
            }
        });
        
        // Disconnected
        socket.on('disconnect', function(reason) {
            console.log('✗ WebSocket disconnected:', reason);
            isConnected = false;
            updateConnectionStatus('Disconnected - Reconnecting...', 'disconnected');
            
            // Fallback to polling
            startAutoRefresh();
        });
        
        // Connection status message
        socket.on('connection_status', function(data) {
            console.log('Connection status:', data.message);
        });
        
        // Real-time status updates
        socket.on('status_update', function(data) {
            updateStatusDisplay(data);
        });
        
        // Error messages
        socket.on('error', function(data) {
            console.error('WebSocket error:', data.message);
        });
        
    } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        updateConnectionStatus('WebSocket Failed - Using Polling', 'error');
        startAutoRefresh();
    }
}

// Update connection status display
function updateConnectionStatus(message, status) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `status-${status}`;
    }
}

// Start automatic refresh (fallback mode)
function startAutoRefresh() {
    if (refreshTimer) return; // Already running
    
    refreshTimer = setInterval(() => {
        updateStatus();
    }, REFRESH_INTERVAL);
    
    console.log('Polling mode activated (5s interval)');
}

// Stop automatic refresh
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
        console.log('Polling mode deactivated');
    }
}

// Update satellite and network status (REST API fallback)
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.error) {
            console.error('API Error:', data.error);
            return;
        }
        
        updateStatusDisplay(data);
        
    } catch (error) {
        console.error('Failed to fetch status:', error);
    }
}

// Update status display (used by both WebSocket and REST API)
function updateStatusDisplay(data) {
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

// ============================================================
// Historical Data Functions (Phase 6)
// ============================================================

function showHistoryTab(tabName) {
    // Hide all content
    document.querySelectorAll('.history-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected content
    document.getElementById(`history-${tabName}`).classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
    
    // Load data for the selected tab
    if (tabName === 'telemetry') {
        loadTelemetryHistory();
    } else if (tabName === 'commands') {
        loadCommandsHistory();
    } else if (tabName === 'tracking') {
        loadTrackingHistory();
    }
}

async function loadTelemetryHistory() {
    const limit = document.getElementById('telemetry-limit').value;
    
    try {
        const response = await fetch(`/api/history/telemetry?limit=${limit}`);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('telemetry-history-table').innerHTML = 
                `<p class="error">Error: ${data.error}</p>`;
            return;
        }
        
        if (data.count === 0) {
            document.getElementById('telemetry-history-table').innerHTML = 
                '<p class="info">No telemetry data available yet. Data will appear after API calls.</p>';
            return;
        }
        
        // Build table
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Ground Station</th>
                        <th>Battery (V)</th>
                        <th>Solar (A)</th>
                        <th>Temp (°C)</th>
                        <th>Mode</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.telemetry.forEach(record => {
            const timestamp = new Date(record.timestamp).toLocaleString();
            html += `
                <tr>
                    <td>${timestamp}</td>
                    <td>${record.ground_station}</td>
                    <td>${record.battery_voltage ? record.battery_voltage.toFixed(2) : 'N/A'}</td>
                    <td>${record.solar_current ? record.solar_current.toFixed(2) : 'N/A'}</td>
                    <td>${record.temperature ? record.temperature.toFixed(1) : 'N/A'}</td>
                    <td><span class="mode-badge">${record.mode || 'N/A'}</span></td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        html += `<p class="info">Showing ${data.count} of ${data.count} records</p>`;
        
        document.getElementById('telemetry-history-table').innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load telemetry history:', error);
        document.getElementById('telemetry-history-table').innerHTML = 
            `<p class="error">Failed to load data: ${error.message}</p>`;
    }
}

async function loadCommandsHistory() {
    const limit = document.getElementById('commands-limit').value;
    
    try {
        const response = await fetch(`/api/history/commands?limit=${limit}`);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('commands-history-table').innerHTML = 
                `<p class="error">Error: ${data.error}</p>`;
            return;
        }
        
        if (data.count === 0) {
            document.getElementById('commands-history-table').innerHTML = 
                '<p class="info">No command history available yet. Send commands to see them here.</p>';
            return;
        }
        
        // Build table
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Command Type</th>
                        <th>Command ID</th>
                        <th>Status</th>
                        <th>Uplink Station</th>
                        <th>Parameters</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.commands.forEach(record => {
            const timestamp = new Date(record.timestamp).toLocaleString();
            const params = JSON.stringify(record.parameters || {});
            html += `
                <tr>
                    <td>${timestamp}</td>
                    <td>${record.command_type}</td>
                    <td>${record.command_id}</td>
                    <td><span class="status-badge ${record.status}">${record.status}</span></td>
                    <td>${record.uplink_station}</td>
                    <td class="params">${params}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        html += `<p class="info">Showing ${data.count} of ${data.count} records</p>`;
        
        document.getElementById('commands-history-table').innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load commands history:', error);
        document.getElementById('commands-history-table').innerHTML = 
            `<p class="error">Failed to load data: ${error.message}</p>`;
    }
}

async function loadTrackingHistory() {
    const limit = document.getElementById('tracking-limit').value;
    const station = document.getElementById('tracking-station').value;
    
    let url = `/api/history/tracking?limit=${limit}`;
    if (station) {
        url += `&station=${station}`;
    }
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) {
            document.getElementById('tracking-history-table').innerHTML = 
                `<p class="error">Error: ${data.error}</p>`;
            return;
        }
        
        if (data.count === 0) {
            document.getElementById('tracking-history-table').innerHTML = 
                '<p class="info">No tracking data available yet. Data is logged during status updates.</p>';
            return;
        }
        
        // Build table
        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Station</th>
                        <th>Azimuth (°)</th>
                        <th>Elevation (°)</th>
                        <th>Range (km)</th>
                        <th>Range Rate (km/s)</th>
                        <th>Visible</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.tracking.forEach(record => {
            const timestamp = new Date(record.timestamp).toLocaleString();
            const visibleIcon = record.is_visible ? '✅' : '❌';
            html += `
                <tr class="${record.is_visible ? 'visible' : 'not-visible'}">
                    <td>${timestamp}</td>
                    <td>${record.station}</td>
                    <td>${record.azimuth_deg ? record.azimuth_deg.toFixed(2) : 'N/A'}</td>
                    <td>${record.elevation_deg ? record.elevation_deg.toFixed(2) : 'N/A'}</td>
                    <td>${record.range_km ? record.range_km.toFixed(2) : 'N/A'}</td>
                    <td>${record.range_rate_km_s ? record.range_rate_km_s.toFixed(3) : 'N/A'}</td>
                    <td>${visibleIcon}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        html += `<p class="info">Showing ${data.count} of ${data.count} records${station ? ` for ${station}` : ''}</p>`;
        
        document.getElementById('tracking-history-table').innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load tracking history:', error);
        document.getElementById('tracking-history-table').innerHTML = 
            `<p class="error">Failed to load data: ${error.message}</p>`;
    }
}


// ============================================================
// Phase 8: Multi-Satellite Support
// ============================================================

async function loadSatellites() {
    try {
        const response = await fetch('/api/satellites');
        const data = await response.json();
        
        const select = document.getElementById('satellite-select');
        select.innerHTML = '';
        
        data.satellites.forEach(sat => {
            const option = document.createElement('option');
            option.value = sat.id;
            option.textContent = `${sat.id} - ${sat.description}`;
            option.selected = sat.is_active;
            select.appendChild(option);
            
            // Show description for active satellite
            if (sat.is_active) {
                document.getElementById('satellite-info').textContent = 
                    `${sat.description} (${sat.orbit_type}, Period: ${sat.orbital_period_min} min)`;
            }
        });
        
        console.log(`✓ Loaded ${data.count} satellites (active: ${data.active})`);
        
    } catch (error) {
        console.error('Failed to load satellites:', error);
    }
}

async function switchSatellite() {
    const select = document.getElementById('satellite-select');
    const satelliteId = select.value;
    
    try {
        const response = await fetch('/api/satellite/select', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ satellite_id: satelliteId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✓ Switched to satellite: ${data.active_satellite}`);
            document.getElementById('satellite-info').textContent = data.description;
            
            // Refresh data
            if (socket && isConnected) {
                socket.emit('request_status');
            }
            loadPasses();
            
            // Show success message
            alert(`Switched to ${data.name}`);
        } else {
            alert(`Failed to switch satellite: ${data.error}`);
        }
        
    } catch (error) {
        console.error('Failed to switch satellite:', error);
        alert('Error switching satellite');
    }
}


// ============================================================
// Phase 9: Data Visualization
// ============================================================

let telemetryChart = null;
let leafletMap = null;
let trackLayer = null;

// Show/hide visualization tabs
function showVizTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.viz-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.viz-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`viz-${tabName}`).classList.add('active');
    
    // Mark button as active
    event.target.classList.add('active');
    
    // Load data for the tab
    if (tabName === 'charts') {
        loadTelemetryChart();
    } else if (tabName === 'groundtrack') {
        loadGroundTrack();
    }
}

async function loadTelemetryChart() {
    const hours = document.getElementById('chart-range').value;
    
    try {
        const response = await fetch(`/api/viz/telemetry?hours=${hours}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Failed to load chart data:', data.error);
            return;
        }
        
        const ctx = document.getElementById('telemetry-chart').getContext('2d');
        
        // Destroy existing chart
        if (telemetryChart) {
            telemetryChart.destroy();
        }
        
        // Create new chart
        telemetryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels.map(ts => new Date(ts).toLocaleTimeString()),
                datasets: [
                    {
                        label: data.datasets.battery_voltage.label,
                        data: data.datasets.battery_voltage.data,
                        borderColor: data.datasets.battery_voltage.borderColor,
                        tension: data.datasets.battery_voltage.tension,
                        yAxisID: 'y-voltage'
                    },
                    {
                        label: data.datasets.temperature.label,
                        data: data.datasets.temperature.data,
                        borderColor: data.datasets.temperature.borderColor,
                        tension: data.datasets.temperature.tension,
                        yAxisID: 'y-temp'
                    },
                    {
                        label: data.datasets.solar_current.label,
                        data: data.datasets.solar_current.data,
                        borderColor: data.datasets.solar_current.borderColor,
                        tension: data.datasets.solar_current.tension,
                        yAxisID: 'y-current'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    'y-voltage': {
                        type: 'linear',
                        position: 'left',
                        title: { display: true, text: 'Voltage (V)' }
                    },
                    'y-temp': {
                        type: 'linear',
                        position: 'right',
                        title: { display: true, text: 'Temperature (°C)' },
                        grid: { drawOnChartArea: false }
                    },
                    'y-current': {
                        type: 'linear',
                        position: 'right',
                        title: { display: true, text: 'Current (A)' },
                        grid: { drawOnChartArea: false }
                    }
                }
            }
        });
        
        console.log(`✓ Loaded telemetry chart (${data.data_points} points, ${hours}h range)`);
        
    } catch (error) {
        console.error('Failed to load telemetry chart:', error);
    }
}

async function loadGroundTrack() {
    const duration = document.getElementById('track-duration').value;
    
    try {
        const response = await fetch(`/api/viz/ground_track?minutes=${duration}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Failed to load ground track:', data.error);
            return;
        }
        
        // Initialize map if needed
        if (!leafletMap) {
            leafletMap = L.map('map-container').setView([0, 0], 2);
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(leafletMap);
        }
        
        // Clear existing track layer
        if (trackLayer) {
            leafletMap.removeLayer(trackLayer);
        }
        
        // Create ground track polyline
        const trackPoints = data.points.map(p => [p.latitude, p.longitude]);
        trackLayer = L.polyline(trackPoints, {
            color: '#ff0000',
            weight: 3,
            opacity: 0.7
        }).addTo(leafletMap);
        
        // Add markers for start and current position
        if (data.points.length > 0) {
            const start = data.points[0];
            const current = data.points[0];
            
            L.marker([start.latitude, start.longitude])
                .addTo(leafletMap)
                .bindPopup(`Start: ${new Date(start.timestamp).toLocaleTimeString()}`);
            
            L.circleMarker([current.latitude, current.longitude], {
                color: '#00ff00',
                fillColor: '#00ff00',
                fillOpacity: 0.8,
                radius: 8
            })
                .addTo(leafletMap)
                .bindPopup(`${data.satellite}<br>Alt: ${current.altitude_km} km`);
        }
        
        // Add ground station markers
        data.ground_stations.forEach(gs => {
            L.marker([gs.lat, gs.lon], {
                icon: L.icon({
                    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            })
                .addTo(leafletMap)
                .bindPopup(gs.name);
        });
        
        // Fit map to track
        leafletMap.fitBounds(trackLayer.getBounds());
        
        console.log(`✓ Loaded ground track (${data.points.length} points, ${duration} min)`);
        
    } catch (error) {
        console.error('Failed to load ground track:', error);
    }
}


// ============================================================
// Phase 10: Advanced Features
// ============================================================

// Show/hide advanced tabs
function showAdvancedTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.advanced-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.advanced-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`advanced-${tabName}`).classList.add('active');
    
    // Mark button as active
    event.target.classList.add('active');
}

async function calculateLinkBudget() {
    const station = document.getElementById('linkbudget-station').value;
    
    try {
        const response = await fetch(`/api/link_budget?station=${station}`);
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        // Display results
        const resultsDiv = document.getElementById('linkbudget-results');
        resultsDiv.innerHTML = `
            <div class="result-item">
                <h4>📡 Downlink Budget</h4>
                <p><strong>Received Power:</strong> ${data.downlink.received_power_dbw} dBW</p>
                <p><strong>Link Margin:</strong> <span class="value">${data.downlink.link_margin_db}</span> <span class="unit">dB</span></p>
                <p><strong>Status:</strong> ${data.downlink.link_status}</p>
                <p class="detail">Path Loss: ${data.downlink.path_loss_db} dB | Atm Loss: ${data.downlink.atmospheric_loss_db} dB</p>
            </div>
            
            <div class="result-item">
                <h4>📡 Uplink Budget</h4>
                <p><strong>Received Power:</strong> ${data.uplink.received_power_dbw} dBW</p>
                <p><strong>Link Margin:</strong> <span class="value">${data.uplink.link_margin_db}</span> <span class="unit">dB</span></p>
                <p><strong>Status:</strong> ${data.uplink.link_status}</p>
                <p class="detail">Path Loss: ${data.uplink.path_loss_db} dB | Atm Loss: ${data.uplink.atmospheric_loss_db} dB</p>
            </div>
            
            <div class="result-item">
                <h4>📊 Tracking Data</h4>
                <p><strong>Station:</strong> ${data.station}</p>
                <p><strong>Elevation:</strong> ${data.tracking.elevation_deg}°</p>
                <p><strong>Azimuth:</strong> ${data.tracking.azimuth_deg}°</p>
                <p><strong>Range:</strong> ${data.tracking.range_km} km</p>
            </div>
            
            <div class="result-item">
                <h4>📻 Frequencies</h4>
                <p><strong>Downlink:</strong> ${data.frequencies.downlink_mhz} MHz</p>
                <p><strong>Uplink:</strong> ${data.frequencies.uplink_mhz} MHz</p>
                <p><strong>Satellite:</strong> ${data.satellite}</p>
            </div>
        `;
        
        console.log(`✓ Link budget calculated for ${station}`);
        
    } catch (error) {
        console.error('Failed to calculate link budget:', error);
        alert('Error calculating link budget');
    }
}

async function optimizeSchedule() {
    const hours = document.getElementById('scheduler-hours').value;
    const maxPasses = document.getElementById('scheduler-maxpasses').value;
    
    try {
        const response = await fetch(`/api/schedule_passes?hours=${hours}&max_passes=${maxPasses}`);
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        // Display results
        const resultsDiv = document.getElementById('scheduler-results');
        
        let html = `
            <p class="info">Optimized ${data.scheduled_passes} best passes from ${data.total_passes_available} available passes</p>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Quality Score</th>
                        <th>Station</th>
                        <th>AOS Time</th>
                        <th>Duration (min)</th>
                        <th>Max Elevation (°)</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        data.passes.forEach((pass, index) => {
            const aosTime = new Date(pass.aos).toLocaleString();
            html += `
                <tr>
                    <td>${index + 1}</td>
                    <td><strong>${pass.quality_score}</strong></td>
                    <td>${pass.station}</td>
                    <td>${aosTime}</td>
                    <td>${pass.duration_min}</td>
                    <td>${pass.max_elevation}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
        resultsDiv.innerHTML = html;
        
        console.log(`✓ Optimized schedule: ${data.scheduled_passes} passes`);
        
    } catch (error) {
        console.error('Failed to optimize schedule:', error);
        alert('Error optimizing schedule');
    }
}

let anomalyAutoCheck = false;
let anomalyTimer = null;

async function checkAnomalies() {
    try {
        const response = await fetch('/api/anomaly_check');
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        // Update health status
        const statusBadge = document.getElementById('health-status');
        statusBadge.textContent = data.health_status;
        statusBadge.className = `status-badge ${data.health_status.toLowerCase()}`;
        
        // Display telemetry
        const resultsDiv = document.getElementById('anomaly-results');
        
        let html = `
            <div class="anomaly-telemetry">
                <h4>Current Telemetry</h4>
                <p>Battery: ${data.telemetry.battery_voltage} V | 
                   Temperature: ${data.telemetry.temperature} °C | 
                   Solar Current: ${data.telemetry.solar_current} A | 
                   Mode: ${data.telemetry.mode}</p>
            </div>
        `;
        
        if (data.anomaly_count === 0) {
            html += '<p class="info">✅ No anomalies detected - All systems nominal</p>';
        } else {
            html += `<p class="warning">⚠️ ${data.anomaly_count} anomaly(ies) detected:</p>`;
            
            data.anomalies.forEach(anomaly => {
                html += `
                    <div class="anomaly-item ${anomaly.severity.toLowerCase()}">
                        <div class="anomaly-type">${anomaly.type} - ${anomaly.severity}</div>
                        <div class="anomaly-details">
                            Parameter: ${anomaly.parameter} | 
                            ${anomaly.value !== undefined ? `Value: ${anomaly.value}` : ''} 
                            ${anomaly.threshold !== undefined ? `| Threshold: ${anomaly.threshold}` : ''}
                            ${anomaly.rate !== undefined ? `| Rate: ${anomaly.rate} | Max Rate: ${anomaly.max_rate}` : ''}
                        </div>
                    </div>
                `;
            });
        }
        
        resultsDiv.innerHTML = html;
        
        console.log(`✓ Anomaly check completed: ${data.health_status} (${data.anomaly_count} anomalies)`);
        
    } catch (error) {
        console.error('Failed to check anomalies:', error);
        alert('Error checking anomalies');
    }
}

function toggleAutoAnomaly() {
    anomalyAutoCheck = !anomalyAutoCheck;
    const btn = document.getElementById('auto-anomaly-btn');
    
    if (anomalyAutoCheck) {
        btn.textContent = 'Disable Auto-Check';
        btn.style.background = '#dc3545';
        anomalyTimer = setInterval(checkAnomalies, 30000); // Check every 30 seconds
        console.log('✓ Auto anomaly detection enabled');
    } else {
        btn.textContent = 'Enable Auto-Check';
        btn.style.background = '#28a745';
        if (anomalyTimer) {
            clearInterval(anomalyTimer);
            anomalyTimer = null;
        }
        console.log('✓ Auto anomaly detection disabled');
    }
}
