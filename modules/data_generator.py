"""
Synthetic Traffic Data Generator for 4-Way Signalized Intersection.
Simulates realistic urban arterial traffic flow patterns with morning and evening peak hours,
approaches, delay characteristics, queue buildup, and HCM Level of Service (LOS).
Includes Streamlit caching for high-performance memory storage.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import numpy as np
import pandas as pd
import streamlit as st

import config


def compute_hcm_los(delay_sec: float) -> str:
    """Classifies control delay into HCM 6th Edition Level of Service A-F."""
    for grade, info in config.LOS_THRESHOLDS.items():
        if delay_sec <= info["max_delay"]:
            return grade
    return "F"


def generate_traffic_dataset(
    days: int = 5,
    interval_minutes: int = 15,
    seed: int = 42,
    output_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Generates a realistic synthetic time-series dataset of traffic metrics for a 4-way intersection.
    Clearly designated as synthetic benchmark data for academic and evaluation purposes.
    """
    np.random.seed(seed)
    
    start_time = datetime(2026, 11, 1, 0, 0, 0)
    total_steps = int((days * 24 * 60) / interval_minutes)
    
    rows = []
    
    for step in range(total_steps):
        current_time = start_time + timedelta(minutes=step * interval_minutes)
        hour = current_time.hour + current_time.minute / 60.0
        is_weekend = current_time.weekday() >= 5
        
        morning_peak = np.exp(-0.5 * ((hour - 8.0) / 1.5) ** 2)
        evening_peak = np.exp(-0.5 * ((hour - 17.5) / 2.0) ** 2)
        base_night = 0.12 + 0.15 * np.sin((hour / 24.0) * np.pi)
        
        if is_weekend:
            weekend_curve = 0.25 + 0.65 * np.exp(-0.5 * ((hour - 13.0) / 3.5) ** 2)
            activity_profile = weekend_curve
        else:
            activity_profile = base_night + 0.85 * morning_peak + 0.95 * evening_peak
            
        activity_profile = max(0.08, min(activity_profile, 1.25))
        
        weather_roll = np.random.rand()
        weather = "Clear"
        weather_factor = 1.0
        if weather_roll < 0.12:
            weather = "Rain"
            weather_factor = 1.18
        elif weather_roll < 0.17:
            weather = "Fog"
            weather_factor = 1.10

        for approach, direction in zip(config.APPROACH_KEYS, config.APPROACHES):
            if not is_weekend:
                if 7.0 <= hour <= 9.5:
                    dir_multiplier = 1.4 if approach in ["NB", "EB"] else 0.75
                elif 16.0 <= hour <= 19.0:
                    dir_multiplier = 1.45 if approach in ["SB", "WB"] else 0.70
                else:
                    dir_multiplier = 1.0
            else:
                dir_multiplier = 1.0 + np.random.uniform(-0.15, 0.15)
            
            mean_vph = 550 * activity_profile * dir_multiplier
            vph = max(40, int(np.random.normal(mean_vph, mean_vph * 0.12)))
            
            fixed_cycle = 90.0
            fixed_green = 40.0
            capacity = config.DEFAULT_SATURATION_FLOW_RATE * (fixed_green / fixed_cycle)
            v_c_ratio = min(1.25, vph / capacity)
            
            fixed_delay = max(11.0, (14.0 / (1.0 - 0.7 * min(0.95, v_c_ratio))) * weather_factor)
            fixed_delay += np.random.normal(0, 2.5)
            fixed_delay = max(7.0, round(fixed_delay, 1))
            
            fixed_queue = max(1, int((vph / 3600.0) * (fixed_cycle - fixed_green) * (1 + 0.6 * v_c_ratio)))
            
            efficiency_gain = 0.28 + (0.12 if v_c_ratio > 0.8 else 0.05)
            ai_delay = max(6.5, round(fixed_delay * (1.0 - efficiency_gain), 1))
            ai_queue = max(1, int(fixed_queue * (1.0 - (efficiency_gain * 0.85))))
            
            fixed_fuel = round((fixed_delay / 3600.0) * config.IDLE_FUEL_RATE_LPH * (vph * (interval_minutes / 60.0)), 3)
            ai_fuel = round((ai_delay / 3600.0) * config.IDLE_FUEL_RATE_LPH * (vph * (interval_minutes / 60.0)), 3)
            
            fixed_co2 = round(fixed_fuel * config.CO2_PER_LITER_GASOLINE_KG, 2)
            ai_co2 = round(ai_fuel * config.CO2_PER_LITER_GASOLINE_KG, 2)
            
            rows.append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "date": current_time.strftime("%Y-%m-%d"),
                "hour": round(hour, 2),
                "approach_key": approach,
                "approach_name": direction,
                "weather": weather,
                "vehicle_flow_vph": vph,
                "v_c_ratio": round(v_c_ratio, 2),
                "fixed_delay_sec": fixed_delay,
                "fixed_queue_veh": fixed_queue,
                "fixed_los": compute_hcm_los(fixed_delay),
                "fixed_fuel_liters": fixed_fuel,
                "fixed_co2_kg": fixed_co2,
                "ai_delay_sec": ai_delay,
                "ai_queue_veh": ai_queue,
                "ai_los": compute_hcm_los(ai_delay),
                "ai_fuel_liters": ai_fuel,
                "ai_co2_kg": ai_co2,
                "delay_saved_sec": round(fixed_delay - ai_delay, 1),
                "fuel_saved_liters": round(fixed_fuel - ai_fuel, 3),
                "co2_saved_kg": round(fixed_co2 - ai_co2, 2),
            })

    df = pd.DataFrame(rows)
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        
    return df


@st.cache_data(show_spinner=False)
def get_or_create_default_dataset() -> pd.DataFrame:
    """Loads default traffic dataset or generates it if absent. Cached for optimal performance."""
    default_csv = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "traffic_data.csv")
    if os.path.exists(default_csv):
        try:
            df = pd.read_csv(default_csv)
            if not df.empty:
                return df
        except Exception:
            pass
            
    df = generate_traffic_dataset(days=5, interval_minutes=15, output_path=default_csv)
    return df
