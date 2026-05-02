---
name: critical-thinking
description: Question assumptions, evaluate trade-offs, and identify potential flaws in technical approaches. Use when users propose solutions and want critique/validation, ask "is this the right way?", "what am I missing?", "should I use X or Y?", evaluate design decisions or algorithm choices, need to validate assumptions about system behavior, or request feedback on their proposed approach. Particularly valuable for TT&C simulations, aerospace systems, and complex engineering projects where assumptions about orbital mechanics, RF propagation, protocols, or system behavior need scrutiny. Trigger when users show uncertainty about their approach or explicitly request critical analysis of their technical decisions.
---

# Critical & Analytical Thinking

This skill guides rigorous analysis of technical proposals, helping users question assumptions, identify potential issues, and evaluate trade-offs systematically. The goal is to strengthen technical decisions through critical examination before implementation.

## When to Use This Skill

Apply this skill when the user:
- Proposes a technical approach and wants validation or critique
- Asks comparative questions ("should I use X or Y?")
- Expresses uncertainty about whether their approach is correct
- Needs to identify what they might be missing or overlooking
- Wants to understand trade-offs between options
- Makes statements about how systems work that need verification

**Common trigger phrases:**
- "Is this the right way to...?"
- "What am I missing?"
- "Should I use X or Y?"
- "Am I right that...?"
- "What's wrong with my approach to...?"
- "Would it be better to...?"

## Critical Analysis Process

### Step 1: Understand the Proposal

Before critiquing, ensure you understand what the user is proposing:

**Clarify the approach:**
- What specifically are they proposing to do?
- What assumptions are they making (stated or implied)?
- What problem are they trying to solve?
- What constraints or requirements exist?

**For TT&C and aerospace contexts:**
- What physical phenomena are being modeled?
- What fidelity level is intended (high-fidelity physics vs. functional approximation)?
- What standards or protocols are involved (CCSDS, etc.)?
- What operational scenarios must be supported?

Don't proceed to critique until the proposal is clear.

### Step 2: Identify Assumptions

Make implicit assumptions explicit. Many technical problems arise from unstated assumptions that turn out to be incorrect.

**Common assumption categories:**

**Physical/Mathematical Assumptions:**
- Simplifications in physics (e.g., "I'll ignore atmospheric drag for LEO satellites")
- Approximations in calculations (e.g., "I'll use small-angle approximations")
- Coordinate system choices (e.g., "Earth-centered inertial is sufficient")

**Operational Assumptions:**
- Usage patterns (e.g., "The ground station will always track one satellite at a time")
- Environmental conditions (e.g., "Weather won't significantly affect the RF link")
- Timing (e.g., "Commands will always be sent when the satellite is in view")

**System Behavior Assumptions:**
- How components interact (e.g., "The telemetry packets will always arrive in order")
- Error handling (e.g., "Packet corruption is rare enough to ignore")
- Performance (e.g., "Real-time processing is fast enough to keep up")

**For each assumption, ask:**
- Is this assumption stated or implied?
- Under what conditions is this assumption valid?
- What happens if this assumption is violated?
- Is the user aware they're making this assumption?

### Step 3: Evaluate Correctness

Assess whether the proposed approach is technically sound.

**Physical accuracy:**
- Does the physics make sense?
- Are the equations appropriate for the scenario?
- Are units consistent?
- Are coordinate systems used correctly?

**Example: Doppler Shift**
- **Assumption**: "Doppler shift only matters for LEO satellites, not GEO"
- **Analysis**: For LEO, range rate can exceed 7 km/s → Doppler shift at 2 GHz is ~47 kHz (significant)
- For GEO, satellite appears stationary → negligible Doppler shift
- **Verdict**: Assumption is generally correct, though GEO satellites in inclined orbits do have small Doppler effects

**Algorithmic correctness:**
- Will the proposed algorithm produce correct results?
- Are there edge cases that break the logic?
- Are there numerical stability concerns?

**Example: Orbit Propagation**
- **Assumption**: "Simple Keplerian two-body propagation is good enough for LEO over days"
- **Analysis**: Two-body neglects J2 (Earth oblateness), which causes significant secular drift in RAAN and argument of perigee for LEO
- Errors accumulate: after 24 hours, position error can exceed 100 km
- **Verdict**: Assumption is incorrect for multi-day simulations; need at least J2 perturbations

**Protocol conformance:**
- If using standards (like CCSDS), does the approach comply?
- Are there required fields or sequences being skipped?

### Step 4: Identify Potential Flaws

Look for weaknesses, vulnerabilities, or failure modes in the proposed approach.

**Categories of flaws:**

**1. Completeness Issues**
- Missing functionality ("What if the satellite enters eclipse during a pass?")
- Unhandled edge cases ("What happens at the pole where azimuth is undefined?")
- Missing validation ("How do you prevent invalid commands from being sent?")

**2. Scalability Concerns**
- Performance bottlenecks ("Will this algorithm scale to 100 satellites?")
- Memory limitations ("Storing full telemetry history could exhaust memory")
- Complexity explosion ("Adding each new feature doubles the state space")

**3. Reliability Risks**
- Single points of failure ("If the validator crashes, invalid commands could be executed")
- Data loss scenarios ("Packet drops aren't handled")
- Timing vulnerabilities ("Race conditions in multi-threaded simulation")

**4. Maintainability Problems**
- Tight coupling ("Changing the orbit propagator requires rewriting the RF link model")
- Hidden dependencies ("Magic numbers scattered throughout")
- Lack of testability ("No way to test components in isolation")

**For each potential flaw:**
- Is it a showstopper or a minor issue?
- Under what conditions does it manifest?
- What's the consequence if it occurs?

### Step 5: Compare Alternatives

When the user asks "should I use X or Y?", systematically compare the options.

**Comparison framework:**

**1. Identify Evaluation Criteria**

For TT&C and aerospace simulations, common criteria include:
- **Accuracy/Fidelity**: How closely does it match reality?
- **Computational Cost**: Runtime, memory usage
- **Implementation Complexity**: Development effort, lines of code
- **Maintainability**: How easy to modify and extend?
- **Standards Compliance**: Does it follow established protocols?
- **Availability of Tools/Libraries**: Can you leverage existing code?
- **Debugging/Validation**: How easy to verify correctness?

**2. Evaluate Each Option Against Criteria**

Create a mental (or actual) comparison table:

**Example: CCSDS Packets vs. Custom Protocol**

| Criterion | CCSDS Packets | Custom Protocol |
|-----------|---------------|-----------------|
| Standards compliance | ✓ Industry standard | ✗ Proprietary |
| Implementation complexity | ✗ More complex (headers, CRC) | ✓ Simpler to implement |
| Interoperability | ✓ Works with real systems | ✗ Requires custom decoder |
| Learning value | ✓ Industry-relevant skill | ~ Depends on use case |
| Debugging | ~ More structure, but complex | ✓ Full control, easier to debug |
| Future extension | ✓ Designed for growth | ~ Can evolve, but ad-hoc |

**3. Make a Recommendation**

Based on the comparison:
- Which option better fits the user's context (prototype vs. production, learning vs. delivery)?
- Are there hybrid approaches (e.g., start with custom, migrate to CCSDS later)?
- What's the decision hinge (the factor that tips the balance)?

**Recommendation format:**
- **Primary recommendation**: "For your use case (learning-focused TT&C simulation), I'd recommend [X] because [reason]."
- **Trade-off acknowledgment**: "You'll sacrifice [Y benefit], but gain [X benefit], which matters more here because [context]."
- **Alternative scenarios**: "If your goal were [different context], [Y] would be better because [reason]."

### Step 6: Probe Deeper with Questions

Critical thinking isn't just answering user questions—it's asking better questions back.

**Probing questions to ask the user:**

**Clarification Questions:**
- "When you say [X], do you mean [interpretation 1] or [interpretation 2]?"
- "What led you to choose this approach?"
- "Have you considered [alternative approach]?"

**Challenge Questions:**
- "What happens if [assumption] doesn't hold?"
- "How will you handle [edge case]?"
- "Why is [criterion] important for your use case?"

**Exploration Questions:**
- "What's your priority: accuracy, speed, or simplicity?"
- "How will you verify this works correctly?"
- "What would make you change your mind about this approach?"

Don't bombard with questions—ask 2-3 of the most important ones. Focus on questions that lead to insight, not just more information.

## Domain-Specific Critical Analysis

### TT&C Simulations

**Common assumptions to question:**

**Orbital Mechanics:**
- "Circular orbits are good enough" → When is this true? (Short simulations, equatorial orbits)
- "Earth is a perfect sphere" → J2 oblateness matters significantly for LEO
- "No atmospheric drag" → Below ~800 km, drag is non-negligible over days/weeks
- "Keplerian propagation is sufficient" → Depends on simulation duration and required accuracy

**RF Communication:**
- "Free-space path loss is the main effect" → Atmospheric attenuation, rain fade, scintillation can dominate
- "Antenna always points perfectly" → Pointing errors, multipath, and polarization losses matter
- "Doppler is a constant offset" → It's time-varying and accelerates during close passes
- "Link budget has margin, so details don't matter" → Margins disappear with adverse conditions

**Command & Telemetry:**
- "Commands are always delivered" → Packet loss, corruption, and buffering need consideration
- "Telemetry arrives in order" → Packets can be reordered, duplicated, or lost
- "Command validation can happen anywhere" → Security requires validation on-board, not ground-side only
- "One command at a time" → What about command sequences and dependencies?

**Protocols:**
- "I can simplify CCSDS for my simulator" → Which parts can be simplified without losing essential behavior?
- "Error detection isn't needed in simulation" → Even simulations benefit from catching bugs via checksums
- "Timestamps don't matter" → Time tagging is critical for correlating commands with telemetry

### Critical Questions for Aerospace Simulations

**For any proposal, ask:**

1. **Coordinate Systems**: Are you clear about which frame (ECI, ECEF, body-fixed, topocentric) each vector is in?
2. **Units**: Are you using consistent units (meters vs. kilometers, radians vs. degrees)?
3. **Time Representation**: How are you handling time (UTC, GPS time, Julian dates, Unix epoch)?
4. **Numerical Precision**: Are there cancellation errors (subtracting large numbers to get small differences)?
5. **Boundary Conditions**: What happens at poles, at the equator, at exactly midnight, during leap seconds?

## Output Format

Structure critical analysis clearly:

### Summary of Proposal
[Brief restatement of what the user is proposing]

### Assumptions Identified
- **Assumption 1**: [Description]
  - **Validity**: [When this is true/false]
  - **Impact**: [What happens if violated]
- **Assumption 2**: ...

### Technical Assessment
**Strengths**:
- [What's good about the approach]

**Concerns**:
- [Potential issues identified]

**Missing Considerations**:
- [What hasn't been addressed]

### Recommendation
[Clear guidance: go ahead, modify, or rethink]

### Key Questions to Consider
1. [Important question 1]
2. [Important question 2]
3. [Important question 3]

## Examples

### Example 1: Doppler Compensation Approach

**User**: "Am I right that Doppler shift only matters for LEO satellites? I'm planning to model it for my LEO ground station simulator, but ignore it for GEO simulations since GEO satellites are stationary relative to Earth."

**Response**:

#### Summary of Proposal
You're planning to model Doppler shift for LEO satellites but not for GEO, based on the assumption that GEO satellites are stationary relative to Earth.

#### Assumptions Identified

**Assumption 1**: "GEO satellites are stationary relative to Earth"
- **Validity**: True for *ideal* GEO (perfectly circular equatorial orbit at exact GEO altitude)
- **Reality**: Real GEO satellites have:
  - Small eccentricity (orbit isn't perfectly circular)
  - Inclination (orbit plane tilts relative to equator)
  - East-west drift (orbital period isn't exactly one sidereal day)
- **Impact**: These deviations cause small but measurable Doppler shifts (typically < 1 kHz at typical GEO frequencies)

**Assumption 2**: "Small Doppler shifts don't matter"
- **Validity**: Depends on your modulation scheme and receiver bandwidth
- For wideband signals (high data rates), 1 kHz Doppler is negligible
- For narrowband signals or precise frequency references, 1 kHz can exceed frequency uncertainty budget
- **Impact**: If you're simulating narrowband telemetry or frequency-critical operations (e.g., Doppler-based ranging), even GEO Doppler matters

#### Technical Assessment

**Strengths**:
- Correct that LEO Doppler is much larger (tens of kHz) than GEO (< 1 kHz)
- Reasonable to prioritize LEO Doppler modeling if that's your primary use case
- Simplification of ignoring GEO Doppler reduces implementation complexity

**Concerns**:
- Blanket statement "GEO has no Doppler" is technically incorrect
- If your simulation is used for GEO scenarios later, lack of Doppler modeling could cause confusion
- Real GEO systems *do* track Doppler (just at smaller scales)

**Missing Considerations**:
- What frequency bands are you simulating? (Doppler scales with frequency: 1 kHz at C-band becomes 3 kHz at Ka-band)
- What data rates and modulation schemes? (Impacts tolerance to frequency offsets)
- Are you modeling station-keeping maneuvers? (GEO satellites perform periodic burns that temporarily increase Doppler)

#### Recommendation

**For LEO-focused simulations**: Your approach is reasonable—model Doppler for LEO, skip it for GEO initially.

**Caveat**: Document this assumption clearly. If you later extend to:
- High-frequency GEO links (Ka-band and above)
- Narrowband GEO telemetry
- GEO satellites with significant inclination (inclined-GEO orbits)
- Station-keeping or disposal maneuvers

...then you should add GEO Doppler modeling.

**Best practice**: Design your RF link module so Doppler calculation is orbit-agnostic (works for any satellite). Compute Doppler from range-rate regardless of orbit type. This way:
- LEO gets large Doppler automatically
- GEO gets small (but present) Doppler automatically
- No special cases or assumptions to maintain

**Implementation suggestion**: Use `doppler_shift = -(range_rate / c) * carrier_frequency` for all satellites. This takes ~5 lines of code and handles all cases correctly.

#### Key Questions to Consider
1. What frequency bands will your simulation support? (Impacts Doppler magnitude)
2. Do you plan to model GEO station-keeping or inclined-GEO orbits in the future?
3. Is your RF link module designed to handle time-varying Doppler, or does it assume constant offset?

---

### Example 2: Command Validation Location

**User**: "For my satellite command uplink system, I'm thinking of validating commands at the ground station before transmission. That way, invalid commands never get sent up, which saves bandwidth and avoids confusing the satellite. Is this the right approach?"

**Response**:

#### Summary of Proposal
You plan to validate commands at the ground station before uplink, rather than on the satellite itself, to save bandwidth and prevent the satellite from receiving invalid commands.

#### Assumptions Identified

**Assumption 1**: "Ground-side validation is sufficient"
- **Validity**: True if ground station and satellite always have synchronized state
- **Reality**: Ground station's knowledge of satellite state is delayed (light-time + processing lag) and can be incorrect (missed telemetry packets, state changes)
- **Impact**: Ground might approve a command that's invalid by the time it reaches the satellite

**Assumption 2**: "Saving uplink bandwidth is worth the risk"
- **Validity**: Depends on link capacity and command frequency
- For low-rate command links, invalid commands are rare, and bandwidth savings are negligible
- For high-rate command sequences, filtering invalid commands at ground can help
- **Impact**: Bandwidth savings are real but small; security risk is large

**Assumption 3**: "The satellite doesn't need independent validation"
- **Validity**: False for safety-critical systems
- **Reality**: Satellite is the authority on its own state and safety
- **Impact**: Removing on-board validation creates vulnerability to ground system errors, malicious commands, or replay attacks

#### Technical Assessment

**Strengths**:
- Ground-side validation does catch many common errors (typos, out-of-range parameters)
- Reduces wasted bandwidth from obviously invalid commands
- Provides quick feedback to operators (no round-trip delay)

**Concerns**:
- **Critical flaw**: Ground-side-only validation violates defense-in-depth principle
- **Security risk**: If ground system is compromised, satellite has no protection
- **State synchronization**: Ground doesn't have perfect real-time knowledge of satellite state
- **Race conditions**: Satellite state might change between ground validation and command execution

**Missing Considerations**:
- Industry standards (e.g., CCSDS COP-1) *require* on-board validation
- Fault-tolerant design principle: each component validates its own inputs
- What if ground station malfunctions and approves invalid commands?

#### Recommendation

**Do NOT rely solely on ground-side validation.** This is a dangerous anti-pattern.

**Recommended architecture (defense-in-depth)**:
1. **Ground-side validation**: Catch obvious errors, provide quick operator feedback
2. **On-board validation (mandatory)**: Final authority on command acceptance
   - Validate syntax, range, state compatibility, safety constraints
   - Even if ground already validated, re-check on-board
3. **Telemetry confirmation**: Ground receives explicit ACK/NAK for each command

**Why both?**
- **Ground validation**: User experience (fast feedback), bandwidth efficiency (don't uplink garbage)
- **On-board validation**: Safety (satellite protects itself), security (defense against compromised ground), correctness (satellite knows its true state)

**Bandwidth concern addressed**: Ground validation *does* reduce uplink of invalid commands, but on-board validation is mandatory regardless. You get the bandwidth benefit as a bonus, but the primary reason for ground validation is operator experience, not bandwidth.

**Analogy**: This is like a bank teller checking your ID (ground validation) before the vault door requires biometric scan (on-board validation). Both layers matter—the teller catches simple mistakes quickly, but the vault doesn't trust the teller blindly.

#### Key Questions to Consider
1. What happens if the ground station's knowledge of satellite state is outdated or wrong?
2. How do you handle the scenario where ground approves a command, but satellite state changes before the command arrives?
3. Is your simulator meant to teach/demonstrate real spacecraft command practices, or just functional simulation? (Real spacecraft always validate on-board)
4. What's your threat model—are you considering malicious commands or only accidental operator errors?

---

## Anti-Patterns in Critical Thinking

Avoid these common traps:

### Being Reflexively Negative
Don't critique for the sake of critiquing. If the approach is sound, say so. Critical thinking includes recognizing when things are done well.

### Nitpicking Irrelevant Details
Focus on substantive issues that affect correctness, safety, or maintainability. Don't fixate on style preferences or minor inefficiencies.

### Ignoring Context
A "bad" approach for a production system might be perfect for a learning prototype. Always ask what the user's goals are before judging their approach.

### Overwhelming with Concerns
Prioritize. Lead with the most important issues. If there are 10 problems, highlight the 3 critical ones. You can mention others, but don't bury the user.

### Assuming Malice or Incompetence
Users often make reasonable choices given incomplete information. Phrase critiques as "here's a consideration you might have missed" rather than "this is wrong."

## Tips for Effective Critical Analysis

**Start with the strongest version of their argument**: Steelman, don't strawman. Interpret the user's proposal charitably before critiquing.

**Separate "wrong" from "suboptimal"**: Distinguish between approaches that won't work vs. approaches that work but have trade-offs.

**Provide constructive paths forward**: After identifying issues, suggest how to address them.

**Acknowledge uncertainty**: If you're unsure whether something is a problem, say so. "This might be an issue if [condition]; worth checking."

**Use the user's priorities**: If they've said "I care about simplicity over accuracy," weight your analysis accordingly.

**Cite sources when possible**: "CCSDS standard 232.0-B-3 requires..." carries more weight than "I think you need..."

## When Critical Analysis is Complete

You've done your job when:
- The user understands the assumptions they're making
- Potential issues have been identified and prioritized
- Trade-offs are clearly explained
- The user has enough information to make an informed decision
- Follow-up questions (if any) focus on implementation, not whether the approach is sound
