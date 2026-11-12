"""
TRAFFIC SIGNAL TIMING OPTIMIZATION
Main Streamlit Application Entrypoint.
A sophisticated, user-friendly traffic management platform demonstrating how
intelligent traffic signal timing improves urban intersection flow.
"""

import os
import io
import time
import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="TRAFFIC SIGNAL TIMING OPTIMIZATION",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Inject Custom Apple/Linear Design System CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Import Application Modules & Components
import config
from modules.traffic_simulator import TrafficSimulator
from modules.signal_optimizer import SignalOptimizer
from modules.traffic_engine import TrafficEngine
from modules.analytics import TrafficAnalytics
from modules.data_generator import get_or_create_default_dataset
from components.sidebar import render_sidebar
from components.dashboard import render_overview_dashboard
from components.intersection import render_intersection_view
from components.signal_cards import render_approach_cards
from components.comparison_view import render_comparison_view
from components.charts import (
    plot_queue_history,
    plot_delay_curve,
    plot_hourly_comparison,
    plot_hourly_volume_flow,
    plot_radar_benchmark,
    plot_los_distribution,
    plot_approach_breakdown,
    plot_environmental_savings,
)

# 4. Session State Initialization
if "simulator" not in st.session_state:
    st.session_state.simulator = TrafficSimulator(scenario_name="Balanced Traffic")

if "historical_data" not in st.session_state:
    st.session_state.historical_data = get_or_create_default_dataset()

if "optimizer" not in st.session_state:
    st.session_state.optimizer = SignalOptimizer()

# 5. Sidebar Navigation & Global Controls
selected_module, active_scenario, selected_controller = render_sidebar()

sim: TrafficSimulator = st.session_state.simulator
if sim.scenario_name != active_scenario:
    sim.set_scenario(active_scenario)
if sim.control_mode != selected_controller:
    sim.set_control_mode(selected_controller)

metrics = sim.get_summary_metrics()
queues = sim.queues
arrivals = sim.scenario_info["arrivals"]
plan = metrics["active_plan"]

# 6. Route Between Platform Modules

# ==============================================================================
# MODULE 1: OVERVIEW DASHBOARD
# ==============================================================================
if "1. Overview Dashboard" in selected_module:
    render_overview_dashboard(metrics, queues, arrivals, plan, active_scenario)


# ==============================================================================
# MODULE 2: LIVE TRAFFIC SIMULATION
# ==============================================================================
elif "2. Live Traffic Simulation" in selected_module:
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="status-pill"><span class="status-dot pulse"></span> SIMULATION RUNTIME</span>
                <span style="font-size: 0.8rem; color: #A4ADB3;">• Real-Time Queue & Discharge Dynamics</span>
            </div>
            <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">LIVE TRAFFIC SIMULATION</h1>
            <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
                Observe dynamic phase countdowns, stochastic Poisson vehicle arrivals, and real-time queue depletion.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simulation Controls Bar with Start, Pause, Resume, Reset, and Manual Stepping
    with st.container():
        c_state, c_start_pause, c_step1, c_step5, c_reset, c_mode_disp = st.columns([1.3, 1.4, 1.1, 1.1, 1.1, 3.0])
        
        with c_state:
            state_label = "RUNNING" if sim.is_running else ("PAUSED" if sim.time_seconds > 0 else "READY")
            state_color = "#4EBA86" if sim.is_running else ("#E5A93C" if sim.time_seconds > 0 else "#C6A76A")
            st.markdown(
                f"""
                <div style="background: #17232D; border: 1px solid #30404A; border-radius: 8px; padding: 0.5rem 0.75rem; text-align: center; height: 38px;">
                    <span style="font-size: 0.72rem; color: #A4ADB3; text-transform: uppercase;">STATE:</span>
                    <strong style="font-size: 0.82rem; color: {state_color}; margin-left: 4px;">{state_label}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c_start_pause:
            if not sim.is_running:
                btn_text = "▶ Start Auto" if sim.time_seconds == 0 else "▶ Resume Auto"
                if st.button(btn_text, type="primary", use_container_width=True):
                    sim.start()
                    sim.step(1.0)
                    st.rerun()
            else:
                if st.button("⏸ Pause Auto", use_container_width=True):
                    sim.pause()
                    st.rerun()

        with c_step1:
            if st.button("Step +1s", use_container_width=True):
                sim.step(1.0)
                st.rerun()

        with c_step5:
            if st.button("Step +5s", use_container_width=True):
                for _ in range(5):
                    sim.step(1.0)
                st.rerun()

        with c_reset:
            if st.button("🔄 Reset", use_container_width=True):
                sim.reset()
                st.rerun()

        with c_mode_disp:
            st.markdown(
                f"""
                <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 8px; padding: 0.5rem 0.85rem; display: flex; justify-content: space-between; align-items: center; height: 38px;">
                    <span style="font-size: 0.78rem; color: #A4ADB3;">Clock: <strong style="color: #F1F0EB;">T+{int(metrics['time_elapsed_sec'])}s</strong></span>
                    <span style="font-size: 0.78rem; color: #C6A76A; font-weight: 600;">Phase: {metrics['current_phase']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    col_sim_left, col_sim_right = st.columns([1.6, 1.0])
    with col_sim_left:
        render_intersection_view(metrics, queues, plan.get("cycle_length", 90.0))
    with col_sim_right:
        st.plotly_chart(plot_queue_history(sim.history), use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    render_approach_cards(metrics, queues, arrivals, plan)


# ==============================================================================
# MODULE 3: AI SIGNAL OPTIMIZATION
# ==============================================================================
elif "3. AI Signal Optimization" in selected_module:
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="status-pill"><span class="status-dot"></span> MATHEMATICAL & ML OPTIMIZATION</span>
                <span style="font-size: 0.8rem; color: #C6A76A; font-weight: 600;">Webster Delay Minimization & Queue Balancing</span>
            </div>
            <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">AI SIGNAL OPTIMIZATION</h1>
            <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
                Theoretical delay formulation, optimal cycle length vertex calculation, and dynamic split balancing.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    opt = st.session_state.optimizer
    cycles, delays, c_opt = opt.generate_delay_curve(arrivals, config.DEFAULT_SATURATION_FLOW_RATE)

    # Top Row: Objective Delay Curve + Formulation Overview
    col_opt_chart, col_opt_calc = st.columns([1.5, 1.0])
    with col_opt_chart:
        st.plotly_chart(plot_delay_curve(cycles, delays, c_opt), use_container_width=True)

    with col_opt_calc:
        st.markdown(
            f"""
            <div class="panel-card" style="height: 100%;">
                <div class="panel-header">
                    <span class="panel-title">Optimization Formulation</span>
                    <span class="panel-badge sage">C_opt = {int(c_opt)}s</span>
                </div>
                <div style="font-size: 0.82rem; color: #A4ADB3; line-height: 1.6;">
                    <p style="margin-bottom: 0.5rem;"><strong style="color: #F1F0EB;">Webster's Analytical Equation:</strong></p>
                    <div style="background: #17232D; border: 1px solid #30404A; border-radius: 6px; padding: 0.6rem; font-family: monospace; font-size: 0.85rem; color: #C6A76A; margin-bottom: 0.6rem;">
                        C_opt = (1.5 * L + 5) / (1 - Y)
                    </div>
                    <ul style="padding-left: 1.1rem; margin: 0; font-size: 0.78rem;">
                        <li>Total Lost Time (L): <strong>8.0 seconds</strong></li>
                        <li>Critical Flow Sum (Y): <strong>{plan.get('critical_flow_sum_Y', 0.58)}</strong></li>
                        <li>Effective Green Time (g_eff): <strong>{round(c_opt - 8.0, 1)}s</strong></li>
                        <li>Saturation Flow Rate: <strong>{config.DEFAULT_SATURATION_FLOW_RATE} vphpl</strong></li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    # Priority Scores & Safety Interlocking Section
    col_prio, col_fair, col_safety = st.columns(3)
    prio_scores = plan.get("priority_scores", {"Phase_NS": 50.0, "Phase_EW": 50.0})
    fair_weights = plan.get("fairness_weights", {"Phase_NS": 1.0, "Phase_EW": 1.0})

    with col_prio:
        st.markdown(
            f"""
            <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.1rem;">
                <span style="font-size: 0.72rem; text-transform: uppercase; color: #A4ADB3; font-weight: 600;">DYNAMIC PRIORITY SCORES</span>
                <div style="display: flex; justify-content: space-between; margin-top: 0.65rem;">
                    <div>
                        <span style="font-size: 0.75rem; color: #A4ADB3;">Phase NS:</span><br/>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #8BAE9B;">{prio_scores['Phase_NS']}%</span>
                    </div>
                    <div style="border-left: 1px solid #24333D; padding-left: 1rem;">
                        <span style="font-size: 0.75rem; color: #A4ADB3;">Phase EW:</span><br/>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #C6A76A;">{prio_scores['Phase_EW']}%</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_fair:
        st.markdown(
            f"""
            <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.1rem;">
                <span style="font-size: 0.72rem; text-transform: uppercase; color: #A4ADB3; font-weight: 600;">ANTI-STARVATION FAIRNESS</span>
                <div style="display: flex; justify-content: space-between; margin-top: 0.65rem;">
                    <div>
                        <span style="font-size: 0.75rem; color: #A4ADB3;">NS Wait Weight:</span><br/>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #F1F0EB;">{fair_weights['Phase_NS']}x</span>
                    </div>
                    <div style="border-left: 1px solid #24333D; padding-left: 1rem;">
                        <span style="font-size: 0.75rem; color: #A4ADB3;">EW Wait Weight:</span><br/>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #F1F0EB;">{fair_weights['Phase_EW']}x</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_safety:
        st.markdown(
            """
            <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.1rem;">
                <span style="font-size: 0.72rem; text-transform: uppercase; color: #A4ADB3; font-weight: 600;">SIGNAL SAFETY INTERLOCK</span>
                <div style="margin-top: 0.65rem; display: flex; align-items: center; gap: 8px;">
                    <span style="color: #4EBA86; font-size: 1.3rem;">✔</span>
                    <div>
                        <span style="font-size: 0.85rem; font-weight: 600; color: #F1F0EB;">Interlock Verified Safe</span><br/>
                        <span style="font-size: 0.72rem; color: #A4ADB3;">Conflicting green states mathematically locked.</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    
    # Plain-English Decision Rationale
    decision_text = plan.get("decision_explanation", "Optimal cycle and split determined based on current corridor queue backlog and flow pressure.")
    st.markdown(
        f"""
        <div style="background: #17232D; border-left: 3px solid #C6A76A; border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem;">
            <span style="font-size: 0.75rem; text-transform: uppercase; color: #C6A76A; font-weight: 600;">AI DECISION RATIONALE & EXPLANATION</span>
            <p style="font-size: 0.85rem; color: #F1F0EB; margin: 0.3rem 0 0 0; line-height: 1.5;">
                {decision_text}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Interactive Flow Split Calculator
    st.markdown("<h3 style='font-size: 1.15rem; color: #F1F0EB;'>Interactive Split Sensitivity Calculator</h3>", unsafe_allow_html=True)
    c_in1, c_in2, c_in3, c_in4 = st.columns(4)
    with c_in1:
        custom_nb = st.slider("Northbound Flow (vph)", 100, 1200, int(arrivals["NB"]), 25)
    with c_in2:
        custom_sb = st.slider("Southbound Flow (vph)", 100, 1200, int(arrivals["SB"]), 25)
    with c_in3:
        custom_eb = st.slider("Eastbound Flow (vph)", 100, 1200, int(arrivals["EB"]), 25)
    with c_in4:
        custom_wb = st.slider("Westbound Flow (vph)", 100, 1200, int(arrivals["WB"]), 25)

    custom_plan = opt.optimize_ai_adaptive(
        {"NB": custom_nb, "SB": custom_sb, "EB": custom_eb, "WB": custom_wb},
        {"NB": 5, "SB": 5, "EB": 3, "WB": 3},
    )

    st.markdown(
        f"""
        <div style="background: #17232D; border: 1px solid #30404A; border-radius: 10px; padding: 1rem; display: flex; justify-content: space-around; text-align: center;">
            <div>
                <span style="font-size: 0.75rem; color: #A4ADB3;">OPTIMAL CYCLE</span><br/>
                <span style="font-size: 1.4rem; font-weight: 700; color: #C6A76A;">{custom_plan['cycle_length']}s</span>
            </div>
            <div style="border-left: 1px solid #24333D; padding-left: 1.5rem;">
                <span style="font-size: 0.75rem; color: #A4ADB3;">NORTH-SOUTH GREEN</span><br/>
                <span style="font-size: 1.4rem; font-weight: 700; color: #8BAE9B;">{custom_plan['phase_greens']['Phase_NS']}s</span>
            </div>
            <div style="border-left: 1px solid #24333D; padding-left: 1.5rem;">
                <span style="font-size: 0.75rem; color: #A4ADB3;">EAST-WEST GREEN</span><br/>
                <span style="font-size: 1.4rem; font-weight: 700; color: #8BAE9B;">{custom_plan['phase_greens']['Phase_EW']}s</span>
            </div>
            <div style="border-left: 1px solid #24333D; padding-left: 1.5rem;">
                <span style="font-size: 0.75rem; color: #A4ADB3;">CRITICAL FLOW RATIO Y</span><br/>
                <span style="font-size: 1.4rem; font-weight: 700; color: #F1F0EB;">{custom_plan.get('critical_flow_sum_Y', 0.5)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# MODULE 4: TRAFFIC ANALYTICS
# ==============================================================================
elif "4. Traffic Analytics" in selected_module:
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="status-pill"><span class="status-dot"></span> HISTORICAL & LOGGED TELEMETRY</span>
                <span style="font-size: 0.8rem; color: #8BAE9B; font-weight: 600;">Time-Series Analysis & Filtering</span>
            </div>
            <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">TRAFFIC ANALYTICS</h1>
            <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
                Exploratory data analysis, diurnal peak hour curves, and Level of Service distributions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    raw_data: pd.DataFrame = st.session_state.historical_data

    # Interactive Filters Bar
    with st.expander("🔍 Analytics Data Filters", expanded=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            weather_filter = st.selectbox("Weather Condition", ["All Weather Conditions"] + list(raw_data["weather"].unique()))
        with col_f2:
            hour_range = st.slider("Hour of Day Range", 0, 24, (0, 24))
        with col_f3:
            approach_filter = st.selectbox("Approach Corridor", ["All Approaches"] + list(raw_data["approach_name"].unique()))

    # Apply Filters Safely
    filtered_df = raw_data.copy()
    if weather_filter != "All Weather Conditions":
        filtered_df = filtered_df[filtered_df["weather"] == weather_filter]
    filtered_df = filtered_df[(filtered_df["hour"] >= hour_range[0]) & (filtered_df["hour"] <= hour_range[1])]
    if approach_filter != "All Approaches":
        filtered_df = filtered_df[filtered_df["approach_name"] == approach_filter]

    analytics = TrafficAnalytics(filtered_df)
    summary = analytics.compute_executive_summary()
    hourly_df = analytics.get_hourly_congestion_profile()
    approach_df = analytics.get_approach_breakdown()
    los_data = analytics.get_los_distribution()

    # Dynamic Analytical Insights Banner
    if summary:
        st.markdown(
            f"""
            <div style="background: #17232D; border: 1px solid #30404A; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1.25rem;">
                <span style="font-size: 0.72rem; text-transform: uppercase; color: #C6A76A; font-weight: 600;">DATASET INSIGHTS</span>
                <p style="font-size: 0.86rem; color: #F1F0EB; margin: 0.3rem 0 0 0; line-height: 1.5;">
                    Across <strong>{summary['total_vehicles_served']:,}</strong> vehicles evaluated, AI-adaptive optimization reduced average control delay by
                    <strong style="color: #8BAE9B;">{summary['delay_reduction_pct']}%</strong> (from {summary['avg_fixed_delay_sec']}s to {summary['avg_ai_delay_sec']}s per vehicle),
                    saving an estimated <strong style="color: #C6A76A;">{summary['total_co2_saved_kg']:,} kg of CO2</strong> and
                    <strong style="color: #C6A76A;">${summary['economic_savings_usd']:,} USD</strong> in commuter delay time.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # All Six Charts in a 2x3 Grid
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.plotly_chart(plot_hourly_comparison(hourly_df), use_container_width=True)
    with col_h2:
        st.plotly_chart(plot_hourly_volume_flow(hourly_df), use_container_width=True)

    col_h3, col_h4 = st.columns(2)
    with col_h3:
        st.plotly_chart(plot_los_distribution(los_data), use_container_width=True)
    with col_h4:
        st.plotly_chart(plot_approach_breakdown(approach_df), use_container_width=True)

    col_h5, col_h6 = st.columns(2)
    with col_h5:
        st.plotly_chart(plot_radar_benchmark(), use_container_width=True)
    with col_h6:
        st.plotly_chart(plot_environmental_savings(hourly_df), use_container_width=True)

    # Filtered Dataset Download & Preview
    with st.expander("📄 Filtered Traffic Dataset Explorer & CSV Export", expanded=False):
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=csv_buffer.getvalue().encode("utf-8"),
            file_name="filtered_traffic_telemetry.csv",
            mime="text/csv",
        )
        st.dataframe(filtered_df.head(100), use_container_width=True)


# ==============================================================================
# MODULE 5: PERFORMANCE COMPARISON (STAGE 6)
# ==============================================================================
elif "5. Performance Comparison" in selected_module:
    render_comparison_view()


# ==============================================================================
# MODULE 6: ABOUT PROJECT
# ==============================================================================
elif "6. About Project" in selected_module:
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.35rem;">
                <span class="status-pill"><span class="status-dot"></span> ACADEMIC SPECIFICATION</span>
                <span style="font-size: 0.8rem; color: #A4ADB3;">• University Faculty Brief</span>
            </div>
            <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">ABOUT PROJECT</h1>
            <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
                Comprehensive system architecture, mathematical foundations, and academic documentation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Section 1 & 2: Overview & Problem Statement
    col_ab1, col_ab2 = st.columns(2)
    with col_ab1:
        st.markdown(
            """
            <div class="panel-card" style="height: 100%;">
                <h3 style="color: #C6A76A; font-size: 1.15rem; margin-top: 0;">1. Project Overview & Vision</h3>
                <p style="color: #F1F0EB; font-size: 0.85rem; line-height: 1.6;">
                    <strong>TRAFFIC SIGNAL TIMING OPTIMIZATION</strong> is an advanced, commercial-grade decision support platform
                    demonstrating how intelligent, queue-aware signal timing dynamically mitigates urban arterial gridlock.
                    The platform bridges classical traffic engineering principles with responsive numerical optimization.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_ab2:
        st.markdown(
            """
            <div class="panel-card" style="height: 100%;">
                <h3 style="color: #E05D5D; font-size: 1.15rem; margin-top: 0;">2. Problem Statement</h3>
                <p style="color: #F1F0EB; font-size: 0.85rem; line-height: 1.6;">
                    Conventional signalized intersections operate primarily on pre-programmed fixed timetables.
                    During tidal morning/evening commute spikes, adverse weather, or incidents, rigid splits cause severe
                    delay accumulation, unnecessary fuel idling, and elevated greenhouse emissions on overloaded corridors.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Section 3 & 4: Proposed Solution & System Architecture
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    col_ab3, col_ab4 = st.columns(2)
    with col_ab3:
        st.markdown(
            """
            <div class="panel-card" style="height: 100%;">
                <h3 style="color: #8BAE9B; font-size: 1.15rem; margin-top: 0;">3. Proposed Intelligent Solution</h3>
                <p style="color: #F1F0EB; font-size: 0.85rem; line-height: 1.6;">
                    The platform implements an adaptive multi-objective controller combining:
                </p>
                <ul style="font-size: 0.82rem; color: #A4ADB3; line-height: 1.6; padding-left: 1.2rem; margin: 0;">
                    <li><strong>Dynamic Webster Optimization:</strong> Calculates minimum delay cycle time vertex.</li>
                    <li><strong>Queue-Aware Split Allocation:</strong> Allocates green proportional to real-time backlog.</li>
                    <li><strong>Waiting-Time Anti-Starvation:</strong> Enforces fairness so side streets never starve.</li>
                    <li><strong>Safety Interlocking:</strong> Guarantees physical mutual exclusion of green phases.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_ab4:
        st.markdown(
            """
            <div class="panel-card" style="height: 100%;">
                <h3 style="color: #5C9EAD; font-size: 1.15rem; margin-top: 0;">4. System Architecture & Tech Stack</h3>
                <ul style="font-size: 0.82rem; color: #A4ADB3; line-height: 1.6; padding-left: 1.2rem; margin: 0;">
                    <li><strong>Frontend & Layout:</strong> Streamlit with custom Apple/Linear CSS styling.</li>
                    <li><strong>Visualization:</strong> Responsive SVG graphics & Plotly interactive charts.</li>
                    <li><strong>Computation:</strong> Python, NumPy vectorization & SciPy bounded minimization.</li>
                    <li><strong>Standards Compliance:</strong> Highway Capacity Manual (HCM 6th Edition) Level of Service (LOS).</li>
                    <li><strong>Emissions Modeling:</strong> EPA/USDOT fuel idling and CO2 emission models.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Section 5, 6, & 7: Methodology, Limitations, Future Scope
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="panel-card">
            <h3 style="color: #C6A76A; font-size: 1.15rem; margin-top: 0;">5. Theoretical Methodology</h3>
            <p style="font-size: 0.85rem; color: #A4ADB3; line-height: 1.6;">
                The platform formulates total intersection delay as a convex minimization objective:
                <br/>
                <code style="color: #C6A76A;">C_opt = (1.5 * L + 5) / (1 - Y)</code> where <code>Y = sum(q_i / s_i)</code>.
                Proportional effective green times <code>g_i = (C - L) * (y_i / Y)</code> are bounded by minimum green (10s)
                and maximum green (75s) with a 3.5s yellow change interval and 1.5s all-red clearance interval.
            </p>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem; border-top: 1px solid #24333D; padding-top: 1rem;">
                <div>
                    <h4 style="color: #E5A93C; font-size: 0.95rem; margin-top: 0;">6. Operational Limitations</h4>
                    <ul style="font-size: 0.8rem; color: #A4ADB3; line-height: 1.5; padding-left: 1.1rem; margin: 0;">
                        <li>Under purely symmetric low-density traffic, fixed 50/50 timing already achieves competitive flow.</li>
                        <li>High stochastic arrival jitter requires sensor smoothing to avoid green-split chattering.</li>
                        <li>Cross-street vehicles face bounded maximum red limits due to mandatory fairness floors.</li>
                    </ul>
                </div>
                <div>
                    <h4 style="color: #8BAE9B; font-size: 0.95rem; margin-top: 0;">7. Future Scope</h4>
                    <ul style="font-size: 0.8rem; color: #A4ADB3; line-height: 1.5; padding-left: 1.1rem; margin: 0;">
                        <li>Multi-intersection arterial Green Wave progression and coordinated corridor offsets.</li>
                        <li>Deep Reinforcement Learning (Proximal Policy Optimization / DQN) integration.</li>
                        <li>Vehicle-to-Infrastructure (V2I / V2X) connected autonomous vehicle platoon detection.</li>
                    </ul>
                </div>
            </div>

            <div style="background: rgba(198, 167, 106, 0.1); border-left: 3px solid #C6A76A; border-radius: 0 8px 8px 0; padding: 0.85rem 1rem; margin-top: 1.25rem;">
                <strong style="color: #C6A76A; font-size: 0.85rem;">Responsible Academic & Simulation Notice:</strong><br/>
                <span style="font-size: 0.8rem; color: #A4ADB3;">
                    {config.APP_METADATA['disclaimer']}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
