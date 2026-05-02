# Phase 4: Web Dashboard - Usage Guide

## Overview

Phase 4 adds a web-based dashboard for real-time satellite monitoring and command uplink.

## Features

- **Real-time Status**: Live satellite telemetry and position tracking
- **Ground Station Network**: Visual display of all 4 ground stations with visibility indicators
- **Pass Predictions**: Upcoming satellite passes for the next 12 hours
- **Command Uplink**: Send commands to the satellite via the web interface
- **Auto-refresh**: Dashboard updates every 5 seconds automatically

## Running the Dashboard

1. Ensure virtual environment is activated:
```bash
# Windows
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

2. Start the Flask web server:
```bash
python src/app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

The dashboard provides the following REST API endpoints:

### GET /api/status
Returns current satellite status, position, and network visibility

**Response:**
```json
{
  "timestamp": "2026-05-03T...",
  "satellite": {
    "name": "ISS",
    "battery_voltage": 28.0,
    "temperature": 20.0,
    "mode": "NOMINAL",
    "position": {
      "latitude": 25.5,
      "longitude": -80.2,
      "altitude_km": 408.5
    }
  },
  "network": {
    "active_stations": ["Miami"],
    "total_stations": 4,
    "visibility": {...}
  }
}
```

### GET /api/telemetry
Returns current telemetry data

### GET /api/passes?hours=12&station=Miami
Predicts upcoming satellite passes

**Parameters:**
- `hours` (optional): Time range in hours (default: 24)
- `station` (optional): Filter by specific station name

### GET /api/network
Returns ground station network statistics

### POST /api/command
Uplinks a command to the satellite

**Request Body:**
```json
{
  "command_type": "SET_MODE",
  "mode": "SCIENCE"
}
```

**Supported Commands:**
- `SET_MODE` (requires `mode`: SAFE, NOMINAL, or SCIENCE)
- `ADJUST_POWER` (requires `power_delta` in volts)
- `RESET_TELEMETRY`
- `PAYLOAD_ON`
- `PAYLOAD_OFF`

## Architecture

```
src/
├── app.py              # Flask application with API routes
├── templates/
│   └── index.html      # Main dashboard HTML
└── static/
    ├── css/
    │   └── style.css   # Dashboard styling
    └── js/
        └── dashboard.js # Frontend JavaScript
```

## Testing

Run the API test suite:
```bash
pytest src/tests/test_api.py -v
```

All 100 tests (including 20 new API tests) should pass.

## Technology Stack

- **Backend**: Flask 2.3.3 (Python web framework)
- **Frontend**: Vanilla JavaScript with AJAX
- **Styling**: Custom CSS with gradient backgrounds
- **Updates**: Auto-refresh every 5 seconds

## Dashboard Features

### Status Overview
- Satellite name, battery voltage, temperature, mode
- Real-time position (lat/lon/altitude)

### Ground Station Network
- 4 global stations: Miami, Goldstone, Madrid, Canberra
- Visibility indicators (green = visible)
- Elevation, azimuth, and range data for visible stations

### Telemetry Panel
- Real-time battery voltage
- Solar current
- Temperature
- Telemetry packet count

### Pass Predictions
- Next 12 hours of passes
- Station selector for filtering
- Duration, max elevation, AOS/LOS times

### Command Uplink
- Drop-down selection of command types
- Dynamic parameter fields
- Command execution log with timestamps
- Success/failure indicators

## Notes

- The dashboard simulates real-time operation using current UTC time
- Commands require at least one ground station to have visibility
- Auto-refresh can be disabled in browser if needed
- All API responses are in JSON format
