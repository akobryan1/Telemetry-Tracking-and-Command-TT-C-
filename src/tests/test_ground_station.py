"""
Unit tests for GroundStation class
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.ground_station import GroundStation


def test_ground_station_initialization():
    """Test ground station initialization."""
    gs = GroundStation(
        name="TestStation",
        latitude=40.0,
        longitude=-75.0,
        altitude_m=100.0,
        min_elevation=10.0
    )
    
    assert gs.name == "TestStation"
    assert gs.latitude == 40.0
    assert gs.longitude == -75.0
    assert gs.altitude_m == 100.0
    assert gs.min_elevation == 10.0
    assert gs.packets_received == 0
    assert len(gs.telemetry_buffer) == 0


def test_receive_telemetry():
    """Test receiving telemetry packets."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # Create test telemetry packet
    telemetry = {
        'timestamp': '2026-05-02T12:00:00Z',
        'battery_voltage': 28.5,
        'temperature': 22.0,
        'mode': 'NOMINAL'
    }
    
    # Receive packet
    result = gs.receive_telemetry(telemetry)
    
    assert result is True
    assert gs.packets_received == 1
    assert len(gs.telemetry_buffer) == 1


def test_receive_telemetry_with_tracking():
    """Test receiving telemetry with tracking data."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    telemetry = {
        'timestamp': '2026-05-02T12:00:00Z',
        'battery_voltage': 28.5
    }
    
    tracking = {
        'azimuth': 180.0,
        'elevation': 45.0,
        'range_km': 500.0,
        'range_rate_km_s': -2.5
    }
    
    gs.receive_telemetry(telemetry, tracking_data=tracking)
    
    # Check that packet includes both telemetry and tracking
    packet = gs.telemetry_buffer[0]
    assert 'battery_voltage' in packet
    assert 'azimuth' in packet
    assert 'elevation' in packet
    assert packet['azimuth'] == 180.0
    assert packet['elevation'] == 45.0


def test_get_telemetry_buffer():
    """Test retrieving telemetry buffer."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # Add some packets
    for i in range(3):
        gs.receive_telemetry({'packet_id': i})
    
    # Get buffer without clearing
    buffer = gs.get_telemetry_buffer(clear_after_read=False)
    assert len(buffer) == 3
    assert len(gs.telemetry_buffer) == 3  # Still in buffer
    
    # Get buffer with clearing
    buffer = gs.get_telemetry_buffer(clear_after_read=True)
    assert len(buffer) == 3
    assert len(gs.telemetry_buffer) == 0  # Cleared


def test_start_new_pass():
    """Test starting a new pass."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # Receive some packets
    gs.receive_telemetry({'packet_id': 1})
    gs.receive_telemetry({'packet_id': 2})
    
    # Start new pass
    gs.start_new_pass()
    
    # Current pass packets should be cleared
    current = gs.get_current_pass_packets()
    assert len(current) == 0
    
    # But total buffer should still have old packets
    assert len(gs.telemetry_buffer) == 2


def test_current_pass_tracking():
    """Test tracking packets for current pass."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # Start new pass
    gs.start_new_pass()
    
    # Receive packets during pass
    gs.receive_telemetry({'packet_id': 1})
    gs.receive_telemetry({'packet_id': 2})
    gs.receive_telemetry({'packet_id': 3})
    
    # Check current pass packets
    current = gs.get_current_pass_packets()
    assert len(current) == 3


def test_end_pass():
    """Test ending a pass and getting statistics."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    gs.start_new_pass()
    
    # Receive some packets
    for i in range(5):
        gs.receive_telemetry({
            'packet_id': i,
            'timestamp': f'2026-05-02T12:00:{i:02d}Z'
        })
    
    # End pass
    stats = gs.end_pass()
    
    assert stats['packets_received'] == 5
    assert stats['pass_complete'] is True
    assert 'first_packet_time' in stats
    assert 'last_packet_time' in stats


def test_clear_buffer():
    """Test clearing telemetry buffer."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # Add packets
    for i in range(5):
        gs.receive_telemetry({'packet_id': i})
    
    assert len(gs.telemetry_buffer) == 5
    
    # Clear buffer
    gs.clear_buffer()
    
    assert len(gs.telemetry_buffer) == 0


def test_get_statistics():
    """Test getting ground station statistics."""
    gs = GroundStation(
        name="TestStation",
        latitude=25.5,
        longitude=-80.0,
        altitude_m=50.0,
        min_elevation=15.0
    )
    
    # Receive some packets
    for i in range(10):
        gs.receive_telemetry({'packet_id': i})
    
    stats = gs.get_statistics()
    
    assert stats['station_name'] == "TestStation"
    assert stats['total_packets_received'] == 10
    assert stats['buffer_size'] == 10
    assert stats['min_elevation'] == 15.0
    assert stats['location']['latitude'] == 25.5
    assert stats['location']['longitude'] == -80.0


def test_multiple_passes():
    """Test handling multiple satellite passes."""
    gs = GroundStation(name="TestStation", latitude=0, longitude=0)
    
    # First pass
    gs.start_new_pass()
    gs.receive_telemetry({'pass': 1, 'packet': 1})
    gs.receive_telemetry({'pass': 1, 'packet': 2})
    stats1 = gs.end_pass()
    assert stats1['packets_received'] == 2
    
    # Second pass
    gs.start_new_pass()
    gs.receive_telemetry({'pass': 2, 'packet': 1})
    gs.receive_telemetry({'pass': 2, 'packet': 2})
    gs.receive_telemetry({'pass': 2, 'packet': 3})
    stats2 = gs.end_pass()
    assert stats2['packets_received'] == 3
    
    # Total packets across all passes
    assert gs.packets_received == 5


def test_str_representation():
    """Test string representation of ground station."""
    gs = GroundStation(name="Miami", latitude=25.7617, longitude=-80.1918)
    
    str_repr = str(gs)
    
    assert "Miami" in str_repr
    assert "25.7617" in str_repr
    assert "-80.1918" in str_repr
