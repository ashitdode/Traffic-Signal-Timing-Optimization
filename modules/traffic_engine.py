"""
Traffic Engineering Core Calculation Engine.
Implements Webster's Minimum Delay formulation, Highway Capacity Manual (HCM 6th Edition)
delay equations, Level of Service (LOS) grade evaluations, and environmental impact models.
"""

from typing import Dict, Tuple, Any
import numpy as np
import config


class TrafficEngine:
    """
    Standard Traffic Engineering analytics and mathematical calculations.
    """

    @staticmethod
    def calculate_webster_optimal_cycle(
        critical_flow_ratios: Dict[str, float],
        total_lost_time: float = 8.0,
        min_cycle: float = config.MIN_CYCLE_LENGTH,
        max_cycle: float = config.MAX_CYCLE_LENGTH,
    ) -> float:
        """
        Calculates Webster's optimal cycle length C_opt:
        C_opt = (1.5 * L + 5) / (1 - Y)
        where:
          L = Total lost time per cycle (startup + clearance)
          Y = Sum of critical flow ratios (q / s)
        """
        Y = sum(critical_flow_ratios.values())
        
        # Guard against hyper-saturation (Y >= 0.92 would cause asymptotic blowup)
        if Y >= 0.92:
            return float(max_cycle)
        if Y <= 0.15:
            return float(min_cycle)
            
        c_opt = (1.5 * total_lost_time + 5.0) / (1.0 - Y)
        return float(np.clip(c_opt, min_cycle, max_cycle))

    @staticmethod
    def calculate_green_splits(
        cycle_length: float,
        critical_flow_ratios: Dict[str, float],
        total_lost_time: float = 8.0,
        min_green: float = config.MIN_GREEN_TIME,
        max_green: float = config.MAX_GREEN_TIME,
    ) -> Dict[str, float]:
        """
        Applies Webster's proportional split method to allocate effective green times:
        g_i = (C - L) * (y_i / Y)
        Constrained by min_green and max_green.
        """
        effective_time = max(10.0, cycle_length - total_lost_time)
        Y = max(0.05, sum(critical_flow_ratios.values()))
        
        raw_splits = {}
        for phase, y_i in critical_flow_ratios.items():
            g_i = effective_time * (y_i / Y)
            raw_splits[phase] = float(np.clip(g_i, min_green, max_green))
            
        # Re-normalize splits so they sum precisely to effective_time
        total_allocated = sum(raw_splits.values())
        if total_allocated > 0:
            scale_factor = effective_time / total_allocated
            final_splits = {
                phase: round(np.clip(g * scale_factor, min_green, max_green), 1)
                for phase, g in raw_splits.items()
            }
        else:
            equal_split = round(effective_time / len(critical_flow_ratios), 1)
            final_splits = {phase: equal_split for phase in critical_flow_ratios}
            
        return final_splits

    @staticmethod
    def compute_webster_delay(
        cycle_length: float,
        green_time: float,
        flow_vph: float,
        saturation_flow_vph: float = config.DEFAULT_SATURATION_FLOW_RATE,
    ) -> float:
        """
        Computes average vehicle control delay using Webster's theoretical delay formula:
        d = [C*(1 - lambda)^2] / [2 * (1 - lambda * x)] + [x^2] / [2 * q * (1 - x)] - empirical_correction
        where:
          lambda = g / C (green ratio)
          c_cap = s * lambda (capacity)
          x = q / c_cap (degree of saturation)
        """
        if flow_vph <= 0:
            return 0.0
            
        C = float(cycle_length)
        g = float(green_time)
        q = flow_vph / 3600.0  # arrivals per second
        s = saturation_flow_vph / 3600.0  # saturation discharge per second
        
        green_ratio = min(0.95, max(0.05, g / C))
        capacity = s * green_ratio  # capacity in veh/sec
        
        x = min(1.2, q / capacity) if capacity > 0 else 1.2  # degree of saturation
        
        # 1. Uniform delay term (d1)
        denom_1 = 2.0 * (1.0 - green_ratio * min(0.99, x))
        d1 = (C * ((1.0 - green_ratio) ** 2)) / denom_1 if denom_1 > 0 else C
        
        # 2. Random overflow delay term (d2)
        if x < 0.98:
            denom_2 = 2.0 * q * (1.0 - x)
            d2 = (x ** 2) / denom_2 if denom_2 > 0 else 25.0
        else:
            # Akcelik / HCM overflow approximation for oversaturated conditions
            t_period = 0.25  # 15 minute analysis period in hours
            c_vph = capacity * 3600.0
            d2 = 900.0 * t_period * ((x - 1.0) + np.sqrt(((x - 1.0) ** 2) + (8.0 * 0.5 * x) / (c_vph * t_period)))
            
        # 3. Empirical correction term (d3)
        d3 = 0.65 * ((C / (q ** 2)) ** (1.0 / 3.0)) * (x ** (2.0 + 5.0 * green_ratio)) if q > 0 and x < 1.0 else 0.0
        
        total_delay = max(4.0, d1 + d2 - d3)
        return float(round(total_delay, 1))

    @staticmethod
    def get_hcm_los_grade(avg_delay_sec: float) -> Tuple[str, str, str]:
        """
        Evaluates HCM 6th Edition Level of Service (LOS).
        Returns: (Grade A-F, Label, Color Hex)
        """
        for grade, threshold in config.LOS_THRESHOLDS.items():
            if avg_delay_sec <= threshold["max_delay"]:
                return grade, threshold["label"], threshold["color"]
        return "F", config.LOS_THRESHOLDS["F"]["label"], config.LOS_THRESHOLDS["F"]["color"]

    @staticmethod
    def estimate_environmental_impact(
        total_delay_seconds: float,
        num_vehicles: int,
    ) -> Dict[str, float]:
        """
        Estimates idle fuel consumed, carbon footprint, and economic loss.
        """
        total_delay_hours = (total_delay_seconds * num_vehicles) / 3600.0
        
        idle_fuel_liters = total_delay_hours * config.IDLE_FUEL_RATE_LPH
        co2_emissions_kg = idle_fuel_liters * config.CO2_PER_LITER_GASOLINE_KG
        economic_loss_usd = total_delay_hours * config.VALUE_OF_TIME_HOURLY_USD
        
        return {
            "total_delay_hours": round(total_delay_hours, 2),
            "idle_fuel_liters": round(idle_fuel_liters, 2),
            "co2_emissions_kg": round(co2_emissions_kg, 2),
            "economic_loss_usd": round(economic_loss_usd, 2),
        }
