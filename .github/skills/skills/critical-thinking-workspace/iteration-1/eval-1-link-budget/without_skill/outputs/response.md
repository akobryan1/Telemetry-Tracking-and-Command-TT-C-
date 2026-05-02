# Link Budget Calculator Evaluation - Baseline Response

## Your Approach
- Free-space path loss (FSPL) equation
- Fixed atmospheric attenuation: 0.5 dB
- Fixed antenna mispointing: 1 dB
- Target: LEO satellites at VHF/UHF bands

## Critical Issues and Missing Components

### 1. **Missing Core Link Budget Terms**
Your approach only addresses path loss and two margin terms. A complete link budget requires:

- **Transmitter EIRP** (Effective Isotropic Radiated Power)
  - Tx power (dBW)
  - Tx antenna gain (dBi)
  - Tx line losses (dB)

- **Receiver Performance**
  - Rx antenna gain (dBi)
  - Rx line losses (dB)
  - System noise temperature or noise figure
  - Required C/N₀ or Eb/N₀ for your modulation scheme

- **Link Margin Calculation**
  - Received power vs. receiver sensitivity
  - Margin against threshold

### 2. **Oversimplified Fixed Margins**

**Atmospheric Attenuation (0.5 dB fixed)**
- VHF/UHF atmospheric absorption is minimal but varies with:
  - Elevation angle (worst at low elevations, ~5-10°)
  - Weather conditions (rain, fog, clouds)
  - Frequency within VHF/UHF range
- At 10° elevation, losses could be 2-3x higher than at zenith
- Rain effects are minimal at VHF but increase at UHF

**Antenna Mispointing (1 dB fixed)**
- Loss depends on:
  - Antenna beamwidth (narrower beams = higher sensitivity to pointing errors)
  - Tracking system accuracy
  - Elevation angle (lower elevations have higher atmospheric refraction)
  - Satellite position uncertainty (TLE accuracy degrades over time)
- For a 3° beamwidth antenna with 1° pointing error: ~1 dB loss
- For a 10° beamwidth: 0.2-0.3 dB loss
- Automatic tracking vs. manual pointing makes a huge difference

### 3. **Missing VHF/UHF-Specific Effects**

**Ionospheric Effects**
- **Faraday rotation**: Linear polarization rotates as it passes through ionosphere
  - Can cause 10-20 dB+ polarization mismatch loss at VHF
  - Highly variable with solar activity, time of day, latitude
  - Critical issue if using linear polarization
  - Less significant with circular polarization
  
- **Ionospheric scintillation**: Signal amplitude/phase fluctuations
  - Worse at low elevations and during solar maximum
  - Can cause several dB of fading at VHF/UHF

- **Total Electron Content (TEC)**: Affects group delay and phase advance

**Doppler Shift**
- LEO satellites have high relative velocities
- VHF/UHF: ±3-10 kHz shifts typical
- Receiver must handle this or link fails

### 4. **Missing Practical Factors**

- **Polarization loss**: 0-3 dB for circular, 0-20+ dB for linear (see Faraday rotation)
- **Cable/connector losses**: 0.5-3 dB depending on length and frequency
- **Multipath interference**: Ground reflections at low elevation angles
- **RFI/noise floor**: Urban vs. rural noise environments differ by 10-20 dB
- **Satellite attitude variations**: Antenna pattern changes if satellite tumbles
- **Elevation angle dependency**: 
  - Lower elevations → longer path → higher FSPL
  - Lower elevations → more atmospheric effects
  - Minimum operational elevation (typically 5-10°)

### 5. **Dynamic Range Issues**

LEO passes have highly variable geometry:
- **Range variation**: 400 km (zenith) to 2000+ km (horizon)
  - This alone causes ~14 dB variation in FSPL
- **Elevation angle**: 90° (overhead) to 5° (horizon)
- **Different analysis needed for**:
  - Best case (satellite overhead)
  - Worst case (low elevation, max range)
  - Statistical analysis (% of pass above threshold)

### 6. **Regulatory and Operational Margins**

- **Fade margin**: 3-6 dB typical for reliable operation
- **Implementation losses**: 1-2 dB (hardware imperfections)
- **Required link availability**: 99%? 99.9%? Drives margin requirements

## What You Should Do Instead

### Minimum Viable Link Budget
```
Received Power (dBW) = EIRP - FSPL - Losses + Rx_Gain

Where:
- EIRP = Satellite Tx Power + Tx Antenna Gain - Tx Line Loss
- FSPL(dB) = 32.45 + 20log₁₀(f_MHz) + 20log₁₀(d_km)
- Losses = Atmospheric + Polarization + Pointing + Cables + Misc
- Rx_Gain = Antenna Gain - Line Loss

Required Margin (dB) = Received Power - Receiver Sensitivity
```

### Better Approach for LEO VHF/UHF

1. **Calculate FSPL for range of scenarios**:
   - Closest approach (satellite overhead)
   - Horizon pass (max range at minimum elevation)
   - Use actual orbital altitude

2. **Model elevation-dependent losses**:
   - Atmospheric: Use ITU-R P.676 model or similar
   - Ionospheric: Use IRI model or statistical worst-case values
   - Antenna gain pattern variation with elevation

3. **Handle polarization properly**:
   - If satellite uses linear → budget for worst-case Faraday rotation
   - If satellite uses circular → use circular ground antenna
   - Polarization loss = 20log₁₀(|cos(rotation angle)|)

4. **Account for all hardware in chain**:
   - LNA noise figure and gain
   - Cable losses at operating frequency
   - Filter insertion losses
   - Connector losses

5. **Calculate link closure for**:
   - Best case (overhead pass)
   - Worst case (horizon pass at minimum elevation)
   - Include adequate fade margin (3-6 dB minimum)

### Tools and Resources

- **Software**: Consider using established tools like STK, GMAT, or Python libraries (Skyfield + custom RF)
- **Models**: 
  - ITU-R P.618 (propagation)
  - ITU-R P.676 (atmospheric gases)
  - IRI model (ionosphere)
- **References**: SMAD (Space Mission Analysis and Design), NASA Systems Engineering Handbook

## Bottom Line

Your simplified approach will likely **underestimate required link margin by 10-20 dB** for LEO VHF/UHF, primarily due to:
- Missing ionospheric effects (especially Faraday rotation)
- No accounting for elevation angle geometry
- Omitting receiver noise performance
- Fixed margins instead of scenario-dependent values

For a functional TT&C ground station, you need at minimum:
- Complete power budget (Tx to Rx)
- Elevation-dependent atmospheric model
- Ionospheric loss budget (critical at VHF/UHF)
- Proper polarization handling
- Analysis across full orbital pass, not just one snapshot
- Adequate link margin (>6 dB for reliable comms)
