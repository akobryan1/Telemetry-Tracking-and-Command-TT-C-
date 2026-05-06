"""
TT&C Web Dashboard - Flask Application (Phase 4 & 5)

Web interface for satellite telemetry, tracking, and command operations.
Provides real-time monitoring and command uplink capabilities.

Phase 5: Cloud deployment with Supabase database integration.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import os

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

# ============================================================
# Flask App Configuration
# ============================================================

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
app.config['JSON_SORT_KEYS'] = False

# ============================================================
# Global State (In production, use a proper state management solution)
# ============================================================

# Simulation state
satellite = None
network = None
ts = None
satellite_orbit = None
observers = {}
db_logger = None

# Configuration
SATELLITE_NAME = "ISS"
TLE_FILE = "data/inputs/tle/stations.txt"
GROUND_STATIONS = [
    {'name': 'Miami', 'latitude': 25.7617, 'longitude': -80.1918, 'altitude_m': 10, 'min_elevation': 10.0},
    {'name': 'Goldstone', 'latitude': 35.4267, 'longitude': -116.8900, 'altitude_m': 1036, 'min_elevation': 10.0},
    {'name': 'Madrid', 'latitude': 40.4319, 'longitude': -4.2489, 'altitude_m': 834, 'min_elevation': 10.0},
    {'name': 'Canberra', 'latitude': -35.4017, 'longitude': 148.9819, 'altitude_m': 691, 'min_elevation': 10.0}
]

def initialize_simulation():
    """Initialize satellite and ground station network."""
    global satellite, network, ts, satellite_orbit, observers, db_logger
    
    # Load timescale
    ts = load.timescale()
    
    # Load satellite TLE
    satellite_orbit = load_satellite_tle(TLE_FILE, SATELLITE_NAME)
    
    # Initialize satellite
    satellite = Satellite(
        name=SATELLITE_NAME,
        initial_battery_voltage=28.0,
        initial_temperature=20.0,
        initial_mode=Satellite.MODE_NOMINAL
    )
    
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
    
    # Initialize database logger if enabled
    database_mode = os.environ.get('DATABASE_MODE', 'csv').lower()
    if database_mode == 'database':
        try:
            from core.database_logger import DatabaseLogger
            db_logger = DatabaseLogger(satellite_name=SATELLITE_NAME)
            print(f"✓ Database logging enabled")
        except Exception as e:
            print(f"⚠️  Failed to initialize database logger: {e}")
            print(f"   Falling back to CSV mode")
    else:
        print(f"✓ CSV logging mode (set DATABASE_MODE=database to enable cloud logging)")
    
    print("✓ Simulation initialized")
    print(f"  Satellite: {SATELLITE_NAME}")
    print(f"  Ground Stations: {len(network.stations)}")

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
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
