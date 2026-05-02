"""
Data Logger Module - CSV Output for TT&C Simulation

This module provides logging functionality for telemetry and tracking data.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DataLogger:
    """
    Handles logging of telemetry and tracking data to CSV files.
    
    Supports separate logging of:
    - Telemetry data (battery, temperature, mode, etc.)
    - Tracking data (azimuth, elevation, range, etc.)
    - Combined telemetry + tracking data
    
    Attributes:
        output_dir (Path): Directory for output files
        telemetry_file (Optional[Path]): Path to telemetry CSV file
        tracking_file (Optional[Path]): Path to tracking CSV file
    """
    
    def __init__(self, output_dir: str = "data/outputs"):
        """
        Initialize the data logger.
        
        Args:
            output_dir: Base directory for output files (default: "data/outputs")
        """
        self.output_dir = Path(output_dir)
        self.telemetry_file: Optional[Path] = None
        self.tracking_file: Optional[Path] = None
        self.command_file: Optional[Path] = None
        
        self._telemetry_writer: Optional[csv.DictWriter] = None
        self._tracking_writer: Optional[csv.DictWriter] = None
        self._command_writer: Optional[csv.DictWriter] = None
        self._telemetry_fp = None
        self._tracking_fp = None
        self._command_fp = None
        
    def create_telemetry_log(self, satellite_name: str, 
                            timestamp: Optional[str] = None) -> Path:
        """
        Create a new telemetry log file.
        
        Args:
            satellite_name: Name of satellite for filename
            timestamp: Optional timestamp string (default: current time)
        
        Returns:
            Path to created telemetry file
        """
        if timestamp is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create telemetry subdirectory
        telemetry_dir = self.output_dir / "telemetry"
        telemetry_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"telemetry_{satellite_name}_{timestamp}.csv"
        self.telemetry_file = telemetry_dir / filename
        
        # Open file and create CSV writer
        self._telemetry_fp = open(self.telemetry_file, 'w', newline='')
        
        # Define columns
        fieldnames = [
            'timestamp',
            'reception_time',
            'ground_station',
            'telemetry_id',
            'battery_voltage',
            'solar_current',
            'temperature',
            'mode',
            'azimuth',
            'elevation',
            'range_km',
            'range_rate_km_s'
        ]
        
        self._telemetry_writer = csv.DictWriter(
            self._telemetry_fp, 
            fieldnames=fieldnames,
            extrasaction='ignore'
        )
        self._telemetry_writer.writeheader()
        
        return self.telemetry_file
    
    def create_tracking_log(self, satellite_name: str,
                           timestamp: Optional[str] = None) -> Path:
        """
        Create a new tracking data log file.
        
        Args:
            satellite_name: Name of satellite for filename
            timestamp: Optional timestamp string (default: current time)
        
        Returns:
            Path to created tracking file
        """
        if timestamp is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create tracking subdirectory
        tracking_dir = self.output_dir / "tracking"
        tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"tracking_{satellite_name}_{timestamp}.csv"
        self.tracking_file = tracking_dir / filename
        
        # Open file and create CSV writer
        self._tracking_fp = open(self.tracking_file, 'w', newline='')
        
        # Define columns
        fieldnames = [
            'timestamp',
            'azimuth_deg',
            'elevation_deg',
            'range_km',
            'range_rate_km_s',
            'is_visible'
        ]
        
        self._tracking_writer = csv.DictWriter(
            self._tracking_fp,
            fieldnames=fieldnames,
            extrasaction='ignore'
        )
        self._tracking_writer.writeheader()
        
        return self.tracking_file
    
    def create_command_log(self, satellite_name: str,
                          timestamp: Optional[str] = None) -> Path:
        """
        Create a new command log file.
        
        Args:
            satellite_name: Name of satellite for filename
            timestamp: Optional timestamp string (default: current time)
        
        Returns:
            Path to created command file
        """
        if timestamp is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create command subdirectory
        command_dir = self.output_dir / "commands"
        command_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"commands_{satellite_name}_{timestamp}.csv"
        self.command_file = command_dir / filename
        
        # Open file and create CSV writer
        self._command_fp = open(self.command_file, 'w', newline='')
        
        # Define columns
        fieldnames = [
            'command_id',
            'command_type',
            'parameters',
            'timestamp',
            'uplink_time',
            'execution_time',
            'status',
            'acknowledgment'
        ]
        
        self._command_writer = csv.DictWriter(
            self._command_fp,
            fieldnames=fieldnames,
            extrasaction='ignore'
        )
        self._command_writer.writeheader()
        
        return self.command_file
    
    def log_command(self, command_data: Dict[str, Any]) -> bool:
        """
        Write a command to the log file.
        
        Args:
            command_data: Dictionary containing command data
        
        Returns:
            True if successfully logged
        
        Raises:
            RuntimeError: If command log file not created
        """
        if self._command_writer is None:
            raise RuntimeError("Command log file not created. Call create_command_log() first.")
        
        # Convert parameters dict to string for CSV
        if 'parameters' in command_data and isinstance(command_data['parameters'], dict):
            command_data = command_data.copy()
            command_data['parameters'] = str(command_data['parameters'])
        
        self._command_writer.writerow(command_data)
        self._command_fp.flush()  # Ensure data is written
        
        return True
    
    def log_telemetry(self, telemetry_packet: Dict[str, Any]) -> bool:
        """
        Write a telemetry packet to the log file.
        
        Args:
            telemetry_packet: Dictionary containing telemetry data
        
        Returns:
            True if successfully logged
        
        Raises:
            RuntimeError: If telemetry log file not created
        """
        if self._telemetry_writer is None:
            raise RuntimeError("Telemetry log file not created. Call create_telemetry_log() first.")
        
        self._telemetry_writer.writerow(telemetry_packet)
        self._telemetry_fp.flush()  # Ensure data is written
        
        return True
    
    def log_tracking(self, tracking_data: Dict[str, Any]) -> bool:
        """
        Write tracking data to the log file.
        
        Args:
            tracking_data: Dictionary containing tracking data
        
        Returns:
            True if successfully logged
        
        Raises:
            RuntimeError: If tracking log file not created
        """
        if self._tracking_writer is None:
            raise RuntimeError("Tracking log file not created. Call create_tracking_log() first.")
        
        self._tracking_writer.writerow(tracking_data)
        self._tracking_fp.flush()  # Ensure data is written
        
        return True
    
    def log_combined(self, telemetry_packet: Dict[str, Any],
                    tracking_data: Dict[str, Any]) -> bool:
        """
        Write combined telemetry and tracking data.
        
        This merges both dictionaries and writes to telemetry log.
        
        Args:
            telemetry_packet: Telemetry data dictionary
            tracking_data: Tracking data dictionary
        
        Returns:
            True if successfully logged
        """
        combined = {**telemetry_packet, **tracking_data}
        return self.log_telemetry(combined)
    
    def close(self):
        """Close all open log files."""
        if self._telemetry_fp:
            self._telemetry_fp.close()
            self._telemetry_fp = None
            self._telemetry_writer = None
        
        if self._tracking_fp:
            self._tracking_fp.close()
            self._tracking_fp = None
            self._tracking_writer = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures files are closed."""
        self.close()
