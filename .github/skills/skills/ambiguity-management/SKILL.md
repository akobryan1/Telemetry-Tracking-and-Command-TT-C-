---
name: ambiguity-management
description: Handle incomplete information and undefined requirements by making deliberate engineering choices and documenting assumptions. Use when users face missing data, unclear specifications, undefined parameters, or need to make progress despite uncertainty. Particularly valuable for TT&C simulations, aerospace systems, and complex projects where perfect information is unavailable. Trigger when users say "I don't know...", "what if I don't have...", "the spec doesn't say...", need to handle missing data gracefully, or must make engineering decisions with partial information.
---

# Ambiguity Management

This skill guides systematic handling of incomplete information, helping users make progress when specifications are unclear, data is missing, or requirements are undefined—while documenting assumptions for future validation.

## When to Use This Skill

Apply this skill when the user faces:
- Missing data or parameters
- Unclear specifications or requirements
- Undefined system behaviors
- Uncertainty about design choices
- Need to make progress despite incomplete information

**Common trigger phrases:**
- "I don't know [parameter/requirement]"
- "What if I don't have [data]?"
- "The spec doesn't say how to handle [case]"
- "Which approach should I use?"
- "How do I proceed without knowing [X]?"

## Ambiguity Management Process

### Step 1: Identify the Source of Ambiguity

Categorize the ambiguity to determine handling strategy:

**Type 1: Missing Data**
- Example: "I don't have the satellite's transmit power"
- Strategy: Use typical value, document assumption, flag for validation

**Type 2: Undefined Behavior**
- Example: "The spec doesn't say what happens if CRC fails during a critical command"
- Strategy: Make a conservative choice (reject command), document decision, seek clarification later

**Type 3: Underspecified Requirements**
- Example: "The requirement says 'low latency' but doesn't define a threshold"
- Strategy: Define a concrete threshold (e.g., <100ms), document rationale, mark for stakeholder confirmation

**Type 4: Multiple Valid Approaches**
- Example: "Should I use SGP4 or a numerical integrator for orbit propagation?"
- Strategy: Evaluate trade-offs, choose based on criteria (accuracy vs. speed), document why

**Type 5: Future Uncertainty**
- Example: "I don't know what satellites we'll track next year"
- Strategy: Design for flexibility (configurable satellite list), avoid hardcoding

### Step 2: Determine Acceptable Risk

Not all ambiguities are equally critical. Assess impact:

**Low Risk** (can proceed immediately):
- Ambiguity affects non-critical path
- Easy to change later
- Failure is detectable and recoverable
- **Action**: Make reasonable assumption, document, proceed

**Medium Risk** (proceed with caution):
- Ambiguity affects important but not safety-critical functionality
- Changing later requires moderate rework
- Failure might go undetected temporarily
- **Action**: Make conservative choice, document explicitly, add validation checks

**High Risk** (must resolve before proceeding):
- Ambiguity affects safety, security, or mission-critical functionality
- Wrong choice could cause data loss, hardware damage, or mission failure
- Changing later requires major rework
- **Action**: Don't guess—seek clarification from stakeholders or halt until resolved

**Example - TT&C Command Validation**:
- **Low risk**: "What units for telemetry timestamps—seconds or milliseconds?" 
  - Impact: Display formatting only, easy to fix
  - Action: Assume seconds (standard), document assumption

- **Medium risk**: "How long should command queue be—10 or 100 commands?"
  - Impact: Affects memory usage and latency
  - Action: Choose 50 (middle ground), document, add configuration parameter for easy tuning

- **High risk**: "What happens if we receive conflicting commands (fire thruster north + fire thruster south simultaneously)?"
  - Impact: Could damage spacecraft or waste propellant
  - Action: **Do not guess**—define conflict resolution policy with spacecraft team before implementing

### Step 3: Make Deliberate Choices

When you must proceed despite ambiguity, make informed, transparent choices:

**A. Use Domain-Specific Defaults**

Many engineering fields have "typical" values:

**TT&C/Aerospace Typical Values**:
- Satellite transmit power: 1-10W (varies by satellite class)
- Ground station antenna gain: 30-50 dBi (depends on dish size)
- Link margin: 3-6 dB (typical for reliable links)
- Bit error rate threshold: 10^-6 (good link) to 10^-3 (marginal link)
- TLE update frequency: Every 3-7 days for LEO
- Command timeout: 5-30 seconds

**Use these when**:
- No specific data available
- Placeholder needed for prototyping
- Order-of-magnitude accuracy sufficient initially

**Always document**: "Assumed 5W transmit power (typical for smallsat); validate with actual spacecraft specs."

**B. Choose Conservative Options**

When uncertain, err on the side of safety/robustness:

**Examples**:
- **If unsure about buffer size**: Make it larger (wastes memory but prevents overflow)
- **If unsure about timeout duration**: Make it longer (reduces false timeouts, slightly increases latency)
- **If unsure about error handling**: Reject questionable data (safer than accepting corrupt data)

**Rationale**: Conservative choices reduce risk. You can optimize later once you have better information.

**C. Make Choices Configurable**

If the "right" value is unknown, make it a parameter:

**Example**:
```python
# Ambiguity: How many satellites will we track simultaneously?
# Resolution: Make it configurable

class GroundStation:
    def __init__(self, max_satellites=5):  # Default: 5 (conservative guess)
        self.max_satellites = max_satellites
        # ...
```

**Benefit**: When you learn the real requirement, change one config value instead of rewriting code.

**D. Defer Decisions When Possible**

Some decisions don't need to be made now:

**Example - Coordinate System Choice**:
- **Immediate need**: Store satellite position
- **Ambiguity**: Should we use ECI, ECEF, or geodetic coordinates?
- **Deferral**: Store in ECI (SGP4 output), add conversion functions for ECEF/geodetic, let user choose coordinate system when retrieving positions
- **Benefit**: Deferred decision doesn't block progress; flexibility maintained

### Step 4: Document Assumptions Explicitly

**Assumptions are technical debt.** Document them so:
- Future you remembers what's uncertain
- Others understand what's provisional
- Validation can target known uncertainties

**Documentation Template**:

```
ASSUMPTION: [What you assumed]
RATIONALE: [Why this assumption is reasonable]
IMPACT: [What breaks if assumption is wrong]
VALIDATION: [How to verify this assumption]
PRIORITY: [Low/Medium/High - urgency of validating]
```

**Example**:

```python
# ASSUMPTION: Satellite transmit power is 5W
# RATIONALE: Typical for smallsats in this class; no spec available yet
# IMPACT: Link budget calculations will be wrong if actual power differs significantly
#         (error scales linearly with power in dB: 10W → +3dB, 2.5W → -3dB)
# VALIDATION: Request transmit power from spacecraft team; update when available
# PRIORITY: Medium (affects link planning but not safety)

satellite_tx_power_watts = 5  # TODO: Replace with actual value
```

**Where to document**:
- **In code**: Comments near assumption (as above)
- **In design docs**: "Assumptions and Limitations" section
- **In README**: Alert users to provisional values
- **In issue tracker**: Create ticket to resolve assumption

### Step 5: Add Validation and Warnings

When operating under assumptions, add checks to detect if assumptions are violated:

**Example - Assumed Antenna Gain**:

```python
# ASSUMPTION: Ground station antenna gain is 40 dBi (typical 3-meter dish)
ANTENNA_GAIN_DBI = 40  # TODO: Measure actual antenna gain

def compute_link_budget(distance_km, freq_ghz):
    # ... calculations ...
    received_power_dbm = eirp - fspl + ANTENNA_GAIN_DBI
    
    # Validation check: warn if received power is unexpectedly high/low
    if received_power_dbm > -50:
        warnings.warn(f"Received power unusually high ({received_power_dbm:.1f} dBm). "
                      f"Check antenna gain assumption ({ANTENNA_GAIN_DBI} dBi).")
    if received_power_dbm < -140:
        warnings.warn(f"Received power unusually low ({received_power_dbm:.1f} dBm). "
                      f"Check antenna gain assumption ({ANTENNA_GAIN_DBI} dBi).")
    
    return received_power_dbm
```

**Benefit**: If assumption is wrong, you get early warning instead of silent incorrect results.

### Step 6: Create a Validation Checklist

Track all assumptions in one place:

**Assumptions Log** (e.g., `ASSUMPTIONS.md`):

| ID | Assumption | Impact | Validation Method | Status | Priority |
|----|------------|--------|-------------------|--------|----------|
| A1 | Satellite TX power = 5W | Link budget ±3 dB | Confirm with spacecraft team | Unvalidated | Medium |
| A2 | TLE updated weekly | Position error <5 km | Monitor TLE age | Validated | Low |
| A3 | Commands <256 bytes | Fits in buffer | Check protocol spec | Validated | High |
| A4 | Max 5 simultaneous satellites | No overflow | Confirm mission ops plan | Unvalidated | High |

**Review this log regularly**: As you gain information, mark assumptions as validated or update with correct values.

## Patterns for Common TT&C Ambiguities

### Pattern 1: Missing Satellite Parameters

**Scenario**: Building a link budget calculator, but don't have actual satellite transmit power, antenna gain, or EIRP.

**Resolution Strategy**:

1. **Research typical values** for satellite class (cubesat, smallsat, traditional)
   - Cubesat (1-3U): 0.5-2W transmit power
   - Smallsat (50-200 kg): 2-10W
   - Traditional (>500 kg): 5-50W

2. **Use mid-range estimate** (e.g., 5W for smallsat)

3. **Add sensitivity analysis**: Show link budget for range of powers (1W, 5W, 10W)
   - Reveals how sensitive results are to this assumption
   - Example output: "Link closes with 3 dB margin if TX power ≥3W"

4. **Document clearly**:
   ```python
   # ASSUMPTION: Satellite transmit power = 5W
   # SENSITIVITY: ±3 dB variation if actual power is 2.5W to 10W
   # VALIDATION: Request from spacecraft team; high priority if link margin <6 dB
   ```

5. **Flag for validation**: Create task "Get actual satellite transmit power from spacecraft team"

### Pattern 2: Undefined Protocol Behavior

**Scenario**: Implementing CCSDS packet parser, but specification doesn't define behavior when packet length field exceeds buffer size.

**Resolution Strategy**:

1. **Identify safety implications**: 
   - If buffer overflow → potential crash or security vulnerability
   - If truncated packet accepted → corrupt data might propagate

2. **Choose conservative behavior**: **Reject packet** (safer than accepting)

3. **Document decision**:
   ```python
   def parse_packet(data):
       packet_length = extract_length_field(data)
       
       # DECISION: Reject packets exceeding buffer size
       # RATIONALE: CCSDS spec doesn't define behavior; rejecting prevents buffer overflow
       # ALTERNATIVE CONSIDERED: Truncate packet (rejected due to corrupt data risk)
       # VALIDATION: Confirm with ground system team; might need to handle large packets differently
       if packet_length > MAX_BUFFER_SIZE:
           logger.warning(f"Packet length {packet_length} exceeds buffer size {MAX_BUFFER_SIZE}; rejecting")
           return None  # Reject packet
       
       # ... parse packet ...
   ```

4. **Log occurrences**: Track how often this happens (if frequent, may indicate buffer size assumption is wrong)

5. **Seek clarification**: Ask protocol designer or standards body for guidance

### Pattern 3: Ambiguous Requirements ("Low Latency")

**Scenario**: Requirement says "command uplink latency should be low" but doesn't quantify "low."

**Resolution Strategy**:

1. **Research domain norms**:
   - Typical command latency for LEO satellites: <5 seconds (limited by contact duration)
   - For time-critical commands (e.g., collision avoidance): <1 second
   - For routine commands (e.g., mode changes): <30 seconds acceptable

2. **Propose concrete threshold**: "Low latency ≡ <5 seconds end-to-end"

3. **Justify choice**:
   - Provides enough time for acknowledgment before satellite passes out of view (typical 10-minute pass)
   - Faster than human operator reaction time (reduces operator stress)

4. **Document and seek approval**:
   ```markdown
   **REQUIREMENT INTERPRETATION**:
   - Original: "Command uplink latency should be low"
   - Interpreted as: Command acknowledged within 5 seconds of ground transmission
   - Rationale: 5 seconds allows for round-trip propagation (0.003s), protocol overhead (0.1s),
     and spacecraft processing (1s), with 3.9s margin for variability
   - Status: **Pending stakeholder approval**
   - Approval from: [Mission Manager, Flight Software Lead]
   ```

5. **Design for the defined threshold**: Implement with 5-second target, add latency monitoring to verify

### Pattern 4: Unknown Future Requirements

**Scenario**: Building ground station for current satellite, but future missions might track different satellite types (GEO, MEO, interplanetary).

**Resolution Strategy**:

1. **Identify what might vary**:
   - Orbital regime (LEO, MEO, GEO, interplanetary)
   - Frequency bands (VHF, UHF, S-band, X-band, Ka-band)
   - Protocols (CCSDS, custom, proprietary)

2. **Design for extensibility** (not full generality—that's over-engineering):
   - **Do**: Make orbit propagator pluggable (SGP4 for Earth orbits, Spice for interplanetary)
   - **Don't**: Support every conceivable orbit type in v1 (YAGNI—"You Aren't Gonna Need It")

3. **Use abstraction where cheap**:
   ```python
   class Satellite(ABC):
       @abstractmethod
       def get_position(self, time):
           """Return position at specified time."""
           pass
   
   class SGP4Satellite(Satellite):
       def get_position(self, time):
           # SGP4-specific implementation
           pass
   
   class SpiceSatellite(Satellite):
       def get_position(self, time):
           # SPICE-specific implementation (for future interplanetary missions)
           pass
   ```

4. **Document extensibility points**:
   ```markdown
   ## Extension Points
   - **Orbit Propagators**: Subclass `Satellite` to add new propagators (currently: SGP4; future: SPICE, numerical)
   - **Frequency Bands**: Add to `SUPPORTED_BANDS` dict in `rf_link.py` (currently: S-band; future: X-band, Ka-band)
   - **Protocols**: Implement `PacketParser` interface (currently: CCSDS; future: custom protocols)
   ```

5. **YAGNI principle**: Don't implement extensibility until you actually need it (but design so it's *possible*)

### Pattern 5: Missing Experimental Data

**Scenario**: Modeling antenna gain pattern, but don't have measured data—only manufacturer's theoretical spec.

**Resolution Strategy**:

1. **Use theoretical model initially**:
   - Manufacturer spec: "40 dBi peak gain, 2° 3-dB beamwidth"
   - Model as Gaussian pattern: `gain(theta) = peak_gain - 12 * (theta / beamwidth)^2`

2. **Document uncertainty**:
   ```python
   # ASSUMPTION: Antenna pattern follows Gaussian model per manufacturer spec
   # UNCERTAINTY: Actual pattern may have sidelobes, asymmetry not captured in model
   # IMPACT: Gain estimate may be off by ±2 dB off-boresight
   # VALIDATION: Measure antenna pattern on antenna range (scheduled Q3 2026)
   # PRIORITY: Low (affects edge cases only; boresight gain is accurate)
   ```

3. **Add measurement hooks**:
   ```python
   def antenna_gain(theta, phi, measured_pattern=None):
       if measured_pattern is not None:
           return measured_pattern.lookup(theta, phi)  # Use actual data if available
       else:
           return gaussian_pattern(theta, phi)  # Fall back to theoretical model
   ```

4. **Plan measurement campaign**: Schedule antenna pattern measurement, prepare to swap in real data

5. **Assess sensitivity**: If gain uncertainty (±2 dB) doesn't affect link closure, defer measurement; if critical, expedite

## Output Format

When managing ambiguity, structure response clearly:

### Ambiguity Identified
**What's missing/unclear**: [Describe the ambiguity]
**Impact**: [How this affects the system/project]
**Risk level**: [Low/Medium/High]

### Proposed Resolution
**Approach**: [What you'll do to proceed]
**Rationale**: [Why this approach is reasonable]
**Alternatives considered**: [Other options, why not chosen]

### Assumptions Made
1. [Assumption 1]
   - **Basis**: [Why this assumption is reasonable]
   - **Impact if wrong**: [What breaks]
   - **Validation plan**: [How to verify]
2. [Assumption 2]
   - ...

### Implementation Guidance
[Code snippet, design decision, or configuration showing how to implement the resolution]

### Validation Checklist
- [ ] [Action 1 to validate assumption]
- [ ] [Action 2 to confirm decision]
- [ ] [Action 3 to measure actual data]

## Example

### Example: Handling Missing Doppler Compensation Data

**User**: "I'm building a satellite receiver, but I don't know how accurately I can predict the satellite's orbit—and that affects Doppler compensation. How do I handle this?"

**Response**:

#### Ambiguity Identified

**What's missing/unclear**: Orbital prediction accuracy (position error in km), which determines Doppler prediction error (frequency error in Hz)

**Impact**: 
- If Doppler prediction error exceeds receiver's tracking bandwidth, signal won't be acquired
- Example: 1 km position error → ~13 Hz Doppler error at 2 GHz
- If tracking bandwidth is ±1 kHz, can tolerate ~75 km position error; if ±100 Hz, need <8 km accuracy

**Risk level**: **Medium** (affects signal acquisition reliability but not safety)

#### Proposed Resolution

**Approach**: 
1. Use fresh TLEs (<3 days old) for orbital prediction → expect ~1-5 km position accuracy
2. Design receiver with ±2 kHz Doppler tracking bandwidth (conservative)
3. Add coarse frequency search (±5 kHz) in case TLE is stale
4. Measure actual Doppler error during initial tests

**Rationale**:
- Fresh TLEs give good accuracy for LEO satellites (validated by satellite tracking community)
- ±2 kHz bandwidth handles up to ~150 km position error (very conservative margin)
- Coarse search catches edge cases (old TLE, unexpected orbit maneuver)
- Measurement during tests will reveal actual error, allowing optimization later

**Alternatives considered**:
- **Narrower bandwidth (±500 Hz)**: Would reduce noise but risk missing signal if TLE is slightly stale (rejected—too risky)
- **Wider bandwidth (±10 kHz)**: Would always acquire but degrades SNR unnecessarily (rejected—wastes performance)

#### Assumptions Made

1. **TLEs updated every 3 days**
   - **Basis**: Standard practice for active tracking (SpaceTrack, Celestrak)
   - **Impact if wrong**: If TLE is 1 week old, position error could reach 10-20 km → Doppler error ~130-260 Hz (still within ±2 kHz bandwidth, okay)
   - **Validation plan**: Monitor TLE age in software; warn if >3 days old

2. **No orbit maneuvers during pass**
   - **Basis**: Most satellites don't maneuver frequently; maneuvers are typically planned/announced
   - **Impact if wrong**: Sudden orbit change could introduce large Doppler error, signal lost
   - **Validation plan**: Subscribe to satellite operator's maneuver notifications; add manual override for predicted Doppler

3. **Receiver can track ±2 kHz Doppler rate**
   - **Basis**: Modern SDRs and PLLs handle this easily (e.g., USRP, PlutoSDR)
   - **Impact if wrong**: If PLL bandwidth is narrower, might lose lock during high Doppler rate (max for LEO ~1 Hz/s)
   - **Validation plan**: Test receiver PLL with simulated Doppler sweep; verify lock maintained

#### Implementation Guidance

```python
import numpy as np
from datetime import datetime, timedelta

class DopplerCompensator:
    def __init__(self, tle_max_age_days=3, doppler_bandwidth_hz=2000):
        self.tle_max_age_days = tle_max_age_days
        self.doppler_bandwidth_hz = doppler_bandwidth_hz
    
    def predict_doppler(self, satellite, ground_station, time, carrier_freq_hz):
        # Check TLE age
        tle_age = (datetime.utcnow() - satellite.tle_epoch).days
        if tle_age > self.tle_max_age_days:
            logger.warning(f"TLE is {tle_age} days old (>{self.tle_max_age_days} days). "
                           f"Doppler prediction accuracy degraded.")
        
        # Predict Doppler from orbital propagation
        velocity = satellite.get_velocity(time)
        range_rate = np.dot(velocity, line_of_sight_vector)
        doppler_hz = -(range_rate / 299792.458) * carrier_freq_hz  # c = 299792.458 km/s
        
        # ASSUMPTION: TLE position error ~1-5 km (fresh TLE)
        # → Doppler error ~13-65 Hz at 2 GHz
        # Our tracking bandwidth (±2 kHz) provides large margin
        
        return doppler_hz
    
    def acquire_signal(self, predicted_doppler_hz):
        # Start with predicted Doppler
        search_center = predicted_doppler_hz
        
        # Search within tracking bandwidth
        for freq_offset in np.arange(-self.doppler_bandwidth_hz, 
                                      self.doppler_bandwidth_hz, 
                                      step=100):  # 100 Hz steps
            if self.try_lock(search_center + freq_offset):
                logger.info(f"Signal acquired at {freq_offset:.0f} Hz from predicted Doppler")
                return search_center + freq_offset
        
        # If not found, expand search (coarse search for stale TLE case)
        logger.warning("Signal not found within ±2 kHz; expanding search to ±5 kHz")
        for freq_offset in np.arange(-5000, 5000, step=500):
            if self.try_lock(search_center + freq_offset):
                logger.warning(f"Signal acquired at {freq_offset:.0f} Hz from predicted (large error!)")
                return search_center + freq_offset
        
        logger.error("Signal acquisition failed")
        return None
```

#### Validation Checklist

- [ ] **Verify TLE update frequency**: Confirm TLEs updated every 3 days (check SpaceTrack)
- [ ] **Measure Doppler error**: During first satellite pass, log predicted vs. actual Doppler → quantify error
- [ ] **Test with stale TLE**: Intentionally use 7-day-old TLE, verify coarse search acquires signal
- [ ] **Test PLL tracking**: Simulate Doppler sweep at max rate (1 Hz/s), verify PLL maintains lock
- [ ] **Optimize bandwidth**: If measured Doppler error is consistently <50 Hz, consider narrowing bandwidth to ±500 Hz (improves SNR)

---

**Next steps**:
1. Implement Doppler compensator with ±2 kHz bandwidth (conservative design)
2. Test with first satellite pass, measure actual Doppler error
3. Refine bandwidth based on measurements (optimize after validation)

---

This resolution lets you proceed immediately (using reasonable assumptions) while documenting what needs validation. After initial tests, you'll have real data to optimize the design.

## Tips for Effective Ambiguity Management

**Don't let ambiguity paralyze you**: Perfect information is rare. Make informed choices and proceed, documenting assumptions clearly.

**Prefer conservative over aggressive**: When uncertain, choose the safer/more robust option. You can optimize later once you have data.

**Track all assumptions**: Maintain an assumptions log or use TODO comments. Untracked assumptions become forgotten bugs.

**Add validation hooks**: Design so assumptions can be swapped out for real data easily (e.g., configuration parameters, pluggable models).

**Communicate uncertainty**: Tell stakeholders "This is based on assumption X; we'll validate in phase Y." Transparency builds trust.

**Revisit assumptions regularly**: Schedule reviews (e.g., monthly) to check if assumptions are still valid or can now be replaced with real data.

**Distinguish "unknown" from "unknowable"**: Some things you'll learn later (satellite transmit power → ask spacecraft team). Others are inherently uncertain (future user needs → design for flexibility, not omniscience).

## When Ambiguity Management is Complete

You've succeeded when:
- The user can proceed despite missing information (not blocked)
- All assumptions are documented with rationale and validation plan
- Risks are assessed and managed appropriately (high-risk ambiguities escalated or resolved)
- Design accommodates likely changes (configurable, extensible where appropriate)
- Validation checkpoints defined (know when to revisit assumptions)
