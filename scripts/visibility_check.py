"""
Visibility Calculator - Phase 0

Calculates when a satellite is visible from a ground station over a time period.
Outputs tracking data to CSV file.

Usage:
    python scripts/visibility_check.py

Output:
    CSV file in data/outputs/tracking/ with columns:
    - timestamp (UTC)
    - azimuth_deg
    - elevation_deg
    - range_km
    - range_rate_km_s
    - is_visible
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from skyfield.api import load
from utils.orbital_mechanics import load_satellite_tle, propagate_orbit
from utils.coordinate_transforms import (
    compute_azimuth_elevation_range,
    is_visible,
    create_ground_station
)


def main():
    """Run visibility calculation for ISS over Miami."""
    
    print("=" * 60)
    print("TT&C Simulation - Visibility Calculator (Phase 0)")
    print("=" * 60)
    
    # Configuration
    TLE_FILE = "data/inputs/tle/stations.txt"
    SATELLITE_NAME = "ISS"
    
    # Miami ground station
    STATION_LAT = 25.7617  # degrees North
    STATION_LON = -80.1918  # degrees West
    STATION_ALT = 10  # meters above ellipsoid
    MIN_ELEVATION = 10.0  # degrees
    
    # Simulation time range (May 2, 2026 - 24 hours)
    START_TIME = datetime(2026, 5, 2, 0, 0, 0)
    END_TIME = datetime(2026, 5, 3, 0, 0, 0)
    TIME_STEP_SECONDS = 10
    
    # Output file
    OUTPUT_DIR = Path("data/outputs/tracking")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUTPUT_FILE = OUTPUT_DIR / f"visibility_{timestamp_str}.csv"
    
    print(f"\nConfiguration:")
    print(f"  Satellite: {SATELLITE_NAME}")
    print(f"  Ground Station: Miami, FL ({STATION_LAT:.4f}°N, {STATION_LON:.4f}°W)")
    print(f"  Altitude: {STATION_ALT} m")
    print(f"  Min Elevation: {MIN_ELEVATION}°")
    print(f"  Time Range: {START_TIME} to {END_TIME}")
    print(f"  Time Step: {TIME_STEP_SECONDS} seconds")
    print(f"  Output: {OUTPUT_FILE}")
    print()
    
    # Load satellite TLE
    print("Loading satellite TLE data...")
    try:
        satellite = load_satellite_tle(TLE_FILE, SATELLITE_NAME)
        print(f"  ✓ Loaded {satellite.name}")
        print(f"  TLE Epoch: {satellite.epoch.utc_iso()}")
    except Exception as e:
        print(f"  ✗ Error loading TLE: {e}")
        return 1
    
    # Create ground station
    print("\nCreating ground station...")
    observer = create_ground_station(STATION_LAT, STATION_LON, STATION_ALT)
    print(f"  ✓ Ground station created at ({STATION_LAT:.4f}°, {STATION_LON:.4f}°)")
    
    # Initialize timescale
    ts = load.timescale()
    
    # Generate time array
    print("\nGenerating time steps...")
    current_time = START_TIME
    total_steps = int((END_TIME - START_TIME).total_seconds() / TIME_STEP_SECONDS)
    print(f"  Total time steps: {total_steps}")
    
    # Track visibility state for AOS/LOS detection
    previous_visible = False
    pass_count = 0
    current_pass = None
    passes = []
    
    # Open output CSV file
    print("\nCalculating visibility...")
    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp',
            'azimuth_deg',
            'elevation_deg',
            'range_km',
            'range_rate_km_s',
            'is_visible'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        step = 0
        while current_time < END_TIME:
            # Convert to Skyfield time
            t = ts.utc(current_time.year, current_time.month, current_time.day,
                      current_time.hour, current_time.minute, current_time.second)
            
            # Compute azimuth, elevation, range
            az, el, rng, rng_rate = compute_azimuth_elevation_range(
                satellite, observer, t
            )
            
            # Check visibility
            visible = is_visible(el, MIN_ELEVATION)
            
            # Detect AOS/LOS events
            if visible and not previous_visible:
                # Acquisition of Signal (AOS)
                pass_count += 1
                current_pass = {
                    'pass_number': pass_count,
                    'aos_time': current_time,
                    'aos_azimuth': az,
                    'aos_elevation': el,
                    'max_elevation': el,
                    'max_elevation_time': current_time
                }
                print(f"  AOS #{pass_count}: {current_time.strftime('%H:%M:%S')} "
                      f"Az={az:.1f}° El={el:.1f}°")
            
            elif not visible and previous_visible:
                # Loss of Signal (LOS)
                if current_pass:
                    current_pass['los_time'] = current_time
                    current_pass['los_azimuth'] = az
                    current_pass['los_elevation'] = el
                    duration = (current_pass['los_time'] - current_pass['aos_time']).total_seconds()
                    current_pass['duration_seconds'] = duration
                    passes.append(current_pass)
                    print(f"  LOS #{pass_count}: {current_time.strftime('%H:%M:%S')} "
                          f"Duration={duration/60:.1f}min MaxEl={current_pass['max_elevation']:.1f}°")
                    current_pass = None
            
            elif visible and current_pass:
                # Update max elevation during pass
                if el > current_pass['max_elevation']:
                    current_pass['max_elevation'] = el
                    current_pass['max_elevation_time'] = current_time
            
            # Write to CSV
            writer.writerow({
                'timestamp': current_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'azimuth_deg': f"{az:.2f}",
                'elevation_deg': f"{el:.2f}",
                'range_km': f"{rng:.2f}",
                'range_rate_km_s': f"{rng_rate:.4f}",
                'is_visible': 'TRUE' if visible else 'FALSE'
            })
            
            previous_visible = visible
            current_time += timedelta(seconds=TIME_STEP_SECONDS)
            step += 1
            
            # Progress indicator
            if step % 360 == 0:  # Every hour
                progress = (step / total_steps) * 100
                print(f"  Progress: {progress:.1f}% ({step}/{total_steps} steps)")
    
    # Handle pass still in progress at end of simulation
    if current_pass:
        current_pass['los_time'] = END_TIME
        duration = (current_pass['los_time'] - current_pass['aos_time']).total_seconds()
        current_pass['duration_seconds'] = duration
        passes.append(current_pass)
        print(f"  LOS #{pass_count}: {END_TIME.strftime('%H:%M:%S')} (simulation end) "
              f"Duration={duration/60:.1f}min MaxEl={current_pass['max_elevation']:.1f}°")
    
    print(f"\n✓ Calculation complete! {step} time steps processed.")
    print(f"✓ Data written to: {OUTPUT_FILE}")
    
    # Summary
    print("\n" + "=" * 60)
    print("PASS SUMMARY")
    print("=" * 60)
    if passes:
        print(f"Total passes: {len(passes)}")
        print()
        for p in passes:
            print(f"Pass #{p['pass_number']}:")
            print(f"  AOS: {p['aos_time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"  LOS: {p['los_time'].strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"  Duration: {p['duration_seconds']/60:.1f} minutes")
            print(f"  Max Elevation: {p['max_elevation']:.1f}° at "
                  f"{p['max_elevation_time'].strftime('%H:%M:%S')} UTC")
            print()
    else:
        print("No passes detected during simulation period.")
    
    print("=" * 60)
    print("\nValidation:")
    print("  Compare these pass times with:")
    print("  - https://www.n2yo.com/")
    print("  - https://www.heavens-above.com/")
    print("  Expected accuracy: ±30 seconds for AOS/LOS, ±5° for elevation")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
