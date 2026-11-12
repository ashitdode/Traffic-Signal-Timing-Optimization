"""
Overview Dashboard Component.
Executive command center displaying high-impact KPI summary cards,
live intersection snapshot, approach telemetry, and operational status.
"""

from typing import Dict, Any
import textwrap
import streamlit as st

import config
from components.intersection import render_intersection_view
from components.signal_cards import render_approach_cards


def render_overview_dashboard(
    metrics: Dict[str, Any],
    queues: Dict[str, int],
    arrivals: Dict[str, float],
    plan: Dict[str, Any],
    scenario_name: str,
):
    """
    Renders the executive Overview Dashboard.
    """
    # Top Header
    header_html = textwrap.dedent(f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="status-pill"><span class="status-dot pulse"></span> LIVE ARTERIAL INTERSECTION</span>
                <span style="font-size: 0.8rem; color: #C6A76A; font-weight: 600;">{scenario_name}</span>
            </div>
            <span class="panel-badge sage">HCM Level of Service: Grade {metrics['los_grade']}</span>
        </div>
        <h1 class="serif-header" style="font-size: 2.2rem; margin: 0 0 0.4rem 0;">OVERVIEW DASHBOARD</h1>
        <p style="font-size: 0.95rem; color: #A4ADB3; margin: 0; line-height: 1.5;">
            Real-time operational command center and dynamic signal telemetry.
        </p>
    </div>
    """).strip()
    st.markdown(header_html, unsafe_allow_html=True)

    # 4 Executive KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        c1_html = textwrap.dedent(f"""
        <div class="kpi-container">
            <div class="kpi-label">Average Vehicle Delay</div>
            <div class="kpi-value">{metrics['avg_delay_sec']} <span style="font-size: 1rem; font-weight: 500; color: #A4ADB3;">s/veh</span></div>
            <div class="kpi-subtext">
                <span>▼ {metrics['delay_reduction_pct']}% vs Fixed Baseline</span>
            </div>
        </div>
        """).strip()
        st.markdown(c1_html, unsafe_allow_html=True)

    with col2:
        c2_html = textwrap.dedent(f"""
        <div class="kpi-container">
            <div class="kpi-label">Total Vehicles Processed</div>
            <div class="kpi-value">{metrics['total_departures']} <span style="font-size: 1rem; font-weight: 500; color: #A4ADB3;">veh</span></div>
            <div class="kpi-subtext">
                <span>Active Cycle Throughput</span>
            </div>
        </div>
        """).strip()
        st.markdown(c2_html, unsafe_allow_html=True)

    with col3:
        c3_html = textwrap.dedent(f"""
        <div class="kpi-container">
            <div class="kpi-label">Current Queue Backlog</div>
            <div class="kpi-value">{metrics['total_current_queue']} <span style="font-size: 1rem; font-weight: 500; color: #A4ADB3;">cars</span></div>
            <div class="kpi-subtext warning">
                <span>Across 4 Approaches</span>
            </div>
        </div>
        """).strip()
        st.markdown(c3_html, unsafe_allow_html=True)

    with col4:
        c4_html = textwrap.dedent(f"""
        <div class="kpi-container">
            <div class="kpi-label">CO2 Emissions Saved</div>
            <div class="kpi-value">{metrics['co2_saved_kg']} <span style="font-size: 1rem; font-weight: 500; color: #A4ADB3;">kg</span></div>
            <div class="kpi-subtext">
                <span>{metrics['fuel_saved_liters']} L Fuel Conserved</span>
            </div>
        </div>
        """).strip()
        st.markdown(c4_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Intersection Visualizer & Approach Telemetry Cards
    col_vis, col_meta = st.columns([1.6, 1.0])
    with col_vis:
        render_intersection_view(metrics, queues, plan.get("cycle_length", 90.0))

    with col_meta:
        meta_html = textwrap.dedent(f"""
        <div class="panel-card" style="height: 100%;">
            <div class="panel-header">
                <span class="panel-title">Active Signal Controller</span>
                <span class="panel-badge">{plan.get('mode', 'AI-Optimized')}</span>
            </div>
            <div style="font-size: 0.85rem; color: #A4ADB3; line-height: 1.6; margin-bottom: 1rem;">
                {plan.get('logic_description', 'Adaptive dynamic signal timing minimization.')}
            </div>
            <div style="background: #17232D; border: 1px solid #30404A; border-radius: 8px; padding: 0.9rem; margin-bottom: 0.9rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.35rem;">
                    <span style="color: #A4ADB3;">Total Cycle Length (C):</span>
                    <strong style="color: #C6A76A;">{plan.get('cycle_length', 90)} seconds</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.35rem;">
                    <span style="color: #A4ADB3;">North-South Green (g_NS):</span>
                    <strong style="color: #8BAE9B;">{plan.get('phase_greens', {}).get('Phase_NS', 40)}s</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span style="color: #A4ADB3;">East-West Green (g_EW):</span>
                    <strong style="color: #8BAE9B;">{plan.get('phase_greens', {}).get('Phase_EW', 40)}s</strong>
                </div>
            </div>
            <div style="font-size: 0.78rem; color: #A4ADB3;">
                <strong style="color: #F1F0EB;">HCM Level of Service (LOS):</strong>
                <p style="margin-top: 0.2rem;">
                    Grade <strong>{metrics['los_grade']}</strong> ({metrics['los_label']}). Average vehicle control delay is currently within optimal arterial tolerances.
                </p>
            </div>
        </div>
        """).strip()
        st.markdown(meta_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.15rem; color: #F1F0EB; margin-bottom: 0.75rem;'>Approach Corridor Telemetry</h3>", unsafe_allow_html=True)
    render_approach_cards(metrics, queues, arrivals, plan)
