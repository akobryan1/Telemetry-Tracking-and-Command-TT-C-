# TT&C Meta-Cognitive Skills Suite

A collection of 6 specialized agentic skills designed to enhance Claude's capabilities for TT&C (Telemetry, Tracking & Command) simulation development and complex aerospace engineering projects.

## Overview

This skill suite provides meta-cognitive capabilities that help with:
- **System Design**: Breaking down complex systems and critically evaluating approaches
- **Knowledge Integration**: Synthesizing multi-domain technical knowledge
- **Development Strategy**: Building incrementally with working checkpoints
- **Communication**: Documenting and explaining technical work effectively
- **Uncertainty Management**: Making progress despite incomplete information

## Skills in This Suite

### 1. Design Decomposition (`design-decomposition`)
**Purpose**: Systematically break down complex systems into manageable components before implementation

**Use when:**
- Starting a new complex project
- Facing "where do I even start?" paralysis
- Need to identify subsystems and their interfaces
- Planning architecture before coding

**Key capabilities:**
- 6-step decomposition process
- Identifies subsystems, dependencies, data flows
- TT&C-specific patterns (satellite subsystems, ground station architecture, protocol stacks)

**Triggers**: "How should I structure...", "Break down this system", "What are the components?"

**Benchmark**: 94.4% pass rate (with skill) vs 83.3% (baseline) → **+11.1% improvement**

---

### 2. Critical Thinking (`critical-thinking`)
**Purpose**: Question assumptions, evaluate trade-offs, and identify potential flaws in technical approaches

**Use when:**
- Evaluating design proposals or implementation plans
- Need to identify hidden assumptions
- Comparing alternative approaches
- Reviewing code or designs for potential issues

**Key capabilities:**
- 6-step critical analysis process
- Assumption identification and validation
- Trade-off evaluation frameworks
- TT&C domain-specific critiques (link budgets, orbital mechanics, protocols)

**Triggers**: "Is this approach sound?", "What could go wrong?", "Should I use X or Y?", "Critique this design"

**Benchmark**: 95% pass rate (with skill) vs 76% (baseline) → **+19% improvement**

---

### 3. Information Synthesis (`info-synthesis`)
**Purpose**: Pull together concepts from multiple technical domains to provide integrated understanding

**Use when:**
- Need to understand how concepts from different fields connect
- Questions spanning orbital mechanics + RF + software + protocols
- Want to see cross-domain dependencies
- Need holistic view of multi-faceted topics

**Key capabilities:**
- 6-step synthesis process
- Multi-domain integration (orbital mechanics affects RF, RF affects protocols, protocols affect software)
- TT&C synthesis patterns
- Concrete cross-domain examples

**Triggers**: "How does X relate to Y?", "Explain how [domain A] affects [domain B]", "What do I need to know about [multi-domain topic]?"

---

### 4. Iterative Problem Solving (`iterative-solving`)
**Purpose**: Start with minimal working systems and layer complexity incrementally

**Use when:**
- Project feels overwhelming
- Don't know where to start
- Need roadmap from basic to full-featured
- Want working checkpoints to validate progress

**Key capabilities:**
- Minimal core definition
- Iteration layer planning
- Dependency-ordered feature addition
- TT&C iteration patterns (physics fidelity ladder, time simulation ladder)

**Triggers**: "Where should I start?", "This feels too complex", "What's the simplest version?", "How do I add [feature]?"

---

### 5. Technical Communication (`tech-communication`)
**Purpose**: Document, explain, and communicate technical work effectively to different audiences

**Use when:**
- Writing documentation (READMEs, design docs, API docs)
- Explaining systems to stakeholders
- Creating diagrams or visualizations
- Need audience-appropriate explanations

**Key capabilities:**
- Audience identification and adaptation
- Hierarchical information structuring
- Diagram creation guidance
- TT&C communication patterns (orbital mechanics for non-experts, simulation assumptions)

**Triggers**: "How do I explain this?", "I need to document...", "Can you help me write...", "How would you describe this to [audience]?"

---

### 6. Ambiguity Management (`ambiguity-management`)
**Purpose**: Handle incomplete information and make deliberate engineering choices with documented assumptions

**Use when:**
- Missing data or parameters
- Unclear specifications
- Undefined system behaviors
- Need to make progress despite uncertainty

**Key capabilities:**
- Ambiguity categorization (missing data, undefined behavior, underspecified requirements)
- Risk assessment (low/medium/high)
- Conservative choice strategies
- Assumption documentation templates
- TT&C ambiguity patterns (missing satellite parameters, undefined protocol behaviors)

**Triggers**: "I don't know [parameter]", "What if I don't have [data]?", "The spec doesn't say...", "How do I proceed without knowing [X]?"

---

## Skill Interactions & Workflows

These skills work independently but also complement each other in common workflows:

### Workflow 1: New Project Start
1. **Design Decomposition** → Break system into components
2. **Iterative Solving** → Plan minimal core and iteration layers
3. **Ambiguity Management** → Handle missing requirements
4. **Tech Communication** → Document architecture

### Workflow 2: Design Review
1. **Critical Thinking** → Evaluate proposed approach
2. **Info Synthesis** → Understand cross-domain implications
3. **Design Decomposition** → Verify completeness of subsystems

### Workflow 3: Implementation
1. **Iterative Solving** → Build incrementally
2. **Ambiguity Management** → Handle missing data
3. **Tech Communication** → Document decisions

### Workflow 4: Stakeholder Communication
1. **Info Synthesis** → Build integrated understanding
2. **Tech Communication** → Explain to appropriate audience
3. **Critical Thinking** → Anticipate questions about trade-offs

## Quick Reference: When to Use Which Skill

| Situation | Primary Skill | Supporting Skills |
|-----------|--------------|-------------------|
| Starting new project | `design-decomposition` | `iterative-solving`, `ambiguity-management` |
| Evaluating approach | `critical-thinking` | `info-synthesis` |
| Understanding multi-domain topic | `info-synthesis` | `tech-communication` |
| Feeling overwhelmed | `iterative-solving` | `design-decomposition` |
| Writing docs | `tech-communication` | `info-synthesis` |
| Missing requirements | `ambiguity-management` | `critical-thinking` |
| Explaining to stakeholders | `tech-communication` | `info-synthesis` |
| Debugging complex system | `info-synthesis` | `design-decomposition` |
| Adding new feature | `iterative-solving` | `critical-thinking` |

## Installation

These skills are VS Code Copilot agent customizations and auto-load from `.github/skills/`:

1. **No installation needed** if skills are already in your workspace at:
   ```
   .github/skills/skills/
   ├── design-decomposition/
   ├── critical-thinking/
   ├── info-synthesis/
   ├── iterative-solving/
   ├── tech-communication/
   └── ambiguity-management/
   ```

2. **Verify skills are loaded**: Ask Copilot a question matching a skill trigger phrase

3. **Test a skill**: Try "Break down a satellite ground station system" (should trigger `design-decomposition`)

## Testing & Validation

Each skill includes evaluation test cases in `evals/evals.json`:

| Skill | Test Cases | Benchmark Status |
|-------|-----------|------------------|
| Design Decomposition | 3 scenarios | ✅ Tested: 94.4% vs 83.3% (+11.1%) |
| Critical Thinking | 3 scenarios | ✅ Tested: 95% vs 76% (+19%) |
| Info Synthesis | 2 scenarios | ⏳ Created, not yet run |
| Iterative Solving | 2 scenarios | ⏳ Created, not yet run |
| Tech Communication | 2 scenarios | ⏳ Created, not yet run |
| Ambiguity Management | 2 scenarios | ⏳ Created, not yet run |

**To run evaluations**:
```bash
# From skill-creator folder
python run_eval.py --skill-path ../skills/[skill-name] --iteration [N]
```

## TT&C Domain Coverage

While these skills are general-purpose meta-cognitive tools, they include extensive TT&C/aerospace domain knowledge:

**Orbital Mechanics**:
- SGP4 propagation, TLEs, Kepler elements
- Coordinate systems (ECI, ECEF, topocentric)
- Orbital perturbations, eclipse calculations
- Pass prediction (AOS/LOS)

**RF Communications**:
- Link budgets (FSPL, EIRP, G/T, noise figure)
- Doppler shift and compensation
- Modulation schemes (BPSK, QPSK)
- BER, SNR, error correction coding

**Protocols**:
- CCSDS Space Packets, Transfer Frames
- Packet parsing, synchronization, CRC validation
- Command uplink, telemetry downlink
- APID routing

**Ground Stations**:
- Antenna pointing (azimuth/elevation)
- Multi-satellite tracking
- Receiver chains (LNA, mixer, demod, decoder)

**Spacecraft Subsystems**:
- Power (solar panels, batteries, power budgets)
- Thermal (heaters, radiators, temperature limits)
- Attitude (ADCS, reaction wheels, magnetorquers)
- Communications (transmitters, antennas, transponders)

**Systems Engineering**:
- Subsystem decomposition and interfaces
- Requirements flow-down
- Command validation across layers
- Trade-off analysis

## Development Methodology

These skills were created using Anthropic's skill-creator framework:

1. ✅ **Skill Definition**: Identify meta-cognitive capability and trigger conditions
2. ✅ **Methodology Development**: Create structured process (6-8 steps each)
3. ✅ **Domain Integration**: Add TT&C examples and patterns
4. ✅ **Evaluation Creation**: Write test cases (2-3 per skill)
5. ⏳ **Testing**: Run with-skill vs baseline subagents (2 of 6 complete)
6. ⏳ **Grading**: Assess responses against criteria
7. ⏳ **Benchmarking**: Aggregate pass rates
8. ⏳ **Description Optimization**: Run optimization loop (not yet started)

## Current Status

**Phase**: Development complete, partial validation

**Completed**:
- ✅ All 6 SKILL.md files created with comprehensive methodologies
- ✅ All 6 evals.json files created with test scenarios
- ✅ Skills #1-2 fully tested and benchmarked (11-19% improvement over baseline)
- ✅ Integration guide and skill boundaries defined

**Remaining**:
- ⏳ Run evaluations for skills #3-6
- ⏳ Generate benchmarks for skills #3-6
- ⏳ Description optimization (requires trigger query generation + run_loop.py)
- ⏳ Cross-skill integration testing
- ⏳ Package individual skills (package_skill.py)

## Skill Architecture

Each skill follows consistent structure:

```
skill-name/
├── SKILL.md              # Main skill methodology
│                         # - YAML frontmatter (name, description)
│                         # - When to use section
│                         # - Step-by-step process
│                         # - TT&C patterns
│                         # - Examples
│
├── evals/
│   └── evals.json       # Test cases for validation
│
└── workspace/           # Evaluation outputs (if run)
    └── iteration-N/
        ├── with-skill/
        └── baseline/
```

**SKILL.md components**:
- **YAML frontmatter**: `name`, `description` (skill discovery triggers)
- **When to Use**: Trigger conditions and example phrases
- **Process**: Structured methodology (typically 6-8 steps)
- **Domain Patterns**: TT&C-specific guidance and examples
- **Output Format**: How to structure responses
- **Examples**: Concrete demonstrations
- **Tips**: Best practices
- **Completion Criteria**: When skill objective achieved

## Trigger Phrase Quick Reference

**Design Decomposition**:
- "How should I structure [system]?"
- "Break down [complex system]"
- "What are the components of..."
- "I need to design [architecture]"

**Critical Thinking**:
- "Is this approach sound?"
- "What could go wrong?"
- "Should I use X or Y?"
- "Critique this design"
- "What are the trade-offs?"

**Info Synthesis**:
- "How does X relate to Y?"
- "Explain how [domain A] affects [domain B]"
- "What do I need to know about [multi-domain topic]?"
- "Walk me through [process]"

**Iterative Solving**:
- "Where should I start?"
- "This feels too complex"
- "What's the simplest version?"
- "How do I add [feature] incrementally?"

**Tech Communication**:
- "How do I explain this?"
- "I need to document..."
- "Can you help me write a README?"
- "How would you describe this to [audience]?"

**Ambiguity Management**:
- "I don't know [parameter]"
- "What if I don't have [data]?"
- "The spec doesn't say..."
- "How do I proceed without knowing [X]?"

## Contributing

Contributions welcome:
- Additional TT&C examples for existing skills
- More evaluation test cases
- Benchmark results for skills #3-6
- Description optimization results
- Bug fixes or methodology improvements

## License

MIT License (or as appropriate for workspace)

---

## Appendix: Skills vs. Traditional Prompting

**Traditional prompt**: "Help me build a ground station"
- Response: Direct implementation or high-level overview
- No structured methodology
- May miss critical steps

**With skills**: "I need to build a ground station but don't know where to start"
- Triggers: `iterative-solving` (overwhelm) + potentially `design-decomposition` (complex system)
- Response: Structured roadmap with minimal core, iteration layers, validation checkpoints
- Methodology: Proven process that avoids common pitfalls

**Value**: Skills encode expert problem-solving strategies, not just domain knowledge.
