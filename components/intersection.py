"""
Intersection Visualization Component.
Renders an interactive high-fidelity SVG/HTML 4-way intersection with active signal heads,
queue counters, crosswalk markings, directional movement arrows, and dynamic phase countdowns.
"""

from typing import Dict, Any
import streamlit as st
import config


def render_intersection_view(
    metrics: Dict[str, Any],
    queues: Dict[str, int],
    cycle_time: float = 90.0,
):
    """
    Renders the modern SVG-based 4-way signalized intersection view.
    """
    ns_light = metrics.get("ns_light", "GREEN")
    ew_light = metrics.get("ew_light", "RED")
    remaining_sec = metrics.get("phase_remaining_sec", 0.0)
    current_phase_desc = metrics.get("current_phase_desc", "Signal Active")
    
    color_off = config.COLOR_SIGNAL_OFF
    red_active = config.COLOR_SIGNAL_RED
    amber_active = config.COLOR_SIGNAL_AMBER
    green_active = config.COLOR_SIGNAL_GREEN

    ns_red_color = red_active if ns_light == "RED" else color_off
    ns_red_glow = "filter: drop-shadow(0 0 7px rgba(224,93,93,0.85));" if ns_light == "RED" else ""
    
    ns_amber_color = amber_active if ns_light == "YELLOW" else color_off
    ns_amber_glow = "filter: drop-shadow(0 0 7px rgba(229,169,60,0.85));" if ns_light == "YELLOW" else ""
    
    ns_green_color = green_active if ns_light == "GREEN" else color_off
    ns_green_glow = "filter: drop-shadow(0 0 7px rgba(78,186,134,0.85));" if ns_light == "GREEN" else ""

    ew_red_color = red_active if ew_light == "RED" else color_off
    ew_red_glow = "filter: drop-shadow(0 0 7px rgba(224,93,93,0.85));" if ew_light == "RED" else ""
    
    ew_amber_color = amber_active if ew_light == "YELLOW" else color_off
    ew_amber_glow = "filter: drop-shadow(0 0 7px rgba(229,169,60,0.85));" if ew_light == "YELLOW" else ""
    
    ew_green_color = green_active if ew_light == "GREEN" else color_off
    ew_green_glow = "filter: drop-shadow(0 0 7px rgba(78,186,134,0.85));" if ew_light == "GREEN" else ""

    q_nb = queues.get("NB", 0)
    q_sb = queues.get("SB", 0)
    q_eb = queues.get("EB", 0)
    q_wb = queues.get("WB", 0)

    phase_badge_color = "#4EBA86" if "GREEN" in metrics.get("current_phase", "") else ("#E5A93C" if "YELLOW" in metrics.get("current_phase", "") else "#E05D5D")

    svg_content = f"""
    <div style="background: #17232D; border: 1px solid #30404A; border-radius: 16px; padding: 1.25rem; box-shadow: 0 4px 20px rgba(0,0,0,0.35);">
        <!-- Intersection Top Bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #24333D; padding-bottom: 0.75rem;">
            <div>
                <span style="font-size: 0.75rem; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; font-weight: 600;">ACTIVE PHASE</span><br/>
                <span style="font-size: 1.05rem; font-weight: 600; color: #F1F0EB;">{current_phase_desc}</span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.75rem; text-transform: uppercase; color: #A4ADB3; letter-spacing: 0.08em; font-weight: 600;">COUNTDOWN</span><br/>
                <span style="font-size: 1.35rem; font-weight: 700; color: {phase_badge_color}; font-family: 'Inter', monospace;">{remaining_sec}s</span>
            </div>
        </div>

        <!-- SVG 4-Way Intersection Rendering -->
        <svg viewBox="0 0 600 600" width="100%" height="auto" style="max-height: 480px; display: block; margin: 0 auto; background: #131E27; border-radius: 12px; border: 1px solid #2A3B46;">
            <!-- Grass / Corner Quadrants -->
            <rect x="0" y="0" width="220" height="220" fill="#17232D" />
            <rect x="380" y="0" width="220" height="220" fill="#17232D" />
            <rect x="0" y="380" width="220" height="220" fill="#17232D" />
            <rect x="380" y="380" width="220" height="220" fill="#17232D" />

            <!-- Road Surfaces -->
            <rect x="220" y="0" width="160" height="600" fill="#1A2833" />
            <rect x="0" y="220" width="600" height="160" fill="#1A2833" />
            
            <!-- Road Border Curbings -->
            <line x1="220" y1="0" x2="220" y2="220" stroke="#30404A" stroke-width="3" />
            <line x1="380" y1="0" x2="380" y2="220" stroke="#30404A" stroke-width="3" />
            <line x1="220" y1="380" x2="220" y2="600" stroke="#30404A" stroke-width="3" />
            <line x1="380" y1="380" x2="380" y2="600" stroke="#30404A" stroke-width="3" />
            <line x1="0" y1="220" x2="220" y2="220" stroke="#30404A" stroke-width="3" />
            <line x1="380" y1="220" x2="600" y2="220" stroke="#30404A" stroke-width="3" />
            <line x1="0" y1="380" x2="220" y2="380" stroke="#30404A" stroke-width="3" />
            <line x1="380" y1="380" x2="600" y2="380" stroke="#30404A" stroke-width="3" />

            <!-- Dashed Yellow Center Divider Lines -->
            <line x1="300" y1="0" x2="300" y2="200" stroke="#C6A76A" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.8" />
            <line x1="300" y1="400" x2="300" y2="600" stroke="#C6A76A" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.8" />
            <line x1="0" y1="300" x2="200" y2="300" stroke="#C6A76A" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.8" />
            <line x1="400" y1="300" x2="600" y2="300" stroke="#C6A76A" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.8" />

            <!-- White Lane Divider Dashes -->
            <line x1="260" y1="0" x2="260" y2="200" stroke="#526572" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.6" />
            <line x1="340" y1="0" x2="340" y2="200" stroke="#526572" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.6" />
            <line x1="260" y1="400" x2="260" y2="600" stroke="#526572" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.6" />
            <line x1="340" y1="400" x2="340" y2="600" stroke="#526572" stroke-width="1.5" stroke-dasharray="6 6" opacity="0.6" />

            <!-- Crosswalk Markings (Zebra Stripes) -->
            <g stroke="#F1F0EB" stroke-width="3" opacity="0.45">
                <line x1="225" y1="205" x2="225" y2="215" /><line x1="245" y1="205" x2="245" y2="215" />
                <line x1="265" y1="205" x2="265" y2="215" /><line x1="285" y1="205" x2="285" y2="215" />
                <line x1="305" y1="205" x2="305" y2="215" /><line x1="325" y1="205" x2="325" y2="215" />
                <line x1="345" y1="205" x2="345" y2="215" /><line x1="365" y1="205" x2="365" y2="215" />
            </g>
            <g stroke="#F1F0EB" stroke-width="3" opacity="0.45">
                <line x1="225" y1="385" x2="225" y2="395" /><line x1="245" y1="385" x2="245" y2="395" />
                <line x1="265" y1="385" x2="265" y2="395" /><line x1="285" y1="385" x2="285" y2="395" />
                <line x1="305" y1="385" x2="305" y2="395" /><line x1="325" y1="385" x2="325" y2="395" />
                <line x1="345" y1="385" x2="345" y2="395" /><line x1="365" y1="385" x2="365" y2="395" />
            </g>
            <g stroke="#F1F0EB" stroke-width="3" opacity="0.45">
                <line x1="205" y1="225" x2="215" y2="225" /><line x1="205" y1="245" x2="215" y2="245" />
                <line x1="205" y1="265" x2="215" y2="265" /><line x1="205" y1="285" x2="215" y2="285" />
                <line x1="205" y1="305" x2="215" y2="305" /><line x1="205" y1="325" x2="215" y2="325" />
                <line x1="205" y1="345" x2="215" y2="345" /><line x1="205" y1="365" x2="215" y2="365" />
            </g>
            <g stroke="#F1F0EB" stroke-width="3" opacity="0.45">
                <line x1="385" y1="225" x2="395" y2="225" /><line x1="385" y1="245" x2="395" y2="245" />
                <line x1="385" y1="265" x2="395" y2="265" /><line x1="385" y1="285" x2="395" y2="285" />
                <line x1="385" y1="305" x2="395" y2="305" /><line x1="385" y1="325" x2="395" y2="325" />
                <line x1="385" y1="345" x2="395" y2="345" /><line x1="385" y1="365" x2="395" y2="365" />
            </g>

            <!-- TRAFFIC LIGHT HEAD 1: Northbound / Southbound (Top Right Corner) -->
            <g transform="translate(388, 140)">
                <rect x="0" y="0" width="28" height="66" rx="6" fill="#101820" stroke="#30404A" stroke-width="1.5" />
                <circle cx="14" cy="14" r="7" fill="{ns_red_color}" style="{ns_red_glow}" />
                <circle cx="14" cy="33" r="7" fill="{ns_amber_color}" style="{ns_amber_glow}" />
                <circle cx="14" cy="52" r="7" fill="{ns_green_color}" style="{ns_green_glow}" />
                <text x="36" y="38" fill="#F1F0EB" font-size="11" font-weight="600" font-family="Inter, sans-serif">N-S</text>
            </g>

            <!-- TRAFFIC LIGHT HEAD 2: Eastbound / Westbound (Bottom Left Corner) -->
            <g transform="translate(140, 395)">
                <rect x="0" y="0" width="28" height="66" rx="6" fill="#101820" stroke="#30404A" stroke-width="1.5" />
                <circle cx="14" cy="14" r="7" fill="{ew_red_color}" style="{ew_red_glow}" />
                <circle cx="14" cy="33" r="7" fill="{ew_amber_color}" style="{ew_amber_glow}" />
                <circle cx="14" cy="52" r="7" fill="{ew_green_color}" style="{ew_green_glow}" />
                <text x="-32" y="38" fill="#F1F0EB" font-size="11" font-weight="600" font-family="Inter, sans-serif">E-W</text>
            </g>

            <!-- Queue Counter Badges -->
            <g transform="translate(240, 80)">
                <rect x="0" y="0" width="50" height="24" rx="4" fill="rgba(27, 41, 51, 0.9)" stroke="#C6A76A" stroke-width="1" />
                <text x="25" y="16" fill="#F1F0EB" font-size="11" font-weight="600" text-anchor="middle" font-family="Inter, sans-serif">SB: {q_sb}</text>
            </g>

            <g transform="translate(310, 490)">
                <rect x="0" y="0" width="50" height="24" rx="4" fill="rgba(27, 41, 51, 0.9)" stroke="#C6A76A" stroke-width="1" />
                <text x="25" y="16" fill="#F1F0EB" font-size="11" font-weight="600" text-anchor="middle" font-family="Inter, sans-serif">NB: {q_nb}</text>
            </g>

            <g transform="translate(70, 315)">
                <rect x="0" y="0" width="50" height="24" rx="4" fill="rgba(27, 41, 51, 0.9)" stroke="#C6A76A" stroke-width="1" />
                <text x="25" y="16" fill="#F1F0EB" font-size="11" font-weight="600" text-anchor="middle" font-family="Inter, sans-serif">EB: {q_eb}</text>
            </g>

            <g transform="translate(480, 260)">
                <rect x="0" y="0" width="50" height="24" rx="4" fill="rgba(27, 41, 51, 0.9)" stroke="#C6A76A" stroke-width="1" />
                <text x="25" y="16" fill="#F1F0EB" font-size="11" font-weight="600" text-anchor="middle" font-family="Inter, sans-serif">WB: {q_wb}</text>
            </g>

            <!-- Directional Flow Arrows -->
            <g stroke="#8BAE9B" stroke-width="2" fill="none" opacity="0.6">
                <line x1="335" y1="250" x2="335" y2="350" />
                <polyline points="330,340 335,350 340,340" />
                
                <line x1="265" y1="350" x2="265" y2="250" />
                <polyline points="260,260 265,250 270,260" />
                
                <line x1="250" y1="335" x2="350" y2="335" />
                <polyline points="340,330 350,335 340,340" />
                
                <line x1="350" y1="265" x2="250" y2="265" />
                <polyline points="260,260 250,265 260,270" />
            </g>
        </svg>
    </div>
    """
    st.markdown(svg_content, unsafe_allow_html=True)
