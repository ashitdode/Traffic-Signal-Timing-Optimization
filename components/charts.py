"""
Data Visualization & Interactive Charts Component.
Plotly figures crafted to match the Apple/Linear minimalist design system with
dark backgrounds (#17232D, #1B2933), gold (#C6A76A) and sage (#8BAE9B) accents.
"""

from typing import List, Dict, Any
import plotly.graph_objects as go
import pandas as pd
import numpy as np

import config

THEME_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(23, 35, 45, 0.6)",
    font=dict(family="Inter, -apple-system, sans-serif", color=config.COLOR_TEXT_PRIMARY, size=12),
    margin=dict(l=40, r=30, t=40, b=40),
    xaxis=dict(
        gridcolor="#24333D",
        zerolinecolor="#30404A",
        tickfont=dict(color=config.COLOR_TEXT_SECONDARY, size=11),
        title_font=dict(color=config.COLOR_TEXT_SECONDARY, size=12),
    ),
    yaxis=dict(
        gridcolor="#24333D",
        zerolinecolor="#30404A",
        tickfont=dict(color=config.COLOR_TEXT_SECONDARY, size=11),
        title_font=dict(color=config.COLOR_TEXT_SECONDARY, size=12),
    ),
    legend=dict(
        font=dict(color=config.COLOR_TEXT_PRIMARY, size=11),
        bgcolor="rgba(27, 41, 51, 0.7)",
        bordercolor="#30404A",
        borderwidth=1,
    ),
)


def plot_queue_history(history_data: List[Dict[str, Any]]) -> go.Figure:
    """Renders time-series line chart of approach queue lengths."""
    fig = go.Figure()
    
    if not history_data:
        fig.add_annotation(text="No simulation history available yet", showarrow=False, font=dict(color="#A4ADB3"))
        fig.update_layout(**THEME_LAYOUT)
        return fig

    times = [h["time_sec"] for h in history_data]
    series_map = [
        ("queue_NB", "Northbound (NB)", "#8BAE9B"),
        ("queue_SB", "Southbound (SB)", "#5C9EAD"),
        ("queue_EB", "Eastbound (EB)", "#C6A76A"),
        ("queue_WB", "Westbound (WB)", "#E05D5D"),
    ]
    
    for key, name, color in series_map:
        fig.add_trace(go.Scatter(
            x=times,
            y=[h.get(key, 0) for h in history_data],
            mode="lines",
            name=name,
            line=dict(color=color, width=2.2),
            hovertemplate="%{y} veh<extra>" + name + "</extra>",
        ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="Real-Time Approach Queue Dynamics (Vehicles)", font=dict(size=14, color="#F1F0EB")),
        xaxis=dict(title="Simulation Time (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Queue Length (veh)", gridcolor="#24333D"),
        hovermode="x unified",
        height=340,
    )
    fig.update_layout(**layout)
    return fig


def plot_delay_curve(cycles: List[float], delays: List[float], c_opt: float) -> go.Figure:
    """Renders Webster Delay vs Cycle Length curve and pinpoints C_optimal."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=cycles,
        y=delays,
        mode="lines",
        name="Delay Objective Curve",
        line=dict(color="#C6A76A", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(198, 167, 106, 0.08)",
        hovertemplate="Cycle: %{x}s<br>Delay: %{y:.1f}s<extra></extra>",
    ))

    min_delay = min(delays) if delays else 10.0
    fig.add_trace(go.Scatter(
        x=[c_opt],
        y=[min_delay],
        mode="markers+text",
        name="Webster C_optimum",
        text=[f"C_opt = {int(c_opt)}s"],
        textposition="top center",
        marker=dict(color="#4EBA86", size=11, line=dict(color="#F1F0EB", width=2)),
        hovertemplate="Optimal Cycle: %{x}s<br>Min Delay: %{y:.1f}s<extra></extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="Webster Minimum Delay Objective Function", font=dict(size=14, color="#F1F0EB")),
        xaxis=dict(title="Cycle Length C (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Average Control Delay (sec/veh)", gridcolor="#24333D"),
        height=320,
    )
    fig.update_layout(**layout)
    return fig


def plot_hourly_comparison(df_hourly: pd.DataFrame) -> go.Figure:
    """Compares Fixed vs AI average vehicle delay across 24 hours."""
    fig = go.Figure()
    
    if df_hourly.empty:
        fig.update_layout(**THEME_LAYOUT)
        return fig

    fig.add_trace(go.Scatter(
        x=df_hourly["hour"],
        y=df_hourly["fixed_delay_sec"],
        mode="lines+markers",
        name="Fixed Timing (Baseline)",
        line=dict(color="#E05D5D", width=2.2, dash="dash"),
        marker=dict(size=5),
        hovertemplate="Hour %{x}: %{y:.1f}s delay<extra>Fixed</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_hourly["hour"],
        y=df_hourly["ai_delay_sec"],
        mode="lines+markers",
        name="AI-Adaptive Optimization",
        line=dict(color="#8BAE9B", width=2.5),
        marker=dict(size=6),
        fill="tonexty",
        fillcolor="rgba(139, 174, 155, 0.12)",
        hovertemplate="Hour %{x}: %{y:.1f}s delay<extra>AI</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="1. Diurnal Delay Profile: Fixed vs AI-Adaptive", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Hour of Day", dtick=2, gridcolor="#24333D"),
        yaxis=dict(title="Average Delay (sec/veh)", gridcolor="#24333D"),
        hovermode="x unified",
        height=330,
    )
    fig.update_layout(**layout)
    return fig


def plot_hourly_volume_flow(df_hourly: pd.DataFrame) -> go.Figure:
    """Renders hourly traffic demand volume (vph) across diurnal schedule."""
    fig = go.Figure()
    if df_hourly.empty:
        fig.update_layout(**THEME_LAYOUT)
        return fig

    fig.add_trace(go.Bar(
        x=df_hourly["hour"],
        y=df_hourly["vehicle_flow_vph"],
        name="Hourly Demand Flow",
        marker=dict(color="#5C9EAD", opacity=0.85),
        hovertemplate="Hour %{x}: %{y:.0f} vph<extra>Volume</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="2. Hourly Traffic Demand Volume (vph)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Hour of Day", dtick=2, gridcolor="#24333D"),
        yaxis=dict(title="Demand (vph)", gridcolor="#24333D"),
        height=330,
    )
    fig.update_layout(**layout)
    return fig


def plot_los_distribution(los_data: Dict[str, Dict[str, int]]) -> go.Figure:
    """Renders grouped bar chart of Level of Service (LOS) grade frequency."""
    grades = list(config.LOS_THRESHOLDS.keys())
    fixed_counts = [los_data.get("fixed", {}).get(g, 0) for g in grades]
    ai_counts = [los_data.get("ai", {}).get(g, 0) for g in grades]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=grades,
        y=fixed_counts,
        name="Fixed Timing",
        marker=dict(color="#E05D5D", opacity=0.85),
    ))
    fig.add_trace(go.Bar(
        x=grades,
        y=ai_counts,
        name="AI-Adaptive",
        marker=dict(color="#8BAE9B", opacity=0.9),
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="3. HCM Level of Service (LOS) Grade Frequency", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="HCM LOS Grade (A = Best, F = Breakdown)", gridcolor="#24333D"),
        yaxis=dict(title="Observed Count", gridcolor="#24333D"),
        barmode="group",
        height=330,
    )
    fig.update_layout(**layout)
    return fig


def plot_approach_breakdown(df_approach: pd.DataFrame) -> go.Figure:
    """Renders delay per approach bar chart."""
    fig = go.Figure()
    if df_approach.empty:
        fig.update_layout(**THEME_LAYOUT)
        return fig

    fig.add_trace(go.Bar(
        x=df_approach["approach_name"],
        y=df_approach["fixed_delay_sec"],
        name="Fixed Delay (sec)",
        marker=dict(color="#E05D5D", opacity=0.8),
    ))

    fig.add_trace(go.Bar(
        x=df_approach["approach_name"],
        y=df_approach["ai_delay_sec"],
        name="AI Delay (sec)",
        marker=dict(color="#C6A76A", opacity=0.9),
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="4. Average Delay by Approach Corridor (sec/veh)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(gridcolor="#24333D"),
        yaxis=dict(title="Delay (sec)", gridcolor="#24333D"),
        barmode="group",
        height=330,
    )
    fig.update_layout(**layout)
    return fig


def plot_radar_benchmark() -> go.Figure:
    """Renders 6-dimensional Radar chart comparing controllers."""
    categories = [
        "Throughput Efficiency",
        "Delay Reduction",
        "Queue Clearance",
        "Fuel Economy",
        "Phase Responsiveness",
        "Robustness to Surges",
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[55, 50, 48, 52, 35, 42],
        theta=categories,
        fill="toself",
        fillcolor="rgba(224, 93, 93, 0.15)",
        name="Fixed-Time",
        line=dict(color="#E05D5D", width=1.8),
    ))

    fig.add_trace(go.Scatterpolar(
        r=[72, 68, 65, 70, 74, 66],
        theta=categories,
        fill="toself",
        fillcolor="rgba(198, 167, 106, 0.15)",
        name="Actuated",
        line=dict(color="#C6A76A", width=1.8),
    ))

    fig.add_trace(go.Scatterpolar(
        r=[94, 92, 89, 93, 95, 91],
        theta=categories,
        fill="toself",
        fillcolor="rgba(139, 174, 155, 0.25)",
        name="AI-Adaptive",
        line=dict(color="#8BAE9B", width=2.5),
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#A4ADB3", gridcolor="#24333D"),
            angularaxis=dict(color="#F1F0EB", gridcolor="#24333D"),
            bgcolor="rgba(23, 35, 45, 0.6)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#F1F0EB"),
        margin=dict(l=60, r=60, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(27, 41, 51, 0.7)",
            bordercolor="#30404A",
        ),
        title=dict(text="5. Multi-Dimensional Performance Radar", font=dict(size=13, color="#F1F0EB")),
        height=330,
    )
    return fig


def plot_environmental_savings(df_hourly: pd.DataFrame) -> go.Figure:
    """Renders cumulative carbon mitigation and fuel conservation curve."""
    fig = go.Figure()
    if df_hourly.empty:
        fig.update_layout(**THEME_LAYOUT)
        return fig

    cum_co2 = df_hourly["co2_saved_kg"].cumsum()
    fig.add_trace(go.Scatter(
        x=df_hourly["hour"],
        y=cum_co2,
        mode="lines+markers",
        name="Cumulative CO2 Saved (kg)",
        line=dict(color="#4EBA86", width=2.4),
        fill="tozeroy",
        fillcolor="rgba(78, 186, 134, 0.12)",
        hovertemplate="Hour %{x}: %{y:.1f} kg CO2<extra></extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="6. Cumulative Carbon Emissions Mitigated (kg CO2)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Hour of Day", dtick=2, gridcolor="#24333D"),
        yaxis=dict(title="CO2 Saved (kg)", gridcolor="#24333D"),
        height=330,
    )
    fig.update_layout(**layout)
    return fig


# ==============================================================================
# STAGE 6 FAIR COMPARISON CHARTS
# ==============================================================================

def plot_comparison_waiting_time(time_series: Dict[str, List[Any]]) -> go.Figure:
    """Renders side-by-side progression of vehicle waiting time."""
    fig = go.Figure()
    times = time_series.get("time", [])

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("trad_avg_wait", []),
        mode="lines",
        name="Traditional (Fixed)",
        line=dict(color="#E05D5D", width=2.2, dash="dash"),
        hovertemplate="Time: %{x}s<br>Wait: %{y:.1f}s<extra>Traditional</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("ai_avg_wait", []),
        mode="lines",
        name="AI-Optimized",
        line=dict(color="#8BAE9B", width=2.6),
        hovertemplate="Time: %{x}s<br>Wait: %{y:.1f}s<extra>AI-Optimized</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="1. Average Vehicle Waiting Time Evolution", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Elapsed Simulation (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Waiting Time (sec/veh)", gridcolor="#24333D"),
        hovermode="x unified",
        height=310,
    )
    fig.update_layout(**layout)
    return fig


def plot_comparison_queue_length(time_series: Dict[str, List[Any]]) -> go.Figure:
    """Renders total intersection queue backlog comparison."""
    fig = go.Figure()
    times = time_series.get("time", [])

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("trad_total_queue", []),
        mode="lines",
        name="Traditional Queue",
        line=dict(color="#E05D5D", width=2.0),
        fill="tozeroy",
        fillcolor="rgba(224, 93, 93, 0.08)",
        hovertemplate="Time: %{x}s<br>Queue: %{y} veh<extra>Traditional</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("ai_total_queue", []),
        mode="lines",
        name="AI-Optimized Queue",
        line=dict(color="#C6A76A", width=2.4),
        fill="tozeroy",
        fillcolor="rgba(198, 167, 106, 0.12)",
        hovertemplate="Time: %{x}s<br>Queue: %{y} veh<extra>AI-Optimized</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="2. Total Intersection Queue Backlog (Vehicles)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Elapsed Simulation (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Total Standing Queue (veh)", gridcolor="#24333D"),
        hovermode="x unified",
        height=310,
    )
    fig.update_layout(**layout)
    return fig


def plot_comparison_throughput(time_series: Dict[str, List[Any]]) -> go.Figure:
    """Renders cumulative vehicles cleared over simulation duration."""
    fig = go.Figure()
    times = time_series.get("time", [])

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("trad_cum_throughput", []),
        mode="lines",
        name="Traditional Cleared",
        line=dict(color="#7D8C99", width=2.0, dash="dot"),
        hovertemplate="Time: %{x}s<br>Processed: %{y} veh<extra>Traditional</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("ai_cum_throughput", []),
        mode="lines",
        name="AI-Optimized Cleared",
        line=dict(color="#4EBA86", width=2.5),
        hovertemplate="Time: %{x}s<br>Processed: %{y} veh<extra>AI-Optimized</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="3. Cumulative Vehicles Processed (Throughput)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Elapsed Simulation (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Cumulative Departures (veh)", gridcolor="#24333D"),
        hovermode="x unified",
        height=310,
    )
    fig.update_layout(**layout)
    return fig


def plot_comparison_utilization(time_series: Dict[str, List[Any]]) -> go.Figure:
    """Renders active signal utilization efficiency over time."""
    fig = go.Figure()
    times = time_series.get("time", [])

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("trad_utilization", []),
        mode="lines",
        name="Traditional Utilization",
        line=dict(color="#E05D5D", width=2.0),
        hovertemplate="Time: %{x}s<br>Util: %{y:.1f}%<extra>Traditional</extra>",
    ))

    fig.add_trace(go.Scatter(
        x=times,
        y=time_series.get("ai_utilization", []),
        mode="lines",
        name="AI-Optimized Utilization",
        line=dict(color="#8BAE9B", width=2.5),
        hovertemplate="Time: %{x}s<br>Util: %{y:.1f}%<extra>AI-Optimized</extra>",
    ))

    layout = THEME_LAYOUT.copy()
    layout.update(
        title=dict(text="4. Signal Efficiency & Green Utilization (%)", font=dict(size=13, color="#F1F0EB")),
        xaxis=dict(title="Elapsed Simulation (seconds)", gridcolor="#24333D"),
        yaxis=dict(title="Active Green Utilization (%)", range=[0, 105], gridcolor="#24333D"),
        hovermode="x unified",
        height=310,
    )
    fig.update_layout(**layout)
    return fig
