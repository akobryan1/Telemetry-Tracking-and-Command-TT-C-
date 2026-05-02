"""
Ground Station Network Module - Multi-Station Management for TT&C Simulation

This module defines the GroundStationNetwork class that manages multiple
ground stations, tracks visibility, and handles station hand-offs.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from .ground_station import GroundStation
from .satellite import Satellite
from .command import Command


class GroundStationNetwork:
    """
    Manages a network of ground stations for satellite tracking and communication.
    
    The network tracks which stations have visibility to satellites, manages
    hand-offs between stations, and coordinates telemetry reception and command
    uplink across the network.
    
    Attributes:
        stations (List[GroundStation]): List of ground stations in the network
        active_station (Optional[GroundStation]): Currently active station
        handoff_history (List[Dict]): Record of station hand-offs
    """
    
    def __init__(self, stations: Optional[List[GroundStation]] = None):
        """
        Initialize a ground station network.
        
        Args:
            stations: List of GroundStation objects (default: empty list)
        """
        self.stations: List[GroundStation] = stations or []
        self.active_station: Optional[GroundStation] = None
        self.handoff_history: List[Dict[str, Any]] = []
        self._visibility_status: Dict[str, bool] = {station.name: False for station in self.stations}
        
    def add_station(self, station: GroundStation) -> None:
        """
        Add a ground station to the network.
        
        Args:
            station: GroundStation object to add
        """
        if station not in self.stations:
            self.stations.append(station)
            self._visibility_status[station.name] = False
    
    def remove_station(self, station_name: str) -> bool:
        """
        Remove a ground station from the network.
        
        Args:
            station_name: Name of the station to remove
            
        Returns:
            True if station was removed, False if not found
        """
        for station in self.stations:
            if station.name == station_name:
                self.stations.remove(station)
                if self.active_station == station:
                    self.active_station = None
                del self._visibility_status[station_name]
                return True
        return False
    
    def get_station(self, station_name: str) -> Optional[GroundStation]:
        """
        Get a ground station by name.
        
        Args:
            station_name: Name of the station to retrieve
            
        Returns:
            GroundStation object or None if not found
        """
        for station in self.stations:
            if station.name == station_name:
                return station
        return None
    
    def update_visibility(self, visibility_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Update visibility status for all stations.
        
        Args:
            visibility_data: Dictionary mapping station names to visibility info
                            e.g., {'Miami': {'is_visible': True, 'elevation': 45.0}, ...}
        """
        for station_name, vis_info in visibility_data.items():
            if station_name in self._visibility_status:
                self._visibility_status[station_name] = vis_info.get('is_visible', False)
    
    def get_visible_stations(self) -> List[GroundStation]:
        """
        Get all stations currently with visibility.
        
        Returns:
            List of GroundStation objects that have visibility
        """
        return [station for station in self.stations 
                if self._visibility_status.get(station.name, False)]
    
    def select_best_station(self, elevation_data: Dict[str, float]) -> Optional[GroundStation]:
        """
        Select the best station based on elevation angle.
        
        Selects the station with the highest elevation angle among visible stations.
        
        Args:
            elevation_data: Dictionary mapping station names to elevation angles
                           e.g., {'Miami': 45.0, 'Goldstone': 30.0}
        
        Returns:
            GroundStation with highest elevation, or None if no stations visible
        """
        visible_stations = self.get_visible_stations()
        
        if not visible_stations:
            return None
        
        # Find station with maximum elevation
        best_station = None
        max_elevation = -1.0
        
        for station in visible_stations:
            elevation = elevation_data.get(station.name, -1.0)
            if elevation > max_elevation:
                max_elevation = elevation
                best_station = station
        
        return best_station
    
    def handoff_station(self, new_station: GroundStation, timestamp: str, 
                       reason: str = "elevation") -> bool:
        """
        Perform a hand-off to a new active station.
        
        Args:
            new_station: The ground station to hand off to
            timestamp: ISO timestamp of the hand-off
            reason: Reason for hand-off (e.g., "elevation", "aos", "los")
        
        Returns:
            True if hand-off successful, False otherwise
        """
        if new_station not in self.stations:
            return False
        
        old_station = self.active_station
        self.active_station = new_station
        
        # Record hand-off
        handoff_record = {
            'timestamp': timestamp,
            'from_station': old_station.name if old_station else None,
            'to_station': new_station.name,
            'reason': reason
        }
        self.handoff_history.append(handoff_record)
        
        return True
    
    def clear_active_station(self, timestamp: str) -> None:
        """
        Clear the active station (e.g., after LOS from all stations).
        
        Args:
            timestamp: ISO timestamp when clearing active station
        """
        if self.active_station:
            handoff_record = {
                'timestamp': timestamp,
                'from_station': self.active_station.name,
                'to_station': None,
                'reason': 'los'
            }
            self.handoff_history.append(handoff_record)
            self.active_station = None
    
    def receive_telemetry(self, telemetry_packet: Dict[str, Any],
                         tracking_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Receive telemetry at the active station.
        
        Args:
            telemetry_packet: Dictionary containing telemetry data
            tracking_data: Optional tracking data (azimuth, elevation, range)
        
        Returns:
            True if successfully received, False if no active station
        """
        if not self.active_station:
            return False
        
        return self.active_station.receive_telemetry(telemetry_packet, tracking_data)
    
    def uplink_command(self, command: Command, uplink_time: str) -> bool:
        """
        Uplink a command via the active station.
        
        Args:
            command: Command object to uplink
            uplink_time: ISO timestamp of uplink
        
        Returns:
            True if successfully uplinked, False if no active station
        """
        if not self.active_station:
            return False
        
        return self.active_station.uplink_command(command, uplink_time)
    
    def get_network_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for the entire network.
        
        Returns:
            Dictionary with network statistics
        """
        total_packets = sum(station.packets_received for station in self.stations)
        total_commands = sum(station.commands_sent for station in self.stations)
        
        station_stats = []
        for station in self.stations:
            station_stats.append({
                'name': station.name,
                'location': f"({station.latitude:.4f}°, {station.longitude:.4f}°)",
                'packets_received': station.packets_received,
                'commands_sent': station.commands_sent,
                'currently_visible': self._visibility_status.get(station.name, False)
            })
        
        return {
            'total_stations': len(self.stations),
            'total_packets': total_packets,
            'total_commands': total_commands,
            'total_handoffs': len(self.handoff_history),
            'active_station': self.active_station.name if self.active_station else None,
            'stations': station_stats,
            'handoff_history': self.handoff_history
        }
    
    def get_handoff_summary(self) -> str:
        """
        Get a formatted summary of station hand-offs.
        
        Returns:
            Formatted string summarizing hand-offs
        """
        if not self.handoff_history:
            return "No hand-offs recorded"
        
        summary_lines = [f"\nStation Hand-offs ({len(self.handoff_history)} total):"]
        summary_lines.append("-" * 60)
        
        for i, handoff in enumerate(self.handoff_history, 1):
            from_station = handoff['from_station'] or 'None'
            to_station = handoff['to_station'] or 'None'
            summary_lines.append(
                f"  {i}. {handoff['timestamp']}: {from_station} → {to_station} "
                f"({handoff['reason']})"
            )
        
        return '\n'.join(summary_lines)
    
    def __repr__(self) -> str:
        """String representation of the network."""
        return (f"GroundStationNetwork(stations={len(self.stations)}, "
                f"active={self.active_station.name if self.active_station else 'None'})")
