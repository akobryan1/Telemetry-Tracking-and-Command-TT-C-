"""
Unit tests for orbital mechanics utilities
"""

import pytest
from pathlib import Path
from skyfield.api import load
from src.utils.orbital_mechanics import (
    load_satellite_tle,
    propagate_orbit,
    get_tle_epoch,
    check_tle_age
)


def test_load_satellite_tle():
    """Test loading satellite TLE from file."""
    tle_file = "data/inputs/tle/stations.txt"
    
    # Load ISS
    satellite = load_satellite_tle(tle_file, "ISS")
    assert satellite is not None
    assert "ISS" in satellite.name or "ZARYA" in satellite.name
    
    # Load without specifying name (should get first satellite)
    satellite = load_satellite_tle(tle_file)
    assert satellite is not None


def test_propagate_orbit():
    """Test orbit propagation."""
    tle_file = "data/inputs/tle/stations.txt"
    satellite = load_satellite_tle(tle_file, "ISS")
    
    # Propagate to a time
    ts = load.timescale()
    t = ts.utc(2026, 5, 2, 12, 0, 0)
    
    position, velocity = propagate_orbit(satellite, t)
    
    # Check position is reasonable for LEO (400-450 km altitude)
    # Position magnitude should be ~6778 km (Earth radius + altitude)
    import numpy as np
    pos_magnitude = np.linalg.norm(position)
    assert 6700 < pos_magnitude < 7000  # km
    
    # Check velocity is reasonable for LEO (~7.6-7.8 km/s)
    vel_magnitude = np.linalg.norm(velocity)
    assert 7.0 < vel_magnitude < 8.5  # km/s


def test_get_tle_epoch():
    """Test extracting TLE epoch."""
    tle_file = "data/inputs/tle/stations.txt"
    satellite = load_satellite_tle(tle_file, "ISS")
    
    epoch = get_tle_epoch(satellite)
    assert epoch is not None
    
    # Check it's a Skyfield time object
    assert hasattr(epoch, 'utc_iso')


def test_check_tle_age():
    """Test TLE age checking."""
    tle_file = "data/inputs/tle/stations.txt"
    satellite = load_satellite_tle(tle_file, "ISS")
    
    # Check against a time close to the TLE epoch
    ts = load.timescale()
    # TLE epoch is around May 2, 2026 (day 122)
    test_time = ts.utc(2026, 5, 2, 12, 0, 0)
    
    is_fresh, age_days = check_tle_age(satellite, test_time, max_age_days=7)
    
    # Age should be small (less than a day if TLE epoch is May 2)
    assert age_days < 1.0
    assert is_fresh == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
