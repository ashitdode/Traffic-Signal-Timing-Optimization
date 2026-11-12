"""
Signal Telemetry Cards Component.
Displays approach-level operational metrics (Northbound, Southbound, Eastbound, Westbound)
including queue meters, allocated green times, flow rates, and HCM Level of Service.
"""

from typing import Dict, Any
import streamlit as st
import config


def render_approach_cards(
    metrics: Dict[str, Any],
    queues: Dict[str, int],
    arrivals: Dict[str, float],
    plan: Dict[str, Any],
):
    """
    Renders 4 refined telemetry cards corresponding to intersection approaches.
    """
    ns_light = metrics.get("ns_light", "RED")
    ew_light = metrics.get("ew_light", "RED")
    
    approach_configs = [
        {
            "key": "NB",
            "name": "Northbound",
            "icon": "▲",
            "light": ns_light,
            "green_alloc": plan.get("approach_greens", {}).get("NB", 40.0),
        },
        {
            "key": "SB",
            "name": "Southbound",
            "icon": "▼",
            "light": ns_light,
            "green_alloc": plan.get("approach_greens", {}).get("SB", 40.0),
        },
        {
            "key": "EB",
            "name": "Eastbound",
            "icon": "▶",
            "light": ew_light,
            "green_alloc": plan.get("approach_greens", {}).get("EB", 40.0),
        },
        {
            "key": "WB",
            "name": "Westbound",
            "icon": "◀",
            "light": ew_light,
            "green_alloc": plan.get("approach_greens", {}).get("WB", 40.0),
        },
    ]

    cols = st.columns(4)
    
    for idx, app in enumerate(approach_configs):
        key = app["key"]
        q_count = queues.get(key, 0)
        vph = arrivals.get(key, 400)
        light_state = app["light"]
        
        if light_state == "GREEN":
            light_badge = '<span style="background: rgba(78,186,134,0.15); color: #4EBA86; border: 1px solid rgba(78,186,134,0.3); padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 600;">GREEN</span>'
        elif light_state == "YELLOW":
            light_badge = '<span style="background: rgba(229,169,60,0.15); color: #E5A93C; border: 1px solid rgba(229,169,60,0.3); padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 600;">AMBER</span>'
        else:
            light_badge = '<span style="background: rgba(224,93,93,0.15); color: #E05D5D; border: 1px solid rgba(224,93,93,0.3); padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 600;">RED</span>'

        meter_pct = min(100, int((q_count / 25.0) * 100))
        meter_color = "#4EBA86" if q_count < 8 else ("#E5A93C" if q_count < 16 else "#E05D5D")

        with cols[idx]:
            card_html = f"""
            <div style="background: #1B2933; border: 1px solid #30404A; border-radius: 12px; padding: 1.1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.25);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                    <span style="font-size: 0.82rem; font-weight: 600; color: #F1F0EB;">
                        <span style="color: #C6A76A; margin-right: 4px;">{app["icon"]}</span> {app["name"]}
                    </span>
                    {light_badge}
                </div>
                
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.5rem;">
                    <div>
                        <span style="font-size: 0.72rem; color: #A4ADB3; text-transform: uppercase;">Current Queue</span><br/>
                        <span style="font-size: 1.5rem; font-weight: 700; color: #F1F0EB;">{q_count}</span>
                        <span style="font-size: 0.75rem; color: #A4ADB3;">veh</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.72rem; color: #A4ADB3; text-transform: uppercase;">Green Split</span><br/>
                        <span style="font-size: 1.15rem; font-weight: 600; color: #8BAE9B;">{app["green_alloc"]}s</span>
                    </div>
                </div>

                <div style="margin-top: 0.85rem; background: #17232D; border-radius: 999px; height: 5px; width: 100%; overflow: hidden; border: 1px solid #24333D;">
                    <div style="width: {meter_pct}%; background: {meter_color}; height: 100%; border-radius: 999px; transition: width 0.3s ease;"></div>
                </div>

                <div style="display: flex; justify-content: space-between; font-size: 0.7rem; color: #A4ADB3; margin-top: 0.55rem;">
                    <span>Demand: <strong style="color: #F1F0EB;">{int(vph)} vph</strong></span>
                    <span>Density: <strong style="color: #C6A76A;">{meter_pct}%</strong></span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
