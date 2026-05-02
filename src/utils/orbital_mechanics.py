"""
Orbital mechanics utilities for satellite propagation using SGP4 via Skyfield.

This module provides functions to:
- Load satellite TLE data
- Propagate satellite orbits
- Compute satellite positions and velocities in ECI frame
"""

from skyfield.api import load, EarthSatellite, wgs84
from skyfield.timelib import Time
from astropy.time import Time as AstroTime
import numpy as np


def load_satellite_tle(tle_file_path, satellite_name=None):
    """
    Load satellite TLE data from a file.
    
    Parameters:
    -----------
    tle_file_path : str
        Path to TLE file
    satellite_name : str, optional
        Name of satellite to load. If None, loads first satellite in file.
        
    Returns:
    --------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
        
    Example:
    --------
    >>> sat = load_satellite_tle('data/inputs/tle/stations.txt', 'ISS')
    """
    with open(tle_file_path, 'r') as f:
        lines = f.readlines()
    
    # TLE format: name, line1, line2
    satellites = []
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            name = lines[i].strip()
            line1 = lines[i + 1].strip()
            line2 = lines[i + 2].strip()
            
            ts = load.timescale()
            sat = EarthSatellite(line1, line2, name, ts)
            satellites.append((name, sat))
    
    if not satellites:
        raise ValueError(f"No TLE data found in {tle_file_path}")
    
    # Find satellite by name or return first
    if satellite_name:
        for name, sat in satellites:
            if satellite_name.upper() in name.upper():
                return sat
        raise ValueError(f"Satellite '{satellite_name}' not found in TLE file")
    
    return satellites[0][1]


def propagate_orbit(satellite, time):
    """
    Propagate satellite orbit to specified time using SGP4.
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
    time : skyfield.timelib.Time or astropy.time.Time
        Time to propagate to
        
    Returns:
    --------
    position : numpy.ndarray
        Position vector in ECI frame (km), shape (3,)
    velocity : numpy.ndarray
        Velocity vector in ECI frame (km/s), shape (3,)
        
    Example:
    --------
    >>> ts = load.timescale()
    >>> t = ts.utc(2026, 5, 2, 12, 0, 0)
    >>> pos, vel = propagate_orbit(satellite, t)
    """
    # Convert astropy Time to skyfield Time if needed
    if isinstance(time, AstroTime):
        ts = load.timescale()
        time = ts.from_astropy(time)
    
    # Get geocentric position (from Earth center in GCRS/ECI frame)
    geocentric = satellite.at(time)
    
    # Position in km
    position = geocentric.position.km
    
    # Velocity in km/s
    velocity = geocentric.velocity.km_per_s
    
    return position, velocity


def get_tle_epoch(satellite):
    """
    Get the epoch time from satellite TLE.
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
        
    Returns:
    --------
    epoch : skyfield.timelib.Time
        Epoch time of TLE
    """
    return satellite.epoch


def get_orbital_period(satellite):
    """
    Calculate orbital period from TLE mean motion.
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
        
    Returns:
    --------
    period_minutes : float
        Orbital period in minutes
        
    Note:
    -----
    Mean motion is in revolutions per day, so period = 1440 / mean_motion
    """
    # Mean motion is stored in the satellite model
    mean_motion = satellite.model.no_kozai  # radians per minute
    period_minutes = 2 * np.pi / mean_motion
    
    return period_minutes


def check_tle_age(satellite, current_time, max_age_days=7):
    """
    Check if TLE is too old and might have significant propagation errors.
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
    current_time : skyfield.timelib.Time
        Current time to check against
    max_age_days : float, optional
        Maximum acceptable TLE age in days (default: 7 for LEO)
        
    Returns:
    --------
    is_fresh : bool
        True if TLE age is within acceptable range
    age_days : float
        Age of TLE in days
        
    Warning:
    --------
    For LEO satellites, TLE older than 7 days can have >10 km position errors
    """
    epoch = satellite.epoch
    age_days = current_time - epoch
    is_fresh = age_days <= max_age_days
    
    return is_fresh, age_days
