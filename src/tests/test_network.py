"""
Unit tests for GroundStationNetwork class
"""

import pytest
from datetime import datetime, timezone
from src.core.network import GroundStationNetwork
from src.core.ground_station import GroundStation
from src.core.command import Command, create_set_mode_command


class TestGroundStationNetworkInitialization:
    """Test network initialization."""
    
    def test_empty_initialization(self):
        """Test creating an empty network."""
        network = GroundStationNetwork()
        assert len(network.stations) == 0
        assert network.active_station is None
        assert len(network.handoff_history) == 0
    
    def test_initialization_with_stations(self):
        """Test creating a network with initial stations."""
        station1 = GroundStation("Miami", 25.7617, -80.1918, 10.0)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900, 1036.0)
        
        network = GroundStationNetwork([station1, station2])
        assert len(network.stations) == 2
        assert network.get_station("Miami") == station1
        assert network.get_station("Goldstone") == station2


class TestStationManagement:
    """Test adding/removing stations."""
    
    def test_add_station(self):
        """Test adding a station to the network."""
        network = GroundStationNetwork()
        station = GroundStation("Miami", 25.7617, -80.1918)
        
        network.add_station(station)
        assert len(network.stations) == 1
        assert network.get_station("Miami") == station
    
    def test_add_duplicate_station(self):
        """Test that adding the same station twice doesn't duplicate."""
        network = GroundStationNetwork()
        station = GroundStation("Miami", 25.7617, -80.1918)
        
        network.add_station(station)
        network.add_station(station)
        assert len(network.stations) == 1
    
    def test_remove_station(self):
        """Test removing a station from the network."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        result = network.remove_station("Miami")
        assert result is True
        assert len(network.stations) == 1
        assert network.get_station("Miami") is None
        assert network.get_station("Goldstone") == station2
    
    def test_remove_nonexistent_station(self):
        """Test removing a station that doesn't exist."""
        network = GroundStationNetwork()
        result = network.remove_station("NonExistent")
        assert result is False
    
    def test_remove_active_station(self):
        """Test that removing active station clears it."""
        station = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station])
        network.active_station = station
        
        network.remove_station("Miami")
        assert network.active_station is None
    
    def test_get_station_by_name(self):
        """Test retrieving a station by name."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        retrieved = network.get_station("Goldstone")
        assert retrieved == station2
        assert retrieved.latitude == 35.4267


class TestVisibilityTracking:
    """Test visibility status tracking."""
    
    def test_update_visibility(self):
        """Test updating visibility status for stations."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        visibility_data = {
            'Miami': {'is_visible': True, 'elevation': 45.0},
            'Goldstone': {'is_visible': False, 'elevation': 5.0}
        }
        
        network.update_visibility(visibility_data)
        visible_stations = network.get_visible_stations()
        
        assert len(visible_stations) == 1
        assert visible_stations[0].name == "Miami"
    
    def test_get_visible_stations_empty(self):
        """Test getting visible stations when none are visible."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        visibility_data = {
            'Miami': {'is_visible': False},
            'Goldstone': {'is_visible': False}
        }
        
        network.update_visibility(visibility_data)
        visible_stations = network.get_visible_stations()
        
        assert len(visible_stations) == 0
    
    def test_select_best_station(self):
        """Test selecting the best station based on elevation."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        station3 = GroundStation("Madrid", 40.4319, -4.2489)
        network = GroundStationNetwork([station1, station2, station3])
        
        visibility_data = {
            'Miami': {'is_visible': True, 'elevation': 30.0},
            'Goldstone': {'is_visible': True, 'elevation': 60.0},
            'Madrid': {'is_visible': False, 'elevation': 5.0}
        }
        
        elevation_data = {
            'Miami': 30.0,
            'Goldstone': 60.0,
            'Madrid': 5.0
        }
        
        network.update_visibility(visibility_data)
        best_station = network.select_best_station(elevation_data)
        
        assert best_station is not None
        assert best_station.name == "Goldstone"
    
    def test_select_best_station_no_visibility(self):
        """Test selecting best station when none are visible."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station1])
        
        visibility_data = {'Miami': {'is_visible': False}}
        network.update_visibility(visibility_data)
        
        best_station = network.select_best_station({'Miami': 30.0})
        assert best_station is None


class TestHandoffs:
    """Test station hand-off functionality."""
    
    def test_handoff_station(self):
        """Test performing a hand-off between stations."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        # Initial handoff to Miami
        result = network.handoff_station(station1, timestamp, "aos")
        assert result is True
        assert network.active_station == station1
        assert len(network.handoff_history) == 1
        assert network.handoff_history[0]['to_station'] == "Miami"
        assert network.handoff_history[0]['from_station'] is None
        
        # Handoff to Goldstone
        result = network.handoff_station(station2, timestamp, "elevation")
        assert result is True
        assert network.active_station == station2
        assert len(network.handoff_history) == 2
        assert network.handoff_history[1]['from_station'] == "Miami"
        assert network.handoff_history[1]['to_station'] == "Goldstone"
    
    def test_handoff_to_nonexistent_station(self):
        """Test that handoff fails for station not in network."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("NotInNetwork", 0.0, 0.0)
        network = GroundStationNetwork([station1])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        result = network.handoff_station(station2, timestamp, "aos")
        
        assert result is False
        assert network.active_station is None
    
    def test_clear_active_station(self):
        """Test clearing the active station."""
        station = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        network.handoff_station(station, timestamp, "aos")
        
        network.clear_active_station(timestamp)
        assert network.active_station is None
        assert len(network.handoff_history) == 2
        assert network.handoff_history[1]['reason'] == "los"


class TestNetworkOperations:
    """Test telemetry and command operations."""
    
    def test_receive_telemetry_with_active_station(self):
        """Test receiving telemetry when a station is active."""
        station = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        network.handoff_station(station, timestamp, "aos")
        
        telemetry = {
            'timestamp': timestamp,
            'battery_voltage': 28.0,
            'temperature': 20.0
        }
        
        result = network.receive_telemetry(telemetry)
        assert result is True
        assert station.packets_received == 1
    
    def test_receive_telemetry_without_active_station(self):
        """Test that telemetry fails when no station is active."""
        network = GroundStationNetwork()
        
        telemetry = {'battery_voltage': 28.0}
        result = network.receive_telemetry(telemetry)
        
        assert result is False
    
    def test_uplink_command_with_active_station(self):
        """Test uplink command when a station is active."""
        station = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        network.handoff_station(station, timestamp, "aos")
        
        command = create_set_mode_command("SCIENCE")
        result = network.uplink_command(command, timestamp)
        
        assert result is True
        assert station.commands_sent == 1
    
    def test_uplink_command_without_active_station(self):
        """Test that command uplink fails when no station is active."""
        network = GroundStationNetwork()
        
        command = create_set_mode_command("SCIENCE")
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        result = network.uplink_command(command, timestamp)
        
        assert result is False


class TestNetworkStatistics:
    """Test network statistics and reporting."""
    
    def test_get_network_statistics(self):
        """Test retrieving network statistics."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        # Simulate some activity
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        network.handoff_station(station1, timestamp, "aos")
        
        telemetry = {'battery_voltage': 28.0}
        network.receive_telemetry(telemetry)
        network.receive_telemetry(telemetry)
        
        stats = network.get_network_statistics()
        
        assert stats['total_stations'] == 2
        assert stats['total_packets'] == 2
        assert stats['total_handoffs'] == 1
        assert stats['active_station'] == "Miami"
        assert len(stats['stations']) == 2
    
    def test_get_handoff_summary(self):
        """Test getting formatted handoff summary."""
        station1 = GroundStation("Miami", 25.7617, -80.1918)
        station2 = GroundStation("Goldstone", 35.4267, -116.8900)
        network = GroundStationNetwork([station1, station2])
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        network.handoff_station(station1, timestamp, "aos")
        network.handoff_station(station2, timestamp, "elevation")
        
        summary = network.get_handoff_summary()
        
        assert "Station Hand-offs" in summary
        assert "2 total" in summary
        assert "Miami" in summary
        assert "Goldstone" in summary
    
    def test_get_handoff_summary_empty(self):
        """Test handoff summary when no handoffs occurred."""
        network = GroundStationNetwork()
        summary = network.get_handoff_summary()
        
        assert summary == "No hand-offs recorded"
    
    def test_network_repr(self):
        """Test network string representation."""
        station = GroundStation("Miami", 25.7617, -80.1918)
        network = GroundStationNetwork([station])
        
        repr_str = repr(network)
        assert "GroundStationNetwork" in repr_str
        assert "stations=1" in repr_str
        assert "active=None" in repr_str
