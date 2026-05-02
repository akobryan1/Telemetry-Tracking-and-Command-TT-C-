---
name: design-decomposition
description: Break down complex systems into manageable components before implementation. Use when users ask how to structure, architect, organize, plan, or design systems—especially for TT&C simulations, aerospace systems, satellite communications, ground stations, or other multi-domain engineering projects. Trigger on questions about system architecture, component hierarchy, module boundaries, dependencies, or "how should I organize/structure/break down" any complex technical system. Also use when users want to plan before coding, need to understand what modules/components they'll need, or are designing the high-level structure of a simulation or software system.
---

# Design Thinking & Decomposition

This skill guides systematic decomposition of complex systems into manageable, implementable components. The goal is to help users think through architecture and design *before* jumping into code, ensuring a well-structured foundation.

## When to Use This Skill

Apply this skill when the user needs to:
- Structure or architect a complex system from scratch
- Break down a multi-domain system (e.g., TT&C simulation combining orbital mechanics, RF, protocols, software)
- Plan what components/modules they'll need before implementing
- Understand dependencies and interfaces between subsystems
- Organize an overwhelming project into logical pieces

**Common trigger phrases:**
- "How should I structure..."
- "What components do I need for..."
- "Break down the architecture of..."
- "How do I organize..."
- "What modules should I create..."

## Decomposition Process

Follow this systematic approach to help users decompose their systems:

### Step 1: Understand the Whole System

Before decomposing, establish a clear picture of what the complete system needs to do:

**Ask clarifying questions:**
- What is the system's primary purpose?
- What are the inputs and outputs?
- What are the key behaviors or functions?
- What domains are involved? (e.g., for TT&C: orbital mechanics, RF communication, command/telemetry protocols, ground systems)
- What's the scope? (prototype vs. production, high-fidelity vs. functional simulation)

**For TT&C simulations specifically:**
- Mission profile (LEO/MEO/GEO, orbit characteristics)
- Communication direction (uplink, downlink, or both)
- Protocols (CCSDS, custom, or simplified)
- Fidelity requirements (physics-accurate vs. functional demonstration)
- Scale (single satellite-ground station link vs. constellation)

Don't proceed to decomposition until you understand the big picture.

### Step 2: Identify Major Subsystems

Break the system into major subsystems based on distinct responsibilities or domains.

**Decomposition principles:**

1. **Separation of Concerns**: Each subsystem handles one primary responsibility
2. **Domain Boundaries**: Group functionality by technical domain (physics, protocols, I/O, etc.)
3. **Data Flow**: Consider how information moves through the system
4. **Independence**: Minimize coupling between subsystems where possible

**Example: TT&C Simulation Major Subsystems**

For a satellite-ground station TT&C simulation, major subsystems might include:
- **Orbital Dynamics Module**: Satellite position/velocity over time
- **RF Link Module**: Signal propagation, path loss, Doppler shift
- **Ground Station Module**: Antenna pointing, signal reception/transmission
- **Command Module**: Command encoding, uplink, validation
- **Telemetry Module**: Data collection, encoding, downlink
- **Protocol Handler**: CCSDS packet structure (if using standards)
- **Simulation Control**: Time management, scenario configuration, event orchestration

Notice how each subsystem has a clear, distinct purpose tied to a domain or responsibility.

### Step 3: Define Interfaces and Data Flow

For each subsystem identified, specify:
- **Inputs**: What data/information does it consume?
- **Outputs**: What data/information does it produce?
- **Dependencies**: Which other subsystems does it depend on?

**Create a data flow diagram (mental or actual):**
```
Example for TT&C downlink:
Orbital Dynamics → Position/Velocity
                      ↓
         RF Link ← Position/Velocity + Ground Station Location
                      ↓
         Signal Characteristics (Doppler, Path Loss)
                      ↓
    Telemetry Module → Encodes Data → RF Link → Ground Station
```

Clear interfaces reduce coupling and make implementation easier.

### Step 4: Decompose Subsystems into Components

For each major subsystem, break it down into smaller components or classes.

**Component-level decomposition:**
- What are the key classes, functions, or modules within this subsystem?
- What data structures are needed?
- What algorithms or calculations are required?

**Example: RF Link Subsystem Components**
- `LinkBudgetCalculator`: Compute signal power at receiver
- `DopplerCalculator`: Calculate frequency shift from relative velocity
- `PropagationModel`: Model atmospheric/free-space path loss
- `AntennaModel`: Represent antenna gain patterns
- `NoiseModel`: Add thermal noise, interference

Each component has a specific, testable responsibility.

### Step 5: Identify Cross-Cutting Concerns

Some concerns span multiple subsystems:
- **Time Management**: Simulation clock, timestep control
- **Configuration**: Parameters, constants, scenario setup
- **Logging/Telemetry**: Debug output, state recording
- **Validation**: Input checking, constraint enforcement
- **Visualization**: Real-time or post-processing displays

Decide how these will be handled:
- Centralized service (e.g., global configuration manager)
- Injected dependency (e.g., logger passed to each module)
- Aspect/decorator pattern (e.g., validation wrappers)

### Step 6: Prioritize Implementation Order

Not all components need to be built at once. Recommend an implementation sequence:

**Prioritization criteria:**
1. **Foundation first**: Core functionality that others depend on
2. **Minimal end-to-end**: Simplest path from input to output
3. **Incremental complexity**: Add features in layers
4. **Testability**: Components that can be validated independently

**Example: TT&C Simulation Build Order**
1. Basic orbital propagator (circular orbit, simplified)
2. Simple ground station (fixed position)
3. Basic RF link (free-space path loss only)
4. Simple telemetry downlink (fixed data packet)
5. Add Doppler shift calculation
6. Add antenna pointing control
7. Add command uplink
8. Enhance orbital propagator (elliptical orbits, perturbations)
9. Add protocol handling (CCSDS)
10. Add noise and signal degradation

This gives working checkpoints and avoids big-bang integration.

## Output Format

Provide decomposition results in a clear, structured format:

### System Overview
**Purpose**: [One sentence describing the system's goal]
**Scope**: [Key scope decisions and constraints]
**Domains Involved**: [List of technical domains, e.g., orbital mechanics, RF, protocols]

### Major Subsystems
For each subsystem:
- **Name**: ClearDescriptiveName
- **Responsibility**: What it does (one sentence)
- **Inputs**: Data/information consumed
- **Outputs**: Data/information produced
- **Dependencies**: Other subsystems it relies on

### Component Breakdown
For each major subsystem (as needed):
- List key components/classes/modules
- Brief description of each component's role

### Data Flow
- High-level diagram or description of how information flows through the system

### Implementation Roadmap
1. [First component/subsystem to build - why it's first]
2. [Second component/subsystem - why it comes next]
3. ...
[Continue until minimal working system is complete]

Then:
- [Features to add incrementally]
- [Enhancements and refinements]

### Key Design Decisions
- [Important architectural choices made]
- [Trade-offs and rationale]

## Domain-Specific Guidance

### TT&C and Aerospace Simulations

When decomposing TT&C or aerospace systems, consider these common patterns:

**Typical Subsystems:**
- **Orbital Dynamics**: Propagation (Kepler, SGP4/SDP4, high-fidelity), coordinate transformations (ECI, ECEF, topocentric)
- **Attitude Dynamics**: Orientation, slew maneuvers, sun-pointing
- **Communication Link**: Carrier frequency, modulation, link budget, Doppler, range/range-rate
- **Ground Network**: Antenna control, signal processing, scheduling
- **Command & Control**: Command validation, sequencing, execution
- **Telemetry**: Data acquisition, packetization, encoding, storage
- **Protocols**: CCSDS, CFDP, or custom framing and error detection

**Common Design Patterns:**
- **Time-stepped simulation**: Discrete time steps with state updates
- **Event-driven simulation**: Queue of scheduled events (e.g., AOS/LOS)
- **Plugin architecture**: Swappable models (e.g., different propagators, noise models)
- **Observer pattern**: Components subscribe to state changes (e.g., position updates)

**Typical Dependencies:**
- Orbital position → Antenna pointing, RF link characteristics, Doppler shift
- Time → All subsystems (synchronized simulation clock)
- Configuration → All subsystems (parameters, constants)

### Multi-Domain Systems

For systems spanning multiple technical domains (like TT&C):
- Identify the core domain that drives others (often dynamics/physics)
- Layer communication and control on top of physics
- Separate domain logic from infrastructure (I/O, visualization, configuration)

### Software Architecture Patterns

Recommend appropriate patterns based on system needs:
- **Model-View-Controller**: Separate physics (model) from visualization (view) and user interaction (controller)
- **Layered Architecture**: Physics → Domain Logic → Application → UI
- **Pipeline Architecture**: Data flows through transformation stages (sensor → processor → encoder → transmitter)
- **Microkernel/Plugin**: Core simulation engine with pluggable models

## Examples

### Example 1: Ground Station Simulator

**User**: "I want to build a ground station simulator for tracking LEO satellites. How should I structure it?"

**Response**:

#### System Overview
**Purpose**: Simulate a ground station receiving telemetry from LEO satellites as they pass overhead.
**Scope**: Single ground station, multiple satellite passes, realistic RF link, CCSDS telemetry packets
**Domains**: Orbital mechanics (satellite motion), RF communication (link budget, Doppler), protocols (CCSDS), ground systems (antenna control)

#### Major Subsystems

1. **Satellite Orbit Propagator**
   - Responsibility: Calculate satellite position and velocity over time
   - Inputs: Orbital elements (TLE or classical elements), current time
   - Outputs: Position (ECEF), velocity vector
   - Dependencies: None (foundational)

2. **Visibility Calculator**
   - Responsibility: Determine when satellite is above horizon (AOS/LOS events)
   - Inputs: Satellite position, ground station location
   - Outputs: Elevation, azimuth, range, visibility flag
   - Dependencies: Orbit Propagator

3. **Antenna Controller**
   - Responsibility: Point antenna at satellite during passes
   - Inputs: Azimuth, elevation targets from Visibility Calculator
   - Outputs: Current antenna pointing direction, tracking status
   - Dependencies: Visibility Calculator

4. **RF Link Simulator**
   - Responsibility: Model signal reception including path loss, Doppler shift
   - Inputs: Satellite position/velocity, ground station antenna pointing, transmit power
   - Outputs: Received signal strength, Doppler-shifted frequency, SNR
   - Dependencies: Orbit Propagator, Visibility Calculator

5. **Telemetry Receiver**
   - Responsibility: Decode CCSDS packets from received signal
   - Inputs: RF signal characteristics (SNR determines success rate)
   - Outputs: Decoded telemetry packets
   - Dependencies: RF Link Simulator

6. **Data Logger**
   - Responsibility: Store received telemetry and pass statistics
   - Inputs: Telemetry packets, pass metadata (AOS/LOS times, max elevation)
   - Outputs: Files or database records
   - Dependencies: Telemetry Receiver, Visibility Calculator

7. **Simulation Controller**
   - Responsibility: Manage simulation time, orchestrate components, configuration
   - Inputs: Scenario configuration (satellite TLEs, ground station location, duration)
   - Outputs: Simulation state, event scheduling
   - Dependencies: None (top-level orchestrator)

#### Implementation Roadmap

**Phase 1: Minimal Working System**
1. **Orbit Propagator**: Start with SGP4 using TLE input (libraries available: `sgp4` in Python)
2. **Visibility Calculator**: Basic geometric calculation (elevation angle > 0°)
3. **Simulation Controller**: Simple time-stepping loop, advance time, query visibility
4. **Verification**: Print AOS/LOS times for known satellite passes, compare to online tools

**Phase 2: Add RF Link**
5. **RF Link Simulator**: Free-space path loss only, fixed antenna gain
6. **Telemetry Receiver**: Simplified packet generation (SNR threshold for success)
7. **Verification**: Check received signal strength vs. hand calculations

**Phase 3: Enhance Realism**
8. **Antenna Controller**: Add pointing dynamics (slew rate limits)
9. **RF Link Simulator**: Add Doppler shift calculation, atmospheric effects
10. **Telemetry Receiver**: Implement actual CCSDS packet parsing
11. **Data Logger**: Save results to CSV or database

**Phase 4: Polish**
12. **Visualization**: Plot satellite passes, antenna pointing, signal strength
13. **Configuration**: Read scenarios from config files
14. **Multi-satellite support**: Track multiple satellites simultaneously

#### Key Design Decisions
- **Time-stepped simulation**: 1-second time steps sufficient for LEO ground station
- **SGP4 propagator**: Industry standard for TLE-based propagation, mature libraries available
- **Simplified RF model initially**: Free-space path loss captures primary effect; atmospheric refraction/scintillation can be added later
- **CCSDS packets**: Use standard for interoperability practice, but start with simplified packet structure

---

This decomposition gives you a clear architecture and implementation path. Start with Phase 1 to get a working foundation, then incrementally add capabilities.

### Example 2: Satellite Command Uplink System

**User**: "How do I structure a command uplink system for a satellite simulator?"

**Response**:

#### System Overview
**Purpose**: Validate, encode, and transmit commands from ground to satellite in simulation
**Scope**: Command validation, protocol encoding, uplink transmission, satellite reception and execution
**Domains**: Command protocols, RF communication, validation logic, state machines

#### Major Subsystems

1. **Command Authoring Interface**
   - Responsibility: Allow user to create and submit commands
   - Inputs: User input (command type, parameters)
   - Outputs: Raw command objects
   - Dependencies: None

2. **Command Validator**
   - Responsibility: Verify command legality and safety
   - Inputs: Raw command objects, current satellite state
   - Outputs: Validated commands or rejection with reason
   - Dependencies: Satellite State (for context-aware validation)

3. **Command Encoder**
   - Responsibility: Encode commands into protocol format (e.g., CCSDS telecommand packets)
   - Inputs: Validated commands
   - Outputs: Binary command packets
   - Dependencies: Command Validator

4. **Uplink Simulator**
   - Responsibility: Transmit command packets over RF link
   - Inputs: Binary command packets, link availability
   - Outputs: Transmitted signal characteristics
   - Dependencies: RF Link Simulator (from ground station)

5. **Satellite Receiver**
   - Responsibility: Receive and decode command packets
   - Inputs: Uplink signal (with potential errors/dropouts)
   - Outputs: Decoded command packets or error flags
   - Dependencies: Uplink Simulator

6. **Command Processor**
   - Responsibility: Execute validated commands on satellite
   - Inputs: Decoded command packets
   - Outputs: State changes, telemetry confirmation
   - Dependencies: Satellite State Model

7. **Telemetry Downlink (for confirmation)**
   - Responsibility: Send command execution confirmation to ground
   - Inputs: Command execution status
   - Outputs: Telemetry packets indicating success/failure
   - Dependencies: Downlink Simulator (existing subsystem)

#### Component Breakdown: Command Validator

This is critical for safety:
- `SyntaxChecker`: Verify command structure and parameters are well-formed
- `RangeValidator`: Ensure numeric parameters are within acceptable ranges
- `StateValidator`: Check if command is allowed in current satellite mode (e.g., can't deploy solar panels if already deployed)
- `SequenceChecker`: Verify command sequences follow required order
- `SafetyLimits`: Enforce constraints (e.g., thruster burn duration limits)

#### Implementation Roadmap

1. **Command Authoring Interface**: Simple CLI or function calls with command name + parameters
2. **Command Validator**: Basic syntax and range checking
3. **Command Encoder**: Simple binary format (command ID + parameters); CCSDS can come later
4. **Satellite Receiver**: Direct delivery (no RF errors initially)
5. **Command Processor**: Execute simple commands (e.g., "SET_MODE", "UPDATE_PARAMETER")
6. **Verification**: Send commands, verify satellite state changes as expected

Then add:
7. **Uplink Simulator**: Integrate with RF link (can fail based on SNR)
8. **Command Encoder**: Upgrade to CCSDS telecommand packet format
9. **State Validator**: Context-aware validation based on satellite mode
10. **Telemetry Confirmation**: Downlink acknowledgment packets

#### Key Design Decisions
- **Validation before encoding**: Catch errors early, before transmission
- **Idempotency**: Commands can be safely retransmitted if acknowledgment is lost
- **Command queuing**: Satellite maintains command queue for execution scheduling
- **Error handling**: Distinguish between transmission errors (retry) and validation errors (reject)

---

This structure separates concerns: validation logic, protocol encoding, RF transmission, and execution are independent subsystems that can be developed and tested separately.

## Anti-Patterns to Avoid

### Premature Implementation
Don't start coding before understanding the decomposition. "I'll figure it out as I go" leads to spaghetti architecture and costly refactoring.

### Over-Engineering
Decompose to a level appropriate for the project scope. A prototype doesn't need the same architecture as a production system. Know when to stop subdividing.

### Ignoring Dependencies
Failing to identify which subsystems depend on others leads to integration nightmares. Make dependencies explicit.

### Domain Mixing
Don't mix physics, protocols, and UI in the same component. Respect domain boundaries for maintainability.

### Big-Bang Integration
Planning to build all subsystems independently and integrate at the end is risky. Recommend incremental integration: build a minimal end-to-end system first, then expand.

## Tips for Effective Decomposition

**Think in Layers**: Bottom layer (physics/math) → Middle layer (domain logic/algorithms) → Top layer (application/UI)

**Identify the "Spine"**: What's the core data flow or state that everything else depends on? For TT&C, often it's orbital position over time.

**Use Standard Patterns**: Don't reinvent architecture. Observer, Strategy, Factory patterns solve common problems.

**Plan for Testing**: Decompose so components can be tested in isolation. If a component can't be unit-tested, it's probably doing too much.

**Document Interfaces**: Even in the design phase, write down what each subsystem's inputs/outputs are. This is your contract.

**Iterate**: First decomposition is rarely perfect. Refine as understanding grows, but do it *before* implementing, not after.

## When Decomposition is Complete

You're ready to implement when you can:
- Explain what each major subsystem does in one sentence
- Describe inputs and outputs for each subsystem
- Draw (or mentally visualize) the data flow
- Identify which component to build first and why
- Answer "Where would this feature go?" for any new requirement

At that point, transition from design to implementation with confidence.
