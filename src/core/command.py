"""
Command Module - Command Uplink for TT&C Simulation

This module defines command types and command execution for satellite control.
"""

from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class CommandType(Enum):
    """Enumeration of available command types."""
    SET_MODE = "SET_MODE"
    RESET_TELEMETRY = "RESET_TELEMETRY"
    ADJUST_POWER = "ADJUST_POWER"
    REBOOT = "REBOOT"
    PAYLOAD_ON = "PAYLOAD_ON"
    PAYLOAD_OFF = "PAYLOAD_OFF"


class CommandStatus(Enum):
    """Enumeration of command execution statuses."""
    PENDING = "PENDING"
    EXECUTING = "EXECUTING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class Command:
    """
    Represents a command to be sent to a satellite.
    
    Commands have a type, parameters, and execution status tracking.
    
    Attributes:
        command_id (int): Unique command identifier
        command_type (CommandType): Type of command
        parameters (Dict): Command-specific parameters
        status (CommandStatus): Current execution status
        timestamp (str): ISO timestamp when command was created
        uplink_time (Optional[str]): When command was uplinked
        execution_time (Optional[str]): When command was executed
        acknowledgment (Optional[str]): Execution result message
    """
    
    _next_id = 1  # Class variable for auto-incrementing IDs
    
    def __init__(self, command_type: CommandType, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize a command.
        
        Args:
            command_type: Type of command to execute
            parameters: Optional dictionary of command parameters
        """
        self.command_id = Command._next_id
        Command._next_id += 1
        
        self.command_type = command_type
        self.parameters = parameters or {}
        self.status = CommandStatus.PENDING
        
        self.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.uplink_time: Optional[str] = None
        self.execution_time: Optional[str] = None
        self.acknowledgment: Optional[str] = None
    
    def mark_uplinked(self, uplink_time: Optional[str] = None):
        """
        Mark command as uplinked to satellite.
        
        Args:
            uplink_time: ISO timestamp of uplink (default: current time)
        """
        if uplink_time is None:
            uplink_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.uplink_time = uplink_time
        self.status = CommandStatus.EXECUTING
    
    def mark_success(self, acknowledgment: str = "Command executed successfully", 
                     execution_time: Optional[str] = None):
        """
        Mark command as successfully executed.
        
        Args:
            acknowledgment: Success message
            execution_time: ISO timestamp of execution (default: current time)
        """
        if execution_time is None:
            execution_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.execution_time = execution_time
        self.status = CommandStatus.SUCCESS
        self.acknowledgment = acknowledgment
    
    def mark_failed(self, error_message: str, execution_time: Optional[str] = None):
        """
        Mark command as failed.
        
        Args:
            error_message: Failure reason
            execution_time: ISO timestamp of failure (default: current time)
        """
        if execution_time is None:
            execution_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        self.execution_time = execution_time
        self.status = CommandStatus.FAILED
        self.acknowledgment = f"FAILED: {error_message}"
    
    def mark_rejected(self, reason: str):
        """
        Mark command as rejected (not executed).
        
        Args:
            reason: Rejection reason
        """
        self.status = CommandStatus.REJECTED
        self.acknowledgment = f"REJECTED: {reason}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to dictionary for logging.
        
        Returns:
            Dictionary representation of command
        """
        return {
            'command_id': self.command_id,
            'command_type': self.command_type.value,
            'parameters': self.parameters,
            'status': self.status.value,
            'timestamp': self.timestamp,
            'uplink_time': self.uplink_time,
            'execution_time': self.execution_time,
            'acknowledgment': self.acknowledgment
        }
    
    def __str__(self) -> str:
        """String representation of command."""
        params_str = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return (f"CMD#{self.command_id} {self.command_type.value}({params_str}) "
                f"[{self.status.value}]")


def create_set_mode_command(mode: str) -> Command:
    """
    Create a SET_MODE command.
    
    Args:
        mode: Target operational mode (SAFE, NOMINAL, SCIENCE)
    
    Returns:
        Command object
    """
    return Command(CommandType.SET_MODE, {'mode': mode})


def create_reset_telemetry_command() -> Command:
    """
    Create a RESET_TELEMETRY command.
    
    Returns:
        Command object
    """
    return Command(CommandType.RESET_TELEMETRY)


def create_adjust_power_command(power_delta: float) -> Command:
    """
    Create an ADJUST_POWER command.
    
    Args:
        power_delta: Voltage adjustment in volts (positive or negative)
    
    Returns:
        Command object
    """
    return Command(CommandType.ADJUST_POWER, {'power_delta': power_delta})


def create_payload_command(payload_on: bool) -> Command:
    """
    Create a PAYLOAD_ON or PAYLOAD_OFF command.
    
    Args:
        payload_on: True for PAYLOAD_ON, False for PAYLOAD_OFF
    
    Returns:
        Command object
    """
    cmd_type = CommandType.PAYLOAD_ON if payload_on else CommandType.PAYLOAD_OFF
    return Command(cmd_type)
