"""
TT&C Integrated Simulation (Phase 3)

This script runs a complete telemetry, tracking, and command simulation
with multiple ground stations and hand-off capabilities:
1. Propagates satellite orbit using SGP4
2. Calculates visibility from multiple ground stations
3. Manages station hand-offs based on elevation
4. Generates satellite telemetry during passes
5. Logs telemetry, tracking, and command data to CSV files

Usage:
    python scripts/simulation.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import csv

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skyfield.api import load

from utils.orbital_mechanics import (
    load_satellite_tle,
    propagate_orbit,
    get_tle_epoch
)
from utils.coordinate_transforms import (
    compute_azimuth_elevation_range,
    is_visible,
    create_ground_station
)
from core.satellite import Satellite
from core.ground_station import GroundStation
from core.network import GroundStationNetwork
from core.data_logger import DataLogger
from core.command import (
    Command,
    CommandType,
    create_set_mode_command,
    create_reset_telemetry_command,
    create_adjust_power_command,
    create_payload_command
)


# ============================================================
# Configuration
# ============================================================

# Satellite configuration
SATELLITE_NAME = "ISS"
TLE_FILE = "data/inputs/tle/stations.txt"

# Ground station network configuration (Phase 3)
GROUND_STATIONS = [
    {
        'name': 'Miami',
        'latitude': 25.7617,
        'longitude': -80.1918,
        'altitude_m': 10,
        'min_elevation': 10.0
    },
    {
        'name': 'Goldstone',  # NASA DSN - California
        'latitude': 35.4267,
        'longitude': -116.8900,
        'altitude_m': 1036,
        'min_elevation': 10.0
    },
    {
        'name': 'Madrid',  # ESA - Spain
        'latitude': 40.4319,
        'longitude': -4.2489,
        'altitude_m': 834,
        'min_elevation': 10.0
    },
    {
        'name': 'Canberra',  # NASA DSN - Australia
        'latitude': -35.4017,
        'longitude': 148.9819,
        'altitude_m': 691,
        'min_elevation': 10.0
    }
]
MIN_ELEVATION = 10.0  # degrees

# Simulation time configuration
START_TIME = datetime(2026, 5, 2, 0, 0, 0)  # UTC
END_TIME = datetime(2026, 5, 3, 0, 0, 0)    # UTC (24 hours)
TIME_STEP_SECONDS = 10

# Output configuration
OUTPUT_DIR = "data/outputs"


# ============================================================
# Main Simulation
# ============================================================

def estimate_sunlit(altitude_km: float, latitude: float, time: datetime) -> bool:
    """
    Simple sunlight estimation based on orbital geometry.
    
    This is a simplified model - assumes satellite is sunlit if it's
    in an elevated orbit or the local time suggests daylight.
    
    Args:
        altitude_km: Satellite altitude in km
        latitude: Sub-satellite point latitude in degrees
        time: Current time
    
    Returns:
        True if satellite is likely in sunlight
    """
    # Very simple model: assume sunlit if altitude is high or local hour is daylight
    # In reality, this depends on beta angle, orbital position, etc.
    # For now, use a simple heuristic
    
    hour_utc = time.hour + time.minute / 60.0
    
    # Assume satellite is sunlit if:
    # - High altitude (always sunlit in high orbits)
    # - Or local UTC hour suggests daylight (rough approximation)
    if altitude_km > 500:
        return True
    
    # For LEO, use simple day/night cycle (this is very approximate)
    # Better model would use solar position calculations
    return 6 <= hour_utc <= 18  # Rough daylight hours


def main():
    """Run the integrated TT&C simulation."""
    
    print("=" * 60)
    print("TT&C Integrated Simulation (Phase 3)")
    print("=" * 60)
    print()
    
    # ========================================
    # 1. Load satellite TLE
    # ========================================
    print("Loading satellite TLE data...")
    ts = load.timescale()
    
    try:
        satellite_orbit = load_satellite_tle(TLE_FILE, SATELLITE_NAME)
        print(f"  ✓ Loaded {satellite_orbit.name}")
        
        epoch = get_tle_epoch(satellite_orbit)
        print(f"  TLE Epoch: {epoch.utc_iso()}")
        
        # Check TLE age (using Skyfield time)
        current_skyfield_time = ts.utc(START_TIME.year, START_TIME.month, START_TIME.day)
        age_days = current_skyfield_time - epoch
        print(f"  TLE Age: {age_days:.1f} days")
        
        if age_days > 7:
            print(f"  ⚠ Warning: TLE is {age_days:.1f} days old (>7 days). Position accuracy may be degraded.")
        
    except Exception as e:
        print(f"  ✗ Error loading TLE: {e}")
        return 1
    
    print()
    
    # ========================================
    # 2. Create ground station network (Phase 3)
    # ========================================
    print("Creating ground station network...")
    
    # Create observers for each ground station
    observers = {}
    stations = []
    
    for gs_config in GROUND_STATIONS:
        # Create Skyfield observer for tracking calculations
        observer = create_ground_station(
            gs_config['latitude'],
            gs_config['longitude'],
            gs_config['altitude_m']
        )
        observers[gs_config['name']] = observer
        
        # Create GroundStation object for telemetry/command operations
        station = GroundStation(
            name=gs_config['name'],
            latitude=gs_config['latitude'],
            longitude=gs_config['longitude'],
            altitude_m=gs_config['altitude_m'],
            min_elevation=gs_config['min_elevation']
        )
        stations.append(station)
        
        print(f"  ✓ Station: {gs_config['name']} "
              f"({gs_config['latitude']:.4f}°, {gs_config['longitude']:.4f}°)")
    
    # Create network
    network = GroundStationNetwork(stations)
    print(f"\n  ✓ Network initialized with {len(network.stations)} stations")
    print()
    
    # ========================================
    # 3. Initialize satellite telemetry
    # ========================================
    print("Initializing satellite telemetry...")
    satellite = Satellite(
        name=SATELLITE_NAME,
        initial_battery_voltage=28.0,
        initial_temperature=20.0,
        initial_mode=Satellite.MODE_NOMINAL
    )
    print(f"  ✓ Satellite initialized: {SATELLITE_NAME}")
    print(f"     Battery: {satellite.battery_voltage}V")
    print(f"     Temperature: {satellite.temperature}°C")
    print(f"     Mode: {satellite.mode}")
    print()
    
    # ========================================
    # 4. Create data logger
    # ========================================
    print("Setting up data logger...")
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    with DataLogger(OUTPUT_DIR) as logger:
        # Create telemetry, tracking, and command log files
        telemetry_file = logger.create_telemetry_log(SATELLITE_NAME, timestamp_str)
        tracking_file = logger.create_tracking_log(SATELLITE_NAME, timestamp_str)
        command_file = logger.create_command_log(SATELLITE_NAME, timestamp_str)
        
        print(f"  ✓ Telemetry log: {telemetry_file}")
        print(f"  ✓ Tracking log: {tracking_file}")
        print(f"  ✓ Command log: {command_file}")
        print()
        
        # ========================================
        # 5. Generate time steps
        # ========================================
        print("Generating time steps...")
        time_steps = []
        current_time = START_TIME
        while current_time < END_TIME:
            time_steps.append(current_time)
            current_time += timedelta(seconds=TIME_STEP_SECONDS)
        
        total_steps = len(time_steps)
        print(f"  Total time steps: {total_steps}")
        print(f"  Time range: {START_TIME} to {END_TIME}")
        print(f"  Step size: {TIME_STEP_SECONDS} seconds")
        print()
        
        # ========================================
        # 6. Run simulation loop
        # ========================================
        print("Running simulation...")
        print()
        
        # Pass tracking variables
        in_pass = False
        pass_count = 0
        current_pass_data = {
            'aos_time': None,
            'los_time': None,
            'active_station': None,
            'stations_used': set(),
            'max_elevation': 0.0,
            'max_el_time': None,
            'max_el_station': None,
            'telemetry_packets': 0,
            'commands_sent': 0
        }
        
        passes = []
        total_telemetry_packets = 0
        total_commands_sent = 0
        previous_active_station = None
        
        for i, step_time in enumerate(time_steps):
            # Create Skyfield time object
            t = ts.utc(step_time.year, step_time.month, step_time.day,
                      step_time.hour, step_time.minute, step_time.second)
            
            # ========================================
            # Compute visibility for all stations (Phase 3)
            # ========================================
            visibility_data = {}
            elevation_data = {}
            tracking_by_station = {}
            
            any_visible = False
            
            for station_name, observer in observers.items():
                # Compute satellite position and tracking angles
                az, el, rng, rng_rate = compute_azimuth_elevation_range(
                    satellite_orbit, observer, t
                )
                
                visible = is_visible(el, MIN_ELEVATION)
                
                visibility_data[station_name] = {
                    'is_visible': visible,
                    'elevation': el
                }
                elevation_data[station_name] = el
                tracking_by_station[station_name] = {
                    'azimuth': az,
                    'elevation': el,
                    'range_km': rng,
                    'range_rate_km_s': rng_rate
                }
                
                if visible:
                    any_visible = True
                
                # Log tracking data for all stations
                tracking_data = {
                    'timestamp': step_time.isoformat() + 'Z',
                    'station': station_name,
                    'azimuth_deg': round(az, 2),
                    'elevation_deg': round(el, 2),
                    'range_km': round(rng, 2),
                    'range_rate_km_s': round(rng_rate, 3),
                    'is_visible': visible
                }
                logger.log_tracking(tracking_data)
            
            # Update network visibility status
            network.update_visibility(visibility_data)
            
            # ========================================
            # Station selection and hand-off (Phase 3)
            # ========================================
            if any_visible:
                # Select best station based on elevation
                best_station = network.select_best_station(elevation_data)
                
                # Detect AOS (Acquisition of Signal)
                if not in_pass:
                    in_pass = True
                    pass_count += 1
                    
                    # Hand-off to best station
                    network.handoff_station(best_station, step_time.isoformat() + 'Z', "aos")
                    
                    current_pass_data = {
                        'aos_time': step_time,
                        'active_station': best_station.name,
                        'stations_used': {best_station.name},
                        'max_elevation': elevation_data[best_station.name],
                        'max_el_time': step_time,
                        'max_el_station': best_station.name,
                        'telemetry_packets': 0,
                        'commands_sent': 0
                    }
                    
                    tracking = tracking_by_station[best_station.name]
                    print(f"AOS #{pass_count}: {step_time.strftime('%H:%M:%S')} "
                          f"Station={best_station.name} "
                          f"Az={tracking['azimuth']:.1f}° El={tracking['elevation']:.1f}°")
                    
                    # ========================================
                    # Command Uplink (Phase 2)
                    # ========================================
                    # Send different commands on different passes (for demonstration)
                    if pass_count == 1:
                        # First pass: Send mode change and payload commands
                        cmd1 = create_set_mode_command("SCIENCE")
                        cmd2 = create_payload_command(True)
                        network.uplink_command(cmd1, step_time.isoformat() + 'Z')
                        network.uplink_command(cmd2, step_time.isoformat() + 'Z')
                        print(f"  ↑ Uplinked: {cmd1}")
                        print(f"  ↑ Uplinked: {cmd2}")
                        current_pass_data['commands_sent'] += 2
                        total_commands_sent += 2
                    
                    elif pass_count == 2:
                        # Second pass: Adjust power
                        cmd = create_adjust_power_command(0.5)
                        network.uplink_command(cmd, step_time.isoformat() + 'Z')
                        print(f"  ↑ Uplinked: {cmd}")
                        current_pass_data['commands_sent'] += 1
                        total_commands_sent += 1
                    
                    elif pass_count == 3:
                        # Third pass: Reset telemetry and set mode back to NOMINAL
                        cmd1 = create_reset_telemetry_command()
                        cmd2 = create_set_mode_command("NOMINAL")
                        network.uplink_command(cmd1, step_time.isoformat() + 'Z')
                        network.uplink_command(cmd2, step_time.isoformat() + 'Z')
                        print(f"  ↑ Uplinked: {cmd1}")
                        print(f"  ↑ Uplinked: {cmd2}")
                        current_pass_data['commands_sent'] += 2
                        total_commands_sent += 2
                    
                    # Transfer commands to satellite
                    commands_to_send = network.active_station.get_command_buffer(clear_after_read=True)
                    for cmd in commands_to_send:
                        satellite.receive_command(cmd)
                    
                    previous_active_station = best_station.name
                
                # Check if we should hand-off to a better station
                elif best_station != network.active_station:
                    old_station = network.active_station.name
                    network.handoff_station(best_station, step_time.isoformat() + 'Z', "elevation")
                    current_pass_data['stations_used'].add(best_station.name)
                    print(f"  ✈ Handoff: {old_station} → {best_station.name} "
                          f"(El: {elevation_data[best_station.name]:.1f}°)")
                    previous_active_station = best_station.name
                
                # Track maximum elevation across all stations
                for station_name, el in elevation_data.items():
                    if el > current_pass_data['max_elevation']:
                        current_pass_data['max_elevation'] = el
                        current_pass_data['max_el_time'] = step_time
                        current_pass_data['max_el_station'] = station_name
                
                # Estimate if satellite is in sunlight (simplified)
                geocentric = satellite_orbit.at(t)
                subpoint = geocentric.subpoint()
                is_sunlit = estimate_sunlit(subpoint.elevation.km, 
                                           subpoint.latitude.degrees,
                                           step_time)
                
                # Generate telemetry
                telemetry = satellite.generate_telemetry(
                    is_sunlit=is_sunlit,
                    time_step_seconds=TIME_STEP_SECONDS
                )
                
                # Add timestamp from simulation (not real time)
                telemetry['timestamp'] = step_time.isoformat() + 'Z'
                
                # Network receives telemetry at active station
                active_tracking = tracking_by_station[network.active_station.name]
                network.receive_telemetry(
                    telemetry,
                    tracking_data=active_tracking
                )
                
                # Log combined telemetry + tracking data
                combined_packet = network.active_station.telemetry_buffer[-1]
                logger.log_telemetry(combined_packet)
                
                current_pass_data['telemetry_packets'] += 1
                total_telemetry_packets += 1
                
                # ========================================
                # Command Processing (Phase 2)
                # ========================================
                # Process any pending commands
                processed_commands = satellite.process_commands(step_time.isoformat() + 'Z')
                for cmd in processed_commands:
                    # Log command execution
                    logger.log_command(cmd.to_dict())
                    print(f"  ✓ Executed: {cmd} - {cmd.acknowledgment}")
                
            else:
                # Detect LOS (Loss of Signal)
                if in_pass:
                    in_pass = False
                    current_pass_data['los_time'] = step_time
                    
                    # Clear active station
                    network.clear_active_station(step_time.isoformat() + 'Z')
                    
                    # Calculate pass duration
                    duration = (current_pass_data['los_time'] - 
                               current_pass_data['aos_time']).total_seconds() / 60.0
                    
                    stations_str = ", ".join(sorted(current_pass_data['stations_used']))
                    print(f"LOS #{pass_count}: {step_time.strftime('%H:%M:%S')} "
                          f"Duration={duration:.1f}min "
                          f"MaxEl={current_pass_data['max_elevation']:.1f}° ({current_pass_data['max_el_station']}) "
                          f"Stations=[{stations_str}] "
                          f"Packets={current_pass_data['telemetry_packets']} "
                          f"Commands={current_pass_data['commands_sent']}")
                    
                    # Store pass data
                    passes.append(current_pass_data.copy())
            
            # Progress indicator (every 5%)
            progress = (i + 1) / total_steps * 100
            if (i + 1) % (total_steps // 20) == 0:
                print(f"  Progress: {progress:.1f}% ({i+1}/{total_steps} steps)")
        
        # Handle case where simulation ends during a pass
        if in_pass:
            current_pass_data['los_time'] = END_TIME
            passes.append(current_pass_data)
        
        print()
        print("✓ Simulation complete!")
        print(f"  Total time steps: {total_steps}")
        print(f"  Total telemetry packets: {total_telemetry_packets}")
        print()
    
    # ========================================
    # 7. Display summary
    # ========================================
    print("=" * 60)
    print("SIMULATION SUMMARY (Phase 3)")
    print("=" * 60)
    print(f"Satellite: {SATELLITE_NAME}")
    print(f"Ground Station Network: {len(network.stations)} stations")
    print(f"Simulation Period: {START_TIME} to {END_TIME}")
    print(f"Total Passes: {len(passes)}")
    print(f"Total Telemetry Packets: {total_telemetry_packets}")
    print(f"Total Commands Executed: {len(satellite.command_history)}")
    print()
    
    print("PASS DETAILS:")
    print("-" * 60)
    for i, p in enumerate(passes, 1):
        duration = (p['los_time'] - p['aos_time']).total_seconds() / 60.0
        stations_str = ", ".join(sorted(p['stations_used']))
        print(f"Pass #{i}:")
        print(f"  AOS: {p['aos_time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  LOS: {p['los_time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"  Duration: {duration:.1f} minutes")
        print(f"  Max Elevation: {p['max_elevation']:.1f}° "
              f"at {p['max_el_time'].strftime('%H:%M:%S')} ({p['max_el_station']})")
        print(f"  Stations Used: {stations_str}")
        print(f"  Telemetry Packets: {p['telemetry_packets']}")
        print(f"  Commands Sent: {p['commands_sent']}")
        print()
    
    # Display network statistics (Phase 3)
    print("=" * 60)
    print("NETWORK STATISTICS:")
    print("-" * 60)
    net_stats = network.get_network_statistics()
    for station_info in net_stats['stations']:
        print(f"{station_info['name']}:")
        print(f"  Location: {station_info['location']}")
        print(f"  Packets Received: {station_info['packets_received']}")
        print(f"  Commands Sent: {station_info['commands_sent']}")
    print()
    
    # Display handoff summary (Phase 3)
    print(network.get_handoff_summary())
    print()
    
    print("=" * 60)
    print(f"Output files:")
    print(f"  Telemetry: {telemetry_file}")
    print(f"  Tracking: {tracking_file}")
    print(f"  Commands: {command_file}")
    print("=" * 60)
    print()
    
    # Display command execution summary
    print("Command Execution Summary:")
    print("-" * 60)
    for cmd in satellite.command_history:
        print(f"  {cmd}")
    print()
    
    # Display satellite final state
    print("Satellite Final State:")
    print(satellite.get_status_summary())
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
