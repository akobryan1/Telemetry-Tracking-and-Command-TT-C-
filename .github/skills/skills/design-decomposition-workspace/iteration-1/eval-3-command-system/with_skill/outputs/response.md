# Satellite Uplink Command System - Component Breakdown

## System Overview
**Purpose**: Send commands from ground station to satellite with validation, execution, and confirmation downlink.

**Scope**: Basic command uplink system with end-to-end flow: ground authoring → uplink → satellite validation → execution → confirmation downlink.

**Domains Involved**: Command protocols, RF communication, validation logic, state management.

---

## Major Subsystems

### 1. **Ground Command Station**
- **Responsibility**: Create and transmit commands to satellite
- **Inputs**: Operator input (command type, parameters)
- **Outputs**: Encoded command packets transmitted via RF
- **Dependencies**: RF Uplink

### 2. **RF Uplink Channel**
- **Responsibility**: Simulate command transmission from ground to satellite
- **Inputs**: Encoded command packets
- **Outputs**: Received signal at satellite (may include transmission errors/delays)
- **Dependencies**: Ground Command Station, Satellite Receiver

### 3. **Satellite Receiver**
- **Responsibility**: Receive and decode incoming command packets
- **Inputs**: Uplink RF signal
- **Outputs**: Decoded command objects
- **Dependencies**: Command Validator

### 4. **Command Validator**
- **Responsibility**: Verify command is legal, safe, and executable in current state
- **Inputs**: Decoded commands, current satellite state
- **Outputs**: Validated commands OR rejection with error reason
- **Dependencies**: Satellite State Model

### 5. **Command Processor**
- **Responsibility**: Execute validated commands on the satellite
- **Inputs**: Validated commands
- **Outputs**: State changes in satellite, execution status
- **Dependencies**: Satellite State Model

### 6. **Satellite State Model**
- **Responsibility**: Maintain current satellite configuration and status
- **Inputs**: Command execution results, sensor updates
- **Outputs**: Current state (mode, parameters, subsystem status)
- **Dependencies**: None (foundational data store)

### 7. **Telemetry Generator**
- **Responsibility**: Create confirmation/acknowledgment messages for executed commands
- **Inputs**: Command execution status (success/failure), error codes
- **Outputs**: Telemetry packets with command ACK/NAK
- **Dependencies**: Command Processor

### 8. **RF Downlink Channel**
- **Responsibility**: Transmit telemetry from satellite back to ground
- **Inputs**: Telemetry packets
- **Outputs**: Received confirmation at ground station
- **Dependencies**: Ground Receiver

---

## Key Component Details

### Command Validator Components
- **Syntax Checker**: Verify command structure is well-formed
- **Range Validator**: Ensure parameters are within acceptable limits
- **State Checker**: Confirm command is allowed in current satellite mode (e.g., can't turn off power to active systems)
- **Safety Enforcer**: Block commands that violate safety constraints

### Command Processor Components
- **Command Dispatcher**: Route commands to appropriate subsystem handlers
- **Execution Engine**: Actually perform the commanded action
- **Status Reporter**: Generate execution result for telemetry

---

## Data Flow

```
Operator Input → Ground Command Station
                      ↓
              [Encode Command]
                      ↓
                 RF Uplink
                      ↓
             Satellite Receiver
                      ↓
              [Decode Command]
                      ↓
            Command Validator ←→ Satellite State
                      ↓
         [Valid?] →  Command Processor → Update Satellite State
                      ↓
            Telemetry Generator
                      ↓
                RF Downlink
                      ↓
           Ground Station Receives Confirmation
```

---

## Implementation Roadmap

**Phase 1: Basic End-to-End (No RF)**
1. **Satellite State Model**: Simple dictionary/object storing mode and a few parameters
2. **Command Processor**: Handle 2-3 simple commands (e.g., `SET_MODE`, `UPDATE_PARAM`)
3. **Ground Command Station**: Function that creates command objects
4. **Direct delivery**: Command goes straight from ground to processor (no RF, no encoding yet)
5. **Telemetry Generator**: Return simple success/failure message
6. **Verify**: Send commands, check satellite state updates, receive confirmation

**Phase 2: Add Validation**
7. **Command Validator**: Add syntax and range checking
8. **State Checker**: Context-aware validation (reject invalid commands based on state)
9. **Verify**: Test that invalid commands are rejected with proper error messages

**Phase 3: Add RF Links**
10. **Command Encoder**: Convert commands to binary packets (simple format or CCSDS)
11. **RF Uplink**: Basic transmission (can add signal degradation later)
12. **Satellite Receiver**: Decode binary packets
13. **RF Downlink**: Transmit telemetry back to ground
14. **Verify**: Full end-to-end with encoding/decoding

**Phase 4: Enhance Realism**
- Add transmission delays based on range
- Simulate packet loss/corruption based on link quality
- Implement command queuing if uplink is unavailable
- Add command sequence validation (multi-step procedures)

---

## Key Design Decisions

**Start with direct command execution**: Skip RF and encoding initially to validate core logic. Once command processing works, layer in communication complexity.

**Keep validation simple initially**: Begin with parameter range checking. Add state-aware validation once basic flow works.

**Use clear separation**: Command creation (ground) and command execution (satellite) should be distinct modules that communicate via well-defined packet structures.

**Telemetry is part of the loop**: Don't forget the confirmation downlink—it's essential for operators to know if commands succeeded.

---

## Getting Started

Start by implementing these three core pieces:
1. A satellite state object (e.g., `{"mode": "SAFE", "power_level": 50}`)
2. A command processor that can modify that state
3. A function to send a command and print the confirmation

Once that works, everything else builds on top.
