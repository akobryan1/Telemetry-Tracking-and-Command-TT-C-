"""
Ground Station Module - Data Reception for TT&C Simulation

This module defines the GroundStation class that receives telemetry
from satellites during visibility windows.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .command import Command


class GroundStation:
    """
    Represents a ground station that receives satellite telemetry.
    
    The ground station maintains a buffer of received telemetry packets
    and provides methods for data retrieval and statistics.
    
    Attributes:
        name (str): Ground station identifier
        latitude (float): Latitude in degrees
        longitude (float): Longitude in degrees
        altitude_m (float): Altitude above sea level in meters
        min_elevation (float): Minimum elevation angle for communications (degrees)
        telemetry_buffer (List[Dict]): Received telemetry packets
        packets_received (int): Total count of received packets
    """
    
    def __init__(self, name: str, latitude: float, longitude: float,
                 altitude_m: float = 0.0, min_elevation: float = 10.0):
        """
        Initialize a ground station.
        
        Args:
            name: Station identifier (e.g., "Miami", "Goldstone")
            latitude: Latitude in decimal degrees (-90 to +90)
            longitude: Longitude in decimal degrees (-180 to +180)
            altitude_m: Altitude above sea level in meters (default: 0)
            min_elevation: Minimum elevation angle in degrees (default: 10)
        """
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.altitude_m = altitude_m
        self.min_elevation = min_elevation
        
        self.telemetry_buffer: List[Dict[str, Any]] = []
        self.packets_received = 0
        self._current_pass_packets: List[Dict[str, Any]] = []
        
        # Command uplink
        self.command_buffer: List[Command] = []
        self.commands_sent = 0
        
    def receive_telemetry(self, telemetry_packet: Dict[str, Any],
                         tracking_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Receive and store a telemetry packet from a satellite.
        
        Args:
            telemetry_packet: Dictionary containing telemetry data
            tracking_data: Optional dictionary with azimuth, elevation, range
        
        Returns:
            True if packet successfully received
        """
        # Create combined data packet
        packet = {
            'reception_time': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'ground_station': self.name,
            **telemetry_packet
        }
        
        # Add tracking data if provided
        if tracking_data:
            packet.update({
                'azimuth': tracking_data.get('azimuth'),
                'elevation': tracking_data.get('elevation'),
                'range_km': tracking_data.get('range_km'),
                'range_rate_km_s': tracking_data.get('range_rate_km_s')
            })
        
        self.telemetry_buffer.append(packet)
        self._current_pass_packets.append(packet)
        self.packets_received += 1
        
        return True
    
    def get_telemetry_buffer(self, clear_after_read: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve all telemetry packets from the buffer.
        
        Args:
            clear_after_read: If True, clear buffer after reading (default: False)
        
        Returns:
            List of telemetry packet dictionaries
        """
        packets = self.telemetry_buffer.copy()
        
        if clear_after_read:
            self.telemetry_buffer.clear()
        
        return packets
    
    def get_current_pass_packets(self) -> List[Dict[str, Any]]:
        """
        Get telemetry packets from the current pass.
        
        Returns:
            List of packets received during current pass
        """
        return self._current_pass_packets.copy()
    
    def start_new_pass(self):
        """Mark the start of a new satellite pass."""
        self._current_pass_packets = []
    
    def end_pass(self) -> Dict[str, Any]:
        """
        Mark the end of a satellite pass and return statistics.
        
        Returns:
            Dictionary with pass statistics (packet count, duration, etc.)
        """
        packet_count = len(self._current_pass_packets)
        
        stats = {
            'packets_received': packet_count,
            'pass_complete': True
        }
        
        if packet_count > 0:
            first_packet = self._current_pass_packets[0]
            last_packet = self._current_pass_packets[-1]
            
            stats['first_packet_time'] = first_packet.get('timestamp')
            stats['last_packet_time'] = last_packet.get('timestamp')
        
        return stats
    
    def clear_buffer(self):
        """Clear all telemetry from the buffer."""
        self.telemetry_buffer.clear()
        self._current_pass_packets.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get ground station statistics.
        
        Returns:
            Dictionary with statistics including total packets received
        """
        return {
            'station_name': self.name,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'altitude_m': self.altitude_m
            },
            'total_packets_received': self.packets_received,
            'buffer_size': len(self.telemetry_buffer),
            'min_elevation': self.min_elevation
        }
    
    def uplink_command(self, command: Command, uplink_time: Optional[str] = None) -> bool:
        """
        Uplink a command to the satellite.
        
        Args:
            command: Command object to send
            uplink_time: Optional timestamp for uplink (default: current time)
        
        Returns:
            True if command successfully queued for uplink
        """
        command.mark_uplinked(uplink_time)
        self.command_buffer.append(command)
        self.commands_sent += 1
        return True
    
    def get_command_buffer(self, clear_after_read: bool = True) -> List[Command]:
        """
        Retrieve commands to be sent to satellite.
        
        Args:
            clear_after_read: If True, clear buffer after reading (default: True)
        
        Returns:
            List of commands to uplink
        """
        commands = self.command_buffer.copy()
        
        if clear_after_read:
            self.command_buffer.clear()
        
        return commands
    
    def __str__(self) -> str:
        """String representation of the ground station."""
        return (f"GroundStation(name='{self.name}', "
                f"lat={self.latitude:.4f}°, lon={self.longitude:.4f}°, "
                f"packets={self.packets_received}, commands={self.commands_sent})")
