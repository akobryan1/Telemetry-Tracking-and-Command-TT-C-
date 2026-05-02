---
name: tech-communication
description: Help document, explain, and communicate technical work effectively to different audiences. Use when users need to write documentation, explain systems to stakeholders, create diagrams, prepare technical presentations, document design decisions, write commit messages, or communicate with non-technical team members. Particularly valuable for TT&C simulations, aerospace systems, and complex projects where technical communication bridges understanding gaps. Trigger when users say "how do I explain this?", "I need to document...", "can you help me write...", need audience-appropriate explanations, or want to create technical diagrams.
---

# Technical Communication

This skill guides effective documentation and explanation of technical work, helping users communicate clearly to diverse audiences—from expert engineers to non-technical stakeholders.

## When to Use This Skill

Apply this skill when the user needs to:
- Write documentation (READMEs, API docs, design docs)
- Explain technical systems to stakeholders
- Create diagrams or visualizations
- Prepare technical presentations
- Document design decisions or trade-offs
- Write clear commit messages or PR descriptions
- Communicate with non-technical team members

**Common trigger phrases:**
- "How do I explain this?"
- "I need to document..."
- "Can you help me write..."
- "How would you describe this to [audience]?"
- "What should go in the README?"

## Communication Process

### Step 1: Identify Your Audience

Technical communication succeeds or fails based on audience understanding. Characterize your audience first:

**Technical Expertise**:
- **Expert**: Domain specialists (can understand jargon, theoretical depth)
- **Proficient**: Engineers in adjacent domains (need context, less jargon)
- **Novice**: New engineers or technical stakeholders (need analogies, minimal jargon)
- **Non-technical**: Management, customers (need outcomes, not mechanisms)

**Information Need**:
- **How to use**: Practical instructions (users, operators)
- **How it works**: Internal mechanisms (maintainers, reviewers)
- **Why it exists**: Motivation and context (stakeholders, decision-makers)
- **What it achieves**: Outcomes and benefits (management, customers)

**Time Constraints**:
- **Skimmers**: Executives, busy stakeholders (need executive summary, visuals)
- **Readers**: Engineers reviewing code (need detail, references)
- **Learners**: Students, new team members (need progressive depth)

**Example**:
- **Audience**: Project manager (non-technical, needs "why", skimmer)
- **Implication**: Lead with outcomes ("reduces outage risk by 40%"), avoid equations, use diagrams, keep it brief

### Step 2: Choose Communication Mode

Different information suits different formats:

**Text**:
- Best for: Procedures, API references, design rationale
- Use when: Audience will read carefully or search for specific info

**Diagrams**:
- Best for: System architecture, data flow, relationships
- Use when: Spatial relationships or hierarchy matter

**Examples/Code**:
- Best for: How-to guides, API usage, concrete demonstrations
- Use when: "Show me" beats "tell me"

**Analogies**:
- Best for: Explaining unfamiliar concepts to non-experts
- Use when: Audience lacks domain background

**Tables/Charts**:
- Best for: Comparisons, trade-offs, performance data
- Use when: Decision-making requires evaluating options

**Combination**: Most effective communication mixes modes (text + diagram + example).

### Step 3: Structure Information Hierarchically

People consume information top-down. Provide layers:

**Layer 1: Executive Summary (1-2 sentences)**
- What is this, why does it matter?
- Everyone reads this

**Layer 2: Overview (1-2 paragraphs)**
- High-level functionality, key concepts
- Skimmers read this

**Layer 3: Details (sections, subsections)**
- How it works, edge cases, implementation
- Readers dive into this

**Layer 4: Deep Dive (appendices, references)**
- Theoretical background, derivations, benchmarks
- Experts and learners explore this

**Example - TT&C Ground Station README**:

**Layer 1**: "A Python ground station simulator for TT&C operations, predicting satellite passes and computing link budgets."

**Layer 2**: "This tool uses SGP4 orbital propagation and RF link budget calculations to predict when satellites are visible from ground stations, estimate signal strength, and compute Doppler shifts. Designed for mission planning and operator training."

**Layer 3**: Sections: Installation, Usage, Architecture, API Reference

**Layer 4**: Appendices: SGP4 Algorithm Details, Link Budget Derivation, Validation Test Cases

### Step 4: Use Clear, Precise Language

**Avoid jargon with non-experts**:
- Bad (to manager): "We're using a PLL for Doppler compensation in the demod chain"
- Good: "We're tracking the satellite's frequency shift automatically as it moves"

**Define jargon when necessary**:
- "The TLE (Two-Line Element set) contains orbital parameters like semi-major axis and eccentricity that define the satellite's orbit."

**Be specific**:
- Vague: "The system is fast"
- Specific: "The system processes 10,000 packets/second"

**Use active voice**:
- Passive: "The packet is validated by the decoder"
- Active: "The decoder validates the packet"

**Keep sentences short**: Aim for 15-20 words per sentence. Long sentences confuse readers.

### Step 5: Explain the "Why" Before the "What"

People understand better when they know motivation:

**Before diving into implementation, explain**:
- Why does this exist? (Problem it solves)
- Why this approach? (Trade-offs considered)
- Why now? (Timing, context)

**Example - Design Decision Documentation**:

Bad:
> "We use SGP4 for orbital propagation."

Good:
> "We use SGP4 for orbital propagation because it's the standard for Earth-orbiting satellites and provides sufficient accuracy (~1 km) for ground station pass predictions. We considered numerical integrators (Runge-Kutta), which are more accurate but 100× slower and unnecessary for our use case—ground station antenna beam widths are typically 1-5°, tolerating kilometer-level position errors."

The "good" version explains why SGP4, why not alternatives, and what accuracy is acceptable.

### Step 6: Use Examples and Concrete Scenarios

Abstract descriptions are hard to grasp. Concrete examples anchor understanding:

**Example - API Documentation**:

Bad:
> "`compute_visibility(satellite, observer, time)` returns boolean indicating visibility."

Good:
> "`compute_visibility(satellite, observer, time)` returns `True` if the satellite is above the observer's horizon at the specified time.
>
> **Example**:
> ```python
> from ttc import compute_visibility
> 
> iss = load_satellite("ISS")
> boston = GroundStation(lat=42.3, lon=-71.0)
> time = datetime(2026, 5, 2, 14, 30, 0)
> 
> if compute_visibility(iss, boston, time):
>     print("ISS is visible from Boston")
> ```
> **Returns**: `True` if satellite elevation > 0°, otherwise `False`."

The example shows *how* to use the function, making the abstract description concrete.

### Step 7: Visualize System Structure

Diagrams often communicate structure better than text. Choose diagram type by purpose:

**Block Diagrams**: Show components and relationships
- Use for: System architecture, data flow
- Example: Ground station components (Antenna → Receiver → Demodulator → Decoder → Database)

**Sequence Diagrams**: Show interactions over time
- Use for: Protocols, handshakes, message exchanges
- Example: CCSDS packet flow (Satellite TX → Ground RX → Parse → Validate → Store)

**State Diagrams**: Show modes and transitions
- Use for: State machines, operational modes
- Example: Satellite modes (Safe → Detumble → Nominal → Science)

**Flowcharts**: Show decision logic
- Use for: Algorithms, control flow
- Example: Command validation (Check CRC → Check mode → Check limits → Execute or Reject)

**For TT&C systems, block diagrams and sequence diagrams are most common.**

**Tools**:
- ASCII art (for simple diagrams in text docs)
- Mermaid (Markdown-compatible diagrams)
- Draw.io, Lucidchart (complex diagrams)
- Python matplotlib (data plots)

**Example - ASCII Block Diagram**:
```
┌─────────────┐
│  Satellite  │
└──────┬──────┘
       │ RF Signal (2.2 GHz)
       ▼
┌─────────────┐
│   Antenna   │
└──────┬──────┘
       │ Analog Signal
       ▼
┌─────────────┐
│  Receiver   │ (Demodulate, Decode)
└──────┬──────┘
       │ Bitstream
       ▼
┌─────────────┐
│   Parser    │ (Extract CCSDS Packets)
└──────┬──────┘
       │ Telemetry Packets
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

### Step 8: Document Decisions and Trade-offs

Future maintainers (including future you) need to understand *why* decisions were made:

**Document**:
- Alternatives considered
- Criteria for choosing this approach
- Trade-offs accepted (what you gave up)
- Assumptions made

**Example - Design Doc Snippet**:

> **Decision**: Use SQLite for telemetry storage
>
> **Alternatives Considered**:
> - PostgreSQL: More robust, better for large-scale deployments
> - Flat files (CSV): Simplest, no dependencies
>
> **Rationale**: SQLite balances simplicity (single file, no server) with query capability (SQL). For our use case (1-2 satellites, <1 GB/day), SQLite performance is sufficient. PostgreSQL would add deployment complexity for negligible benefit. CSV files would require custom query logic.
>
> **Trade-offs**: 
> - Accepted: Limited concurrency (single writer)
> - Accepted: No network access (local file only)
> - Gain: Zero-configuration, embeddable
>
> **Assumptions**:
> - Data volume stays below 10 GB (SQLite handles this well)
> - Single ground station (no multi-station synchronization needed)
>
> **Revisit if**: Data volume exceeds 10 GB or we add multi-station coordination

This documentation prevents future confusion ("why didn't we use PostgreSQL?") and identifies conditions for revisiting the decision.

## Communication Patterns for TT&C

### Pattern 1: Explaining Orbital Mechanics to Non-Experts

**Challenge**: Orbital mechanics involves non-intuitive physics (orbits speed up when slowing down, satellites "fall" continuously without crashing).

**Strategy**:
1. **Start with familiar analogy**: "A satellite is like a ball thrown horizontally—it falls due to gravity, but if thrown fast enough, Earth curves away beneath it at the same rate it falls."
2. **Visualize**: Show orbit diagram with satellite position over time
3. **Introduce one concept at a time**: Altitude → Velocity → Orbital period (don't dump all Kepler's laws at once)
4. **Connect to outcomes**: "Higher altitude means longer communication time per pass but weaker signals"

**Example**:

Bad (to non-expert):
> "The satellite's semi-major axis determines its orbital period via Kepler's third law, and the eccentricity describes the orbit's deviation from circularity."

Good:
> "The satellite's altitude determines how fast it orbits Earth. Higher satellites move slower and take longer to complete one orbit—a satellite at 400 km altitude circles Earth every 90 minutes, while a satellite at 35,786 km (geostationary) takes 24 hours. This affects how long we can communicate with the satellite during each pass."

### Pattern 2: Documenting Simulation Assumptions

Simulations simplify reality. Document what you've simplified to prevent misinterpretation:

**Template**:

> **Simulation Assumptions**:
> 1. [Assumption 1]: [What's simplified] → [Implication]
> 2. [Assumption 2]: ...
>
> **Validity Range**: [When is this simulation trustworthy?]
> **Limitations**: [What can't this simulation predict?]

**Example - Link Budget Simulator**:

> **Simulation Assumptions**:
> 1. **Free-space propagation**: Ignores atmospheric refraction, rain fade, ionospheric effects → Valid for clear-weather S-band links; underestimates attenuation during rain
> 2. **Perfect antenna pointing**: Assumes antenna tracks satellite perfectly → Overestimates signal strength if antenna has pointing errors >0.5°
> 3. **Constant transmit power**: Assumes satellite transmitter outputs constant power → Doesn't capture power variations due to battery discharge
>
> **Validity Range**: 
> - Frequency: 1-3 GHz (S-band)
> - Weather: Clear sky conditions
> - Elevation: >10° (below 10°, atmospheric effects dominate)
>
> **Limitations**: 
> - Cannot predict link performance during rainstorms
> - Does not model multipath interference near horizon

This transparency helps users understand when to trust the simulation and when to seek more detailed models.

### Pattern 3: Writing Effective Commit Messages

Commit messages communicate *why* changes were made, not just *what* changed (the diff shows "what").

**Template**:
```
[Short summary: what changed, 50 chars max]

[Optional body: why this change, what problem it solves, 
alternatives considered, side effects]

[Optional footer: issue references, breaking changes]
```

**Example - Good Commit Message**:

```
Fix Doppler calculation sign error

The Doppler shift was inverted (positive when satellite receding,
negative when approaching), causing frequency tracking failures 
during satellite passes. Root cause: range rate calculation used
(satellite - observer) instead of (observer - satellite).

This fix swaps the subtraction order, correcting the sign.

Validated against known ISS Doppler profile (±52 kHz at max 
range rate).

Fixes #47
```

**Why this is good**:
- Short summary describes the fix
- Body explains the bug's impact and root cause
- Shows validation was done
- References issue tracker

### Pattern 4: Creating Effective Diagrams for TT&C Systems

**Use case**: Explaining ground station architecture

**Diagram Evolution**:

**Level 1 - Simplified Block Diagram** (for non-experts):
```
Satellite → Antenna → Receiver → Computer → Display
```

**Level 2 - Detailed Block Diagram** (for engineers):
```
                     ┌───────────┐
                     │ Satellite │
                     └─────┬─────┘
                           │ 2.2 GHz RF
                           ▼
                     ┌───────────┐
                     │  Antenna  │ (3m parabolic)
                     └─────┬─────┘
                           │ Analog signal
                           ▼
       ┌───────────────────┴────────────────┐
       │          Receiver                  │
       │  ┌─────┐  ┌──────┐  ┌──────────┐  │
       │  │ LNA ├─→│ PLL  ├─→│ Demod    │  │
       │  └─────┘  └──────┘  └────┬─────┘  │
       └────────────────────────────┼────────┘
                                    │ Bitstream
                                    ▼
       ┌────────────────────────────────────┐
       │     Baseband Processor             │
       │  ┌────────┐  ┌────────┐  ┌──────┐ │
       │  │ Frame  ├─→│ Packet ├─→│ CRC  │ │
       │  │ Sync   │  │ Parse  │  │Check │ │
       │  └────────┘  └────────┘  └───┬──┘ │
       └─────────────────────────────┼─────┘
                                     │ Valid packets
                                     ▼
                              ┌──────────┐
                              │ Database │
                              └──────────┘
```

**When to use each**:
- Level 1: Executive summary, high-level overview
- Level 2: Technical documentation, design review

## Output Format

Tailor output structure to communication goal:

### For Documentation (README, Design Doc)

```markdown
# [Title]

## Overview
[1-2 sentence summary]

## Purpose
[Why this exists, problem it solves]

## Features
- [Key feature 1]
- [Key feature 2]
...

## Installation
[Step-by-step setup instructions]

## Usage
[Examples showing common use cases]

## Architecture
[System structure, component diagram]

## API Reference (if applicable)
[Function/class documentation]

## Assumptions and Limitations
[What's simplified, when to use/not use]

## Contributing / Contact
[How to get involved or ask questions]
```

### For Explanations to Non-Experts

```
1. Analogy or familiar concept
2. High-level overview (no jargon)
3. Concrete example
4. Why it matters (connect to business/mission outcomes)
5. [Optional] One level deeper for curious readers
```

### For Technical Presentations

```
Slide 1: Title + One-Sentence Summary
Slide 2: Problem / Motivation (Why are we here?)
Slide 3: High-Level Approach (How do we solve it?)
Slide 4-N: Key Technical Details (one concept per slide)
Slide N+1: Results / Validation (Does it work?)
Slide N+2: Conclusions / Next Steps (What's next?)
```

**Keep slides minimal**: 5-7 bullets max, large fonts (24pt+), diagrams over text.

## Examples

### Example 1: Writing a README for a TT&C Simulator

**User**: "I built a ground station simulator. Can you help me write a good README?"

**Response**:

Here's a structured README for your TT&C ground station simulator:

```markdown
# TT&C Ground Station Simulator

A Python-based ground station simulator for satellite Telemetry, Tracking & Command (TT&C) operations.

## Overview

This tool predicts satellite passes over ground stations, computes RF link budgets, and simulates telemetry reception. Designed for mission planning, operator training, and link performance analysis.

**Key Features**:
- Satellite pass prediction using SGP4 orbital propagation
- RF link budget calculation (free-space path loss, Doppler shift)
- Multi-satellite tracking
- CCSDS packet simulation
- Export to CSV or database

## Installation

**Requirements**: Python 3.8+, pip

```bash
git clone https://github.com/yourname/ttc-ground-station
cd ttc-ground-station
pip install -r requirements.txt
```

**Dependencies**: `skyfield` (orbital mechanics), `numpy`, `matplotlib`

## Quick Start

**Predict ISS passes over Boston for the next 24 hours**:

```python
from ttc import GroundStation, load_satellite, predict_passes

# Define ground station
boston = GroundStation(lat=42.36, lon=-71.06, name="Boston")

# Load satellite TLE
iss = load_satellite("ISS")

# Predict passes
passes = predict_passes(iss, boston, duration_hours=24)

for p in passes:
    print(f"AOS: {p.start_time}, LOS: {p.end_time}, Max Elev: {p.max_elevation:.1f}°")
```

**Output**:
```
AOS: 2026-05-02 14:23:10, LOS: 2026-05-02 14:31:45, Max Elev: 78.3°
AOS: 2026-05-02 16:01:22, LOS: 2026-05-02 16:08:17, Max Elev: 22.1°
```

## Architecture

```
┌──────────────┐
│ Satellite    │ (TLE → SGP4 propagator)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Ground Stn   │ (Lat/Lon/Alt → Topocentric coords)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Pass Finder  │ (Detect AOS/LOS, compute elevation)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Link Budget  │ (FSPL, Doppler, received power)
└──────────────┘
```

## Use Cases

1. **Mission Planning**: Determine contact windows for satellite operations
2. **Link Analysis**: Estimate signal strength, identify coverage gaps
3. **Operator Training**: Simulate realistic pass scenarios for training
4. **Antenna Scheduling**: Generate pointing commands for automated antennas

## Assumptions and Limitations

**Assumptions**:
- SGP4 propagation (accuracy: ~1 km for LEO satellites)
- Free-space path loss model (no atmospheric attenuation beyond 0.3 dB)
- Perfect antenna pointing (no pointing errors)

**Limitations**:
- Does not model weather effects (rain fade, tropospheric scintillation)
- Not suitable for precision orbit determination (use numerical integrators)
- TLEs must be updated regularly (<7 days old for best accuracy)

**Validity**: Best for LEO/MEO satellites, clear-weather link budgets, ground station planning.

## API Reference

See [API.md](API.md) for detailed function documentation.

**Key Functions**:
- `predict_passes(satellite, observer, duration_hours)`: Find satellite passes
- `compute_link_budget(satellite, observer, time, freq)`: Calculate received power
- `compute_doppler(satellite, observer, time, freq)`: Calculate Doppler shift

## Contributing

Contributions welcome! Please open an issue or pull request.

**Roadmap**:
- [ ] Add atmospheric attenuation model
- [ ] Support for multi-ground-station networks
- [ ] Real-time tracking mode
- [ ] Web dashboard for visualization

## License

MIT License. See LICENSE file.

## Contact

Questions? Open an issue or email: yourname@example.com
```

---

**Why this README works**:
1. **Layered information**: Overview → Installation → Quick Start → Detailed Sections
2. **Concrete example**: Shows actual code and output (not just abstract description)
3. **Transparency**: Clearly states assumptions and limitations (prevents misuse)
4. **Actionable**: Users can get started immediately with Quick Start
5. **Visual**: Architecture diagram clarifies structure
6. **Complete**: Covers installation, usage, API, limitations, contributing

---

Adapt sections as needed (e.g., remove "Contributing" if closed-source, expand "API Reference" if complex library).

## Tips for Effective Communication

**Know when to stop explaining**: Over-explanation is as bad as under-explanation. If the audience has enough to proceed, stop. They can ask for more if needed.

**Test your explanations**: Ask a colleague (or ChatGPT) to summarize what you wrote. If the summary is wrong, your explanation was unclear.

**Use consistent terminology**: Don't call it "telemetry" in one place and "housekeeping data" in another. Pick one term and stick with it.

**Update documentation as code evolves**: Outdated docs are worse than no docs—they mislead. Treat docs as code (version control, review, update with changes).

**Link to references**: If you mention "SGP4," link to the reference (Vallado's book, Celestrak). Readers can dive deeper if curious.

**Avoid hedging excessively**: "This might possibly potentially work" lacks confidence. Say "This works under these conditions" or "This is experimental."

## When Technical Communication is Complete

You've succeeded when:
- The audience understands enough to use/evaluate/decide (matched to their need)
- Questions are clarifications, not "I don't understand what this is"
- Documentation is layered (skimmers and deep-divers both find what they need)
- Decisions are documented with rationale (future maintainers understand "why")
- Examples make abstract concepts concrete
