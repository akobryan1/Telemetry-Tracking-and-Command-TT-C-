"""
Unit tests for Flask Web Dashboard API (Phase 4)
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from app import app, initialize_simulation


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    
    # Initialize simulation before tests
    initialize_simulation()
    
    with app.test_client() as client:
        yield client


class TestWebRoutes:
    """Test web page routes."""
    
    def test_index_page(self, client):
        """Test that index page loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'TT&C Dashboard' in response.data


class TestAPIStatus:
    """Test /api/status endpoint."""
    
    def test_status_endpoint(self, client):
        """Test status endpoint returns valid data."""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'timestamp' in data
        assert 'satellite' in data
        assert 'network' in data
    
    def test_status_satellite_data(self, client):
        """Test satellite data in status response."""
        response = client.get('/api/status')
        data = response.get_json()
        
        satellite = data['satellite']
        assert satellite['name'] == 'ISS'
        assert 'battery_voltage' in satellite
        assert 'temperature' in satellite
        assert 'mode' in satellite
        assert 'position' in satellite
        
        # Check position data
        position = satellite['position']
        assert 'latitude' in position
        assert 'longitude' in position
        assert 'altitude_km' in position
    
    def test_status_network_data(self, client):
        """Test network data in status response."""
        response = client.get('/api/status')
        data = response.get_json()
        
        network = data['network']
        assert 'active_stations' in network
        assert 'total_stations' in network
        assert 'visibility' in network
        assert network['total_stations'] == 4  # Miami, Goldstone, Madrid, Canberra


class TestAPITelemetry:
    """Test /api/telemetry endpoint."""
    
    def test_telemetry_endpoint(self, client):
        """Test telemetry endpoint returns valid data."""
        response = client.get('/api/telemetry')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'timestamp' in data
        assert 'battery_voltage' in data
        assert 'solar_current' in data
        assert 'temperature' in data
        assert 'mode' in data
        assert 'telemetry_id' in data
    
    def test_telemetry_data_types(self, client):
        """Test that telemetry data has correct types."""
        response = client.get('/api/telemetry')
        data = response.get_json()
        
        assert isinstance(data['battery_voltage'], (int, float))
        assert isinstance(data['solar_current'], (int, float))
        assert isinstance(data['temperature'], (int, float))
        assert isinstance(data['mode'], str)
        assert isinstance(data['telemetry_id'], int)


class TestAPIPasses:
    """Test /api/passes endpoint."""
    
    def test_passes_endpoint_default(self, client):
        """Test passes endpoint with default parameters."""
        response = client.get('/api/passes')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'prediction_time' in data
        assert 'time_range_hours' in data
        assert 'passes' in data
        assert data['time_range_hours'] == 24  # Default
    
    def test_passes_custom_hours(self, client):
        """Test passes endpoint with custom time range."""
        response = client.get('/api/passes?hours=12')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['time_range_hours'] == 12
    
    def test_passes_specific_station(self, client):
        """Test passes for a specific station."""
        response = client.get('/api/passes?station=Miami')
        assert response.status_code == 200
        
        data = response.get_json()
        passes = data['passes']
        assert 'Miami' in passes
        # Should only have Miami passes when filtered
    
    def test_passes_data_structure(self, client):
        """Test that pass data has correct structure."""
        response = client.get('/api/passes?hours=24')
        data = response.get_json()
        
        # Check that passes are organized by station
        passes = data['passes']
        for station_name, station_passes in passes.items():
            if len(station_passes) > 0:
                # Check structure of first pass
                first_pass = station_passes[0]
                assert 'aos' in first_pass
                assert 'los' in first_pass
                assert 'duration_min' in first_pass
                assert 'max_elevation' in first_pass
                assert 'aos_azimuth' in first_pass


class TestAPINetwork:
    """Test /api/network endpoint."""
    
    def test_network_endpoint(self, client):
        """Test network statistics endpoint."""
        response = client.get('/api/network')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'total_stations' in data
        assert 'stations' in data
        assert data['total_stations'] == 4
    
    def test_network_station_data(self, client):
        """Test that each station has correct data."""
        response = client.get('/api/network')
        data = response.get_json()
        
        stations = data['stations']
        assert len(stations) == 4
        
        for station in stations:
            assert 'name' in station
            assert 'location' in station
            assert 'packets_received' in station
            assert 'commands_sent' in station


class TestAPICommand:
    """Test /api/command endpoint."""
    
    def test_command_set_mode(self, client):
        """Test sending SET_MODE command."""
        command_data = {
            'command_type': 'SET_MODE',
            'mode': 'SCIENCE'
        }
        
        response = client.post('/api/command',
                               json=command_data,
                               content_type='application/json')
        
        # May succeed or fail depending on visibility, but should return valid JSON
        assert response.status_code in [200, 400]
        data = response.get_json()
        
        if response.status_code == 200:
            assert 'success' in data
            assert 'command_id' in data
            assert 'status' in data
    
    def test_command_reset_telemetry(self, client):
        """Test sending RESET_TELEMETRY command."""
        command_data = {
            'command_type': 'RESET_TELEMETRY'
        }
        
        response = client.post('/api/command',
                               json=command_data,
                               content_type='application/json')
        
        assert response.status_code in [200, 400]
        data = response.get_json()
        assert 'success' in data or 'error' in data
    
    def test_command_adjust_power(self, client):
        """Test sending ADJUST_POWER command."""
        command_data = {
            'command_type': 'ADJUST_POWER',
            'power_delta': 0.5
        }
        
        response = client.post('/api/command',
                               json=command_data,
                               content_type='application/json')
        
        assert response.status_code in [200, 400]
    
    def test_command_payload_on(self, client):
        """Test sending PAYLOAD_ON command."""
        command_data = {
            'command_type': 'PAYLOAD_ON'
        }
        
        response = client.post('/api/command',
                               json=command_data,
                               content_type='application/json')
        
        assert response.status_code in [200, 400]
    
    def test_command_missing_type(self, client):
        """Test that missing command_type returns error."""
        response = client.post('/api/command',
                               json={},
                               content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_command_invalid_type(self, client):
        """Test that invalid command type returns error."""
        command_data = {
            'command_type': 'INVALID_COMMAND'
        }
        
        response = client.post('/api/command',
                               json=command_data,
                               content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_invalid_endpoint(self, client):
        """Test that invalid endpoints return 404."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_command_wrong_method(self, client):
        """Test that GET request to command endpoint fails."""
        response = client.get('/api/command')
        assert response.status_code == 405  # Method Not Allowed
