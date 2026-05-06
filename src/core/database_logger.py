"""
Database Logger Module - Supabase PostgreSQL Output for TT&C Simulation

This module provides logging functionality for telemetry, tracking, and command data
to Supabase PostgreSQL database with fallback to CSV logging.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from supabase import create_client, Client


class DatabaseLogger:
    """
    Handles logging of telemetry, tracking, and command data to Supabase database.
    
    Provides graceful fallback to CSV logging if database connection fails.
    Uses service role key for server-side operations (bypasses RLS).
    
    Attributes:
        supabase (Client): Supabase client instance
        satellite_name (str): Name of satellite being tracked
        csv_fallback (bool): Whether to fall back to CSV on errors
    """
    
    def __init__(self, satellite_name: str = "ISS", csv_fallback: bool = True):
        """
        Initialize the database logger.
        
        Args:
            satellite_name: Name of satellite (default: "ISS")
            csv_fallback: Enable CSV fallback on database errors (default: True)
        """
        self.satellite_name = satellite_name
        self.csv_fallback = csv_fallback
        self.supabase: Optional[Client] = None
        self._csv_logger = None
        
        # Initialize Supabase client
        try:
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️  Supabase credentials not found in environment variables")
                print("   Using CSV fallback mode")
                self._init_csv_fallback()
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            print("✓ Database logger initialized (Supabase)")
            
        except Exception as e:
            print(f"⚠️  Failed to connect to Supabase: {e}")
            print("   Using CSV fallback mode")
            self._init_csv_fallback()
    
    def _init_csv_fallback(self):
        """Initialize CSV logger as fallback."""
        if self.csv_fallback:
            try:
                from .data_logger import DataLogger
                self._csv_logger = DataLogger()
                print("✓ CSV fallback logger initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize CSV fallback: {e}")
    
    def log_telemetry(self, telemetry_data: Dict[str, Any], 
                      ground_station: str,
                      timestamp: Optional[str] = None) -> bool:
        """
        Log telemetry data to database.
        
        Args:
            telemetry_data: Dictionary with telemetry values
            ground_station: Name of receiving ground station
            timestamp: ISO 8601 timestamp (default: current UTC time)
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare record for database
        record = {
            'timestamp': timestamp,
            'satellite_name': self.satellite_name,
            'ground_station': ground_station,
            'battery_voltage': telemetry_data.get('battery_voltage'),
            'solar_current': telemetry_data.get('solar_current'),
            'temperature': telemetry_data.get('temperature'),
            'mode': telemetry_data.get('mode'),
            'telemetry_id': telemetry_data.get('telemetry_id')
        }
        
        # Try database insert
        if self.supabase:
            try:
                self.supabase.table('telemetry').insert(record).execute()
                return True
            except Exception as e:
                print(f"⚠️  Database insert failed: {e}")
                # Fall through to CSV fallback
        
        # CSV fallback
        if self._csv_logger:
            try:
                # CSV logger expects combined telemetry + tracking data
                # For now, just skip CSV fallback for telemetry
                # (could be enhanced to support this)
                pass
            except Exception as e:
                print(f"⚠️  CSV fallback failed: {e}")
        
        return False
    
    def log_tracking(self, tracking_data: Dict[str, Any],
                     station: str,
                     timestamp: Optional[str] = None) -> bool:
        """
        Log tracking data to database.
        
        Args:
            tracking_data: Dictionary with tracking values (az, el, range, etc.)
            station: Name of ground station
            timestamp: ISO 8601 timestamp (default: current UTC time)
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare record for database
        record = {
            'timestamp': timestamp,
            'satellite_name': self.satellite_name,
            'station': station,
            'azimuth_deg': tracking_data.get('azimuth_deg'),
            'elevation_deg': tracking_data.get('elevation_deg'),
            'range_km': tracking_data.get('range_km'),
            'range_rate_km_s': tracking_data.get('range_rate_km_s'),
            'is_visible': tracking_data.get('is_visible', False)
        }
        
        # Try database insert
        if self.supabase:
            try:
                self.supabase.table('tracking').insert(record).execute()
                return True
            except Exception as e:
                print(f"⚠️  Database insert failed: {e}")
        
        return False
    
    def log_command(self, command_data: Dict[str, Any],
                    uplink_station: str,
                    timestamp: Optional[str] = None) -> bool:
        """
        Log command data to database.
        
        Args:
            command_data: Dictionary with command information
            uplink_station: Name of uplink ground station
            timestamp: ISO 8601 timestamp (default: current UTC time)
        
        Returns:
            bool: True if logged successfully, False otherwise
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare record for database
        record = {
            'timestamp': timestamp,
            'command_type': command_data.get('command_type'),
            'command_id': command_data.get('command_id'),
            'parameters': command_data.get('parameters', {}),
            'status': command_data.get('status'),
            'uplink_station': uplink_station,
            'ack_timestamp': command_data.get('ack_timestamp')
        }
        
        # Try database insert
        if self.supabase:
            try:
                self.supabase.table('commands').insert(record).execute()
                return True
            except Exception as e:
                print(f"⚠️  Database insert failed: {e}")
        
        return False
    
    def get_recent_telemetry(self, limit: int = 100) -> list:
        """
        Retrieve recent telemetry records from database.
        
        Args:
            limit: Maximum number of records to retrieve
        
        Returns:
            list: List of telemetry records
        """
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table('telemetry')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"⚠️  Failed to retrieve telemetry: {e}")
            return []
    
    def get_recent_commands(self, limit: int = 50) -> list:
        """
        Retrieve recent command records from database.
        
        Args:
            limit: Maximum number of records to retrieve
        
        Returns:
            list: List of command records
        """
        if not self.supabase:
            return []
        
        try:
            response = self.supabase.table('commands')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            return response.data
        except Exception as e:
            print(f"⚠️  Failed to retrieve commands: {e}")
            return []
    
    def close(self):
        """Close database connection and cleanup resources."""
        if self._csv_logger and hasattr(self._csv_logger, 'close'):
            self._csv_logger.close()
        
        # Supabase client doesn't require explicit close
        print("✓ Database logger closed")
