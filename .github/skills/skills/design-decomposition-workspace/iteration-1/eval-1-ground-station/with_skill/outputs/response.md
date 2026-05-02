# TT&C Ground Station System Decomposition

## System Overview

**Purpose**: Simulate a TT&C ground station that autonomously tracks multiple LEO satellites, receives and decodes their telemetry using CCSDS protocols, and transmits commands with proper RF link modeling including Doppler compensation.

**Scope**: 
- Multi-satellite tracking with automatic handoff between passes
- Bidirectional communication (uplink commands, downlink telemetry)
- Realistic RF link modeling (path loss, Doppler shift, noise)
- CCSDS packet encoding/decoding for both telecommands and telemetry
- Automatic antenna pointing with tracking dynamics
- High-fidelity functional simulation (not necessarily real-time hardware control)

**Domains Involved**:
- **Orbital Mechanics**: Satellite propagation, coordinate transformations
- **RF Communication**: Link budgets, signal propagation, Doppler effects, noise
- **Antenna Control**: Automatic pointing, tracking algorithms, slew dynamics
- **Protocol Handling**: CCSDS packet structures (telecommands and telemetry)
- **Software Engineering**: Simulation control, event management, configuration, logging

**Key Challenges Identified**:
- Managing multiple satellite contacts simultaneously or in quick succession
- Real-time Doppler shift compensation for frequency tuning
- Antenna slewing between targets while maintaining contact quality
- Packet synchronization and decoding under varying signal conditions
- Command validation and confirmation across the RF link

---

## Major Subsystems

### 1. Orbital Dynamics Module
**Responsibility**: Propagate satellite orbits and provide position/velocity for all tracked satellites

**Inputs**:
- Orbital elements (TLEs or classical elements) for each satellite
- Current simulation time
- Optional perturbation models (J2, drag, etc.)

**Outputs**:
- Satellite position in ECEF coordinates
- Velocity vectors
- Position in ECI (if needed for other calculations)

**Dependencies**: None (foundational subsystem)

**Key Components**:
- `OrbitPropagator`: SGP4/SDP4 implementation for TLE-based propagation
- `CoordinateTransformer`: ECI ↔ ECEF conversions
- `SatelliteTracker`: Manages multiple satellite state updates
- `PerturbationModels`: Optional high-fidelity perturbations (for future enhancement)

---

### 2. Visibility & Access Calculator
**Responsibility**: Determine when satellites are visible from the ground station and compute geometric parameters

**Inputs**:
- Satellite positions (ECEF) from Orbital Dynamics Module
- Ground station location (latitude, longitude, altitude)
- Minimum elevation angle threshold (typically 5-10°)

**Outputs**:
- Elevation and azimuth angles for each satellite
- Slant range and range rate
- Visibility flags (in-view vs. below horizon)
- Access events (AOS/LOS predictions)

**Dependencies**: Orbital Dynamics Module

**Key Components**:
- `TopocentricConverter`: ECEF → Topocentric (SEZ) coordinates
- `AccessCalculator`: Predict AOS/LOS times
- `GeometryCalculator`: Compute elevation, azimuth, range, range-rate
- `PassScheduler`: Schedule and prioritize upcoming satellite passes

---

### 3. Antenna Control System
**Responsibility**: Automatically point the antenna at selected satellites and manage tracking dynamics

**Inputs**:
- Target azimuth and elevation from Visibility Calculator
- Antenna slew rate limits and acceleration constraints
- Current antenna position
- Priority-ordered list of satellites to track

**Outputs**:
- Commanded antenna pointing direction (az/el)
- Actual antenna position (accounting for dynamics)
- Tracking lock status
- Pointing error magnitude

**Dependencies**: Visibility & Access Calculator

**Key Components**:
- `TrackingController`: Select which satellite to track (scheduling logic)
- `PointingKinematics`: Model antenna slew dynamics (velocity/acceleration limits)
- `ServoSimulator`: Simulate servo response and tracking errors
- `AutoTrackMode`: Closed-loop tracking with error correction
- `HandoffManager`: Coordinate smooth transitions between satellite contacts

---

### 4. RF Link Budget Module
**Responsibility**: Model signal propagation characteristics for uplink and downlink paths

**Inputs**:
- Satellite position and velocity
- Ground station transmit power, antenna gain, frequency
- Atmospheric conditions (optional)
- Range and range-rate from Visibility Calculator

**Outputs**:
- Received signal strength (uplink at satellite, downlink at ground)
- Path loss (free-space and atmospheric)
- Signal-to-noise ratio (SNR)
- Link margin

**Dependencies**: Visibility & Access Calculator, Antenna Control System

**Key Components**:
- `LinkBudgetCalculator`: Friis equation with gains and losses
- `PathLossModel`: Free-space loss, atmospheric attenuation
- `AntennaGainPattern`: Directional gain based on pointing error
- `NoiseFloorCalculator`: System temperature, thermal noise

---

### 5. Doppler Compensation Module
**Responsibility**: Calculate and compensate for Doppler frequency shift in both uplink and downlink

**Inputs**:
- Satellite velocity vector and ground station position
- Carrier frequency (uplink/downlink)
- Range rate from Visibility Calculator

**Outputs**:
- Doppler shift magnitude (Hz)
- Compensated transmit/receive frequencies
- Rate of change of Doppler (for tracking loops)

**Dependencies**: Visibility & Access Calculator, Orbital Dynamics Module

**Key Components**:
- `DopplerCalculator`: Compute shift from relative velocity
- `FrequencySynthesizer`: Adjust transmit/receive frequencies
- `DopplerRatePredictor`: Estimate Doppler rate for phase-locked loops

---

### 6. Command Uplink Subsystem
**Responsibility**: Validate, encode, and transmit commands to satellites

**Inputs**:
- User-authored commands (command type, parameters)
- Current satellite state (for validation)
- Link availability and quality from RF Link Module

**Outputs**:
- CCSDS telecommand packets
- Uplink signal transmission
- Command transmission status (queued, transmitted, acknowledged)

**Dependencies**: RF Link Budget Module, Doppler Compensation Module, CCSDS Protocol Handler

**Key Components**:
- `CommandAuthoring`: Interface for creating commands
- `CommandValidator`: Syntax, range, state, and safety checking
- `CCSDSTelecommandEncoder`: Encode commands into CCSDS TC packets
- `UplinkTransmitter`: Modulate and transmit command packets
- `CommandQueue`: Buffer commands for transmission when link available
- `AcknowledgmentTracker`: Monitor command receipt confirmations

---

### 7. Telemetry Downlink Subsystem
**Responsibility**: Receive, decode, and process telemetry data from satellites

**Inputs**:
- Downlink RF signal from satellites
- SNR and link quality from RF Link Module
- Doppler-compensated receive frequency

**Outputs**:
- Decoded CCSDS telemetry packets
- Telemetry data streams (organized by APID or virtual channel)
- Frame synchronization status
- Bit error statistics

**Dependencies**: RF Link Budget Module, Doppler Compensation Module, CCSDS Protocol Handler

**Key Components**:
- `SignalReceiver`: Demodulate downlink signal
- `FrameSynchronizer`: Detect and lock onto CCSDS frame sync markers
- `CCSDSTelemetryDecoder`: Parse telemetry transfer frames and packets
- `BitErrorSimulator`: Model bit errors based on SNR
- `TelemetryRouter`: Route packets by APID to appropriate handlers
- `DataLogger`: Archive received telemetry

---

### 8. CCSDS Protocol Handler
**Responsibility**: Implement CCSDS packet structures for both telecommands and telemetry

**Inputs**:
- Raw command data (for encoding)
- Raw bit streams (for decoding)
- Protocol configuration (frame lengths, sync markers, virtual channels)

**Outputs**:
- Properly formatted CCSDS packets/frames
- Parsed packet headers and data fields
- CRC validation results

**Dependencies**: None (used by Command and Telemetry subsystems)

**Key Components**:
- `TelemetryTransferFrame`: CCSDS TM frame structure
- `TelecommandTransferFrame`: CCSDS TC frame structure  
- `PacketPrimaryHeader`: Standard packet header parsing/generation
- `CRCCalculator`: Cyclic redundancy check validation
- `VirtualChannelManager`: Multiplex/demultiplex virtual channels
- `SequenceCounter`: Track packet sequence numbers for loss detection

---

### 9. Simulation Control & Event Manager
**Responsibility**: Orchestrate the simulation, manage time, schedule events, and coordinate subsystems

**Inputs**:
- Scenario configuration (satellite TLEs, ground station location, simulation duration)
- Start/stop commands from user
- Real-time event triggers (AOS/LOS, loss of signal, command timeouts)

**Outputs**:
- Current simulation time
- Scheduled event execution
- Subsystem coordination signals
- Simulation state (running, paused, completed)

**Dependencies**: All other subsystems (top-level orchestrator)

**Key Components**:
- `SimulationClock`: Time management (real-time factor, step size)
- `EventQueue`: Priority queue for scheduled events (AOS, LOS, command execution)
- `ScenarioLoader`: Read configuration files
- `SubsystemCoordinator`: Initialize and synchronize all modules
- `StatePublisher`: Broadcast state updates to subscribers

---

### 10. Data Logging & Visualization
**Responsibility**: Record simulation data and provide real-time/post-processing visualization

**Inputs**:
- All subsystem outputs (orbital states, link budgets, received telemetry, sent commands)
- Visualization requests from user

**Outputs**:
- Log files (CSV, HDF5, or database)
- Real-time plots (satellite ground tracks, antenna pointing, signal strength)
- Post-processing reports (pass summaries, link statistics)

**Dependencies**: All data-producing subsystems

**Key Components**:
- `TimeSeriesLogger`: Record time-series data efficiently
- `PassSummaryGenerator`: Create reports for each satellite pass
- `GroundTrackPlotter`: Visualize satellite positions on map
- `LinkBudgetPlotter`: Plot signal strength, Doppler, elevation vs. time
- `ConstellationVisualizer`: 3D view of satellite positions (optional)

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Simulation Control & Event Manager            │
│                    (Time, Events, Coordination)                 │
└────────────┬──────────────────────────────────────┬─────────────┘
             │                                      │
             ▼                                      ▼
┌────────────────────────┐            ┌──────────────────────────┐
│  Orbital Dynamics      │            │  CCSDS Protocol Handler  │
│  - Propagate orbits    │            │  - Packet structures     │
│  - Position/velocity   │            │  - Encoding/decoding     │
└──────────┬─────────────┘            └──────────┬───────────────┘
           │                                     │
           ▼                                     │
┌────────────────────────┐                       │
│  Visibility &          │                       │
│  Access Calculator     │                       │
│  - AOS/LOS events      │                       │
│  - Az/El/Range         │                       │
└──────────┬─────────────┘                       │
           │                                     │
           ├─────────────┬───────────────┬───────┼────────────┐
           ▼             ▼               ▼       ▼            ▼
┌──────────────┐  ┌─────────────┐ ┌──────────────┐  ┌────────────────┐
│   Antenna    │  │   Doppler   │ │  RF Link     │  │   Command      │
│   Control    │  │ Compensation│ │  Budget      │  │   Uplink       │
│   System     │  │             │ │  Module      │  │   Subsystem    │◄──┤
└──────┬───────┘  └──────┬──────┘ └──────┬───────┘  └────────┬───────┘   │
       │                 │               │                   │           │
       └─────────────────┼───────────────┼───────────────────┘           │
                         │               │                               │
                         ▼               ▼                               │
                  ┌──────────────────────────────┐                       │
                  │   Telemetry Downlink         │                       │
                  │   Subsystem                  │                       │
                  │   - Receive & decode         │                       │
                  └──────────────┬───────────────┘                       │
                                 │                                       │
                                 ▼                                       │
                  ┌──────────────────────────────┐                       │
                  │   Data Logging &             │                       │
                  │   Visualization              │                       │
                  └──────────────────────────────┘                       │
                                                                         │
User Commands ──────────────────────────────────────────────────────────┘
```

**Key Data Flows**:
1. **Orbital Position Flow**: Orbital Dynamics → Visibility → Antenna Control, RF Link, Doppler
2. **Downlink Path**: Satellite → RF Link → Doppler Compensation → Telemetry Decoder → Logger
3. **Uplink Path**: User Command → Validator → CCSDS Encoder → Doppler Compensation → RF Link → Satellite
4. **Event Flow**: Visibility Calculator generates AOS/LOS events → Event Manager schedules actions
5. **Tracking Flow**: Visibility Calculator provides target → Antenna Control commands pointing

---

## Implementation Roadmap

### Phase 1: Foundation (Minimal Working System)
**Goal**: Predict satellite passes and demonstrate basic visibility

1. **Orbital Dynamics Module**: Implement SGP4 propagator
   - Use existing library (Python: `sgp4`, C++: `libsgp4`)
   - Load TLEs for test satellites
   - Output position/velocity in ECEF
   - *Verification*: Compare positions to online tools (Heavens-Above, N2YO)

2. **Visibility Calculator**: Basic geometric calculations
   - ECEF → Topocentric conversion
   - Elevation angle > threshold = visible
   - Compute azimuth, elevation, range
   - *Verification*: Predict AOS/LOS times, compare to online predictions

3. **Simulation Controller**: Simple time-stepping loop
   - Initialize with scenario (TLEs, ground station location)
   - Step through time (1-second increments)
   - Query visibility for each satellite
   - Print AOS/LOS events
   - *Verification*: Run 24-hour scenario, validate pass predictions

**Deliverable**: Program that prints "AOS at HH:MM:SS, elevation 45°, azimuth 180°" for satellite passes

---

### Phase 2: RF Link Modeling
**Goal**: Add realistic signal propagation

4. **RF Link Budget Module**: Free-space path loss
   - Friis transmission equation
   - Fixed antenna gains (initial)
   - Calculate received power
   - Simple noise floor → SNR
   - *Verification*: Hand-calculate link budget for known geometry, compare to tool output

5. **Doppler Compensation Module**: Calculate frequency shift
   - Use range-rate from Visibility Calculator
   - Compute Doppler shift: Δf = (v_r / c) × f_carrier
   - Output both uplink and downlink Doppler
   - *Verification*: Check against analytical formula for circular orbit

**Deliverable**: During each pass, plot signal strength and Doppler shift vs. time

---

### Phase 3: Antenna Tracking
**Goal**: Automatic antenna pointing with realistic dynamics

6. **Antenna Control System**: Automatic tracking
   - Target = current satellite az/el from Visibility Calculator
   - Simple model: instant slew (no dynamics yet)
   - Pointing error = 0 when locked
   - *Verification*: Verify antenna always points at visible satellite

7. **Antenna Dynamics**: Add slew rate limits
   - Maximum slew rate (e.g., 5°/s)
   - Model servo lag and acceleration
   - Pointing error during rapid slews
   - *Verification*: Plot commanded vs. actual antenna position during pass

8. **Multi-satellite handoff**: Track multiple satellites
   - Priority queue of upcoming passes
   - Automatic switch to next satellite after LOS
   - Pre-pointing before AOS
   - *Verification*: Test scenario with overlapping passes

**Deliverable**: Antenna automatically tracks satellites, handles handoffs, respects slew limits

---

### Phase 4: Telemetry Downlink (Simplified)
**Goal**: Receive and decode telemetry data

9. **CCSDS Protocol Handler**: Telemetry packet structure
   - Implement CCSDS telemetry transfer frame format
   - Packet primary header
   - CRC calculation and validation
   - *Verification*: Encode test data, decode, verify round-trip

10. **Telemetry Downlink Subsystem**: Basic reception
    - Generate simulated satellite telemetry (mock data)
    - Success probability based on SNR threshold
    - Frame synchronization (simplified: assume sync when SNR > threshold)
    - Decode packets
    - *Verification*: During pass, log received packets; check success rate vs. SNR

11. **Data Logging**: Store received telemetry
    - Write decoded packets to CSV or HDF5
    - Log pass metadata (AOS/LOS, max elevation, total packets)
    - *Verification*: Review logs after test scenario

**Deliverable**: System receives and logs telemetry during satellite passes

---

### Phase 5: Command Uplink
**Goal**: Send commands to satellites

12. **Command Uplink Subsystem**: Command validation and encoding
    - Define simple command set (e.g., SET_MODE, ADJUST_PARAMETER)
    - Basic validation (syntax, range checking)
    - CCSDS telecommand packet encoding
    - *Verification*: Create command, encode, verify packet structure

13. **Uplink Transmission**: Send commands over RF link
    - Queue commands for transmission when satellite visible
    - Account for uplink SNR (can fail if link poor)
    - Doppler-compensated transmit frequency
    - *Verification*: Send test commands during pass, confirm delivery

14. **Command Acknowledgment**: Downlink confirmation
    - Satellite sends acknowledgment in telemetry
    - Track command status: queued → transmitted → acknowledged
    - Timeout and retry logic
    - *Verification*: Send command, verify acknowledgment received

**Deliverable**: Ground station can send commands and receive acknowledgments

---

### Phase 6: Enhancement and Realism
**Goal**: Add fidelity and features for production-quality simulation

15. **Enhanced RF Model**: Atmospheric effects
    - Tropospheric/ionospheric attenuation
    - Rain fade (optional)
    - Multipath and fading (optional)

16. **Realistic Noise and Bit Errors**: Signal degradation
    - Add thermal noise to signal
    - Bit error rate (BER) based on SNR
    - Frame sync loss and reacquisition
    - Packet loss and retransmission

17. **Advanced Antenna Control**: Autotrack algorithms
    - Monopulse or conical scan tracking
    - Pointing error feedback
    - Wind disturbance rejection

18. **Orbital Perturbations**: High-fidelity propagation
    - J2 gravity harmonic
    - Atmospheric drag
    - Solar radiation pressure
    - Optional: numerical propagator (RK4, etc.)

19. **Configuration Management**: Scenario files
    - JSON/YAML configuration for scenarios
    - Parameter sweeps (e.g., different ground station locations)
    - Mission templates

20. **Visualization**: Real-time and post-processing
    - 2D ground track on map
    - 3D constellation view
    - Time-series plots (elevation, signal strength, Doppler)
    - Pass summary reports

**Deliverable**: Production-ready TT&C simulation with configurable scenarios and rich visualization

---

### Phase 7: Advanced Features (Optional)
**Goal**: Support complex operational scenarios

21. **Multiple ground stations**: Network operations
22. **Constellation support**: Coordinate tracking across many satellites
23. **Frequency planning**: Avoid interference between links
24. **Data replay**: Replay recorded telemetry for analysis
25. **Hardware-in-the-loop**: Interface with real antenna controllers or SDRs

---

## Key Design Decisions & Rationale

### 1. **Time-Stepped vs. Event-Driven Simulation**
**Decision**: Hybrid approach
- Time-stepping for continuous physics (orbital propagation, RF link)
- Event queue for discrete events (AOS/LOS, command transmission, timeouts)

**Rationale**: Physics requires regular updates; events are sparse and benefit from scheduling

### 2. **SGP4 vs. High-Fidelity Propagator**
**Decision**: Start with SGP4, option to upgrade later

**Rationale**: 
- SGP4 is industry-standard for TLE-based tracking
- Sufficient accuracy for LEO over short periods (minutes to hours)
- Mature, well-tested libraries available
- Can add high-fidelity propagator as plugin if sub-kilometer accuracy needed

### 3. **CCSDS Packets: Full Implementation vs. Simplified**
**Decision**: Implement core CCSDS structures, defer advanced features

**Rationale**:
- Transfer frames (TM/TC) and packet headers are essential for realism
- Advanced features (CFDP file transfer, encrypted commands) can be added incrementally
- Allows testing with real CCSDS ground systems if needed

### 4. **Antenna Model: Ideal vs. Realistic Dynamics**
**Decision**: Start ideal (instant slew), add dynamics in Phase 3

**Rationale**:
- Validates core algorithms first
- Antenna dynamics straightforward to add later
- Slew rate limits and pointing errors are measurable effects in real systems

### 5. **SNR Threshold vs. Detailed Modulation/Coding**
**Decision**: Use SNR threshold for packet success initially

**Rationale**:
- Captures first-order effect (link quality → data loss)
- Adding modulation schemes (BPSK, QPSK) and error correction (Reed-Solomon, Turbo codes) is complex
- Can model BER curves later if needed for specific mission analysis

### 6. **Multi-Satellite Scheduling: Manual vs. Automatic**
**Decision**: Automatic scheduling with priority queue

**Rationale**:
- Realistic ground stations autonomously switch between satellites
- Priority based on elevation, link quality, or mission importance
- Manual override capability can be added for operator control

### 7. **Data Storage: Real-Time Database vs. Files**
**Decision**: Log to files (CSV/HDF5) initially, database optional

**Rationale**:
- Simpler implementation
- Sufficient for post-processing analysis
- Database can be added if real-time querying or large-scale data needed

### 8. **Doppler Compensation: Pre-calculated vs. Real-Time**
**Decision**: Real-time calculation at each time step

**Rationale**:
- More realistic (matches real ground station behavior)
- Allows testing Doppler rate tracking loops
- Negligible computational cost

---

## Testing & Validation Strategy

### Unit Testing
- Each module tested independently with known inputs/outputs
- Example: Doppler calculator tested with circular orbit (analytical solution)
- CCSDS encoder/decoder round-trip tests

### Integration Testing
- Test subsystem interactions: Orbital → Visibility → Antenna
- Verify data flow between modules
- Check event scheduling (AOS triggers antenna slew)

### Scenario-Based Testing
- Use real satellite TLEs (e.g., ISS, Starlink)
- Compare predictions to online tools (Heavens-Above, N2YO)
- Validate link budgets against published satellite specs

### Regression Testing
- Maintain test scenarios with known outputs
- Re-run after changes to detect regressions

---

## Technology Stack Recommendations

### Programming Language
**Python** (Recommended for rapid development)
- Rich ecosystem for aerospace (sgp4, astropy, poliastro)
- Excellent visualization (matplotlib, plotly)
- Easy prototyping and testing

**C++** (Alternative for performance-critical applications)
- Faster execution for large constellations
- Libraries: libsgp4, Orekit (via JNI)

### Key Libraries
- **Orbit Propagation**: `sgp4` (Python/C++), `poliastro`, `Orekit`
- **CCSDS**: `space_packet_parser` (Python), custom implementation
- **Coordinate Transformations**: `astropy`, `pyproj`
- **Visualization**: `matplotlib`, `plotly`, `cesiumpy` (3D)
- **Configuration**: `PyYAML`, `configparser`
- **Logging**: `pandas` (CSV), `h5py` (HDF5)

### Development Environment
- Version control: Git
- Testing: `pytest` (Python), `Google Test` (C++)
- Documentation: Markdown, Jupyter notebooks for examples

---

## Cross-Cutting Concerns

### Time Management
- Central simulation clock
- Configurable time step (default: 1 second)
- Real-time factor (1x, 10x, 100x speedup)
- Leap second handling (use GPS time or UTC with leap tables)

### Configuration
- Scenario files (YAML/JSON)
  - Satellite TLEs
  - Ground station parameters (lat/lon/alt, antenna specs, RF config)
  - Simulation duration and time step
  - Logging options
- Parameter validation on load

### Logging & Telemetry
- Multi-level logging (DEBUG, INFO, WARNING, ERROR)
- Separate logs for each subsystem
- Telemetry data separate from debug logs
- Configurable log verbosity

### Error Handling
- Graceful degradation (e.g., if satellite below horizon, skip antenna pointing)
- Validation of inputs (TLEs, frequencies, coordinates)
- Clear error messages for misconfigurations

### Visualization
- Real-time plots (updated each time step or on-demand)
- Post-processing (load logs, generate reports)
- Export formats (PNG, PDF, interactive HTML)

---

## Summary

This decomposition provides a clear architecture for your TT&C ground station simulation:

**Major Subsystems** (10 total):
1. Orbital Dynamics
2. Visibility & Access
3. Antenna Control
4. RF Link Budget
5. Doppler Compensation
6. Command Uplink
7. Telemetry Downlink
8. CCSDS Protocol Handler
9. Simulation Control & Event Manager
10. Data Logging & Visualization

**Implementation Phases** (1-6):
- Phase 1-3: Foundation → RF → Antenna (working system with automatic tracking)
- Phase 4-5: Telemetry downlink → Command uplink (full bidirectional TT&C)
- Phase 6-7: Enhancement and optional advanced features

**Build Order Rationale**:
- Start with orbit propagation (foundation everything depends on)
- Add visibility and basic simulation control (working end-to-end, even if simple)
- Layer in RF link and antenna control (realism and automation)
- Add communication protocols incrementally (downlink before uplink, as it's simpler)
- Enhance fidelity and add features once core working

This approach gives you working checkpoints at each phase, allows testing and validation incrementally, and avoids big-bang integration. You can stop at any phase and have a functional (if simplified) system, or continue to production-quality simulation.

**Next Steps**:
1. Set up development environment and version control
2. Choose technology stack (Python recommended for rapid development)
3. Implement Phase 1 (orbital propagation and visibility)
4. Validate against known satellite passes
5. Proceed through phases incrementally

Good luck with your TT&C ground station simulation!
