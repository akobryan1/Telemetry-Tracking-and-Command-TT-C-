# Propagator Choice: SGP4 vs Numerical Integration with J2

## Question
For my satellite simulator, should I use SGP4 propagator or a numerical integrator with J2 perturbations? I'm simulating LEO satellites over 7-day periods and need position accuracy to within a few kilometers.

## Analysis

For **LEO satellites over 7 days with few-kilometer accuracy requirements**, here's my recommendation:

### Use SGP4 if:
- You're working with operational satellites where TLEs are readily available
- Your accuracy requirement is "within a few kilometers" (SGP4 typically achieves 1-2 km near the TLE epoch, degrading to 2-5 km over a week)
- You want simplicity and don't need to model custom spacecraft or maneuvers
- Implementation speed matters (SGP4 libraries are widely available and well-tested)

### Use Numerical Integration with J2 if:
- You need predictable accuracy guarantees throughout the 7-day period
- You're simulating custom spacecraft designs or mission planning scenarios
- You have accurate initial state vectors (not just TLEs)
- You might need to add more perturbations later (atmospheric drag, solar radiation pressure, third-body effects)
- You need sub-kilometer accuracy consistently

## Recommendation: **Start with SGP4**

For your stated requirements, SGP4 should be sufficient:
- 7 days is within SGP4's reasonable accuracy window when using fresh TLEs
- "Within a few kilometers" aligns well with SGP4's typical performance
- The simplicity advantage is significant for initial development
- You can always upgrade to numerical integration later if you need better accuracy

**However**, if you're developing a simulator for mission planning or trajectory design (not just tracking existing satellites), numerical integration with J2 (and potentially J3, J4) would be the better foundation, as it gives you more control and extensibility.

## Key Question
Are you tracking real satellites (use SGP4) or designing missions (use numerical integration)?

## Technical Details

### SGP4 Characteristics:
- Analytical propagator specifically designed for TLE data
- Includes simplified drag and perturbation models
- Accuracy: ~1-2 km near epoch, degrading over time
- Very fast computation
- Cannot model spacecraft maneuvers

### Numerical Integration + J2 Characteristics:
- Solves differential equations of motion numerically (e.g., RK4, RK45)
- J2 term accounts for Earth's oblateness (primary perturbation in LEO)
- Accuracy depends on integration step size and force models
- More computationally intensive but still efficient for LEO
- Extensible to additional perturbations (J3, J4, drag, SRP, third-body)
- Requires good initial conditions (position and velocity vectors)

### For 7-Day LEO Simulations:
- Both approaches can meet "few kilometer" accuracy
- SGP4 advantage: Direct use of publicly available TLE data
- Numerical integration advantage: Consistent accuracy, easier to add physics
- Hybrid approach possible: Use SGP4 for quick analysis, numerical for detailed studies
