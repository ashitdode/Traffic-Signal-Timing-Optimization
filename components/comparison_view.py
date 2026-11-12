"""
Performance Comparison Module (Stage 6).
Evaluates Traditional Fixed-Time Signal Control vs AI-Optimized Adaptive Control
under strictly identical traffic arrival patterns, starting conditions, and durations.
"""

from typing import Dict, Any
import io
import textwrap
import pandas as pd
import streamlit as st

import config
from modules.comparison_engine import FairComparisonEngine
from components.charts import (
    plot_comparison_waiting_time,
    plot_comparison_queue_length,
    plot_comparison_throughput,
    plot_comparison_utilization,
)


def render_comparison_view():
    """
    Renders the complete Stage 6 Performance Comparison Interface.
    """
    # Header Section
    header_html = textwrap.dedent("""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
            <span class="status-pill" style="border-color: #C6A76A; color: #C6A76A; font-weight: 600;">STAGE 6 EVALUATION</span>
            <span style="font-size: 0.78rem; color: #A4ADB3;">• Controlled Head-to-Head Testing</span>
        </div>
        <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">PERFORMANCE COMPARISON</h1>
        <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
            Evaluating adaptive signal intelligence against conventional traffic management.
        </p>
    </div>
    """).strip()
    st.markdown(header_html, unsafe_allow_html=True)

    # Comparison Engine Initialization in Session State
    if "comparison_engine" not in st.session_state:
        st.session_state.comparison_engine = FairComparisonEngine()

    # Scenario Controls & Parameters Bar
    with st.expander("⚙️ Scenario Selection & Benchmark Configuration", expanded=True):
        col_scen, col_dur, col_cycle, col_split = st.columns([2.5, 1.5, 1.5, 1.5])
        
        scenario_options = [
            "Balanced Traffic",
            "Heavy North-South Traffic",
            "Heavy East-West Traffic",
            "Uneven Traffic",
            "Randomized Traffic Demand",
        ]
        
        with col_scen:
            selected_scenario = st.selectbox(
                "Evaluation Scenario",
                options=scenario_options,
                index=0,
                help="Select the traffic demand pattern to feed into both controllers identically.",
            )
            
        with col_dur:
            sim_duration = st.slider(
                "Duration (seconds)",
                min_value=300,
                max_value=1200,
                value=600,
                step=60,
                help="Identical simulation runtime for both systems.",
            )

        with col_cycle:
            fixed_cycle = st.slider(
                "Baseline Fixed Cycle (s)",
                min_value=50,
                max_value=130,
                value=90,
                step=5,
                help="Traditional system total cycle length.",
            )

        with col_split:
            fixed_split = st.slider(
                "Baseline NS Split (%)",
                min_value=30,
                max_value=70,
                value=50,
                step=5,
                help="Traditional system North-South green split fraction.",
            )

        col_run, col_seed = st.columns([3, 1])
        with col_seed:
            random_seed = st.number_input("RNG Arrival Seed", min_value=1, max_value=9999, value=42)
        with col_run:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            run_btn = st.button("▶ Run Controlled Head-to-Head Benchmark", type="primary", use_container_width=True)

    # Execute or Retrieve Benchmark Results
    benchmark_key = f"benchmark_res_{selected_scenario}_{sim_duration}_{fixed_cycle}_{fixed_split}_{random_seed}"
    
    if run_btn or benchmark_key not in st.session_state:
        with st.spinner("Executing decoupled simulations against identical arrival schedules..."):
            res = st.session_state.comparison_engine.run_benchmark(
                scenario_name=selected_scenario,
                duration_seconds=sim_duration,
                fixed_cycle_length=float(fixed_cycle),
                fixed_ns_split=float(fixed_split) / 100.0,
                random_seed=random_seed,
            )
            st.session_state[benchmark_key] = res
            st.session_state.active_benchmark_key = benchmark_key

    benchmark_data = st.session_state.get(st.session_state.get("active_benchmark_key", benchmark_key))
    if not benchmark_data:
        st.warning("Please click 'Run Controlled Head-to-Head Benchmark' above to execute evaluation.")
        return

    comp = benchmark_data["comparison_metrics"]
    insights = benchmark_data["insights"]
    time_series = benchmark_data["time_series"]

    # ==========================================================================
    # TOP SECTION: TWO ELEGANT COMPARISON CARDS
    # ==========================================================================
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_card_trad, col_card_ai = st.columns(2)

    with col_card_trad:
        card_trad_html = textwrap.dedent(f"""
        <div style="background: #1B2933; border: 1px solid #30404A; border-top: 3px solid #E05D5D; border-radius: 14px; padding: 1.4rem; box-shadow: 0 4px 15px rgba(0,0,0,0.25); height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <span style="font-size: 0.76rem; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; font-weight: 600;">CONTROL BASELINE</span>
                <span class="status-pill" style="border-color: rgba(224,93,93,0.3); color: #E05D5D;">Conventional</span>
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #F1F0EB; margin: 0 0 0.5rem 0;">TRADITIONAL SYSTEM</h3>
            <p style="font-size: 0.85rem; color: #C6A76A; font-weight: 500; margin-bottom: 0.85rem;">
                Fixed-time signal control
            </p>
            <ul style="font-size: 0.82rem; color: #A4ADB3; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                <li><strong>Fixed green-light duration:</strong> Rigid {fixed_cycle}s cycle with constant phase green.</li>
                <li><strong>Predetermined signal sequence:</strong> Operates on fixed timetable clock.</li>
                <li><strong>Static timing:</strong> Blind to actual arrival volume variations or queue spikes.</li>
                <li><strong>Standard yellow transition:</strong> Standard {config.DEFAULT_YELLOW_TIME}s amber clearance.</li>
                <li><strong>No prioritization:</strong> Congested corridors receive no adaptive extra green.</li>
            </ul>
        </div>
        """).strip()
        st.markdown(card_trad_html, unsafe_allow_html=True)

    with col_card_ai:
        card_ai_html = textwrap.dedent("""
        <div style="background: #1B2933; border: 1px solid #30404A; border-top: 3px solid #8BAE9B; border-radius: 14px; padding: 1.4rem; box-shadow: 0 4px 15px rgba(0,0,0,0.25); height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                <span style="font-size: 0.76rem; text-transform: uppercase; color: #8BAE9B; letter-spacing: 0.08em; font-weight: 600;">OPTIMIZED SYSTEM</span>
                <span class="status-pill" style="border-color: rgba(139,174,155,0.3); color: #8BAE9B;">Intelligent</span>
            </div>
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #F1F0EB; margin: 0 0 0.5rem 0;">AI-OPTIMIZED SYSTEM</h3>
            <p style="font-size: 0.85rem; color: #8BAE9B; font-weight: 500; margin-bottom: 0.85rem;">
                Adaptive traffic-aware signal control
            </p>
            <ul style="font-size: 0.82rem; color: #A4ADB3; line-height: 1.6; margin: 0; padding-left: 1.2rem;">
                <li><strong>Traffic-density-based priority:</strong> Senses approaching vehicle density.</li>
                <li><strong>Dynamic green-light duration:</strong> Optimizes cycle and split per traffic flow.</li>
                <li><strong>Queue-aware allocation:</strong> Allocates green where residual queues are deepest.</li>
                <li><strong>Waiting-time consideration:</strong> Escalates priority for vehicles waiting longest.</li>
                <li><strong>Fairness mechanism:</strong> Anti-starvation safeguards prevent side-street lockout.</li>
            </ul>
        </div>
        """).strip()
        st.markdown(card_ai_html, unsafe_allow_html=True)

    # ==========================================================================
    # MIDDLE SECTION: SIDE-BY-SIDE METRIC COMPARISONS
    # ==========================================================================
    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
    bench_header_html = textwrap.dedent("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 0.8rem;">
        <div>
            <h3 style="font-size: 1.15rem; color: #F1F0EB; margin: 0;">Comprehensive Metric Benchmark</h3>
            <span style="font-size: 0.8rem; color: #A4ADB3;">Direct side-by-side performance comparison under identical vehicle arrivals.</span>
        </div>
        <span class="panel-badge sage">Fair Evaluation Protocol Active</span>
    </div>
    """).strip()
    st.markdown(bench_header_html, unsafe_allow_html=True)

    metrics_def = [
        ("avg_wait_time_sec", "1. Avg Vehicle Waiting Time", "sec/veh", True),
        ("avg_queue_length_veh", "2. Average Queue Length", "veh", True),
        ("total_vehicles_processed", "3. Vehicles Processed", "veh", False),
        ("max_queue_length_veh", "4. Maximum Queue Length", "veh", True),
        ("avg_signal_utilization_pct", "5. Signal Utilization", "%", False),
        ("traffic_throughput_vph", "6. Traffic Throughput", "vph", False),
    ]

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m4, col_m5, col_m6 = st.columns(3)
    card_cols = [col_m1, col_m2, col_m3, col_m4, col_m5, col_m6]

    for idx, (mkey, label, unit, lower_better) in enumerate(metrics_def):
        mdata = comp[mkey]
        trad_val = mdata["traditional"]
        ai_val = mdata["ai_optimized"]
        pct_change = mdata["pct_change"]
        status = mdata["status"]
        status_class = mdata["status_class"]

        arrow = "↓" if pct_change < 0 else "↑"
        sign = "+" if pct_change > 0 else ""
        delta_str = f"{sign}{pct_change}%"

        with card_cols[idx]:
            metric_card_html = textwrap.dedent(f"""
            <div style="background: #17232D; border: 1px solid #30404A; border-radius: 12px; padding: 1.1rem; margin-bottom: 0.85rem; box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.78rem; font-weight: 600; color: #F1F0EB;">{label}</span>
                    <span class="delta-pill {status_class}">{arrow} {delta_str}</span>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.6rem; border-top: 1px solid #24333D; padding-top: 0.6rem;">
                    <div>
                        <span style="font-size: 0.7rem; color: #A4ADB3; text-transform: uppercase;">Traditional</span><br/>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #E05D5D;">{trad_val}</span>
                        <span style="font-size: 0.7rem; color: #A4ADB3;">{unit}</span>
                    </div>
                    <div style="border-left: 1px solid #24333D; padding-left: 0.5rem;">
                        <span style="font-size: 0.7rem; color: #A4ADB3; text-transform: uppercase;">AI-Optimized</span><br/>
                        <span style="font-size: 1.25rem; font-weight: 700; color: #8BAE9B;">{ai_val}</span>
                        <span style="font-size: 0.7rem; color: #A4ADB3;">{unit}</span>
                    </div>
                </div>
                
                <div style="margin-top: 0.55rem; font-size: 0.72rem; color: #A4ADB3; display: flex; justify-content: space-between;">
                    <span>Assessment:</span>
                    <strong style="color: {'#8BAE9B' if status == 'Improvement' else ('#E05D5D' if status == 'Deterioration' else '#A4ADB3')};">
                        {status}
                    </strong>
                </div>
            </div>
            """).strip()
            st.markdown(metric_card_html, unsafe_allow_html=True)

    # ==========================================================================
    # LOWER SECTION: INTERACTIVE CHARTS
    # ==========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <h3 style="font-size: 1.15rem; color: #F1F0EB; margin-bottom: 0.75rem;">
            Simulation Trajectory & Telemetry Visualizations
        </h3>
        """,
        unsafe_allow_html=True,
    )

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(plot_comparison_waiting_time(time_series), use_container_width=True)
    with chart_col2:
        st.plotly_chart(plot_comparison_queue_length(time_series), use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)
    with chart_col3:
        st.plotly_chart(plot_comparison_throughput(time_series), use_container_width=True)
    with chart_col4:
        st.plotly_chart(plot_comparison_utilization(time_series), use_container_width=True)

    # ==========================================================================
    # SECTION 7: COMPARISON INSIGHTS & RIGOROUS FINDINGS
    # ==========================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <h3 style="font-size: 1.15rem; color: #F1F0EB; margin-bottom: 0.75rem;">
            Comparative Findings & Analytical Insights
        </h3>
        """,
        unsafe_allow_html=True,
    )

    col_ins_summary, col_ins_details = st.columns([1.5, 2.5])
    
    with col_ins_summary:
        winner_color = "#8BAE9B" if "AI" in insights["winner"] else "#E05D5D"
        ins_sum_html = textwrap.dedent(f"""
        <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.25rem; height: 100%;">
            <span style="font-size: 0.72rem; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; font-weight: 600;">SUPERIOR CONTROLLER</span>
            <h4 style="font-size: 1.3rem; color: {winner_color}; margin: 0.35rem 0 0.75rem 0;">{insights["winner"]}</h4>
            <p style="font-size: 0.85rem; color: #F1F0EB; line-height: 1.5; margin: 0;">
                {insights["summary_statement"]}
            </p>
        </div>
        """).strip()
        st.markdown(ins_sum_html, unsafe_allow_html=True)

    with col_ins_details:
        improved_tags = "".join([f"<li style='color: #8BAE9B;'>{item}</li>" for item in insights["improved_metrics"]]) or "<li style='color: #A4ADB3;'>None</li>"
        deteriorated_tags = "".join([f"<li style='color: #E05D5D;'>{item}</li>" for item in insights["deteriorated_metrics"]]) or "<li style='color: #A4ADB3;'>None</li>"
        limitations_text = "".join([f"<li>{item}</li>" for item in insights["limitations"]])

        ins_detail_html = textwrap.dedent(f"""
        <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.25rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0.85rem;">
                <div>
                    <span style="font-size: 0.72rem; text-transform: uppercase; color: #8BAE9B; font-weight: 600;">Improved Metrics</span>
                    <ul style="font-size: 0.8rem; margin: 0.35rem 0 0 0; padding-left: 1.1rem; line-height: 1.45;">
                        {improved_tags}
                    </ul>
                </div>
                <div>
                    <span style="font-size: 0.72rem; text-transform: uppercase; color: #E05D5D; font-weight: 600;">Deteriorated Metrics</span>
                    <ul style="font-size: 0.8rem; margin: 0.35rem 0 0 0; padding-left: 1.1rem; line-height: 1.45;">
                        {deteriorated_tags}
                    </ul>
                </div>
            </div>
            <div style="border-top: 1px solid #24333D; padding-top: 0.75rem;">
                <span style="font-size: 0.72rem; text-transform: uppercase; color: #C6A76A; font-weight: 600;">Observed Behavioral Constraints & Tradeoffs</span>
                <ul style="font-size: 0.8rem; color: #A4ADB3; margin: 0.35rem 0 0 0; padding-left: 1.1rem; line-height: 1.45;">
                    {limitations_text}
                </ul>
            </div>
        </div>
        """).strip()
        st.markdown(ins_detail_html, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 9: EXPORT CAPABILITIES
    # ==========================================================================
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    export_box_html = textwrap.dedent("""
    <div style="background: #17232D; border: 1px solid #30404A; border-radius: 12px; padding: 1.25rem; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h4 style="font-size: 1rem; color: #F1F0EB; margin: 0 0 0.25rem 0;">Export Controlled Benchmark Data</h4>
            <p style="font-size: 0.78rem; color: #A4ADB3; margin: 0;">
                Download complete benchmark report including scenario parameters, metric deltas, and second-by-second telemetry.
            </p>
        </div>
    </div>
    """).strip()
    st.markdown(export_box_html, unsafe_allow_html=True)

    # Prepare CSV Export Dataframe
    export_rows = []
    for mkey, label, unit, _ in metrics_def:
        m = comp[mkey]
        export_rows.append({
            "Scenario": selected_scenario,
            "Simulation_Duration_Sec": sim_duration,
            "Metric_Name": label,
            "Traditional_Baseline": m["traditional"],
            "AI_Optimized": m["ai_optimized"],
            "Unit": unit,
            "Percentage_Change": m["pct_change"],
            "Assessment": m["status"],
        })
    df_export = pd.DataFrame(export_rows)
    csv_buffer = io.StringIO()
    df_export.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    # Prepare Textual Summary
    txt_summary = f"""================================================================================
TRAFFIC SIGNAL TIMING OPTIMIZATION - PERFORMANCE COMPARISON REPORT
================================================================================
Scenario: {selected_scenario}
Duration: {sim_duration} seconds
Baseline Configuration: Cycle={fixed_cycle}s, NS Split={fixed_split}%
Superior Controller: {insights['winner']}

Summary:
{insights['summary_statement']}

METRIC BENCHMARKS:
--------------------------------------------------------------------------------
1. Average Vehicle Waiting Time:
   Traditional: {comp['avg_wait_time_sec']['traditional']} sec/veh
   AI-Optimized: {comp['avg_wait_time_sec']['ai_optimized']} sec/veh
   Change: {comp['avg_wait_time_sec']['pct_change']}% ({comp['avg_wait_time_sec']['status']})

2. Average Queue Length:
   Traditional: {comp['avg_queue_length_veh']['traditional']} veh
   AI-Optimized: {comp['avg_queue_length_veh']['ai_optimized']} veh
   Change: {comp['avg_queue_length_veh']['pct_change']}% ({comp['avg_queue_length_veh']['status']})

3. Total Vehicles Processed:
   Traditional: {comp['total_vehicles_processed']['traditional']} veh
   AI-Optimized: {comp['total_vehicles_processed']['ai_optimized']} veh
   Change: {comp['total_vehicles_processed']['pct_change']}% ({comp['total_vehicles_processed']['status']})

4. Maximum Queue Length:
   Traditional: {comp['max_queue_length_veh']['traditional']} veh
   AI-Optimized: {comp['max_queue_length_veh']['ai_optimized']} veh
   Change: {comp['max_queue_length_veh']['pct_change']}% ({comp['max_queue_length_veh']['status']})

5. Average Signal Utilization:
   Traditional: {comp['avg_signal_utilization_pct']['traditional']}%
   AI-Optimized: {comp['avg_signal_utilization_pct']['ai_optimized']}%
   Change: {comp['avg_signal_utilization_pct']['pct_change']}% ({comp['avg_signal_utilization_pct']['status']})

6. Traffic Throughput:
   Traditional: {comp['traffic_throughput_vph']['traditional']} vph
   AI-Optimized: {comp['traffic_throughput_vph']['ai_optimized']} vph
   Change: {comp['traffic_throughput_vph']['pct_change']}% ({comp['traffic_throughput_vph']['status']})

OBSERVED LIMITATIONS & TRADEOFFS:
- {' '.join(insights['limitations'])}
================================================================================
"""

    col_btn_csv, col_btn_txt = st.columns(2)
    with col_btn_csv:
        st.download_button(
            label="📥 Download CSV Benchmark Report",
            data=csv_bytes,
            file_name=f"traffic_benchmark_{selected_scenario.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_btn_txt:
        st.download_button(
            label="📄 Download Analytical Executive Brief (TXT)",
            data=txt_summary.encode("utf-8"),
            file_name=f"traffic_brief_{selected_scenario.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
        )
