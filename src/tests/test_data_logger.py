"""
Unit tests for DataLogger class
"""

import pytest
import sys
from pathlib import Path
import csv
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.data_logger import DataLogger


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir)


def test_data_logger_initialization(temp_output_dir):
    """Test DataLogger initialization."""
    logger = DataLogger(output_dir=temp_output_dir)
    
    assert logger.output_dir == Path(temp_output_dir)
    assert logger.telemetry_file is None
    assert logger.tracking_file is None


def test_create_telemetry_log(temp_output_dir):
    """Test creating a telemetry log file."""
    logger = DataLogger(output_dir=temp_output_dir)
    
    telemetry_file = logger.create_telemetry_log("TestSat", "20260502_120000")
    
    # Check file was created
    assert telemetry_file.exists()
    assert "telemetry_TestSat_20260502_120000.csv" in str(telemetry_file)
    
    # Check directory structure
    assert telemetry_file.parent.name == "telemetry"
    
    logger.close()


def test_create_tracking_log(temp_output_dir):
    """Test creating a tracking log file."""
    logger = DataLogger(output_dir=temp_output_dir)
    
    tracking_file = logger.create_tracking_log("TestSat", "20260502_120000")
    
    # Check file was created
    assert tracking_file.exists()
    assert "tracking_TestSat_20260502_120000.csv" in str(tracking_file)
    
    # Check directory structure
    assert tracking_file.parent.name == "tracking"
    
    logger.close()


def test_log_telemetry(temp_output_dir):
    """Test logging telemetry data."""
    logger = DataLogger(output_dir=temp_output_dir)
    logger.create_telemetry_log("TestSat", "test")
    
    # Log telemetry packet
    telemetry = {
        'timestamp': '2026-05-02T12:00:00Z',
        'battery_voltage': 28.5,
        'solar_current': 2.3,
        'temperature': 22.0,
        'mode': 'NOMINAL',
        'telemetry_id': 1
    }
    
    result = logger.log_telemetry(telemetry)
    assert result is True
    
    logger.close()
    
    # Read file and verify data was written
    with open(logger.telemetry_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['battery_voltage'] == '28.5'
        assert rows[0]['mode'] == 'NOMINAL'


def test_log_tracking(temp_output_dir):
    """Test logging tracking data."""
    logger = DataLogger(output_dir=temp_output_dir)
    logger.create_tracking_log("TestSat", "test")
    
    # Log tracking data
    tracking = {
        'timestamp': '2026-05-02T12:00:00Z',
        'azimuth_deg': 180.5,
        'elevation_deg': 45.2,
        'range_km': 500.3,
        'range_rate_km_s': -2.5,
        'is_visible': True
    }
    
    result = logger.log_tracking(tracking)
    assert result is True
    
    logger.close()
    
    # Read file and verify
    with open(logger.tracking_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['elevation_deg'] == '45.2'


def test_log_multiple_entries(temp_output_dir):
    """Test logging multiple telemetry entries."""
    logger = DataLogger(output_dir=temp_output_dir)
    logger.create_telemetry_log("TestSat", "test")
    
    # Log multiple packets
    for i in range(5):
        telemetry = {
            'timestamp': f'2026-05-02T12:00:{i:02d}Z',
            'battery_voltage': 28.0 + i * 0.1,
            'telemetry_id': i + 1
        }
        logger.log_telemetry(telemetry)
    
    logger.close()
    
    # Verify all entries were written
    with open(logger.telemetry_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 5


def test_log_without_create_raises_error(temp_output_dir):
    """Test that logging without creating file raises RuntimeError."""
    logger = DataLogger(output_dir=temp_output_dir)
    
    telemetry = {'timestamp': '2026-05-02T12:00:00Z'}
    
    with pytest.raises(RuntimeError):
        logger.log_telemetry(telemetry)
    
    logger.close()


def test_context_manager(temp_output_dir):
    """Test DataLogger as context manager."""
    with DataLogger(output_dir=temp_output_dir) as logger:
        logger.create_telemetry_log("TestSat", "test")
        logger.log_telemetry({'timestamp': '2026-05-02T12:00:00Z'})
    
    # File should be closed after context exit
    # This is verified by being able to read the file
    assert logger.telemetry_file.exists()


def test_csv_headers(temp_output_dir):
    """Test that CSV files have correct headers."""
    logger = DataLogger(output_dir=temp_output_dir)
    
    # Create telemetry log
    logger.create_telemetry_log("TestSat", "test")
    logger.close()
    
    # Check headers
    with open(logger.telemetry_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        expected_headers = [
            'timestamp', 'reception_time', 'ground_station', 'telemetry_id',
            'battery_voltage', 'solar_current', 'temperature', 'mode',
            'azimuth', 'elevation', 'range_km', 'range_rate_km_s'
        ]
        
        assert headers == expected_headers


def test_log_combined(temp_output_dir):
    """Test logging combined telemetry and tracking data."""
    logger = DataLogger(output_dir=temp_output_dir)
    logger.create_telemetry_log("TestSat", "test")
    
    telemetry = {
        'timestamp': '2026-05-02T12:00:00Z',
        'battery_voltage': 28.5,
        'temperature': 22.0
    }
    
    tracking = {
        'azimuth': 180.0,
        'elevation': 45.0,
        'range_km': 500.0
    }
    
    result = logger.log_combined(telemetry, tracking)
    assert result is True
    
    logger.close()
    
    # Verify combined data
    with open(logger.telemetry_file, 'r') as f:
        reader = csv.DictReader(f)
        row = next(reader)
        assert row['battery_voltage'] == '28.5'
        assert row['azimuth'] == '180.0'
        assert row['elevation'] == '45.0'


def test_close_idempotent(temp_output_dir):
    """Test that close() can be called multiple times safely."""
    logger = DataLogger(output_dir=temp_output_dir)
    logger.create_telemetry_log("TestSat", "test")
    
    # Close multiple times should not raise error
    logger.close()
    logger.close()
    logger.close()
