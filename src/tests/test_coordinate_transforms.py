"""
Unit tests for coordinate transformation utilities
"""

import pytest
import numpy as np
from skyfield.api import load, wgs84
from src.utils.coordinate_transforms import (
    is_visible,
    create_ground_station,
    geodetic_to_geocentric,
    angle_difference
)


def test_is_visible():
    """Test visibility determination based on elevation angle."""
    # Above threshold
    assert is_visible(15.0, min_elevation=10.0) == True
    assert is_visible(10.0, min_elevation=10.0) == True
    
    # Below threshold
    assert is_visible(9.99, min_elevation=10.0) == False
    assert is_visible(0.0, min_elevation=10.0) == False
    assert is_visible(-5.0, min_elevation=10.0) == False


def test_create_ground_station():
    """Test ground station creation."""
    # Miami ground station
    miami = create_ground_station(25.7617, -80.1918, altitude_m=10)
    
    # Check it's a valid Skyfield geographic position
    assert hasattr(miami, 'latitude')
    assert hasattr(miami, 'longitude')
    assert hasattr(miami, 'elevation')
    
    # Check coordinates (Skyfield uses Angle objects)
    assert abs(miami.latitude.degrees - 25.7617) < 0.001
    assert abs(miami.longitude.degrees - (-80.1918)) < 0.001
    assert abs(miami.elevation.m - 10) < 0.1


def test_geodetic_to_geocentric():
    """Test conversion from geodetic to geocentric coordinates."""
    # Equator at prime meridian, sea level
    x, y, z = geodetic_to_geocentric(0, 0, 0)
    # Should be approximately at equatorial radius
    assert abs(x - 6378.137) < 1  # km, WGS84 equatorial radius
    assert abs(y) < 0.1
    assert abs(z) < 0.1
    
    # North pole
    x, y, z = geodetic_to_geocentric(90, 0, 0)
    assert abs(x) < 0.1
    assert abs(y) < 0.1
    # Should be approximately at polar radius
    assert abs(z - 6356.752) < 1  # km, WGS84 polar radius
    
    # Miami location
    x, y, z = geodetic_to_geocentric(25.7617, -80.1918, 10)
    # Should be roughly at Earth radius
    radius = np.sqrt(x**2 + y**2 + z**2)
    assert 6370 < radius < 6380  # km


def test_angle_difference():
    """Test angle difference calculation with wraparound."""
    # Simple cases
    assert abs(angle_difference(10, 5) - 5) < 0.001
    assert abs(angle_difference(5, 10) - (-5)) < 0.001
    
    # Wraparound cases
    assert abs(angle_difference(10, 350) - 20) < 0.001
    assert abs(angle_difference(350, 10) - (-20)) < 0.001
    
    # 180-degree cases (can be ±180, both valid)
    result = angle_difference(0, 180)
    assert abs(result) == 180 or abs(result) < 0.001
    
    # Same angle
    assert abs(angle_difference(45, 45)) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
