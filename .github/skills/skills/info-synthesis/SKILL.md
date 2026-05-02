---
name: info-synthesis
description: Pull together concepts from multiple technical domains to provide integrated understanding. Use when users need to understand how concepts from different fields connect and interact—particularly for TT&C simulations, aerospace systems, or multi-domain engineering projects. Trigger when users ask how different concepts relate ("how does X affect Y?"), need knowledge spanning orbital mechanics + RF + software + protocols, want to understand cross-domain dependencies, or ask "what do I need to know about Z?" where Z involves multiple technical areas. Also use for questions requiring synthesis of theoretical knowledge with practical implementation concerns.
---

# Information Synthesis

This skill guides the integration of knowledge across multiple technical domains, helping users understand how concepts connect, interact, and influence each other. The goal is to build coherent mental models that span domain boundaries.

## When to Use This Skill

Apply this skill when the user needs:
- Understanding how multiple domains interact (e.g., orbital mechanics affects RF link budgets)
- Integrated knowledge spanning theory and practice
- Connections between abstract concepts and concrete implementation
- Cross-domain dependencies and their implications
- Holistic view of a multi-faceted technical topic

**Common trigger phrases:**
- "How does X relate to Y?"
- "Explain how [domain A] affects [domain B]"
- "What do I need to know about [multi-domain topic]?"
- "How do these pieces fit together?"
- "Walk me through [process spanning multiple domains]"

## Synthesis Process

### Step 1: Identify the Domains Involved

Determine which technical domains the question spans:

**Common domains in TT&C/aerospace:**
- Orbital mechanics (Kepler's laws, perturbations, coordinate systems)
- Attitude dynamics (orientation, rotation, control)
- RF communication (link budgets, modulation, propagation)
- Signal processing (filtering, decoding, error correction)
- Protocols (CCSDS, framing, packet structures)
- Software architecture (design patterns, data flow)
- Control theory (feedback loops, stability)
- Systems engineering (requirements, interfaces, testing)

**For each domain, identify:**
- What concepts are relevant to this question?
- What's the level of detail needed (overview vs. deep dive)?
- Which domain is primary, which are supporting?

### Step 2: Establish the Connecting Thread

Find the relationship or dependency chain linking the domains:

**Types of connections:**

**Causal Chains**: A causes B, which causes C
- Example: Orbital motion → satellite velocity → Doppler shift → frequency error → demodulation difficulty

**Shared Parameters**: One value affects multiple domains
- Example: Satellite altitude affects orbital period (mechanics) AND link budget (RF) AND eclipse duration (power)

**Constraint Propagation**: Limits in one domain constrain another
- Example: Antenna beam width (RF) constrains pointing accuracy requirements (control) which affects attitude control system design (dynamics)

**Feedback Loops**: Domains influence each other cyclically
- Example: Battery charge (power) limits heater operation (thermal), which affects battery temperature (thermal), which affects battery capacity (power)

**Identify the specific connection for this question.**

### Step 3: Build from Foundation

Start with foundational concepts and layer additional domains progressively.

**Order matters:**
1. Start with the primary domain (the one most central to the question)
2. Add supporting domains in dependency order
3. Show how each layer builds on the previous

**Example: "How does orbital mechanics affect RF link budgets?"**

**Foundation (Orbital Mechanics):**
- Satellite follows elliptical orbit determined by semi-major axis, eccentricity
- Range to ground station varies continuously
- Velocity varies (faster at perigee, slower at apogee)

**Add Geometry (Bridging Domain):**
- Range determines free-space path loss: FSPL ∝ distance²
- Elevation angle affects atmospheric path length
- Velocity determines Doppler shift

**Complete with RF (Target Domain):**
- Greater range → more path loss → weaker signal
- Low elevation → more atmosphere → additional attenuation
- High velocity → large Doppler → frequency tracking challenge
- All combine in link budget: Received Power = EIRP - FSPL - Atmospheric Loss - Other Losses + Receiver Gain

### Step 4: Provide Concrete Examples

Abstract connections are hard to grasp. Use specific numbers and scenarios.

**Example continues:**
- **LEO satellite at 400 km altitude, 7.8 km/s velocity**:
  - At zenith: range = 400 km, FSPL (at 2 GHz) = 140 dB
  - At 10° elevation: range = 1200 km, FSPL = 150 dB (+10 dB loss)
  - Doppler shift: ±52 kHz (max) at 2 GHz
  - Atmospheric attenuation: 0.3 dB (zenith) to 3 dB (low elevation)

- **GEO satellite at 35,786 km altitude, ~0 m/s relative velocity**:
  - Range ≈ 36,000 km (constant)
  - FSPL (at 12 GHz) = 206 dB
  - Doppler shift: < 1 kHz (nearly stationary)
  - Atmospheric attenuation: ~0.5 dB (always high elevation)

**Contrast shows HOW the domain-domain connection plays out differently depending on parameters.**

### Step 5: Highlight Key Insights

Synthesis should produce "aha moments"—insights that only emerge from connecting domains.

**Types of insights:**

**Unexpected Consequences**:
- "I didn't realize orbital mechanics drives frequency tracking complexity"
- **Why it matters**: System design must account for Doppler, not just signal strength

**Trade-off Revelation**:
- "Lower altitude gives shorter communication windows but stronger signals"
- **Why it matters**: Orbit selection involves RF trade-offs, not just coverage geometry

**Design Implications**:
- "GEO and LEO ground stations need fundamentally different receiver designs"
- **Why it matters**: Can't reuse LEO ground station hardware for GEO without major changes

**Bottleneck Identification**:
- "Orbital prediction error is the limiting factor for antenna pointing accuracy"
- **Why it matters**: Improving antenna servo precision won't help if orbit knowledge is poor

**State these insights explicitly after the synthesis.**

### Step 6: Provide Actionable Knowledge

Synthesis isn't just theoretical—show how the integrated understanding guides decisions.

**For implementation questions:**
- What does this multi-domain understanding mean for your code structure?
- Which domain drives the architecture?
- What interfaces are needed between domain-specific modules?

**For design questions:**
- Which domain's requirements are most stringent?
- Where can you simplify? Where must you be rigorous?
- What parameters couple the domains (and thus need careful management)?

**For debugging/analysis:**
- If you see [symptom], which domain likely has the issue?
- How do you isolate domain-specific problems from interaction effects?

## Synthesis Patterns for TT&C

### Pattern 1: Orbital Mechanics → Everything

Orbital motion is the foundation for most TT&C systems. It affects:

**→ RF Link**
- Range (path loss)
- Velocity (Doppler)
- Elevation angle (atmospheric effects)
- Line-of-sight (blockage, multipath)

**→ Antenna Pointing**
- Target angles (azimuth, elevation)
- Angular rates (tracking speed requirements)
- Slew distance between passes

**→ Communication Windows**
- Contact duration (time above horizon)
- Data volume throughput (window length × data rate)
- Handover timing (multi-ground-station networks)

**→ Power & Thermal**
- Eclipse periods (solar panel output drops to zero)
- Sun angle on panels (power generation)
- Solar heating vs. eclipse cooling

**Synthesis example**: "For a LEO satellite in sun-synchronous orbit, orbital mechanics determines not just contact times but also whether passes occur during day or night, which affects both RF link budgets (ionospheric conditions vary day/night) and satellite power availability (eclipse duration affects battery capacity needs)."

### Pattern 2: RF → Protocols → Software

Signal quality drives protocol choices, which drive software architecture:

**RF Domain:**
- Signal-to-noise ratio (SNR)
- Bit error rate (BER)
- Doppler-induced frequency uncertainty

**→ Protocol Domain:**
- Error correction needed (Reed-Solomon, turbo codes)
- Frame synchronization robustness
- Packet size (short packets for high BER environments)
- Retransmission strategies

**→ Software Domain:**
- Decoder complexity (soft vs. hard decision decoding)
- Buffer sizing (for out-of-order packets)
- State machine design (for protocol handling)
- Real-time constraints (decoding latency vs. tracking loop)

**Synthesis example**: "Low SNR LEO links (SNR = 3 dB) require strong error correction (rate-1/2 turbo codes), which demands soft-decision Viterbi decoders, which in turn require floating-point processing and can introduce 10-100ms latency—this latency feeds back into your antenna tracking loop design, potentially requiring open-loop prediction during critical tracking phases."

### Pattern 3: Command Validation Across Domains

Command validation isn't one domain—it's synthesis of:

**Software/Protocol Layer:**
- Syntax checking (well-formed packets)
- CRC validation (uncorrupted transmission)
- Sequence number continuity

**→ Spacecraft State Layer:**
- Mode checking (command allowed in current mode?)
- Subsystem status (is the target subsystem operational?)
- Resource availability (enough power/memory?)

**→ Physics/Safety Layer:**
- Parameter bounds (thruster burn within propellant budget?)
- Thermal limits (won't overheat components?)
- Attitude constraints (sun-pointing safe for solar panels?)

**→ Mission Rules Layer:**
- Operational procedures (pre-requisite commands executed?)
- Ground authorization (command authenticated?)
- Conflict resolution (contradictory commands in queue?)

**Synthesis example**: "A command to fire a thruster must pass four validation layers: (1) Protocol layer confirms packet integrity and proper CCSDS framing, (2) State layer verifies spacecraft is in 'maneuver-enabled' mode and thruster subsystem reports healthy, (3) Physics layer checks burn duration doesn't exceed propellant reserves and resulting delta-V won't violate attitude constraints, (4) Mission rules layer confirms ground authorization signature and no conflicting commands in queue. Only when all four layers approve does the command execute."

## Output Format

Structure synthesized information clearly:

### Topic Overview
[One paragraph: what domains are involved, what question we're answering]

### Foundation: [Primary Domain]
[Core concepts from the foundational domain]

### Connection: [How Primary Domain Affects Secondary Domain]
[Explicit causal chain or dependency]

### Integration: [Secondary Domain(s)]
[How the additional domains respond to or interact with primary domain]

### Concrete Example
**Scenario**: [Specific parameters]
**Domain 1 Behavior**: [What happens in domain 1]
**→ Domain 2 Impact**: [How domain 2 responds]
**→ Domain 3 Impact** (if applicable): [How domain 3 responds]
**Result**: [Overall system behavior]

### Key Insights
1. [Insight 1: something not obvious from single-domain view]
2. [Insight 2: ...]
3. [Insight 3: ...]

### Practical Implications
**For implementation**: [How this affects code/design]
**For analysis**: [How to debug/validate this multi-domain interaction]
**For decision-making**: [What this understanding lets you choose wisely]

## Examples

### Example 1: How CCSDS Packets Flow Through a Ground Station

**User**: "Explain how CCSDS packets flow through a ground station from antenna to data archive."

**Response**:

#### Topic Overview
CCSDS telemetry packet processing spans four domains: RF (signal reception), signal processing (demodulation/decoding), protocol handling (packet extraction), and data management (storage/distribution). Each layer transforms the signal progressively from electromagnetic waves to structured data.

#### Foundation: RF Domain

An electromagnetic wave carrying CCSDS-encoded telemetry arrives at the ground station antenna:
- **Frequency**: Carrier frequency (e.g., 2.2 GHz for S-band)
- **Modulation**: Typically BPSK or QPSK
- **Power level**: Very weak (often -120 dBm at antenna)
- **Doppler shift**: ±tens of kHz for LEO

The antenna captures this weak signal and sends it to the receiver.

#### Connection: RF → Signal Processing

The receiver performs several critical functions:

**Frequency Tracking**:
- Input: Doppler-shifted carrier (e.g., 2.200.035 GHz instead of 2.200.000 GHz)
- Process: Phase-locked loop (PLL) locks onto carrier despite Doppler
- Output: Downconverted baseband signal, frequency-stabilized

**Demodulation**:
- Input: Modulated baseband signal
- Process: Demodulator extracts symbols (e.g., BPSK → bits)
- Output: Raw bitstream with errors

**Error Correction**:
- Input: Raw bitstream (might have bit errors from noise)
- Process: Reed-Solomon or turbo code decoder corrects errors
- Output: Corrected bitstream (high confidence)

**Why this matters**: If the RF SNR is too low (< required threshold), error correction fails, and no valid packets emerge downstream—the RF domain gatekeeps everything.

#### Integration: Protocol Layer

The corrected bitstream now enters CCSDS protocol processing:

**Frame Synchronization**:
- Input: Continuous bitstream
- Process: Search for CCSDS synchronization marker (0x1ACFFC1D)
- Output: Frame boundaries identified

**Frame Decommutation**:
- Input: CCSDS Transfer Frames
- Process: Extract packets from frames, de-randomize, check frame CRC
- Output: CCSDS Space Packets

**Packet Processing**:
- Input: Space Packets (each with header: version, type, APID, sequence count, length)
- Process: Parse headers, validate packet integrity, route by APID
- Output: Data field extracted, routed to appropriate handler

**Why this matters**: Each CCSDS packet header contains an Application Process Identifier (APID) that tells the ground station which subsystem generated this data—engineering telemetry, payload data, housekeeping, etc. The protocol layer demultiplexes packets to the right destination based on APID.

#### Integration: Data Management Layer

Finally, extracted telemetry data flows to storage and distribution:

**Database Insertion**:
- Packets are parsed into engineering units (voltages, temperatures, etc.)
- Time-tagged with ground receipt time or spacecraft time (from packet header)
- Stored in telemetry database (e.g., PostgreSQL, InfluxDB)

**Real-time Distribution**:
- Live telemetry streamed to mission control displays
- Alerts generated if values exceed thresholds

**Archive**:
- Raw packets archived for replay/reprocessing
- Processed data stored for long-term analysis

#### Concrete Example

**Scenario**: ISS telemetry downlink

**RF Domain**:
- S-band downlink at 2.2 GHz
- Received power: -115 dBm (very weak)
- SNR after low-noise amplifier: 8 dB
- Doppler shift: up to ±40 kHz (ISS velocity: 7.7 km/s)

**→ Signal Processing**:
- PLL tracks 40 kHz Doppler shift, locks onto carrier
- QPSK demodulator extracts 2 bits per symbol
- Rate-1/2 convolution code decoder corrects errors, outputs 12 Mbps bitstream

**→ Protocol Layer**:
- Frame sync finds CCSDS frames (every 1115 bytes)
- Packets extracted: APID 100 (power system), APID 200 (thermal), APID 300 (payload)
- Each packet routed to appropriate processor

**→ Data Management**:
- Power system telemetry (APID 100) → database table `power_telemetry`
- Thermal data (APID 200) → real-time display in mission control
- Payload data (APID 300) → science data archive

**Result**: Photons from ISS solar panels powering a transmitter 400 km away become database entries on Earth showing battery voltage = 160V, within 2-3 seconds of measurement on ISS.

#### Key Insights

1. **RF quality gatekeeps everything**: If SNR drops below decoder threshold, the entire downstream processing chain gets zero valid packets. RF is the bottleneck.

2. **APID is the routing key**: The protocol layer doesn't "understand" telemetry content—it just reads APID from packet headers and routes accordingly. Application layer interprets packet data fields.

3. **Multiple time-tagging layers**: RF layer timestamps signal lock, frame sync timestamps frame arrival, packet processor timestamps packet extraction, and packet data itself may contain spacecraft clock time. These timestamps serve different purposes (RF diagnostics vs. data correlation).

4. **Buffering requirements compound**: Each layer buffers data during processing. RF receiver buffers samples (ms-level), demodulator buffers symbols (ms-level), packet processor buffers frames (seconds), database buffers transactions (minutes). End-to-end latency accumulates across all layers.

#### Practical Implications

**For implementation**:
- Your ground station software architecture should mirror these layers: RF→Demod→Protocol→Data modules
- Use producer-consumer queues between layers (RF thread → demod thread → protocol thread → database thread)
- Each layer should be testable independently (inject known bitstream into demod, bypass RF)

**For debugging**:
- If no packets appear in database: check each layer in order
  - RF lock indicator (PLL locked?)
  - Demodulator SNR (above threshold?)
  - Frame sync status (finding sync markers?)
  - Packet parser (CRC passing?)
- Symptoms localize to specific layers (e.g., "frame sync works but no valid packets" → packet CRC failures → bit errors after frame sync)

**For performance tuning**:
- Bottleneck is usually the RF layer (can't improve if signal is too weak) or database insertion (can overwhelm with high data rates)
- Optimize intermediate layers (demod, protocol) for throughput, but they rarely limit performance

---

This synthesis connects RF physics → signal processing → protocol standards → software architecture, showing how a photon becomes a database entry.

## Tips for Effective Synthesis

**Start broad, then drill deep selectively**: Give overview of all domains first, then deep-dive into the most critical connections.

**Use analogies across domains**: "RF Doppler tracking is like a car's cruise control—both are feedback loops compensating for external disturbances."

**Make implicit dependencies explicit**: State things like "this parameter from domain A is an input to calculation in domain B."

**Quantify when possible**: "The link budget varies by 10 dB" is more informative than "the link budget varies significantly."

**Acknowledge complexity**: If the full story requires graduate-level knowledge in three fields, say so—but still provide an accessible synthesis at a useful level.

**Connect to user's goal**: Is this synthesis for understanding, implementation, or troubleshooting? Tailor the emphasis.

## When Synthesis is Complete

You've successfully synthesized when:
- The user understands how domains connect and influence each other
- Cross-domain dependencies are explicit
- The user can explain a multi-domain process in their own words
- Follow-up questions focus on implementation details within a single domain, not cross-domain confusion
- The user can predict how changes in one domain affect others
