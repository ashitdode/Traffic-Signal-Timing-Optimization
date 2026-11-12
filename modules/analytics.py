"""
Analytics & Benchmark Evaluation Module.
Processes simulated logs and historical time-series datasets to calculate
aggregate delay reduction, queue clearance, emission mitigation, and LOS distributions.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import config


class TrafficAnalytics:
    """
    Statistical and exploratory analytics suite for traffic signal evaluation.
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def compute_executive_summary(self) -> Dict[str, Any]:
        """
        Computes high-level benchmark numbers comparing Fixed vs AI-Optimized controllers.
        """
        if self.data.empty:
            return {}

        avg_fixed_delay = self.data["fixed_delay_sec"].mean()
        avg_ai_delay = self.data["ai_delay_sec"].mean()
        delay_reduction_pct = ((avg_fixed_delay - avg_ai_delay) / avg_fixed_delay) * 100.0
        
        avg_fixed_queue = self.data["fixed_queue_veh"].mean()
        avg_ai_queue = self.data["ai_queue_veh"].mean()
        queue_reduction_pct = ((avg_fixed_queue - avg_ai_queue) / avg_fixed_queue) * 100.0

        total_vehicles = self.data["vehicle_flow_vph"].sum() // 4
        total_co2_saved = self.data["co2_saved_kg"].sum()
        total_fuel_saved = self.data["fuel_saved_liters"].sum()
        
        hours_saved = (self.data["delay_saved_sec"].sum() * (15.0 / 60.0)) / 3600.0
        economic_savings_usd = hours_saved * config.VALUE_OF_TIME_HOURLY_USD

        return {
            "avg_fixed_delay_sec": round(avg_fixed_delay, 1),
            "avg_ai_delay_sec": round(avg_ai_delay, 1),
            "delay_reduction_pct": round(delay_reduction_pct, 1),
            "avg_fixed_queue_veh": round(avg_fixed_queue, 1),
            "avg_ai_queue_veh": round(avg_ai_queue, 1),
            "queue_reduction_pct": round(queue_reduction_pct, 1),
            "total_vehicles_served": int(total_vehicles),
            "total_co2_saved_kg": round(total_co2_saved, 1),
            "total_fuel_saved_liters": round(total_fuel_saved, 1),
            "economic_savings_usd": round(economic_savings_usd, 2),
        }

    def get_hourly_congestion_profile(self) -> pd.DataFrame:
        """
        Aggregates traffic flow and delay by hour of the day.
        """
        if self.data.empty:
            return pd.DataFrame()
            
        grouped = self.data.groupby("hour").agg({
            "vehicle_flow_vph": "mean",
            "fixed_delay_sec": "mean",
            "ai_delay_sec": "mean",
            "fixed_queue_veh": "mean",
            "ai_queue_veh": "mean",
            "co2_saved_kg": "sum",
        }).reset_index()
        
        return grouped

    def get_approach_breakdown(self) -> pd.DataFrame:
        """
        Computes performance metrics broken down by approach direction.
        """
        if self.data.empty:
            return pd.DataFrame()

        grouped = self.data.groupby(["approach_key", "approach_name"]).agg({
            "vehicle_flow_vph": "mean",
            "fixed_delay_sec": "mean",
            "ai_delay_sec": "mean",
            "delay_saved_sec": "mean",
            "ai_queue_veh": "mean",
        }).reset_index()

        grouped["delay_improvement_pct"] = (
            (grouped["fixed_delay_sec"] - grouped["ai_delay_sec"]) / grouped["fixed_delay_sec"]
        ) * 100.0
        
        return grouped.round(1)

    def get_los_distribution(self) -> Dict[str, Dict[str, int]]:
        """
        Computes LOS grade frequency distribution for Fixed vs AI controllers.
        """
        if self.data.empty:
            return {"fixed": {}, "ai": {}}
            
        grades = list(config.LOS_THRESHOLDS.keys())
        fixed_counts = self.data["fixed_los"].value_counts().to_dict()
        ai_counts = self.data["ai_los"].value_counts().to_dict()
        
        fixed_dist = {g: fixed_counts.get(g, 0) for g in grades}
        ai_dist = {g: ai_counts.get(g, 0) for g in grades}
        
        return {"fixed": fixed_dist, "ai": ai_dist}
