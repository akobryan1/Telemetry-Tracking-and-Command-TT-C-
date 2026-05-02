"""
Unit tests for Satellite class
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.satellite import Satellite


def test_satellite_initialization():
    """Test satellite is initialized with correct default values."""
    sat = Satellite(name="TestSat")
    
    assert sat.name == "TestSat"
    assert sat.battery_voltage == 28.0
    assert sat.temperature == 20.0
    assert sat.mode == Satellite.MODE_NOMINAL
    assert sat.telemetry_count == 0


def test_satellite_custom_initialization():
    """Test satellite initialization with custom parameters."""
    sat = Satellite(
        name="CustomSat",
        initial_battery_voltage=29.5,
        initial_temperature=25.0,
        initial_mode=Satellite.MODE_SCIENCE
    )
    
    assert sat.name == "CustomSat"
    assert sat.battery_voltage == 29.5
    assert sat.temperature == 25.0
    assert sat.mode == Satellite.MODE_SCIENCE


def test_telemetry_generation():
    """Test telemetry packet generation."""
    sat = Satellite(name="TestSat")
    
    # Generate telemetry
    telemetry = sat.generate_telemetry(is_sunlit=True)
    
    # Check packet structure
    assert 'timestamp' in telemetry
    assert 'battery_voltage' in telemetry
    assert 'solar_current' in telemetry
    assert 'temperature' in telemetry
    assert 'mode' in telemetry
    assert 'telemetry_id' in telemetry
    
    # Check telemetry count incremented
    assert sat.telemetry_count == 1
    assert telemetry['telemetry_id'] == 1


def test_telemetry_sunlit_vs_eclipse():
    """Test that solar current differs between sunlit and eclipse."""
    sat = Satellite(name="TestSat")
    
    # Generate telemetry in sunlight
    telemetry_sunlit = sat.generate_telemetry(is_sunlit=True)
    
    # Reset satellite
    sat2 = Satellite(name="TestSat")
    
    # Generate telemetry in eclipse
    telemetry_eclipse = sat2.generate_telemetry(is_sunlit=False)
    
    # Solar current should be higher when sunlit
    assert telemetry_sunlit['solar_current'] > 1.0  # Significant current
    assert abs(telemetry_eclipse['solar_current']) < 0.1  # Near zero in eclipse


def test_battery_charging():
    """Test battery charges when in sunlight."""
    sat = Satellite(name="TestSat", initial_battery_voltage=27.0)
    
    # Generate several telemetry packets in sunlight
    for _ in range(10):
        sat.generate_telemetry(is_sunlit=True)
    
    # Battery should have charged above initial value
    assert sat.battery_voltage > 27.0


def test_battery_draining():
    """Test battery drains when in eclipse."""
    sat = Satellite(name="TestSat", initial_battery_voltage=28.0)
    
    # Generate several telemetry packets in eclipse
    for _ in range(10):
        sat.generate_telemetry(is_sunlit=False)
    
    # Battery should have drained below initial value
    assert sat.battery_voltage < 28.0


def test_mode_transitions():
    """Test operational mode changes based on battery voltage."""
    # Start with low battery - should go to SAFE mode
    sat = Satellite(name="TestSat", initial_battery_voltage=26.2)
    telemetry = sat.generate_telemetry(is_sunlit=False)
    assert telemetry['mode'] == Satellite.MODE_SAFE
    
    # High battery - should go to SCIENCE mode
    sat2 = Satellite(name="TestSat", initial_battery_voltage=29.0)
    telemetry2 = sat2.generate_telemetry(is_sunlit=True)
    assert telemetry2['mode'] == Satellite.MODE_SCIENCE
    
    # Mid-range battery - should be NOMINAL
    sat3 = Satellite(name="TestSat", initial_battery_voltage=27.5)
    telemetry3 = sat3.generate_telemetry(is_sunlit=True)
    assert telemetry3['mode'] == Satellite.MODE_NOMINAL


def test_telemetry_count_increment():
    """Test telemetry counter increments correctly."""
    sat = Satellite(name="TestSat")
    
    for i in range(1, 6):
        telemetry = sat.generate_telemetry()
        assert sat.telemetry_count == i
        assert telemetry['telemetry_id'] == i


def test_reset_telemetry_count():
    """Test resetting telemetry counter."""
    sat = Satellite(name="TestSat")
    
    # Generate some telemetry
    sat.generate_telemetry()
    sat.generate_telemetry()
    assert sat.telemetry_count == 2
    
    # Reset
    sat.reset_telemetry_count()
    assert sat.telemetry_count == 0


def test_set_mode_valid():
    """Test setting valid operational modes."""
    sat = Satellite(name="TestSat")
    
    sat.set_mode(Satellite.MODE_SAFE)
    assert sat.mode == Satellite.MODE_SAFE
    
    sat.set_mode(Satellite.MODE_SCIENCE)
    assert sat.mode == Satellite.MODE_SCIENCE


def test_set_mode_invalid():
    """Test that invalid mode raises ValueError."""
    sat = Satellite(name="TestSat")
    
    with pytest.raises(ValueError):
        sat.set_mode("INVALID_MODE")


def test_status_summary():
    """Test status summary generation."""
    sat = Satellite(name="TestSat")
    sat.generate_telemetry()
    
    summary = sat.get_status_summary()
    
    assert "TestSat" in summary
    assert "Battery" in summary
    assert "Temperature" in summary
    assert "Mode" in summary
    assert "Telemetry Packets" in summary


def test_temperature_variation():
    """Test that temperature varies over multiple telemetry cycles."""
    sat = Satellite(name="TestSat")
    
    temperatures = []
    for _ in range(100):
        telemetry = sat.generate_telemetry()
        temperatures.append(telemetry['temperature'])
    
    # Temperature should vary (not all the same)
    assert len(set(temperatures)) > 10  # At least 10 different values
    
    # Temperature should stay within reasonable bounds
    assert all(-20 < t < 50 for t in temperatures)
