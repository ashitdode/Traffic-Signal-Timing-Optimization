"""
Sidebar Navigation and Global Controls Component.
Refined Apple/Linear aesthetic with clean navigation, scenario selection, and status telemetry.
"""

import os
import streamlit as st
from PIL import Image
import config


def render_sidebar():
    """
    Renders the sophisticated dark sidebar with module navigation and global controls.
    Returns:
      (selected_module, active_scenario, selected_controller)
    """
    with st.sidebar:
        # App Branding Header
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        col_logo, col_title = st.columns([1, 3.2])
        
        with col_logo:
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                st.image(logo_img, width=54)
            else:
                st.write("🚦")
                
        with col_title:
            st.markdown(
                """
                <div style="line-height: 1.15; padding-top: 4px;">
                    <span style="font-size: 0.95rem; font-weight: 700; color: #F1F0EB; letter-spacing: -0.01em;">
                        TRAFFIC OPTIMIZER
                    </span><br/>
                    <span style="font-size: 0.72rem; color: #C6A76A; font-weight: 500; letter-spacing: 0.04em;">
                        AI SIGNAL SUITE v2.4
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # System Health Pill
        st.markdown(
            """
            <div class="status-pill" style="margin-bottom: 1.2rem; width: 100%; justify-content: space-between;">
                <span style="display: flex; align-items: center; gap: 6px;">
                    <span class="status-dot pulse"></span>
                    <span style="color: #F1F0EB; font-weight: 500;">Core Engine Active</span>
                </span>
                <span style="color: #8BAE9B; font-size: 0.7rem; font-weight: 600;">HCM 6th ED</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; margin-bottom: 0.4rem;'>PLATFORM MODULES</p>",
            unsafe_allow_html=True,
        )

        modules = [
            "1. Overview Dashboard",
            "2. Live Traffic Simulation",
            "3. AI Signal Optimization",
            "4. Traffic Analytics",
            "5. Performance Comparison",
            "6. About Project",
        ]
        
        selected_module = st.radio(
            "Navigation",
            options=modules,
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("<hr style='border: none; border-top: 1px solid #30404A; margin: 1.25rem 0;'>", unsafe_allow_html=True)
        
        # Scenario Selector
        st.markdown(
            "<p style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; margin-bottom: 0.4rem;'>GLOBAL SCENARIO PRESET</p>",
            unsafe_allow_html=True,
        )
        
        scenario_options = list(config.TRAFFIC_SCENARIOS.keys())
        default_idx = scenario_options.index("Balanced Traffic") if "Balanced Traffic" in scenario_options else 0
        active_scenario = st.selectbox(
            "Select Scenario",
            options=scenario_options,
            index=default_idx,
            label_visibility="collapsed",
            key="sidebar_scenario_select",
        )
        
        sc_desc = config.TRAFFIC_SCENARIOS[active_scenario]["description"]
        st.markdown(
            f"""
            <div style="background: #17232D; border: 1px solid #30404A; border-radius: 8px; padding: 0.65rem 0.8rem; margin-top: 0.4rem; font-size: 0.76rem; color: #A4ADB3; line-height: 1.35;">
                <span style="color: #C6A76A; font-weight: 600;">Profile:</span><br/>
                {sc_desc}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if active_scenario == "Manual Traffic Input":
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div style="background: rgba(198, 167, 106, 0.08); border: 1px solid rgba(198, 167, 106, 0.35); border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 0.75rem; font-weight: 700; color: #C6A76A; text-transform: uppercase; letter-spacing: 0.05em;">MANUAL VEHICLE COUNTS (0 - 200)</span>
                    <p style="font-size: 0.72rem; color: #A4ADB3; margin: 3px 0 0 0;">Enter vehicle queue counts per approach corridor.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                in_nb = st.number_input(
                    "North (NB)",
                    min_value=0,
                    max_value=200,
                    value=int(st.session_state.get("manual_nb", 35)),
                    step=1,
                    key="sidebar_manual_nb",
                    help="Northbound vehicle count (0 to 200)",
                )
                in_eb = st.number_input(
                    "East (EB)",
                    min_value=0,
                    max_value=200,
                    value=int(st.session_state.get("manual_eb", 25)),
                    step=1,
                    key="sidebar_manual_eb",
                    help="Eastbound vehicle count (0 to 200)",
                )
            with col_m2:
                in_sb = st.number_input(
                    "South (SB)",
                    min_value=0,
                    max_value=200,
                    value=int(st.session_state.get("manual_sb", 30)),
                    step=1,
                    key="sidebar_manual_sb",
                    help="Southbound vehicle count (0 to 200)",
                )
                in_wb = st.number_input(
                    "West (WB)",
                    min_value=0,
                    max_value=200,
                    value=int(st.session_state.get("manual_wb", 20)),
                    step=1,
                    key="sidebar_manual_wb",
                    help="Westbound vehicle count (0 to 200)",
                )

            # Strict validation: prevent negative values, clamp between 0 and 200
            val_nb = max(0, min(200, int(in_nb)))
            val_sb = max(0, min(200, int(in_sb)))
            val_eb = max(0, min(200, int(in_eb)))
            val_wb = max(0, min(200, int(in_wb)))

            if st.button("Apply Traffic Input", type="primary", use_container_width=True, key="btn_apply_sidebar_manual"):
                st.session_state["manual_nb"] = val_nb
                st.session_state["manual_sb"] = val_sb
                st.session_state["manual_eb"] = val_eb
                st.session_state["manual_wb"] = val_wb
                st.session_state["manual_counts_pending"] = {
                    "NB": val_nb,
                    "SB": val_sb,
                    "EB": val_eb,
                    "WB": val_wb,
                }
                st.rerun()

        st.markdown("<hr style='border: none; border-top: 1px solid #30404A; margin: 1.25rem 0;'>", unsafe_allow_html=True)
        
        # Control Algorithm Selector
        st.markdown(
            "<p style='font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; margin-bottom: 0.4rem;'>ACTIVE SIMULATOR CONTROLLER</p>",
            unsafe_allow_html=True,
        )
        
        controller_options = [
            "AI-Adaptive (Webster + ML Surrogate)",
            "Fixed-Time (Pre-timed 50/50)",
            "Actuated (Sensor Gap-Out)",
        ]
        
        selected_controller = st.selectbox(
            "Controller",
            options=controller_options,
            index=0,
            label_visibility="collapsed",
            key="sidebar_controller_select",
        )

        st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
        
        # Academic & Simulation Notice
        st.markdown(
            """
            <div style="background: rgba(48, 64, 74, 0.35); border-left: 2px solid #C6A76A; padding: 0.6rem 0.75rem; border-radius: 0 6px 6px 0; font-size: 0.72rem; color: #A4ADB3;">
                <span style="color: #F1F0EB; font-weight: 600;">Simulated Testbed:</span><br/>
                All metrics derived from mathematical models and synthetic arterial sensors.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return selected_module, active_scenario, selected_controller
