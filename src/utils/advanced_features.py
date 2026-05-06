"""
Advanced TT&C Features (Phase 10)

Implements:
- Link budget calculator
- Pass scheduler/optimizer
- Anomaly detection system
"""

import math
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


class LinkBudgetCalculator:
    """
    Calculate satellite communication link budget.
    
    Link Budget = Tx Power + Tx Gain - Path Loss - Atmospheric Loss 
                  + Rx Gain - System Losses
    """
    
    # Physical constants
    SPEED_OF_LIGHT = 299792.458  # km/s
    BOLTZMANN_CONSTANT = -228.6  # dBW/K/Hz
    
    def __init__(self):
        """Initialize link budget calculator."""
        pass
    
    def calculate_free_space_path_loss(self, frequency_mhz: float, 
                                      range_km: float) -> float:
        """
        Calculate free space path loss (FSPL).
        
        FSPL (dB) = 20*log10(d) + 20*log10(f) + 32.45
        where d is range in km, f is frequency in MHz
        
        Args:
            frequency_mhz: Frequency in MHz
            range_km: Range in kilometers
        
        Returns:
            Path loss in dB
        """
        if range_km <= 0 or frequency_mhz <= 0:
            return 0.0
        
        fspl = 20 * math.log10(range_km) + 20 * math.log10(frequency_mhz) + 32.45
        return round(fspl, 2)
    
    def calculate_atmospheric_loss(self, elevation_deg: float, 
                                   frequency_mhz: float) -> float:
        """
        Estimate atmospheric attenuation.
        
        Simplified model: increases at low elevations and high frequencies.
        
        Args:
            elevation_deg: Elevation angle in degrees
            frequency_mhz: Frequency in MHz
        
        Returns:
            Atmospheric loss in dB
        """
        if elevation_deg <= 0:
            return 10.0  # High loss below horizon
        
        # Simplified atmospheric model
        # Higher loss at low elevations (longer path through atmosphere)
        elevation_factor = 1.0 / math.sin(math.radians(max(elevation_deg, 5)))
        
        # Frequency-dependent loss (increases with frequency)
        if frequency_mhz < 3000:  # S-band and below
            freq_loss = 0.5
        elif frequency_mhz < 12000:  # X-band
            freq_loss = 1.0
        else:  # Ku-band and above
            freq_loss = 2.0
        
        atm_loss = freq_loss * elevation_factor
        return round(min(atm_loss, 10.0), 2)  # Cap at 10 dB
    
    def calculate_link_budget(self, tx_power_dbw: float, tx_gain_dbi: float,
                             rx_gain_dbi: float, frequency_mhz: float,
                             range_km: float, elevation_deg: float,
                             system_losses_db: float = 3.0) -> Dict[str, float]:
        """
        Calculate complete link budget.
        
        Args:
            tx_power_dbw: Transmit power in dBW
            tx_gain_dbi: Transmit antenna gain in dBi
            rx_gain_dbi: Receive antenna gain in dBi
            frequency_mhz: Frequency in MHz
            range_km: Range in km
            elevation_deg: Elevation angle in degrees
            system_losses_db: System losses (cables, connectors, etc.)
        
        Returns:
            Dictionary with link budget components
        """
        # Calculate losses
        path_loss = self.calculate_free_space_path_loss(frequency_mhz, range_km)
        atm_loss = self.calculate_atmospheric_loss(elevation_deg, frequency_mhz)
        
        # Calculate received power
        # Pr = Pt + Gt - Lpath - Latm + Gr - Lsys
        received_power = (tx_power_dbw + tx_gain_dbi - path_loss - 
                         atm_loss + rx_gain_dbi - system_losses_db)
        
        # Link margin (assume noise floor of -130 dBW)
        noise_floor = -130.0  # Typical for narrowband receivers
        link_margin = received_power - noise_floor
        
        return {
            'tx_power_dbw': round(tx_power_dbw, 2),
            'tx_gain_dbi': round(tx_gain_dbi, 2),
            'rx_gain_dbi': round(rx_gain_dbi, 2),
            'path_loss_db': round(path_loss, 2),
            'atmospheric_loss_db': round(atm_loss, 2),
            'system_losses_db': round(system_losses_db, 2),
            'received_power_dbw': round(received_power, 2),
            'noise_floor_dbw': round(noise_floor, 2),
            'link_margin_db': round(link_margin, 2),
            'link_status': 'GOOD' if link_margin > 10 else ('MARGINAL' if link_margin > 3 else 'POOR')
        }


class PassScheduler:
    """
    Optimize satellite pass scheduling across network.
    
    Prioritizes passes based on:
    - Maximum elevation
    - Pass duration
    - Station availability
    - Link quality
    """
    
    def __init__(self):
        """Initialize pass scheduler."""
        pass
    
    def score_pass(self, max_elevation: float, duration_min: float,
                  link_margin_db: float) -> float:
        """
        Calculate pass quality score (0-100).
        
        Args:
            max_elevation: Maximum elevation in degrees
            duration_min: Pass duration in minutes
            link_margin_db: Link margin in dB
        
        Returns:
            Pass quality score (0-100)
        """
        # Elevation score (0-40 points)
        # Max at 90 degrees
        elevation_score = (max_elevation / 90.0) * 40.0
        
        # Duration score (0-30 points)
        # Max at 10+ minutes
        duration_score = min(duration_min / 10.0, 1.0) * 30.0
        
        # Link quality score (0-30 points)
        # Max at 20+ dB margin
        link_score = min(max(link_margin_db, 0) / 20.0, 1.0) * 30.0
        
        total_score = elevation_score + duration_score + link_score
        return round(total_score, 1)
    
    def optimize_schedule(self, passes: List[Dict[str, Any]], 
                         max_passes: int = 10) -> List[Dict[str, Any]]:
        """
        Select best passes from available options.
        
        Args:
            passes: List of pass dictionaries with timing and metrics
            max_passes: Maximum number of passes to schedule
        
        Returns:
            Sorted list of best passes
        """
        # Score each pass
        for p in passes:
            score = self.score_pass(
                p.get('max_elevation', 0),
                p.get('duration_min', 0),
                p.get('link_margin_db', 10)  # Default to moderate margin
            )
            p['quality_score'] = score
        
        # Sort by score (descending) and return top N
        sorted_passes = sorted(passes, key=lambda x: x.get('quality_score', 0), 
                             reverse=True)
        
        return sorted_passes[:max_passes]


class AnomalyDetector:
    """
    Detect anomalies in telemetry data.
    
    Uses simple threshold-based detection and trend analysis.
    """
    
    # Normal ranges for telemetry
    NORMAL_RANGES = {
        'battery_voltage': (26.0, 30.0),
        'solar_current': (0.0, 3.5),
        'temperature': (-15.0, 45.0)
    }
    
    # Rate of change limits (per minute)
    RATE_LIMITS = {
        'battery_voltage': 0.5,  # V/min
        'solar_current': 1.0,    # A/min
        'temperature': 5.0       # C/min
    }
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.history = []  # Store recent telemetry
        self.max_history = 100  # Keep last 100 samples
    
    def add_sample(self, telemetry: Dict[str, float], timestamp: datetime):
        """
        Add telemetry sample to history.
        
        Args:
            telemetry: Telemetry data dictionary
            timestamp: Timestamp of sample
        """
        sample = {
            'timestamp': timestamp,
            'battery_voltage': telemetry.get('battery_voltage', 0),
            'solar_current': telemetry.get('solar_current', 0),
            'temperature': telemetry.get('temperature', 0)
        }
        
        self.history.append(sample)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def check_thresholds(self, telemetry: Dict[str, float]) -> List[Dict[str, str]]:
        """
        Check if telemetry values are within normal ranges.
        
        Args:
            telemetry: Current telemetry data
        
        Returns:
            List of anomaly dictionaries
        """
        anomalies = []
        
        for param, (min_val, max_val) in self.NORMAL_RANGES.items():
            value = telemetry.get(param, 0)
            
            if value < min_val:
                anomalies.append({
                    'type': 'THRESHOLD_LOW',
                    'parameter': param,
                    'value': value,
                    'threshold': min_val,
                    'severity': 'HIGH' if value < min_val * 0.9 else 'MEDIUM'
                })
            elif value > max_val:
                anomalies.append({
                    'type': 'THRESHOLD_HIGH',
                    'parameter': param,
                    'value': value,
                    'threshold': max_val,
                    'severity': 'HIGH' if value > max_val * 1.1 else 'MEDIUM'
                })
        
        return anomalies
    
    def check_rate_of_change(self, telemetry: Dict[str, float]) -> List[Dict[str, str]]:
        """
        Check for rapid changes in telemetry.
        
        Args:
            telemetry: Current telemetry data
        
        Returns:
            List of rate-of-change anomalies
        """
        anomalies = []
        
        if len(self.history) < 2:
            return anomalies  # Need at least 2 samples
        
        # Compare with most recent sample
        prev = self.history[-1]
        time_delta_min = 1.0  # Assume 1 minute between samples
        
        for param, max_rate in self.RATE_LIMITS.items():
            current_val = telemetry.get(param, 0)
            prev_val = prev.get(param, 0)
            
            rate = abs(current_val - prev_val) / time_delta_min
            
            if rate > max_rate:
                anomalies.append({
                    'type': 'RATE_CHANGE',
                    'parameter': param,
                    'rate': round(rate, 3),
                    'max_rate': max_rate,
                    'severity': 'HIGH' if rate > max_rate * 2 else 'MEDIUM'
                })
        
        return anomalies
    
    def detect_anomalies(self, telemetry: Dict[str, float], 
                        timestamp: datetime) -> Dict[str, Any]:
        """
        Comprehensive anomaly detection.
        
        Args:
            telemetry: Current telemetry data
            timestamp: Timestamp of data
        
        Returns:
            Dictionary with anomaly report
        """
        # Check thresholds
        threshold_anomalies = self.check_thresholds(telemetry)
        
        # Check rate of change
        rate_anomalies = self.check_rate_of_change(telemetry)
        
        # Add to history
        self.add_sample(telemetry, timestamp)
        
        # Combine results
        all_anomalies = threshold_anomalies + rate_anomalies
        
        # Determine overall health
        if not all_anomalies:
            health_status = 'NOMINAL'
        elif any(a['severity'] == 'HIGH' for a in all_anomalies):
            health_status = 'CRITICAL'
        else:
            health_status = 'WARNING'
        
        return {
            'timestamp': timestamp.isoformat(),
            'health_status': health_status,
            'anomaly_count': len(all_anomalies),
            'anomalies': all_anomalies
        }
