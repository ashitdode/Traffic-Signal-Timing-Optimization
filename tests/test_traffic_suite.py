"""
Comprehensive Automated Test Suite for Traffic Signal Timing Optimization Platform.
Validates signal timing boundaries, priority calculations, fairness constraints,
queue dynamics, state transitions, analytics, comparison benchmarking, and exports.
"""

import os
import sys
import unittest
import numpy as np
import pandas as pd

# Add workspace root to Python sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.traffic_engine import TrafficEngine
from modules.signal_optimizer import SignalOptimizer
from modules.traffic_simulator import TrafficSimulator
from modules.comparison_engine import FairComparisonEngine
from modules.analytics import TrafficAnalytics
from modules.data_generator import generate_traffic_dataset


class TestTrafficSignalOptimization(unittest.TestCase):
    """Automated unit and integration test suite."""

    def setUp(self):
        self.engine = TrafficEngine()
        self.optimizer = SignalOptimizer()
        self.simulator = TrafficSimulator("Balanced Traffic")
        self.comparison_engine = FairComparisonEngine()

    def test_01_signal_timing_boundaries(self):
        """Validates that optimal cycle and green splits respect minimum and maximum bounds."""
        # Extreme low flow
        low_flows = {"NB": 80, "SB": 80, "EB": 80, "WB": 80}
        plan_low = self.optimizer.optimize_ai_adaptive(low_flows, {"NB": 1, "SB": 1, "EB": 1, "WB": 1})
        self.assertGreaterEqual(plan_low["cycle_length"], config.MIN_CYCLE_LENGTH)
        self.assertLessEqual(plan_low["cycle_length"], config.MAX_CYCLE_LENGTH)
        self.assertGreaterEqual(plan_low["phase_greens"]["Phase_NS"], config.MIN_GREEN_TIME)
        self.assertGreaterEqual(plan_low["phase_greens"]["Phase_EW"], config.MIN_GREEN_TIME)

        # Extreme high flow
        high_flows = {"NB": 1200, "SB": 1150, "EB": 1100, "WB": 1050}
        plan_high = self.optimizer.optimize_ai_adaptive(high_flows, {"NB": 15, "SB": 15, "EB": 12, "WB": 12})
        self.assertLessEqual(plan_high["cycle_length"], config.MAX_CYCLE_LENGTH)
        self.assertLessEqual(plan_high["phase_greens"]["Phase_NS"], config.MAX_GREEN_TIME)
        self.assertLessEqual(plan_high["phase_greens"]["Phase_EW"], config.MAX_GREEN_TIME)

    def test_02_priority_and_fairness_constraints(self):
        """Validates that priority scores sum to 100% and waiting-time fairness weights scale appropriately."""
        flows = {"NB": 950, "SB": 900, "EB": 300, "WB": 250}
        queues = {"NB": 10, "SB": 8, "EB": 2, "WB": 2}
        waits = {"NB": 5.0, "SB": 5.0, "EB": 60.0, "WB": 50.0}  # EW waiting a long time!

        plan = self.optimizer.optimize_ai_adaptive(flows, queues, waits)
        prio = plan["priority_scores"]
        
        # Priority percentages sum close to 100%
        self.assertAlmostEqual(prio["Phase_NS"] + prio["Phase_EW"], 100.0, places=1)
        
        # Fairness weight for Phase EW must be elevated due to high wait time
        self.assertGreater(plan["fairness_weights"]["Phase_EW"], 1.0)
        self.assertGreaterEqual(plan["phase_greens"]["Phase_EW"], config.MIN_GREEN_TIME)

    def test_03_signal_safety_interlocking(self):
        """Validates physical mutual exclusion of green phases."""
        for phase in self.simulator.PHASES:
            # Conflicting movements must never receive green simultaneously
            self.assertFalse(
                phase["ns_light"] == "GREEN" and phase["ew_light"] == "GREEN",
                f"Safety violation in phase {phase['name']}"
            )

    def test_04_vehicle_queue_dynamics_and_non_negativity(self):
        """Validates queue generation, vehicle discharge, and queue non-negativity."""
        self.simulator.reset()
        for _ in range(30):
            self.simulator.step(1.0)
            for app, count in self.simulator.queues.items():
                self.assertGreaterEqual(count, 0, f"Negative queue detected on {app}")
        
        metrics = self.simulator.get_summary_metrics()
        self.assertGreater(metrics["time_elapsed_sec"], 0)
        self.assertGreaterEqual(metrics["total_departures"], 0)

    def test_05_simulation_lifecycle_state_transitions(self):
        """Validates Start, Pause, Resume, Reset lifecycle operations."""
        sim = self.simulator
        sim.reset()
        self.assertFalse(sim.is_running)
        self.assertEqual(sim.time_seconds, 0)

        sim.start()
        self.assertTrue(sim.is_running)

        sim.step(5.0)
        self.assertEqual(sim.time_seconds, 5.0)

        sim.pause()
        self.assertFalse(sim.is_running)

        sim.resume()
        self.assertTrue(sim.is_running)

        sim.reset()
        self.assertFalse(sim.is_running)
        self.assertEqual(sim.time_seconds, 0)

    def test_06_analytics_and_hcm_los_calculations(self):
        """Validates HCM Level of Service classifications and analytics computations."""
        # LOS Grade Thresholds
        self.assertEqual(self.engine.get_hcm_los_grade(5.0)[0], "A")
        self.assertEqual(self.engine.get_hcm_los_grade(15.0)[0], "B")
        self.assertEqual(self.engine.get_hcm_los_grade(28.0)[0], "C")
        self.assertEqual(self.engine.get_hcm_los_grade(45.0)[0], "D")
        self.assertEqual(self.engine.get_hcm_los_grade(65.0)[0], "E")
        self.assertEqual(self.engine.get_hcm_los_grade(95.0)[0], "F")

        # Analytics Executive Summary
        dummy_df = generate_traffic_dataset(days=1, interval_minutes=60, seed=123)
        analytics = TrafficAnalytics(dummy_df)
        summary = analytics.compute_executive_summary()
        self.assertIn("avg_fixed_delay_sec", summary)
        self.assertIn("avg_ai_delay_sec", summary)
        self.assertIn("delay_reduction_pct", summary)
        self.assertIn("total_co2_saved_kg", summary)

    def test_07_fair_comparison_benchmarking(self):
        """Validates controlled head-to-head benchmarking with identical traffic inputs."""
        res = self.comparison_engine.run_benchmark(
            scenario_name="Heavy North-South Traffic",
            duration_seconds=300,
            fixed_cycle_length=90.0,
            fixed_ns_split=0.5,
            random_seed=42,
        )

        self.assertIn("traditional_metrics", res)
        self.assertIn("ai_metrics", res)
        self.assertIn("comparison_metrics", res)
        self.assertIn("insights", res)

        comp = res["comparison_metrics"]
        self.assertIn("avg_wait_time_sec", comp)
        self.assertIn("traffic_throughput_vph", comp)
        self.assertIn("pct_change", comp["avg_wait_time_sec"])

        # Under heavy NS flow, AI must demonstrate waiting time reduction
        self.assertLess(comp["avg_wait_time_sec"]["pct_change"], 0)

    def test_08_export_functionality(self):
        """Validates export dataset creation and CSV format integrity."""
        dummy_df = generate_traffic_dataset(days=1, interval_minutes=60, seed=456)
        csv_str = dummy_df.to_csv(index=False)
        self.assertGreater(len(csv_str), 100)
        self.assertIn("timestamp", csv_str)
        self.assertIn("vehicle_flow_vph", csv_str)

    def test_09_manual_traffic_input_bounds_and_optimization(self):
        """Validates manual traffic input bounding (0-200), negative value prevention, and dynamic plan re-optimization."""
        # 1. Negative count prevention and clamping within [0, 200]
        test_counts = {"NB": -15, "SB": 85, "EB": 250, "WB": 0}
        applied = self.simulator.apply_manual_traffic_counts(test_counts)
        self.assertEqual(applied["NB"], 0)    # Clamped from -15 to 0
        self.assertEqual(applied["SB"], 85)   # Exact valid count
        self.assertEqual(applied["EB"], 200)  # Clamped from 250 to 200
        self.assertEqual(applied["WB"], 0)    # Zero boundary preserved
        
        # Verify queues in simulator
        self.assertEqual(self.simulator.queues["NB"], 0)
        self.assertEqual(self.simulator.queues["SB"], 85)
        self.assertEqual(self.simulator.queues["EB"], 200)
        self.assertEqual(self.simulator.queues["WB"], 0)

        # 2. Check that signal timing plan updated dynamically
        metrics = self.simulator.get_summary_metrics()
        self.assertEqual(metrics["total_current_queue"], 285)
        self.assertGreater(metrics["avg_delay_sec"], 0)
        
        # Phase EW has heavy queue (200 veh) vs NS (85 veh), so EW must receive significant green allocation
        plan = metrics["active_plan"]
        self.assertGreaterEqual(plan["phase_greens"]["Phase_EW"], plan["phase_greens"]["Phase_NS"])

        # 3. Test dataset appending for analytics
        from modules.data_generator import append_manual_input_to_dataset
        dummy_df = generate_traffic_dataset(days=1, interval_minutes=60, seed=789)
        initial_len = len(dummy_df)
        updated_df = append_manual_input_to_dataset(dummy_df, applied)
        self.assertEqual(len(updated_df), initial_len + 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
