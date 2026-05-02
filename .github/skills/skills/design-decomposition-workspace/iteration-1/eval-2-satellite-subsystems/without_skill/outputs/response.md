# Satellite Simulation Decomposition - Baseline Response

## Problem Context

Building a satellite simulation with tightly coupled subsystems:
- **Attitude control** (reaction wheels and magnetorquers)
- **Power management** (solar panels and batteries tracking sun angle and eclipse periods)
- **Thermal management** (heaters controlled based on component temperatures)

Key couplings:
- Attitude affects which solar panels see the sun
- Sun exposure affects power generation
- Power availability affects whether heaters can run
- Temperature affects component operation

## Breaking Down the Coupled System

### Understanding the Challenge

You're facing a classic **tightly-coupled system** where subsystems have circular dependencies. The key to managing this is to recognize that these couplings exist at different timescales and to establish a clear **data flow architecture**.

### Decomposition Strategy

#### 1. **Identify State Variables and Their Owners**

First, clearly define what each subsystem owns:

- **Attitude Subsystem** owns:
  - Quaternion/Euler angles (spacecraft orientation)
  - Angular velocity
  - Reaction wheel speeds
  - Magnetorquer currents

- **Power Subsystem** owns:
  - Battery state of charge
  - Solar panel currents/voltages
  - Power bus voltage
  - Available power budget

- **Thermal Subsystem** owns:
  - Component temperatures (battery, reaction wheels, electronics, etc.)
  - Heater states (on/off)
  - Heat flows

#### 2. **Define Unidirectional Data Flow**

Break the circular dependencies by establishing a **computation order** within each simulation timestep:

```
Time step n:
┌─────────────────────────────────────────┐
│ 1. Orbital Mechanics (Environment)      │
│    - Compute sun vector                 │
│    - Compute eclipse state              │
│    - Compute magnetic field vector      │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 2. Attitude Control                     │
│    - Read current attitude (from t-1)   │
│    - Compute control torques            │
│    - Update attitude state              │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 3. Power Generation                     │
│    - Use updated attitude               │
│    - Compute sun angles on panels       │
│    - Calculate power generation         │
│    - Update battery SOC                 │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 4. Thermal Management                   │
│    - Use power availability             │
│    - Decide heater states               │
│    - Update temperatures                │
└─────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────┐
│ 5. Power Consumption                    │
│    - Tally all loads (attitude, thermal)│
│    - Update final battery state         │
└─────────────────────────────────────────┘
```

This is a **forward Euler-style approach** where you use previous timestep values to compute current values, accepting one-timestep lag.

#### 3. **Create a Clean Interface Layer**

Define a **context object** or **state vector** that gets passed between subsystems:

```python
class SimulationState:
    # Environment
    sun_vector_body: np.ndarray  # Sun direction in body frame
    eclipse: bool
    magnetic_field_body: np.ndarray
    
    # Attitude
    quaternion: np.ndarray
    angular_velocity: np.ndarray
    
    # Power
    battery_soc: float  # 0-1
    available_power: float  # Watts
    
    # Thermal
    temperatures: dict  # {'battery': 273, 'rw1': 298, ...}
```

Each subsystem receives this state, updates its portion, and passes it forward.

#### 4. **Implementation Roadmap**

**Phase 1: Isolated Subsystems**
- Build each subsystem independently with **mock inputs**
- Attitude control: hardcode sun vector, test reaction wheel logic
- Power: hardcode attitude, test power generation math
- Thermal: hardcode power availability, test temperature propagation

**Phase 2: Pairwise Integration**
- Attitude + Power: Verify sun angle calculations affect power correctly
- Power + Thermal: Verify heaters respond to power availability
- Create integration tests for each pair

**Phase 3: Full System Integration**
- Wire all subsystems together following your data flow
- Use a **simulation manager** that orchestrates the sequence

**Phase 4: Iterative Refinement**
- Add predictor-corrector if one-step lag causes instability
- Add more sophisticated coupling (e.g., reaction wheel heat affects thermal)

### Practical Implementation Pattern

Here's a skeleton structure:

```python
class SimulationManager:
    def __init__(self, timestep):
        self.dt = timestep
        self.env = OrbitalEnvironment()
        self.attitude = AttitudeControl()
        self.power = PowerSystem()
        self.thermal = ThermalSystem()
        self.state = SimulationState()
    
    def step(self):
        # 1. Environment
        self.env.update(self.state, self.dt)
        
        # 2. Attitude (uses old power constraints)
        power_limit = self.state.available_power
        self.attitude.update(self.state, self.dt, power_limit)
        
        # 3. Power generation (uses new attitude)
        self.power.update_generation(self.state, self.dt)
        
        # 4. Thermal (uses available power)
        heater_power = self.thermal.update(self.state, self.dt)
        
        # 5. Final power accounting
        self.power.apply_loads({
            'attitude': self.attitude.get_power_consumption(),
            'thermal': heater_power
        })
```

### Handling Tight Coupling

For cases where one-timestep lag isn't acceptable:

1. **Iteration within timestep**: 
   - Compute power → thermal → power again until convergence
   - Usually 2-3 iterations suffice

2. **Implicit integration**:
   - For thermal diffusion equations, use implicit methods
   - Allows larger timesteps

3. **Event detection**:
   - Detect eclipse entry/exit precisely
   - Adjust timestep around critical events

### Key Principles

1. **Separation of concerns**: Each subsystem doesn't need to know *how* others work, only *what* data they provide
2. **Explicit dependencies**: Make data flow obvious in code
3. **Test in isolation**: Unit test each subsystem with synthetic inputs
4. **Progressive integration**: Don't try to make everything work at once
5. **Accept approximations**: Perfect physical accuracy isn't needed for first version

### Starting Point

I'd recommend starting with:

1. **Fixed attitude** (nadir-pointing) → Build power system
2. **Add simple attitude control** → Verify power coupling works
3. **Add thermal with fixed heater schedule** → Verify power drain
4. **Make thermal reactive** → Close the loop

This gives you working increments at each step rather than trying to build everything simultaneously.

## Summary

The key to managing this coupled system is:

1. **Accept one-timestep lag** in most couplings (for performance and simplicity)
2. **Define clear data flow** with a fixed computation order
3. **Build incrementally** - don't integrate everything at once
4. **Use a shared state object** that each subsystem reads from and writes to
5. **Test subsystems in isolation** before integration

Start simple (fixed attitude), add complexity incrementally, and verify each coupling works before adding the next. This approach turns an overwhelming problem into manageable steps.
