"""
Unit tests for Command class
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.command import (
    Command,
    CommandType,
    CommandStatus,
    create_set_mode_command,
    create_reset_telemetry_command,
    create_adjust_power_command,
    create_payload_command
)


def test_command_initialization():
    """Test command initialization."""
    cmd = Command(CommandType.SET_MODE, {'mode': 'SCIENCE'})
    
    assert cmd.command_type == CommandType.SET_MODE
    assert cmd.parameters == {'mode': 'SCIENCE'}
    assert cmd.status == CommandStatus.PENDING
    assert cmd.command_id > 0
    assert cmd.uplink_time is None
    assert cmd.execution_time is None


def test_command_id_increment():
    """Test that command IDs auto-increment."""
    cmd1 = Command(CommandType.SET_MODE)
    cmd2 = Command(CommandType.RESET_TELEMETRY)
    
    assert cmd2.command_id > cmd1.command_id


def test_mark_uplinked():
    """Test marking command as uplinked."""
    cmd = Command(CommandType.PAYLOAD_ON)
    
    cmd.mark_uplinked("2026-05-02T12:00:00Z")
    
    assert cmd.uplink_time == "2026-05-02T12:00:00Z"
    assert cmd.status == CommandStatus.EXECUTING


def test_mark_success():
    """Test marking command as successful."""
    cmd = Command(CommandType.SET_MODE, {'mode': 'NOMINAL'})
    
    cmd.mark_success("Mode changed successfully", "2026-05-02T12:01:00Z")
    
    assert cmd.status == CommandStatus.SUCCESS
    assert cmd.acknowledgment == "Mode changed successfully"
    assert cmd.execution_time == "2026-05-02T12:01:00Z"


def test_mark_failed():
    """Test marking command as failed."""
    cmd = Command(CommandType.ADJUST_POWER)
    
    cmd.mark_failed("Invalid power value", "2026-05-02T12:02:00Z")
    
    assert cmd.status == CommandStatus.FAILED
    assert "FAILED" in cmd.acknowledgment
    assert "Invalid power value" in cmd.acknowledgment
    assert cmd.execution_time == "2026-05-02T12:02:00Z"


def test_mark_rejected():
    """Test marking command as rejected."""
    cmd = Command(CommandType.REBOOT)
    
    cmd.mark_rejected("Satellite in safe mode")
    
    assert cmd.status == CommandStatus.REJECTED
    assert "REJECTED" in cmd.acknowledgment
    assert "Satellite in safe mode" in cmd.acknowledgment


def test_to_dict():
    """Test converting command to dictionary."""
    cmd = Command(CommandType.SET_MODE, {'mode': 'SCIENCE'})
    cmd.mark_uplinked("2026-05-02T12:00:00Z")
    cmd.mark_success("Success", "2026-05-02T12:00:10Z")
    
    cmd_dict = cmd.to_dict()
    
    assert cmd_dict['command_type'] == 'SET_MODE'
    assert cmd_dict['parameters'] == {'mode': 'SCIENCE'}
    assert cmd_dict['status'] == 'SUCCESS'
    assert cmd_dict['uplink_time'] == "2026-05-02T12:00:00Z"
    assert cmd_dict['execution_time'] == "2026-05-02T12:00:10Z"


def test_create_set_mode_command():
    """Test set mode command factory."""
    cmd = create_set_mode_command("SCIENCE")
    
    assert cmd.command_type == CommandType.SET_MODE
    assert cmd.parameters['mode'] == "SCIENCE"


def test_create_reset_telemetry_command():
    """Test reset telemetry command factory."""
    cmd = create_reset_telemetry_command()
    
    assert cmd.command_type == CommandType.RESET_TELEMETRY
    assert cmd.parameters == {}


def test_create_adjust_power_command():
    """Test adjust power command factory."""
    cmd = create_adjust_power_command(0.5)
    
    assert cmd.command_type == CommandType.ADJUST_POWER
    assert cmd.parameters['power_delta'] == 0.5


def test_create_payload_on_command():
    """Test payload ON command factory."""
    cmd = create_payload_command(True)
    
    assert cmd.command_type == CommandType.PAYLOAD_ON


def test_create_payload_off_command():
    """Test payload OFF command factory."""
    cmd = create_payload_command(False)
    
    assert cmd.command_type == CommandType.PAYLOAD_OFF


def test_command_str_representation():
    """Test command string representation."""
    cmd = Command(CommandType.SET_MODE, {'mode': 'SCIENCE'})
    cmd_str = str(cmd)
    
    assert 'SET_MODE' in cmd_str
    assert 'mode=SCIENCE' in cmd_str
    assert 'PENDING' in cmd_str


def test_command_workflow():
    """Test complete command workflow."""
    # Create command
    cmd = Command(CommandType.ADJUST_POWER, {'power_delta': 1.0})
    assert cmd.status == CommandStatus.PENDING
    
    # Uplink
    cmd.mark_uplinked("2026-05-02T12:00:00Z")
    assert cmd.status == CommandStatus.EXECUTING
    assert cmd.uplink_time is not None
    
    # Execute successfully
    cmd.mark_success("Power adjusted", "2026-05-02T12:00:05Z")
    assert cmd.status == CommandStatus.SUCCESS
    assert cmd.execution_time is not None
    assert cmd.acknowledgment == "Power adjusted"
