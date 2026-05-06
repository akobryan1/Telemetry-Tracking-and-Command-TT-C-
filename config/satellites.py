"""
Satellite Configuration - Multi-Satellite Support (Phase 8)

Defines available satellites and their properties.
"""

SATELLITES = {
    'ISS': {
        'name': 'ISS (ZARYA)',
        'norad_id': 25544,
        'tle_file': 'data/inputs/tle/satellites.txt',
        'initial_battery_voltage': 28.0,
        'initial_temperature': 20.0,
        'initial_mode': 'NOMINAL',
        'description': 'International Space Station',
        'orbit_type': 'LEO',
        'orbital_period_min': 92.9,
        'frequency_downlink_mhz': 2250.0,
        'frequency_uplink_mhz': 2050.0,
        'antenna_gain_dbi': 3.0
    },
    'HUBBLE': {
        'name': 'HUBBLE SPACE TELESCOPE',
        'norad_id': 20580,
        'tle_file': 'data/inputs/tle/satellites.txt',
        'initial_battery_voltage': 27.5,
        'initial_temperature': 15.0,
        'initial_mode': 'SCIENCE',
        'description': 'Hubble Space Telescope',
        'orbit_type': 'LEO',
        'orbital_period_min': 95.4,
        'frequency_downlink_mhz': 2287.5,
        'frequency_uplink_mhz': 2106.4,
        'antenna_gain_dbi': 5.0
    },
    'STARLINK': {
        'name': 'STARLINK-1007',
        'norad_id': 44713,
        'tle_file': 'data/inputs/tle/satellites.txt',
        'initial_battery_voltage': 29.0,
        'initial_temperature': 10.0,
        'initial_mode': 'NOMINAL',
        'description': 'Starlink Communications Satellite',
        'orbit_type': 'LEO',
        'orbital_period_min': 95.5,
        'frequency_downlink_mhz': 11700.0,
        'frequency_uplink_mhz': 14000.0,
        'antenna_gain_dbi': 35.0
    }
}

# Default satellite
DEFAULT_SATELLITE = 'ISS'

def get_satellite_config(satellite_id: str) -> dict:
    """Get configuration for a specific satellite."""
    return SATELLITES.get(satellite_id.upper(), SATELLITES[DEFAULT_SATELLITE])

def get_all_satellites() -> dict:
    """Get all available satellites."""
    return SATELLITES
