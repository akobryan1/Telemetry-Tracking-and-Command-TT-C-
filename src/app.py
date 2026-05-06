"""
TT&C Web Dashboard - Flask Application (Phases 4-10)

Web interface for satellite telemetry, tracking, and command operations.
Provides real-time monitoring and command uplink capabilities.

Phase 5: Cloud deployment with Supabase database integration
Phase 6: Active database logging and historical data
Phase 7: Real-time WebSocket updates
Phase 8: Multi-satellite support (ISS, Hubble, Starlink)
Phase 9: Data visualization (charts, ground tracks)
Phase 10: Advanced features (link budget, scheduling, anomaly detection)
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import os
import threading
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from skyfield.api import load
from core.satellite import Satellite
from core.network import GroundStationNetwork
from core.ground_station import GroundStation
from core.command import (
    create_set_mode_command,
    create_reset_telemetry_command,
    create_adjust_power_command,
    create_payload_command
)
from utils.orbital_mechanics import load_satellite_tle, get_tle_epoch
from utils.coordinate_transforms import (
    compute_azimuth_elevation_range,
    is_visible,
    create_ground_station
)
from utils.advanced_features import (
    LinkBudgetCalculator,
    PassScheduler,
    AnomalyDetector
)

# Import satellite configuration (Phase 8)
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.satellites import get_satellite_config, get_all_satellites, DEFAULT_SATELLITE

# ============================================================
# Flask App Configuration
# ============================================================

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ttc-dashboard-secret-key-2026')

# Initialize SocketIO for real-time updates (Phase 7)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ============================================================
# Global State (In production, use a proper state management solution)
# ============================================================

# Simulation state (Phase 8: Multi-satellite support)
satellites = {}  # Dictionary of satellite instances by satellite_id
active_satellite_id = DEFAULT_SATELLITE  # Currently selected satellite
satellite = None  # Active satellite instance
network = None
ts = None
satellite_orbits = {}  # Dictionary of orbital elements by satellite_id
satellite_orbit = None  # Active satellite orbit
observers = {}
db_loggers = {}  # Database logger per satellite
db_logger = None  # Active database logger

# Advanced features (Phase 10)
link_calculator = None
pass_scheduler = None
anomaly_detectors = {}  # Anomaly detector per satellite

# Configuration (Phase 8: Now supports multiple satellites)
# Use absolute path for production deployment
BASE_DIR = Path(__file__).parent.parent
TLE_FILE = str(BASE_DIR / "data" / "inputs" / "tle" / "satellites.txt")
GROUND_STATIONS = [
    {'name': 'Miami', 'latitude': 25.7617, 'longitude': -80.1918, 'altitude_m': 10, 'min_elevation': 10.0},
    {'name': 'Goldstone', 'latitude': 35.4267, 'longitude': -116.8900, 'altitude_m': 1036, 'min_elevation': 10.0},
    {'name': 'Madrid', 'latitude': 40.4319, 'longitude': -4.2489, 'altitude_m': 834, 'min_elevation': 10.0},
    {'name': 'Canberra', 'latitude': -35.4017, 'longitude': 148.9819, 'altitude_m': 691, 'min_elevation': 10.0}
]

def initialize_simulation():
    """Initialize satellites and ground station network (Phase 8: Multi-satellite support)."""
    global satellites, active_satellite_id, satellite, network, ts, satellite_orbits, satellite_orbit
    global observers, db_loggers, db_logger, link_calculator, pass_scheduler, anomaly_detectors
    
    # Load timescale
    ts = load.timescale()
    
    # Phase 8: Initialize all available satellites
    all_satellites = get_all_satellites()
    print(f"\nInitializing {len(all_satellites)} satellites...")
    
    for sat_id, sat_config in all_satellites.items():
        try:
            # Load satellite TLE
            orbit = load_satellite_tle(sat_config['tle_file'], sat_config['name'])
            satellite_orbits[sat_id] = orbit
            
            # Initialize satellite
            sat_instance = Satellite(
                name=sat_config['name'],
                initial_battery_voltage=sat_config['initial_battery_voltage'],
                initial_temperature=sat_config['initial_temperature'],
                initial_mode=sat_config['initial_mode']
            )
            satellites[sat_id] = sat_instance
            
            # Initialize anomaly detector (Phase 10)
            anomaly_detectors[sat_id] = AnomalyDetector()
            
            # Initialize database logger if enabled
            database_mode = os.environ.get('DATABASE_MODE', 'csv').lower()
            if database_mode == 'database':
                try:
                    from core.database_logger import DatabaseLogger
                    db_loggers[sat_id] = DatabaseLogger(satellite_name=sat_config['name'])
                except Exception as e:
                    print(f"⚠️  Failed to initialize database logger for {sat_id}: {e}")
            
            print(f"  ✓ {sat_id}: {sat_config['name']} ({sat_config['orbit_type']})")
            
        except Exception as e:
            print(f"  ✗ Failed to initialize {sat_id}: {e}")
    
    # Set active satellite
    satellite = satellites[active_satellite_id]
    satellite_orbit = satellite_orbits[active_satellite_id]
    db_logger = db_loggers.get(active_satellite_id)
    
    # Phase 10: Initialize advanced features
    link_calculator = LinkBudgetCalculator()
    pass_scheduler = PassScheduler()
    
    print(f"\n✓ Active satellite: {active_satellite_id}")
    
    # Create ground station network
    stations = []
    for gs_config in GROUND_STATIONS:
        # Create Skyfield observer
        observer = create_ground_station(
            gs_config['latitude'],
            gs_config['longitude'],
            gs_config['altitude_m']
        )
        observers[gs_config['name']] = observer
        
        # Create GroundStation object
        station = GroundStation(
            name=gs_config['name'],
            latitude=gs_config['latitude'],
            longitude=gs_config['longitude'],
            altitude_m=gs_config['altitude_m'],
            min_elevation=gs_config['min_elevation']
        )
        stations.append(station)
    
    network = GroundStationNetwork(stations)
    
    print(f"✓ Simulation initialized")
    print(f"  Satellites: {len(satellites)}")
    print(f"  Ground Stations: {len(network.stations)}")
    print(f"  Advanced features enabled: Link Budget, Pass Scheduler, Anomaly Detection")

# Initialize on module import (needed for Gunicorn)
initialize_simulation()

# ============================================================
# Web Routes
# ============================================================

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

# ============================================================
# API Endpoints
# ============================================================

@app.route('/api/status')
def api_status():
    """Get current satellite and network status."""
    if satellite is None or network is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    # Get current time
    now = datetime.now(timezone.utc)
    t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    # Compute visibility for all stations
    visibility_data = {}
    active_stations = []
    
    for station_name, observer in observers.items():
        az, el, rng, rng_rate = compute_azimuth_elevation_range(
            satellite_orbit, observer, t
        )
        visible = is_visible(el, 10.0)
        
        visibility_data[station_name] = {
            'is_visible': bool(visible),  # Convert numpy bool to Python bool
            'elevation': round(float(el), 2),
            'azimuth': round(float(az), 2),
            'range_km': round(float(rng), 2),
            'range_rate_km_s': round(float(rng_rate), 3)
        }
        
        if visible:
            active_stations.append(station_name)
        
        # Log tracking data to database if enabled
        if db_logger:
            try:
                tracking_data = {
                    'azimuth_deg': float(az),
                    'elevation_deg': float(el),
                    'range_km': float(rng),
                    'range_rate_km_s': float(rng_rate),
                    'is_visible': bool(visible)
                }
                db_logger.log_tracking(tracking_data, station_name, now.isoformat())
            except Exception as e:
                print(f"⚠️  Failed to log tracking data: {e}")
    
    # Get satellite position
    geocentric = satellite_orbit.at(t)
    subpoint = geocentric.subpoint()
    
    response = {
        'timestamp': now.isoformat(),
        'satellite': {
            'name': satellite.name,
            'battery_voltage': round(satellite.battery_voltage, 2),
            'temperature': round(satellite.temperature, 1),
            'mode': satellite.mode,
            'telemetry_count': satellite.telemetry_count,
            'position': {
                'latitude': round(subpoint.latitude.degrees, 4),
                'longitude': round(subpoint.longitude.degrees, 4),
                'altitude_km': round(subpoint.elevation.km, 2)
            }
        },
        'network': {
            'active_stations': active_stations,
            'total_stations': len(network.stations),
            'visibility': visibility_data
        }
    }
    
    return jsonify(response)

@app.route('/api/passes')
def api_passes():
    """Predict upcoming satellite passes for all stations."""
    if satellite_orbit is None or network is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    # Get parameters
    hours = request.args.get('hours', default=24, type=int)
    station_name = request.args.get('station', default=None, type=str)
    
    # Time range
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(hours=hours)
    
    # Generate time steps (1 minute intervals for pass prediction)
    time_steps = []
    current = now
    while current < end_time:
        time_steps.append(current)
        current += timedelta(minutes=1)
    
    # Predict passes for each station
    passes_by_station = {}
    
    stations_to_check = [station_name] if station_name else observers.keys()
    
    for stn_name in stations_to_check:
        observer = observers[stn_name]
        station_passes = []
        in_pass = False
        current_pass = {}
        
        for step_time in time_steps:
            t = ts.utc(step_time.year, step_time.month, step_time.day,
                      step_time.hour, step_time.minute, step_time.second)
            
            az, el, rng, _ = compute_azimuth_elevation_range(satellite_orbit, observer, t)
            visible = is_visible(el, 10.0)
            
            if visible and not in_pass:
                # AOS
                in_pass = True
                current_pass = {
                    'aos': step_time.isoformat(),
                    'aos_azimuth': round(az, 1),
                    'aos_elevation': round(el, 1),
                    'max_elevation': el,
                    'max_el_time': step_time.isoformat()
                }
            elif visible and in_pass:
                # Update max elevation
                if el > current_pass['max_elevation']:
                    current_pass['max_elevation'] = el
                    current_pass['max_el_time'] = step_time.isoformat()
            elif not visible and in_pass:
                # LOS
                in_pass = False
                duration = (step_time - datetime.fromisoformat(current_pass['aos'])).total_seconds() / 60.0
                current_pass['los'] = step_time.isoformat()
                current_pass['duration_min'] = round(duration, 1)
                current_pass['max_elevation'] = round(current_pass['max_elevation'], 1)
                station_passes.append(current_pass)
        
        passes_by_station[stn_name] = station_passes
    
    return jsonify({
        'prediction_time': now.isoformat(),
        'time_range_hours': hours,
        'passes': passes_by_station
    })

@app.route('/api/telemetry')
def api_telemetry():
    """Get current telemetry data."""
    if satellite is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    # Generate current telemetry (simplified - assume sunlit for demo)
    telemetry = satellite.generate_telemetry(is_sunlit=True, time_step_seconds=10)
    timestamp = datetime.now(timezone.utc).isoformat()
    telemetry['timestamp'] = timestamp
    
    # Log to database if enabled
    if db_logger:
        try:
            # Determine active ground station (or use first visible)
            ground_station = network.active_station.name if network.active_station else 'N/A'
            if ground_station == 'N/A':
                visible = network.get_visible_stations()
                if visible:
                    ground_station = visible[0].name
            
            db_logger.log_telemetry(telemetry, ground_station, timestamp)
        except Exception as e:
            print(f"⚠️  Failed to log telemetry to database: {e}")
    
    return jsonify(telemetry)

@app.route('/api/network')
def api_network():
    """Get ground station network statistics."""
    if network is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    stats = network.get_network_statistics()
    return jsonify(stats)

@app.route('/api/command', methods=['POST'])
def api_command():
    """Uplink a command to the satellite."""
    if satellite is None or network is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    data = request.get_json()
    
    if not data or 'command_type' not in data:
        return jsonify({'error': 'Missing command_type'}), 400
    
    command_type = data['command_type']
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Create command based on type
    try:
        if command_type == 'SET_MODE':
            mode = data.get('mode', 'NOMINAL')
            command = create_set_mode_command(mode)
        elif command_type == 'RESET_TELEMETRY':
            command = create_reset_telemetry_command()
        elif command_type == 'ADJUST_POWER':
            power_delta = data.get('power_delta', 0.0)
            command = create_adjust_power_command(power_delta)
        elif command_type == 'PAYLOAD_ON':
            command = create_payload_command(True)
        elif command_type == 'PAYLOAD_OFF':
            command = create_payload_command(False)
        else:
            return jsonify({'error': f'Unknown command type: {command_type}'}), 400
        
        # Try to uplink via active station or any visible station
        if network.active_station:
            success = network.uplink_command(command, timestamp)
            station = network.active_station.name
        else:
            # Find any visible station
            visible_stations = network.get_visible_stations()
            if visible_stations:
                network.handoff_station(visible_stations[0], timestamp, "command_uplink")
                success = network.uplink_command(command, timestamp)
                station = visible_stations[0].name
            else:
                return jsonify({'error': 'No stations have visibility'}), 400
        
        if success:
            # Execute command immediately (in real system, would wait for satellite processing)
            satellite.receive_command(command)
            processed = satellite.process_commands(timestamp)
            
            if processed:
                cmd = processed[0]
                
                # Log command to database if enabled
                if db_logger:
                    try:
                        command_data = {
                            'command_type': command_type,
                            'command_id': cmd.command_id,
                            'parameters': data,
                            'status': cmd.status.name,
                            'ack_timestamp': timestamp
                        }
                        db_logger.log_command(command_data, station, timestamp)
                    except Exception as e:
                        print(f"⚠️  Failed to log command to database: {e}")
                
                return jsonify({
                    'success': True,
                    'command_id': cmd.command_id,
                    'status': cmd.status.name,
                    'acknowledgment': cmd.acknowledgment,
                    'uplink_station': station
                })
        
        return jsonify({'error': 'Command failed'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history/telemetry')
def api_history_telemetry():
    """Get historical telemetry data from database."""
    if db_logger is None:
        return jsonify({'error': 'Database logging not enabled'}), 400
    
    limit = request.args.get('limit', default=100, type=int)
    limit = min(limit, 1000)  # Cap at 1000 records
    
    try:
        records = db_logger.get_recent_telemetry(limit=limit)
        return jsonify({
            'count': len(records),
            'limit': limit,
            'telemetry': records
        })
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve telemetry: {str(e)}'}), 500

@app.route('/api/history/commands')
def api_history_commands():
    """Get historical command data from database."""
    if db_logger is None:
        return jsonify({'error': 'Database logging not enabled'}), 400
    
    limit = request.args.get('limit', default=50, type=int)
    limit = min(limit, 500)  # Cap at 500 records
    
    try:
        records = db_logger.get_recent_commands(limit=limit)
        return jsonify({
            'count': len(records),
            'limit': limit,
            'commands': records
        })
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve commands: {str(e)}'}), 500

@app.route('/api/history/tracking')
def api_history_tracking():
    """Get historical tracking data from database."""
    if db_logger is None:
        return jsonify({'error': 'Database logging not enabled'}), 400
    
    station = request.args.get('station', default=None, type=str)
    limit = request.args.get('limit', default=100, type=int)
    limit = min(limit, 1000)  # Cap at 1000 records
    
    try:
        # Query tracking data
        query = db_logger.supabase.table('tracking').select('*').order('timestamp', desc=True).limit(limit)
        
        if station:
            query = query.eq('station', station)
        
        response = query.execute()
        
        return jsonify({
            'count': len(response.data),
            'limit': limit,
            'station_filter': station,
            'tracking': response.data
        })
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve tracking data: {str(e)}'}), 500


# ============================================================
# Phase 8: Multi-Satellite API Endpoints
# ============================================================

@app.route('/api/satellites')
def api_satellites():
    """Get list of available satellites."""
    sat_list = []
    all_sats = get_all_satellites()
    
    for sat_id, config in all_sats.items():
        sat_list.append({
            'id': sat_id,
            'name': config['name'],
            'description': config['description'],
            'orbit_type': config['orbit_type'],
            'orbital_period_min': config['orbital_period_min'],
            'is_active': sat_id == active_satellite_id
        })
    
    return jsonify({
        'satellites': sat_list,
        'active': active_satellite_id,
        'count': len(sat_list)
    })

@app.route('/api/satellite/select', methods=['POST'])
def api_select_satellite():
    """Switch active satellite (Phase 8)."""
    global satellite, satellite_orbit, db_logger, active_satellite_id
    
    data = request.get_json()
    satellite_id = data.get('satellite_id', '').upper()
    
    if not satellite_id:
        return jsonify({'error': 'Missing satellite_id'}), 400
    
    if satellite_id not in satellites:
        return jsonify({'error': f'Unknown satellite: {satellite_id}'}), 400
    
    # Switch active satellite
    active_satellite_id = satellite_id
    satellite = satellites[satellite_id]
    satellite_orbit = satellite_orbits[satellite_id]
    db_logger = db_loggers.get(satellite_id)
    
    config = get_satellite_config(satellite_id)
    
    return jsonify({
        'success': True,
        'active_satellite': satellite_id,
        'name': config['name'],
        'description': config['description']
    })


# ============================================================
# Phase 9: Data Visualization API Endpoints
# ============================================================

@app.route('/api/viz/telemetry')
def api_viz_telemetry():
    """Get telemetry data formatted for charting (Phase 9)."""
    if db_logger is None:
        return jsonify({'error': 'Database logging not enabled'}), 400
    
    hours = request.args.get('hours', default=1, type=int)
    hours = min(hours, 24)  # Cap at 24 hours
    
    try:
        # Get recent telemetry
        records = db_logger.get_recent_telemetry(limit=500)
        
        # Filter by time window
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        filtered = [r for r in records 
                   if datetime.fromisoformat(r['timestamp'].replace('Z', '+00:00')) > cutoff]
        
        # Format for Chart.js
        timestamps = [r['timestamp'] for r in filtered]
        battery_voltage = [r['battery_voltage'] for r in filtered]
        temperature = [r['temperature'] for r in filtered]
        solar_current = [r.get('solar_current', 0) for r in filtered]
        
        return jsonify({
            'labels': timestamps,
            'datasets': {
                'battery_voltage': {
                    'label': 'Battery Voltage (V)',
                    'data': battery_voltage,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                },
                'temperature': {
                    'label': 'Temperature (°C)',
                    'data': temperature,
                    'borderColor': 'rgb(255, 99, 132)',
                    'tension': 0.1
                },
                'solar_current': {
                    'label': 'Solar Current (A)',
                    'data': solar_current,
                    'borderColor': 'rgb(255, 205, 86)',
                    'tension': 0.1
                }
            },
            'time_range_hours': hours,
            'data_points': len(filtered)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve visualization data: {str(e)}'}), 500

@app.route('/api/viz/ground_track')
def api_viz_ground_track():
    """Get satellite ground track for map visualization (Phase 9)."""
    if satellite_orbit is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    minutes = request.args.get('minutes', default=90, type=int)
    minutes = min(minutes, 180)  # Cap at 3 hours
    
    # Generate ground track points
    now = datetime.now(timezone.utc)
    points = []
    
    for i in range(0, minutes, 1):  # 1-minute intervals
        time_offset = now + timedelta(minutes=i)
        t = ts.utc(time_offset.year, time_offset.month, time_offset.day,
                  time_offset.hour, time_offset.minute, time_offset.second)
        
        geocentric = satellite_orbit.at(t)
        subpoint = geocentric.subpoint()
        
        points.append({
            'timestamp': time_offset.isoformat(),
            'latitude': round(subpoint.latitude.degrees, 4),
            'longitude': round(subpoint.longitude.degrees, 4),
            'altitude_km': round(subpoint.elevation.km, 2)
        })
    
    return jsonify({
        'satellite': satellite.name,
        'track_duration_min': minutes,
        'points': points,
        'ground_stations': [
            {'name': gs['name'], 'lat': gs['latitude'], 'lon': gs['longitude']}
            for gs in GROUND_STATIONS
        ]
    })


# ============================================================
# Phase 10: Advanced Features API Endpoints
# ============================================================

@app.route('/api/link_budget')
def api_link_budget():
    """Calculate link budget for current satellite pass (Phase 10)."""
    if satellite_orbit is None or link_calculator is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    station_name = request.args.get('station', default='Miami', type=str)
    
    if station_name not in observers:
        return jsonify({'error': f'Unknown station: {station_name}'}), 400
    
    # Get current tracking data
    now = datetime.now(timezone.utc)
    t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    observer = observers[station_name]
    az, el, rng, rng_rate = compute_azimuth_elevation_range(satellite_orbit, observer, t)
    
    # Get satellite configuration
    sat_config = get_satellite_config(active_satellite_id)
    
    # Typical ground station parameters
    gs_tx_power_dbw = 10.0  # 10W = 10 dBW
    gs_antenna_gain_dbi = 20.0  # 20 dBi parabolic dish
    
    # Calculate downlink budget
    downlink = link_calculator.calculate_link_budget(
        tx_power_dbw=3.0,  # Satellite TX power (3W = 4.77 dBW, use 3 for margin)
        tx_gain_dbi=sat_config['antenna_gain_dbi'],
        rx_gain_dbi=gs_antenna_gain_dbi,
        frequency_mhz=sat_config['frequency_downlink_mhz'],
        range_km=float(rng),
        elevation_deg=float(el),
        system_losses_db=3.0
    )
    
    # Calculate uplink budget
    uplink = link_calculator.calculate_link_budget(
        tx_power_dbw=gs_tx_power_dbw,
        tx_gain_dbi=gs_antenna_gain_dbi,
        rx_gain_dbi=sat_config['antenna_gain_dbi'],
        frequency_mhz=sat_config['frequency_uplink_mhz'],
        range_km=float(rng),
        elevation_deg=float(el),
        system_losses_db=3.0
    )
    
    return jsonify({
        'timestamp': now.isoformat(),
        'satellite': satellite.name,
        'station': station_name,
        'tracking': {
            'elevation_deg': round(float(el), 2),
            'azimuth_deg': round(float(az), 2),
            'range_km': round(float(rng), 2)
        },
        'downlink': downlink,
        'uplink': uplink,
        'frequencies': {
            'downlink_mhz': sat_config['frequency_downlink_mhz'],
            'uplink_mhz': sat_config['frequency_uplink_mhz']
        }
    })

@app.route('/api/schedule_passes')
def api_schedule_passes():
    """Optimize pass schedule across network (Phase 10)."""
    if satellite_orbit is None or pass_scheduler is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    hours = request.args.get('hours', default=24, type=int)
    max_passes = request.args.get('max_passes', default=10, type=int)
    
    # Get all passes from api_passes logic
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(hours=hours)
    
    # Generate time steps (1 minute intervals)
    time_steps = []
    current = now
    while current < end_time:
        time_steps.append(current)
        current += timedelta(minutes=1)
    
    # Collect all passes across all stations
    all_passes = []
    
    for stn_name, observer in observers.items():
        in_pass = False
        current_pass = {}
        
        for step_time in time_steps:
            t = ts.utc(step_time.year, step_time.month, step_time.day,
                      step_time.hour, step_time.minute, step_time.second)
            
            az, el, rng, _ = compute_azimuth_elevation_range(satellite_orbit, observer, t)
            visible = is_visible(el, 10.0)
            
            if visible and not in_pass:
                # AOS
                in_pass = True
                current_pass = {
                    'station': stn_name,
                    'aos': step_time.isoformat(),
                    'aos_azimuth': round(az, 1),
                    'aos_elevation': round(el, 1),
                    'max_elevation': el,
                    'max_el_time': step_time.isoformat(),
                    'aos_range_km': round(float(rng), 2)
                }
            elif visible and in_pass:
                # Update max elevation
                if el > current_pass['max_elevation']:
                    current_pass['max_elevation'] = el
                    current_pass['max_el_time'] = step_time.isoformat()
            elif not visible and in_pass:
                # LOS
                in_pass = False
                duration = (step_time - datetime.fromisoformat(current_pass['aos'])).total_seconds() / 60.0
                current_pass['los'] = step_time.isoformat()
                current_pass['duration_min'] = round(duration, 1)
                current_pass['max_elevation'] = round(current_pass['max_elevation'], 1)
                all_passes.append(current_pass)
    
    # Optimize using pass scheduler
    optimized = pass_scheduler.optimize_schedule(all_passes, max_passes=max_passes)
    
    return jsonify({
        'satellite': satellite.name,
        'prediction_time': now.isoformat(),
        'time_range_hours': hours,
        'total_passes_available': len(all_passes),
        'scheduled_passes': len(optimized),
        'passes': optimized
    })

@app.route('/api/anomaly_check')
def api_anomaly_check():
    """Check telemetry for anomalies (Phase 10)."""
    if satellite is None:
        return jsonify({'error': 'Simulation not initialized'}), 500
    
    detector = anomaly_detectors.get(active_satellite_id)
    if not detector:
        return jsonify({'error': 'Anomaly detector not initialized'}), 500
    
    # Get current telemetry
    telemetry = satellite.generate_telemetry(is_sunlit=True, time_step_seconds=10)
    timestamp = datetime.now(timezone.utc)
    
    # Run anomaly detection
    anomaly_report = detector.detect_anomalies(telemetry, timestamp)
    
    # Add current telemetry to report
    anomaly_report['telemetry'] = {
        'battery_voltage': round(telemetry['battery_voltage'], 2),
        'solar_current': round(telemetry['solar_current'], 2),
        'temperature': round(telemetry['temperature'], 1),
        'mode': telemetry['mode']
    }
    
    return jsonify(anomaly_report)


# ============================================================
# WebSocket Event Handlers (Phase 7)
# ============================================================

# Track connected clients
connected_clients = 0
realtime_broadcast_active = False
broadcast_thread = None

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    global connected_clients, realtime_broadcast_active, broadcast_thread
    connected_clients += 1
    print(f'✓ Client connected (total: {connected_clients})')
    emit('connection_status', {'status': 'connected', 'message': 'Real-time updates enabled'})
    
    # Start broadcast thread if not already running
    if not realtime_broadcast_active:
        realtime_broadcast_active = True
        broadcast_thread = threading.Thread(target=broadcast_realtime_updates, daemon=True)
        broadcast_thread.start()
        print('✓ Real-time broadcast thread started')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    global connected_clients, realtime_broadcast_active
    connected_clients -= 1
    print(f'✓ Client disconnected (total: {connected_clients})')
    
    # Stop broadcast if no clients connected
    if connected_clients <= 0:
        realtime_broadcast_active = False
        print('✓ Real-time broadcast thread stopped (no clients)')

@socketio.on('request_status')
def handle_status_request():
    """Handle manual status request from client."""
    try:
        # Get current status data (same as REST API)
        now = datetime.now(timezone.utc)
        t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
        
        visibility_data = {}
        active_stations = []
        
        for station_name, observer in observers.items():
            az, el, rng, rng_rate = compute_azimuth_elevation_range(
                satellite_orbit, observer, t
            )
            visible = is_visible(el, 10.0)
            
            visibility_data[station_name] = {
                'is_visible': bool(visible),
                'elevation': round(float(el), 2),
                'azimuth': round(float(az), 2),
                'range_km': round(float(rng), 2),
                'range_rate_km_s': round(float(rng_rate), 3)
            }
            
            if visible:
                active_stations.append(station_name)
        
        geocentric = satellite_orbit.at(t)
        subpoint = geocentric.subpoint()
        
        response = {
            'timestamp': now.isoformat(),
            'satellite': {
                'name': satellite.name,
                'battery_voltage': round(satellite.battery_voltage, 2),
                'temperature': round(satellite.temperature, 1),
                'mode': satellite.mode,
                'telemetry_count': satellite.telemetry_count,
                'position': {
                    'latitude': round(subpoint.latitude.degrees, 4),
                    'longitude': round(subpoint.longitude.degrees, 4),
                    'altitude_km': round(subpoint.elevation.km, 2)
                }
            },
            'network': {
                'active_stations': active_stations,
                'total_stations': len(network.stations),
                'visibility': visibility_data
            }
        }
        
        emit('status_update', response)
        
    except Exception as e:
        print(f'⚠️  Error in status request: {e}')
        emit('error', {'message': str(e)})

def broadcast_realtime_updates():
    """Background thread to broadcast real-time updates to all connected clients."""
    print('✓ Real-time broadcast loop started')
    
    while realtime_broadcast_active:
        try:
            if connected_clients > 0 and satellite and network:
                # Get current time
                now = datetime.now(timezone.utc)
                t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, now.second)
                
                # Compute visibility for all stations
                visibility_data = {}
                active_stations = []
                
                for station_name, observer in observers.items():
                    az, el, rng, rng_rate = compute_azimuth_elevation_range(
                        satellite_orbit, observer, t
                    )
                    visible = is_visible(el, 10.0)
                    
                    visibility_data[station_name] = {
                        'is_visible': bool(visible),
                        'elevation': round(float(el), 2),
                        'azimuth': round(float(az), 2),
                        'range_km': round(float(rng), 2),
                        'range_rate_km_s': round(float(rng_rate), 3)
                    }
                    
                    if visible:
                        active_stations.append(station_name)
                    
                    # Log tracking data to database if enabled
                    if db_logger:
                        try:
                            tracking_data = {
                                'azimuth_deg': float(az),
                                'elevation_deg': float(el),
                                'range_km': float(rng),
                                'range_rate_km_s': float(rng_rate),
                                'is_visible': bool(visible)
                            }
                            db_logger.log_tracking(tracking_data, station_name, now.isoformat())
                        except Exception as e:
                            print(f'⚠️  Failed to log tracking data: {e}')
                
                # Get satellite position
                geocentric = satellite_orbit.at(t)
                subpoint = geocentric.subpoint()
                
                # Build status update
                status_update = {
                    'timestamp': now.isoformat(),
                    'satellite': {
                        'name': satellite.name,
                        'battery_voltage': round(satellite.battery_voltage, 2),
                        'temperature': round(satellite.temperature, 1),
                        'mode': satellite.mode,
                        'telemetry_count': satellite.telemetry_count,
                        'position': {
                            'latitude': round(subpoint.latitude.degrees, 4),
                            'longitude': round(subpoint.longitude.degrees, 4),
                            'altitude_km': round(subpoint.elevation.km, 2)
                        }
                    },
                    'network': {
                        'active_stations': active_stations,
                        'total_stations': len(network.stations),
                        'visibility': visibility_data
                    }
                }
                
                # Broadcast to all connected clients
                socketio.emit('status_update', status_update, namespace='/')
                
            # Sleep for update interval (2 seconds for real-time feel)
            time.sleep(2)
            
        except Exception as e:
            print(f'⚠️  Error in broadcast loop: {e}')
            time.sleep(5)  # Wait longer on error
    
    print('✓ Real-time broadcast loop stopped')


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TT&C Web Dashboard (Phase 4 & 5)")
    print("=" * 60)
    print()
    
    # Already initialized at module level for Gunicorn compatibility
    
    print()
    print("Starting Flask web server...")
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running in production
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = flask_env != 'production'
    
    if debug_mode:
        print(f"Dashboard: http://localhost:{port}")
        print(f"API Status: http://localhost:{port}/api/status")
    else:
        print(f"Running in production mode on port {port}")
    
    print()
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
