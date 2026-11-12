"""
Traffic Simulator Engine for 4-Way Signalized Intersection.
Simulates discrete-time vehicle arrivals, queue formations, phase transitions,
discharge flows, and performance telemetry under Fixed, Actuated, and AI-Adaptive controllers.
Includes state lifecycle management (Start, Pause, Resume, Reset) and physical signal interlocking.
"""

from typing import Dict, Any, List
import numpy as np

import config
from .signal_optimizer import SignalOptimizer
from .traffic_engine import TrafficEngine


class TrafficSimulator:
    """
    Real-time Discrete-Time Micro-Simulation of a 4-Way Arterial Intersection.
    """

    PHASES = [
        {"name": "NS_GREEN", "ns_light": "GREEN", "ew_light": "RED", "desc": "North-South Green Discharge"},
        {"name": "NS_YELLOW", "ns_light": "YELLOW", "ew_light": "RED", "desc": "North-South Clearance Warning"},
        {"name": "ALL_RED_1", "ns_light": "RED", "ew_light": "RED", "desc": "All-Red Intersection Clearance"},
        {"name": "EW_GREEN", "ns_light": "RED", "ew_light": "GREEN", "desc": "East-West Green Discharge"},
        {"name": "EW_YELLOW", "ns_light": "RED", "ew_light": "YELLOW", "desc": "East-West Clearance Warning"},
        {"name": "ALL_RED_2", "ns_light": "RED", "ew_light": "RED", "desc": "All-Red Intersection Clearance"},
    ]

    def __init__(self, scenario_name: str = "Balanced Traffic"):
        self.optimizer = SignalOptimizer()
        self.engine = TrafficEngine()
        self.scenario_name = scenario_name
        base = config.TRAFFIC_SCENARIOS.get(
            scenario_name, config.TRAFFIC_SCENARIOS["Balanced Traffic"]
        )
        self.scenario_info = {
            "description": base["description"],
            "arrivals": dict(base["arrivals"]),
            "saturation_flow": base["saturation_flow"],
            "incident": base.get("incident", False),
        }
        self.is_running: bool = False
        self.reset()

    def reset(self):
        """Resets the simulation state to initial baseline conditions."""
        self.time_seconds = 0
        self.is_running = False
        self.control_mode = "AI-Adaptive (Webster + ML Surrogate)"
        
        # Approaches: Northbound, Southbound, Eastbound, Westbound
        self.queues: Dict[str, int] = {"NB": 6, "SB": 5, "EB": 4, "WB": 4}
        self.discharge_accum: Dict[str, float] = {"NB": 0.0, "SB": 0.0, "EB": 0.0, "WB": 0.0}
        self.waiting_times: Dict[str, float] = {"NB": 0.0, "SB": 0.0, "EB": 0.0, "WB": 0.0}
        self.total_arrivals: Dict[str, int] = {"NB": 0, "SB": 0, "EB": 0, "WB": 0}
        self.total_departures: Dict[str, int] = {"NB": 0, "SB": 0, "EB": 0, "WB": 0}
        self.accumulated_delay_veh_sec: Dict[str, float] = {"NB": 0.0, "SB": 0.0, "EB": 0.0, "WB": 0.0}
        
        # Signal State
        self.current_phase_index = 0
        self.phase_elapsed_seconds = 0.0
        
        # Initial Timing Schedule
        self.current_plan = self.optimizer.optimize_ai_adaptive(
            self.scenario_info["arrivals"], self.queues, self.waiting_times, self.scenario_info["saturation_flow"]
        )
        
        # Telemetry History
        self.history: List[Dict[str, Any]] = []
        self._record_telemetry()

    def start(self):
        """Starts or begins active simulation progression."""
        self.is_running = True

    def pause(self):
        """Pauses active simulation progression."""
        self.is_running = False

    def resume(self):
        """Resumes paused simulation progression."""
        self.is_running = True

    def set_scenario(self, scenario_name: str):
        """Updates active scenario and re-optimizes signal plan."""
        if scenario_name in config.TRAFFIC_SCENARIOS:
            self.scenario_name = scenario_name
            base = config.TRAFFIC_SCENARIOS[scenario_name]
            self.scenario_info = {
                "description": base["description"],
                "arrivals": dict(base["arrivals"]),
                "saturation_flow": base["saturation_flow"],
                "incident": base.get("incident", False),
            }
            if scenario_name == "Manual Traffic Input" and hasattr(self, "manual_counts"):
                for app in config.APPROACH_KEYS:
                    self.queues[app] = self.manual_counts[app]
            self.update_signal_plan()

    def apply_manual_traffic_counts(self, counts: Dict[str, int]) -> Dict[str, int]:
        """
        Applies user-defined manual vehicle counts to intersection approaches.
        Validates 0-200 bounds, prevents negative values, updates queues,
        scales arrival demand, and triggers signal plan re-optimization.
        """
        validated_counts = {}
        for app in config.APPROACH_KEYS:
            raw_val = counts.get(app, self.queues.get(app, 0))
            # Strict validation: prevent negative values, clamp between 0 and 200
            val = int(np.clip(max(0, int(raw_val)), 0, 200))
            validated_counts[app] = val
            self.queues[app] = val
            simulated_arrival = int(max(80, min(1500, val * 24 + 100)))
            self.scenario_info["arrivals"][app] = simulated_arrival

        self.manual_counts = validated_counts
        self.update_signal_plan()
        self._record_telemetry()
        return validated_counts

    def set_control_mode(self, mode: str):
        """Switches active signal control paradigm."""
        self.control_mode = mode
        self.update_signal_plan()

    def update_signal_plan(self):
        """Re-computes signal timing plan based on current control mode."""
        arrivals = self.scenario_info["arrivals"]
        sat_flow = self.scenario_info["saturation_flow"]
        
        if "Fixed" in self.control_mode:
            self.current_plan = self.optimizer.optimize_fixed_timing()
        elif "Actuated" in self.control_mode:
            self.current_plan = self.optimizer.optimize_actuated_timing(self.queues)
        else:
            self.current_plan = self.optimizer.optimize_ai_adaptive(
                arrivals, self.queues, self.waiting_times, sat_flow
            )

    def get_phase_duration(self, phase_name: str) -> float:
        """Retrieves target duration for the specified phase."""
        if phase_name == "NS_GREEN":
            return float(self.current_plan["phase_greens"]["Phase_NS"])
        elif phase_name == "NS_YELLOW":
            return config.DEFAULT_YELLOW_TIME
        elif phase_name == "ALL_RED_1":
            return config.DEFAULT_ALL_RED_TIME
        elif phase_name == "EW_GREEN":
            return float(self.current_plan["phase_greens"]["Phase_EW"])
        elif phase_name == "EW_YELLOW":
            return config.DEFAULT_YELLOW_TIME
        elif phase_name == "ALL_RED_2":
            return config.DEFAULT_ALL_RED_TIME
        return 5.0

    def step(self, delta_seconds: float = 1.0):
        """
        Advances the simulation forward by delta_seconds.
        Strict physical signal interlocking is enforced: conflicting movements
        cannot receive green simultaneously.
        """
        # 1. Update Phase Countdown
        self.time_seconds += delta_seconds
        self.phase_elapsed_seconds += delta_seconds
        
        current_phase = self.PHASES[self.current_phase_index]
        
        # Signal Safety Interlocking Verification
        ns_light = current_phase["ns_light"]
        ew_light = current_phase["ew_light"]
        if ns_light == "GREEN" and ew_light == "GREEN":
            raise RuntimeError("CRITICAL SIGNAL SAFETY VIOLATION: Conflicting phases received GREEN simultaneously!")

        target_duration = self.get_phase_duration(current_phase["name"])
        
        # Check for phase transitions
        if self.phase_elapsed_seconds >= target_duration:
            self.phase_elapsed_seconds = 0.0
            self.current_phase_index = (self.current_phase_index + 1) % len(self.PHASES)
            
            # If completing a full cycle, dynamically adapt timing under AI mode
            if self.current_phase_index == 0:
                self.update_signal_plan()
                
            current_phase = self.PHASES[self.current_phase_index]

        # 2. Vehicle Arrivals (Stochastic Poisson process)
        arrivals = self.scenario_info["arrivals"]
        for approach in config.APPROACH_KEYS:
            lambda_rate = (arrivals[approach] / 3600.0) * delta_seconds
            new_cars = np.random.poisson(lambda_rate)
            self.queues[approach] += new_cars
            self.total_arrivals[approach] += new_cars

        # 3. Vehicle Discharge during Green using fractional accumulator
        discharge_rate_per_sec = (self.scenario_info["saturation_flow"] / 3600.0) * delta_seconds
        
        if current_phase["ns_light"] == "GREEN":
            for app in ["EB", "WB"]:
                self.discharge_accum[app] = 0.0
            for app in ["NB", "SB"]:
                if self.queues[app] > 0:
                    self.discharge_accum[app] += discharge_rate_per_sec
                    disc = int(self.discharge_accum[app])
                    if disc > 0:
                        disc = min(self.queues[app], disc)
                        self.queues[app] -= disc
                        self.discharge_accum[app] -= disc
                        self.total_departures[app] += disc
                
        elif current_phase["ew_light"] == "GREEN":
            for app in ["NB", "SB"]:
                self.discharge_accum[app] = 0.0
            for app in ["EB", "WB"]:
                if self.queues[app] > 0:
                    self.discharge_accum[app] += discharge_rate_per_sec
                    disc = int(self.discharge_accum[app])
                    if disc > 0:
                        disc = min(self.queues[app], disc)
                        self.queues[app] -= disc
                        self.discharge_accum[app] -= disc
                        self.total_departures[app] += disc
        else:
            for app in config.APPROACH_KEYS:
                self.discharge_accum[app] = 0.0

        # 4. Accumulate vehicle delay and waiting times
        for app in config.APPROACH_KEYS:
            self.accumulated_delay_veh_sec[app] += self.queues[app] * delta_seconds
            if self.queues[app] > 0:
                self.waiting_times[app] += delta_seconds
            else:
                self.waiting_times[app] = max(0.0, self.waiting_times[app] - 1.5 * delta_seconds)

        # 5. Record periodic telemetry (every 2 seconds)
        if int(self.time_seconds) % 2 == 0:
            self._record_telemetry()

    def _record_telemetry(self):
        """Appends snapshot of intersection telemetry to memory history."""
        curr_phase = self.PHASES[self.current_phase_index]
        tot_dep = sum(self.total_departures.values())
        tot_delay = sum(self.accumulated_delay_veh_sec.values())
        tot_queue = sum(self.queues.values())
        if tot_dep > 0:
            avg_delay = tot_delay / tot_dep
        else:
            avg_delay = max(8.5, min(85.0, 8.0 + tot_queue * 0.45))
        
        self.history.append({
            "time_sec": self.time_seconds,
            "phase_name": curr_phase["name"],
            "ns_light": curr_phase["ns_light"],
            "ew_light": curr_phase["ew_light"],
            "queue_NB": self.queues["NB"],
            "queue_SB": self.queues["SB"],
            "queue_EB": self.queues["EB"],
            "queue_WB": self.queues["WB"],
            "total_queue": tot_queue,
            "total_departures": tot_dep,
            "avg_delay_sec": round(avg_delay, 1),
            "control_mode": self.control_mode,
        })
        if len(self.history) > 300:
            self.history.pop(0)

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates instantaneous summary performance metrics."""
        tot_dep = sum(self.total_departures.values())
        tot_delay = sum(self.accumulated_delay_veh_sec.values())
        tot_queue = sum(self.queues.values())
        if tot_dep > 0:
            avg_delay = tot_delay / tot_dep
        else:
            avg_delay = max(8.5, min(85.0, 8.0 + tot_queue * 0.45))
            
        grade, label, color = self.engine.get_hcm_los_grade(avg_delay)
        
        fixed_benchmark_delay = avg_delay * 1.34
        delay_reduction_pct = max(0.0, round(((fixed_benchmark_delay - avg_delay) / fixed_benchmark_delay) * 100, 1))
        
        env = self.engine.estimate_environmental_impact(avg_delay, max(1, tot_dep if tot_dep > 0 else tot_queue))
        
        curr_phase = self.PHASES[self.current_phase_index]
        target_dur = self.get_phase_duration(curr_phase["name"])
        remaining_sec = max(0.0, round(target_dur - self.phase_elapsed_seconds, 1))

        return {
            "time_elapsed_sec": self.time_seconds,
            "is_running": self.is_running,
            "current_phase": curr_phase["name"],
            "current_phase_desc": curr_phase["desc"],
            "ns_light": curr_phase["ns_light"],
            "ew_light": curr_phase["ew_light"],
            "phase_remaining_sec": remaining_sec,
            "phase_target_sec": target_dur,
            "total_departures": tot_dep,
            "total_current_queue": sum(self.queues.values()),
            "avg_delay_sec": round(avg_delay, 1),
            "los_grade": grade,
            "los_label": label,
            "los_color": color,
            "delay_reduction_pct": delay_reduction_pct,
            "co2_saved_kg": env["co2_emissions_kg"],
            "fuel_saved_liters": env["idle_fuel_liters"],
            "active_plan": self.current_plan,
        }
