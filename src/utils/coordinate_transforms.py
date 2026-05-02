"""
Coordinate transformation utilities for TT&C simulation.

This module provides transformations between:
- ECI (Earth-Centered Inertial) - J2000/GCRS
- ECEF (Earth-Centered Earth-Fixed) - rotating with Earth
- Topocentric (observer-relative) - East-North-Up (ENU)
- Az/El/Range - antenna pointing coordinates
"""

from skyfield.api import wgs84
import numpy as np


def compute_azimuth_elevation_range(satellite, observer_location, time):
    """
    Compute azimuth, elevation, and range from observer to satellite.
    
    This is the primary function for visibility calculations, using Skyfield's
    built-in coordinate transformations that handle all the complexity of:
    - ECI to ECEF conversion (accounting for Earth rotation)
    - ECEF to topocentric conversion
    - Topocentric to Az/El conversion
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Skyfield satellite object
    observer_location : skyfield.toposlib.GeographicPosition
        Observer position on Earth (from wgs84.latlon())
    time : skyfield.timelib.Time
        Observation time
        
    Returns:
    --------
    azimuth : float
        Azimuth angle in degrees (0° = North, 90° = East)
    elevation : float
        Elevation angle in degrees (0° = horizon, 90° = zenith)
    range_km : float
        Slant range from observer to satellite in km
    range_rate : float
        Rate of change of range in km/s (for Doppler)
        
    Example:
    --------
    >>> from skyfield.api import load, wgs84
    >>> ts = load.timescale()
    >>> t = ts.utc(2026, 5, 2, 12, 0, 0)
    >>> observer = wgs84.latlon(25.7617, -80.1918, elevation_m=10)
    >>> az, el, rng, rng_rate = compute_azimuth_elevation_range(sat, observer, t)
    """
    # Compute difference vector from observer to satellite
    difference = satellite - observer_location
    topocentric = difference.at(time)
    
    # Get azimuth, altitude (elevation), and distance
    alt, az, distance = topocentric.altaz()
    
    # Get range rate (velocity component along line of sight)
    # Positive range_rate means satellite is moving away
    range_rate = topocentric.velocity.km_per_s
    
    # Skyfield returns Distance object, extract km
    range_km = distance.km
    
    # Compute range rate (scalar projection of velocity onto range vector)
    # For Doppler calculation
    position = topocentric.position.km
    velocity_vec = topocentric.velocity.km_per_s
    range_unit = position / np.linalg.norm(position)
    range_rate_scalar = np.dot(velocity_vec, range_unit)
    
    return az.degrees, alt.degrees, range_km, range_rate_scalar


def is_visible(elevation, min_elevation=10.0):
    """
    Determine if satellite is visible based on elevation angle.
    
    Parameters:
    -----------
    elevation : float
        Elevation angle in degrees
    min_elevation : float, optional
        Minimum elevation threshold in degrees (default: 10°)
        Typical values: 5-10° for reliable communications
        
    Returns:
    --------
    visible : bool
        True if satellite is above minimum elevation
        
    Note:
    -----
    Lower elevation angles have:
    - More atmospheric attenuation
    - Higher multipath interference
    - Lower antenna gain (wider beam required)
    Typical minimum for operations: 5-10 degrees
    """
    return elevation >= min_elevation


def create_ground_station(latitude, longitude, altitude_m=0):
    """
    Create a ground station observer location.
    
    Parameters:
    -----------
    latitude : float
        Geodetic latitude in degrees (-90 to 90)
    longitude : float
        Geodetic longitude in degrees (-180 to 180)
    altitude_m : float, optional
        Altitude above WGS84 ellipsoid in meters (default: 0)
        
    Returns:
    --------
    location : skyfield.toposlib.GeographicPosition
        Observer location for visibility calculations
        
    Example:
    --------
    >>> miami = create_ground_station(25.7617, -80.1918, altitude_m=10)
    """
    return wgs84.latlon(latitude, longitude, elevation_m=altitude_m)


def geodetic_to_geocentric(latitude, longitude, altitude_m=0):
    """
    Convert geodetic coordinates to geocentric ECEF coordinates.
    
    Parameters:
    -----------
    latitude : float
        Geodetic latitude in degrees
    longitude : float
        Geodetic longitude in degrees
    altitude_m : float, optional
        Height above WGS84 ellipsoid in meters
        
    Returns:
    --------
    x, y, z : tuple of float
        ECEF coordinates in kilometers
        
    Note:
    -----
    Uses WGS84 ellipsoid model. Earth is not a perfect sphere:
    - Equatorial radius: 6378.137 km
    - Polar radius: 6356.752 km
    - Flattening: 1/298.257223563
    """
    location = wgs84.latlon(latitude, longitude, elevation_m=altitude_m)
    
    # Get ECEF position (Skyfield internal conversion)
    # This is relative to Earth center
    x, y, z = location.itrs_xyz.km
    
    return x, y, z


def compute_ground_track(satellite, times):
    """
    Compute satellite ground track (sub-satellite points).
    
    Parameters:
    -----------
    satellite : skyfield.sgp4lib.EarthSatellite
        Satellite object
    times : skyfield.timelib.Time or array
        Time(s) to compute ground track
        
    Returns:
    --------
    latitudes : numpy.ndarray
        Geodetic latitudes in degrees
    longitudes : numpy.ndarray
        Geodetic longitudes in degrees
    altitudes_km : numpy.ndarray
        Altitudes above ellipsoid in km
        
    Example:
    --------
    >>> ts = load.timescale()
    >>> times = ts.utc(2026, 5, 2, 0, range(0, 3600, 10))  # Every 10 sec for 1 hour
    >>> lats, lons, alts = compute_ground_track(satellite, times)
    """
    geocentric = satellite.at(times)
    subpoint = wgs84.subpoint(geocentric)
    
    return subpoint.latitude.degrees, subpoint.longitude.degrees, subpoint.elevation.km


def angle_difference(angle1, angle2):
    """
    Compute smallest difference between two angles (handles wraparound).
    
    Parameters:
    -----------
    angle1, angle2 : float
        Angles in degrees
        
    Returns:
    --------
    diff : float
        Smallest angular difference in degrees (-180 to 180)
        
    Example:
    --------
    >>> angle_difference(10, 350)  # Returns 20 (not 340)
    """
    diff = (angle1 - angle2 + 180) % 360 - 180
    return diff
