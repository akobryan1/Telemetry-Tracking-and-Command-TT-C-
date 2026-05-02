---
name: iterative-solving
description: Start with minimal working systems and layer complexity incrementally. Use when users feel overwhelmed by project complexity, don't know where to begin, need a roadmap from basic to full-featured, or want to build incrementally with working checkpoints. Particularly valuable for TT&C simulations, aerospace systems, and complex projects where building everything at once risks big-bang integration failures. Trigger when users say "this feels too complex", "where should I start?", "what's the simplest version?", need step-by-step development guidance, or want to add features progressively to an existing system.
---

# Iterative Problem Solving

This skill guides incremental development of complex systems, helping users start simple, validate early, and add sophistication progressively. The goal is to avoid overwhelming complexity by building working systems in layers.

## When to Use This Skill

Apply this skill when the user:
- Feels overwhelmed by a complex project ("too much to build at once")
- Doesn't know where to start ("what's step 1?")
- Wants a roadmap from minimal to full-featured
- Needs working checkpoints to validate progress
- Wants to add features to an existing system incrementally
- Has experienced big-bang integration failures before

**Common trigger phrases:**
- "Where should I start?"
- "This feels too complex to tackle"
- "What's the simplest version that works?"
- "How do I add [feature] to my existing [system]?"
- "I'm stuck—too many things to build"

## Iterative Development Process

### Step 1: Define "Working"

Before iterating, establish what "working" means at each stage.

**For simulations**:
- **Level 0 (Skeleton)**: Program runs, produces output (even if wrong)
- **Level 1 (Minimal Correct)**: Simplest physically correct behavior
- **Level 2 (Validated)**: Results match hand calculations or known test cases
- **Level 3 (Featured)**: Handles realistic scenarios with key features
- **Level 4 (Production)**: Robust error handling, performance, documentation

**Start by defining Level 1**: What's the simplest thing that's *correct* (not just runs)?

**Example - TT&C Ground Station**:
- **Level 0**: Program prints "satellite is visible" (hardcoded, doesn't compute anything)
- **Level 1**: Computes satellite position using SGP4, determines if above horizon (correct but minimal)
- **Level 2**: Validated against online satellite trackers (Heavens-Above, N2YO)
- **Level 3**: Tracks multiple satellites, computes RF link budgets, handles Doppler
- **Level 4**: Handles edge cases (pole crossing, leap seconds), optimized, documented

### Step 2: Identify the Minimal Core

What's the absolute minimum that demonstrates the system's primary function?

**Criteria for minimal core**:
1. **Essential functionality only**: Solves the core problem, ignores refinements
2. **No edge cases**: Handle the happy path, defer error handling
3. **Simplified physics**: Use the simplest model that's still correct
4. **Minimal I/O**: Hardcoded inputs, print outputs—no fancy UI yet
5. **No optimization**: Slow is fine; correct is mandatory

**Example - Satellite Orbit Propagator**:
**Minimal core**: Compute satellite position at time T using SGP4 and TLE
- Input: TLE (hardcoded or from file)
- Process: Call SGP4 library
- Output: Print position (X, Y, Z in kilometers)
- **Not included**: Coordinate transformations, multi-satellite tracking, visualization, time stepping

**Why this matters**: You can build and validate the minimal core in hours, not weeks. Early validation catches fundamental misunderstandings.

### Step 3: Build the Minimal Core

Implement only what's defined in Step 2. Resist temptation to add "just one more feature."

**Best practices**:
- **Use libraries**: Don't implement SGP4 from scratch when `skyfield` (Python) exists
- **Hardcode initially**: Hardcode inputs until core logic works
- **Print liberally**: Console output is fine for validation
- **Write one test**: Verify against known answer (e.g., ISS position at specific time)

**Validation checkpoint**: Before proceeding, ensure core produces correct output for at least one test case.

### Step 4: Plan Iteration Layers

Break remaining features into layers, each building on the previous.

**Layering principles**:

**1. Dependency order**: Build foundations before features that depend on them
- Orbit propagation → Visibility calculation → Antenna pointing
- (You can't point the antenna without knowing visibility, can't determine visibility without orbit propagation)

**2. Incremental complexity**: Add one complication at a time
- Circular orbits → Elliptical orbits → Perturbations (J2) → Drag
- (Each layer adds physics; validate each before the next)

**3. Feature independence**: When possible, add features that don't interact
- Add Doppler calculation and atmospheric loss modeling in parallel—they don't depend on each other
- (Parallel tracks let you validate independently)

**4. Defer optimization**: Performance tuning is the last layer, not the first
- Correct but slow → Profiled → Optimized hotspots
- (Premature optimization wastes time on code you might refactor)

**Example - TT&C Ground Station Iteration Layers**:
1. **Core**: Orbital propagation (SGP4 + TLE → position)
2. **Layer 1**: Visibility (position + ground station location → elevation/azimuth)
3. **Layer 2**: Time stepping (propagate over pass duration)
4. **Layer 3**: RF link (basic free-space path loss)
5. **Layer 4**: Doppler shift (range rate → frequency offset)
6. **Layer 5**: Multi-satellite tracking
7. **Layer 6**: CCSDS packet simulation
8. **Layer 7**: Realistic atmospheric effects
9. **Layer 8**: Performance optimization

Each layer produces a working system; you can stop after any layer and have something useful.

### Step 5: Implement One Layer at a Time

For each iteration layer:

**A. Define the layer's scope**:
- What feature am I adding?
- What's the simplest version of this feature?
- What's my test case?

**B. Implement minimally**:
- Add code only for this feature
- Stub complex parts if needed
- Keep existing code working

**C. Validate immediately**:
- Run test case
- Check output against expectation
- Debug until correct

**D. Refactor if needed**:
- If the code is becoming messy, clean it up *now* (before adding more layers)
- Resist urge to "fix it later"—later never comes

**E. Commit/checkpoint**:
- Version control: commit working code
- Or: save a backup copy
- This is your rollback point if the next layer breaks things

**Example - Adding Doppler Layer**:

**A. Scope**: Calculate Doppler shift from satellite velocity relative to ground station

**B. Implement**:
```python
def calculate_doppler(satellite_velocity, ground_station_velocity, carrier_freq):
    relative_velocity = satellite_velocity - ground_station_velocity
    range_rate = np.dot(relative_velocity, line_of_sight_unit_vector)
    doppler_shift = -(range_rate / speed_of_light) * carrier_freq
    return doppler_shift
```

**C. Validate**:
- Test case: ISS overhead pass, 2 GHz carrier
- Expected: ~±52 kHz Doppler at max range rate
- Actual: 51.8 kHz ✓

**D. Refactor**: Move vector calculations into separate utility module (was getting messy)

**E. Commit**: `git commit -m "Add Doppler shift calculation, validated against ISS"`

**Now ready for next layer.**

### Step 6: Handle Feature Addition vs. Refinement

Not all iterations are "add a feature"—some are "make existing feature better."

**Feature addition** (new capability):
- Example: "Add command uplink" to a system that only had telemetry downlink
- Test: Can I send a command and see it received?

**Refinement** (improve existing capability):
- Example: "Replace simplified atmospheric loss (fixed 2 dB) with elevation-dependent model"
- Test: Does loss now vary correctly with elevation angle?

**Guideline**: Alternate between adding features and refining existing ones. Don't refine prematurely (you might remove the feature later), but don't stack features on buggy foundations.

### Step 7: Know When to Stop Iterating

Iteration can continue forever. Decide stopping criteria based on goals:

**For learning projects**:
- Stop when you've learned the concept
- It doesn't need to be feature-complete

**For prototypes**:
- Stop when key feasibility questions are answered
- Robustness isn't needed

**For production systems**:
- Stop when requirements are met *and* validated
- Include error handling, performance, documentation

**Red flag**: Iterating to avoid finishing. If you keep adding "nice to have" features instead of calling it done, you're procrastinating. Ship it.

## Iteration Patterns for TT&C

### Pattern 1: Physics Fidelity Ladder

Start with simplified physics, increase fidelity iteratively:

**Level 1 - Point Mass**:
- Satellite is a point with position/velocity
- No attitude, no size, no shape

**Level 2 - Spherical Body**:
- Satellite has attitude (orientation)
- Still spherical (no complex geometry)

**Level 3 - Realistic Geometry**:
- Satellite has solar panels, antennas (actual shape)
- Orientation affects which faces see sun/ground

**Example - Solar Panel Power Model**:
1. **Simple**: `power = 100W` (constant)
2. **Basic physics**: `power = panel_area * solar_flux * cos(sun_angle)`
3. **Eclipse-aware**: `power = 0 if in_eclipse else panel_area * solar_flux * cos(sun_angle)`
4. **Multi-panel**: Sum over all panels with individual orientations
5. **Realistic**: Add panel efficiency, temperature dependence, degradation over time

Each level is correct for its assumptions. Choose the level appropriate for your needs.

### Pattern 2: Time Simulation Ladder

Start with single-point calculations, add time-stepping iteratively:

**Level 1 - Single Point**:
- Calculate satellite position at one specific time
- Useful for validating propagator

**Level 2 - Fixed Time Steps**:
- Loop over time with constant step size (e.g., 1 second)
- Simple, predictable

**Level 3 - Event-Driven**:
- Detect events (AOS, LOS, eclipse entry/exit)
- Variable time steps (large steps between events, small steps during events)

**Level 4 - Real-Time**:
- Synchronize simulation time with wall clock
- Needed for hardware-in-the-loop testing

Start with Level 1 (easiest to debug), progress as needed.

### Pattern 3: Data Flow Ladder

Start with direct coupling, add proper architecture iteratively:

**Level 1 - Monolithic**:
- All code in one function/file
- Direct variable access
- Gets something working fast

**Level 2 - Functional Decomposition**:
- Break into functions
- Pass data as function arguments
- Still simple, more organized

**Level 3 - Object-Oriented**:
- Classes for major components (Satellite, GroundStation, RFLink)
- Encapsulation (data hiding)
- Clear interfaces

**Level 4 - Publish-Subscribe**:
- Components publish events (e.g., "satellite position updated")
- Subscribers receive events (e.g., antenna controller subscribes to position updates)
- Decoupled, extensible

Don't jump to Level 4 initially—it's over-engineered for small systems. Evolve architecture as system grows.

## Output Format

Provide iteration roadmap in clear stages:

### Minimal Core (Iteration 0)
**Goal**: [Simplest working version]
**Functionality**: [What it does]
**Validation**: [How to verify it works]
**Expected Time**: [Realistic time estimate]

### Iteration 1: [Feature/Refinement Name]
**Goal**: [What this adds]
**Prerequisites**: [What must be working first]
**Implementation**: [High-level approach]
**Validation**: [Test case]
**Expected Time**: [Estimate]

### Iteration 2: ...
[Continue for each layer]

### Optional Iterations (if time allows)
- [Feature 1]: [When to add this]
- [Feature 2]: [When to add this]

### Stopping Criteria
**Minimum viable**: [Iteration X produces this]
**Full-featured**: [Iteration Y produces this]
**Production-ready**: [Iteration Z + error handling + docs]

## Examples

### Example 1: Building a TT&C Ground Station Incrementally

**User**: "I want to build a TT&C ground station simulator but it feels overwhelming. Where do I even start?"

**Response**:

Let's break this down into manageable iterations, each producing a working system:

#### Minimal Core (Iteration 0)
**Goal**: Compute whether a satellite is visible from a ground station at a given time

**Functionality**:
- Input: TLE for ISS, ground station lat/lon, time
- Process: Use SGP4 to get satellite position, compute elevation angle
- Output: Print "ISS is visible" or "ISS is below horizon"

**Validation**: Compare with Heavens-Above for ISS pass over your location tomorrow

**Expected Time**: 2-4 hours (mostly learning SGP4 library)

**Implementation sketch**:
```python
from skyfield.api import load, Topos, EarthSatellite

# Load TLE
tle_line1 = "1 25544U ..." 
tle_line2 = "2 25544 ..."
satellite = EarthSatellite(tle_line1, tle_line2)

# Ground station
ground_station = Topos(latitude_degrees=40, longitude_degrees=-75)

# Time
ts = load.timescale()
t = ts.utc(2026, 5, 2, 14, 30)

# Visibility
diff = satellite - ground_station
topocentric = diff.at(t)
alt, az, distance = topocentric.altaz()

if alt.degrees > 0:
    print(f"ISS is visible at elevation {alt.degrees:.1f}°")
else:
    print("ISS is below horizon")
```

**Why start here**: This validates your fundamental building block (orbital mechanics) before adding complexity. If this doesn't work, nothing else will.

---

#### Iteration 1: Time-Stepped Pass Prediction
**Goal**: Predict entire satellite pass (AOS to LOS)

**Prerequisites**: Iteration 0 working

**Implementation**:
- Loop over time (e.g., 1-minute steps for next 24 hours)
- Track when satellite goes from below horizon to above (AOS) and back (LOS)
- Print pass start time, end time, duration, max elevation

**Validation**: Compare pass times with Heavens-Above predictions

**Expected Time**: 1-2 hours

---

#### Iteration 2: Multiple Satellites
**Goal**: Track multiple satellites (e.g., ISS, Starlink, NOAA satellites)

**Prerequisites**: Iteration 1 working

**Implementation**:
- Load multiple TLEs
- Run pass prediction for each satellite
- Sort passes chronologically

**Validation**: Check that passes for different satellites don't overlap suspiciously (would indicate bug)

**Expected Time**: 1 hour

---

#### Iteration 3: Basic RF Link Budget
**Goal**: Estimate received signal strength during passes

**Prerequisites**: Iteration 1 working (need range data)

**Implementation**:
- For each time step during a pass, calculate:
  - Free-space path loss: `FSPL = 20*log10(distance) + 20*log10(freq) + 32.45`
  - Received power: `P_rx = P_tx + G_tx + G_rx - FSPL`
- Plot received power vs. time during pass

**Validation**: Verify power is max when satellite is overhead (minimum distance)

**Expected Time**: 2-3 hours

---

#### Iteration 4: Doppler Shift
**Goal**: Calculate frequency offset due to satellite motion

**Prerequisites**: Iteration 1 working (need velocity data)

**Implementation**:
- Compute range rate (relative velocity along line of sight)
- Doppler shift: `delta_f = -(range_rate / c) * carrier_freq`
- Plot Doppler vs. time during pass

**Validation**: Doppler should be positive (blue-shifted) as satellite approaches, negative as it recedes, zero at closest approach

**Expected Time**: 1-2 hours

---

#### Iteration 5: Antenna Pointing
**Goal**: Compute antenna azimuth/elevation commands to track satellite

**Prerequisites**: Iteration 1 working (need topocentric coordinates)

**Implementation**:
- Convert satellite position to azimuth/elevation angles
- Output time-stamped pointing commands
- (Optional) Simulate antenna slew rate limits

**Validation**: Plot antenna path on sky chart; should trace satellite trajectory

**Expected Time**: 2-3 hours

---

#### Iteration 6: CCSDS Packet Simulation
**Goal**: Generate realistic telemetry packets during passes

**Prerequisites**: Iteration 3 working (RF link affects packet success rate)

**Implementation**:
- Create CCSDS Space Packets with dummy telemetry data
- Simulate packet loss based on link budget (low SNR → higher loss rate)
- Log received packets

**Validation**: Packet loss rate should be low during high-elevation passes, higher during low-elevation passes

**Expected Time**: 4-6 hours (CCSDS is complex)

---

### Stopping Criteria

**Minimum viable** (Iteration 3): You can predict passes and estimate link quality — useful for mission planning

**Full-featured** (Iteration 6): Realistic ground station simulation — useful for protocol testing and training

**Production-ready** (Iteration 6 + error handling + UI): 
- Add: TLE auto-update, configuration files, GUI or web interface, database logging
- Time: +10-15 hours

**Recommendation**: Build through Iteration 3 in your first session (one day). If it's working and you're learning, continue to Iterations 4-5. Save Iteration 6 for later if you actually need CCSDS testing.

---

This roadmap gives you 5-6 working checkpoints. You can stop after any iteration and have something useful.

## Tips for Successful Iteration

**Resist feature creep**: "While I'm adding Doppler, I might as well add atmospheric refraction..." No. One feature at a time.

**Validate early and often**: Don't stack 3 unvalidated layers. If Layer 3 breaks, you won't know if the bug is in Layer 1, 2, or 3.

**Keep old versions**: Use version control (git), or save dated copies (`ground_station_v2_working.py`). Fearless refactoring requires safety nets.

**Celebrate checkpoints**: Each working iteration is progress. Don't dismiss it as "not done yet."

**Write TODO comments for future layers**: When you think "I should add error handling here," write `# TODO: add error handling` and move on. Capture the idea without derailing current work.

**Know your dependencies**: If Layer 5 needs data from Layer 3, make sure Layer 3 exposes it. Don't hack around with global variables—refactor Layer 3 to return what Layer 5 needs.

## When Iterative Solving is Complete

You've succeeded when:
- The user has a clear next step (not paralyzed by complexity)
- The roadmap fits their timeline and skill level
- Each iteration is small enough to complete and validate
- The user understands why this order (dependencies explicit)
- The user knows when they can stop (minimum viable defined)
