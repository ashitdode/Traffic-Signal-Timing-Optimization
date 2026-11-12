"""
Configuration module for Traffic Signal Timing Optimization Platform.
Contains color palettes, intersection geometry, signal timings, HCM thresholds,
and scenario presets.
"""

from typing import Dict, Any

# ==============================================================================
# 1. VISUAL DESIGN SYSTEM & COLOR PALETTE
# ==============================================================================
COLOR_BG_PRIMARY = "#101820"
COLOR_BG_SECONDARY = "#17232D"
COLOR_BG_CARD = "#1B2933"
COLOR_ACCENT_GOLD = "#C6A76A"
COLOR_ACCENT_SAGE = "#8BAE9B"
COLOR_TEXT_PRIMARY = "#F1F0EB"
COLOR_TEXT_SECONDARY = "#A4ADB3"
COLOR_BORDER = "#30404A"

# Signal Status Colors
COLOR_SIGNAL_RED = "#E05D5D"
COLOR_SIGNAL_AMBER = "#E5A93C"
COLOR_SIGNAL_GREEN = "#4EBA86"
COLOR_SIGNAL_OFF = "#23333F"

# Data Visualization Colors
PALETTE_SERIES = [
    "#C6A76A",  # Muted Gold
    "#8BAE9B",  # Sage Green
    "#5C9EAD",  # Slate Cyan
    "#E05D5D",  # Muted Coral
    "#D99B6A",  # Warm Bronze
    "#7D8C99",  # Steel Grey
]

# ==============================================================================
# 2. INTERSECTION GEOMETRY & TRAFFIC PARAMETERS
# ==============================================================================
APPROACHES = ["Northbound", "Southbound", "Eastbound", "Westbound"]
APPROACH_KEYS = ["NB", "SB", "EB", "WB"]

# Saturation Flow Rate in vehicles per hour of green per lane (vphpl)
DEFAULT_SATURATION_FLOW_RATE = 1800  # standard urban arterial saturation flow

# Lost times per phase (seconds) - startup lost time + clearance lost time
DEFAULT_LOST_TIME_PER_PHASE = 4.0

# Yellow interval and all-red clearance interval (seconds)
DEFAULT_YELLOW_TIME = 3.5
DEFAULT_ALL_RED_TIME = 1.5

# Signal Cycle Length Constraints (seconds)
MIN_CYCLE_LENGTH = 40
MAX_CYCLE_LENGTH = 150
DEFAULT_CYCLE_LENGTH = 90

# Phase Green Time Constraints (seconds)
MIN_GREEN_TIME = 10.0
MAX_GREEN_TIME = 75.0

# Fixed Timing Baseline Defaults
FIXED_PHASE_NS_GREEN = 40.0
FIXED_PHASE_EW_GREEN = 40.0

# ==============================================================================
# 3. HIGHWAY CAPACITY MANUAL (HCM 6TH EDITION) LEVEL OF SERVICE (LOS)
# Criteria based on Average Control Delay (seconds / vehicle)
# ==============================================================================
LOS_THRESHOLDS = {
    "A": {"max_delay": 10.0, "label": "Free Flow", "color": "#4EBA86"},
    "B": {"max_delay": 20.0, "label": "Stable Flow", "color": "#8BAE9B"},
    "C": {"max_delay": 35.0, "label": "Acceptable Delay", "color": "#C6A76A"},
    "D": {"max_delay": 55.0, "label": "Approaching Unstable", "color": "#E5A93C"},
    "E": {"max_delay": 80.0, "label": "Unstable Flow", "color": "#D97B55"},
    "F": {"max_delay": 99999.0, "label": "Forced Breakdown", "color": "#E05D5D"},
}

# ==============================================================================
# 4. ENVIRONMENTAL & ECONOMIC EMISSION CONSTANTS
# ==============================================================================
IDLE_FUEL_RATE_LPH = 1.38  # Liters / hr / stopped vehicle
CO2_PER_LITER_GASOLINE_KG = 2.31  # kg CO2 / Liter
VALUE_OF_TIME_HOURLY_USD = 21.50  # USDOT commuter value standard

# ==============================================================================
# 5. PRESET TRAFFIC SCENARIOS
# Values define average arrival rates (vehicles/hour) per approach
# ==============================================================================
TRAFFIC_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "Manual Traffic Input": {
        "description": "User-defined vehicle counts (0-200) entered dynamically per approach corridor.",
        "arrivals": {"NB": 500, "SB": 480, "EB": 420, "WB": 400},
        "saturation_flow": 1800,
        "incident": False,
    },
    "Balanced Traffic": {
        "description": "Equally distributed traffic flow across all four intersection corridors.",
        "arrivals": {"NB": 450, "SB": 430, "EB": 440, "WB": 420},
        "saturation_flow": 1800,
        "incident": False,
    },
    "Heavy North-South Traffic": {
        "description": "Major arterial commute with heavy directional flow on the North-South corridor.",
        "arrivals": {"NB": 920, "SB": 860, "EB": 280, "WB": 260},
        "saturation_flow": 1850,
        "incident": False,
    },
    "Heavy East-West Traffic": {
        "description": "Cross-town transit corridor bottleneck with heavy East-West traffic discharge.",
        "arrivals": {"NB": 300, "SB": 280, "EB": 950, "WB": 890},
        "saturation_flow": 1850,
        "incident": False,
    },
    "Uneven Traffic": {
        "description": "Severe directional disparity with asymmetric queues across approaches.",
        "arrivals": {"NB": 1050, "SB": 420, "EB": 680, "WB": 250},
        "saturation_flow": 1750,
        "incident": False,
    },
    "Randomized Traffic Demand": {
        "description": "Dynamic stochastic arrival variations across all approaches reflecting unpredictable urban demand.",
        "arrivals": {"NB": 600, "SB": 750, "EB": 500, "WB": 850},
        "saturation_flow": 1800,
        "incident": False,
    },
    "Adverse Weather Congestion": {
        "description": "Wet pavement and low visibility reducing roadway saturation flow rate by 20%.",
        "arrivals": {"NB": 650, "SB": 620, "EB": 600, "WB": 580},
        "saturation_flow": 1450,
        "incident": False,
    },
}

# ==============================================================================
# 6. SYSTEM METADATA & DISCLAIMER
# ==============================================================================
APP_METADATA = {
    "name": "Traffic Signal Timing Optimization",
    "version": "2.4.0 Commercial Release",
    "developer_role": "AI Traffic Systems & Urban Analytics",
    "disclaimer": (
        "Notice: This application runs advanced mathematical and machine learning "
        "simulations for academic demonstration and decision support. All traffic feeds "
        "and sensor streams are simulated representations and do not control live "
        "municipal physical infrastructure."
    ),
}
