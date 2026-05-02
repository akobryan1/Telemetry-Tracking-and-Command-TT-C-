"""
Satellite Module - Telemetry Generation for TT&C Simulation

This module defines the Satellite class that simulates spacecraft telemetry
including battery voltage, solar current, temperature, and operational modes.
"""

import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import numpy as np
from .command import Command, CommandType, CommandStatus


class Satellite:
    """
    Represents a satellite with simulated telemetry generation.
    
    The satellite generates realistic telemetry data including:
    - Battery voltage (26-30V typical for spacecraft)
    - Solar array current (0-3A depending on sunlight)
    - Temperature (-10 to +40°C with orbital variation)
    - Operational mode (SAFE, NOMINAL, SCIENCE)
    
    Attributes:
        name (str): Satellite identifier
        battery_voltage (float): Current battery voltage in volts
        temperature (float): Current temperature in Celsius
        mode (str): Current operational mode
        telemetry_count (int): Number of telemetry packets generated
    """
    
    # Operational modes
    MODE_SAFE = "SAFE"
    MODE_NOMINAL = "NOMINAL"
    MODE_SCIENCE = "SCIENCE"
    
    def __init__(self, name: str, initial_battery_voltage: float = 28.0,
                 initial_temperature: float = 20.0, initial_mode: str = "NOMINAL"):
        """
        Initialize a satellite with default telemetry state.
        
        Args:
            name: Satellite identifier (e.g., "ISS", "GOES-16")
            initial_battery_voltage: Starting battery voltage in volts (default: 28.0)
            initial_temperature: Starting temperature in Celsius (default: 20.0)
            initial_mode: Starting operational mode (default: "NOMINAL")
        """
        self.name = name
        self.battery_voltage = initial_battery_voltage
        self.temperature = initial_temperature
        self.mode = initial_mode
        self.telemetry_count = 0
        
        # Command processing
        self.command_queue: List[Command] = []
        self.command_history: List[Command] = []
        
        # Internal state for realistic simulation
        self._battery_drain_rate = 0.001  # V per telemetry cycle
        self._solar_charging_rate = 0.002  # V per telemetry cycle when sunlit
        self._temp_drift = 0.0  # Temperature drift accumulator
        
    def generate_telemetry(self, is_sunlit: bool = True, 
                          time_step_seconds: float = 10.0) -> Dict[str, Any]:
        """
        Generate a telemetry packet with simulated sensor values.
        
        This simulates realistic spacecraft behavior:
        - Battery drains slowly, charges when solar arrays in sun
        - Temperature varies with orbital period (~90 min for LEO)
        - Solar current depends on sun illumination
        - Mode transitions based on battery level
        
        Args:
            is_sunlit: Whether satellite is in sunlight (affects solar current)
            time_step_seconds: Time since last telemetry (for drift calculations)
        
        Returns:
            Dictionary containing:
                - timestamp: ISO format timestamp
                - battery_voltage: Battery voltage in volts
                - solar_current: Solar array current in amperes
                - temperature: Spacecraft temperature in Celsius
                - mode: Operational mode string
                - telemetry_id: Sequential packet counter
        """
        self.telemetry_count += 1
        
        # Update battery voltage (charge in sun, drain in eclipse)
        if is_sunlit:
            self.battery_voltage += self._solar_charging_rate
            self.battery_voltage = min(self.battery_voltage, 30.0)  # Max voltage
        else:
            self.battery_voltage -= self._battery_drain_rate
            self.battery_voltage = max(self.battery_voltage, 26.0)  # Min safe voltage
        
        # Add small random variation
        battery_noise = random.uniform(-0.05, 0.05)
        
        # Calculate solar current (0 in eclipse, 2-3A in sunlight with variation)
        if is_sunlit:
            solar_current = 2.5 + random.uniform(-0.3, 0.5)
        else:
            solar_current = 0.0 + random.uniform(-0.01, 0.01)  # Minimal noise
        
        # Simulate temperature variation
        # LEO orbital period ~90 min = 5400 sec, so full cycle every ~540 telemetry packets (10s steps)
        orbital_temp_variation = 15.0 * np.sin(2 * np.pi * self.telemetry_count / 540)
        self._temp_drift += random.uniform(-0.1, 0.1)  # Random walk
        self._temp_drift = max(-5.0, min(5.0, self._temp_drift))  # Limit drift
        
        self.temperature = 20.0 + orbital_temp_variation + self._temp_drift
        
        # Determine operational mode based on battery voltage
        if self.battery_voltage < 26.5:
            self.mode = self.MODE_SAFE
        elif self.battery_voltage > 28.5:
            self.mode = self.MODE_SCIENCE
        else:
            self.mode = self.MODE_NOMINAL
        
        # Build telemetry packet
        telemetry_packet = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'battery_voltage': round(self.battery_voltage + battery_noise, 2),
            'solar_current': round(solar_current, 2),
            'temperature': round(self.temperature, 1),
            'mode': self.mode,
            'telemetry_id': self.telemetry_count
        }
        
        return telemetry_packet
    
    def reset_telemetry_count(self):
        """Reset the telemetry packet counter to zero."""
        self.telemetry_count = 0
    
    def set_mode(self, mode: str):
        """
        Manually set the operational mode.
        
        Args:
            mode: One of MODE_SAFE, MODE_NOMINAL, or MODE_SCIENCE
        
        Raises:
            ValueError: If mode is not a valid mode string
        """
        valid_modes = [self.MODE_SAFE, self.MODE_NOMINAL, self.MODE_SCIENCE]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {valid_modes}")
        self.mode = mode
    
    def receive_command(self, command: Command) -> bool:
        """
        Receive a command from ground station.
        
        Args:
            command: Command object to queue for execution
        
        Returns:
            True if command accepted
        """
        self.command_queue.append(command)
        return True
    
    def process_commands(self, simulation_time: Optional[str] = None) -> List[Command]:
        """
        Process all pending commands in the queue.
        
        Args:
            simulation_time: Current simulation time for logging
        
        Returns:
            List of processed commands with updated status
        """
        processed = []
        
        while self.command_queue:
            cmd = self.command_queue.pop(0)
            
            # Execute command based on type
            try:
                if cmd.command_type == CommandType.SET_MODE:
                    mode = cmd.parameters.get('mode')
                    self.set_mode(mode)
                    cmd.mark_success(f"Mode set to {mode}", simulation_time)
                
                elif cmd.command_type == CommandType.RESET_TELEMETRY:
                    self.reset_telemetry_count()
                    cmd.mark_success("Telemetry counter reset", simulation_time)
                
                elif cmd.command_type == CommandType.ADJUST_POWER:
                    power_delta = cmd.parameters.get('power_delta', 0)
                    self.battery_voltage += power_delta
                    self.battery_voltage = max(26.0, min(30.0, self.battery_voltage))
                    cmd.mark_success(f"Battery adjusted by {power_delta}V to {self.battery_voltage:.2f}V", 
                                   simulation_time)
                
                elif cmd.command_type == CommandType.PAYLOAD_ON:
                    cmd.mark_success("Payload activated", simulation_time)
                
                elif cmd.command_type == CommandType.PAYLOAD_OFF:
                    cmd.mark_success("Payload deactivated", simulation_time)
                
                elif cmd.command_type == CommandType.REBOOT:
                    self.telemetry_count = 0
                    cmd.mark_success("Satellite rebooted", simulation_time)
                
                else:
                    cmd.mark_failed(f"Unknown command type: {cmd.command_type}", simulation_time)
            
            except Exception as e:
                cmd.mark_failed(str(e), simulation_time)
            
            self.command_history.append(cmd)
            processed.append(cmd)
        
        return processed
    
    def get_command_history(self) -> List[Command]:
        """
        Get the command execution history.
        
        Returns:
            List of all executed commands
        """
        return self.command_history.copy()
    
    def get_status_summary(self) -> str:
        """
        Get a human-readable status summary.
        
        Returns:
            Formatted string with current satellite state
        """
        return (f"Satellite: {self.name}\n"
                f"  Battery: {self.battery_voltage:.2f}V\n"
                f"  Temperature: {self.temperature:.1f}°C\n"
                f"  Mode: {self.mode}\n"
                f"  Telemetry Packets: {self.telemetry_count}\n"
                f"  Commands Executed: {len(self.command_history)}\n"
                f"  Commands Pending: {len(self.command_queue)}")
