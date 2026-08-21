"""Interactive Plotly charts generated from validated engineering results."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .engineering.pipeline import PressureProfileResult


def build_pressure_profile_figure(profile: PressureProfileResult) -> go.Figure:
    """Create a pressure, elevation, and energy-head chart for one pipeline route.

    The left axis shows engineering heads in metres. The right axis shows gauge
    pressure in kPa. Both hydraulic grade line and energy grade line are shown
    because they are useful for checking how friction and elevation affect the
    available pressure along the route.
    """

    distance_m = [point.distance_m for point in profile.points]
    elevation_m = [point.elevation_m for point in profile.points]
    hydraulic_grade_line_m = [
        point.elevation_m + point.pressure_head_m for point in profile.points
    ]
    energy_grade_line_m = [point.total_energy_head_m for point in profile.points]
    gauge_pressure_kpa = [point.gauge_pressure_kpa for point in profile.points]
    locations = [point.location for point in profile.points]

    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(
        go.Scatter(
            x=distance_m,
            y=elevation_m,
            name="Pipeline elevation",
            mode="lines+markers",
            line={"color": "#6B7280", "width": 3},
            marker={"symbol": "square", "size": 8},
            customdata=locations,
            hovertemplate=(
                "%{customdata}<br>Distance: %{x:.2f} m<br>"
                "Elevation: %{y:.2f} m<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=distance_m,
            y=hydraulic_grade_line_m,
            name="Hydraulic grade line",
            mode="lines+markers",
            line={"color": "#2563EB", "width": 3},
            marker={"size": 8},
            customdata=locations,
            hovertemplate=(
                "%{customdata}<br>Distance: %{x:.2f} m<br>"
                "Hydraulic grade: %{y:.2f} m<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=distance_m,
            y=energy_grade_line_m,
            name="Energy grade line",
            mode="lines+markers",
            line={"color": "#059669", "width": 3, "dash": "dash"},
            marker={"symbol": "diamond", "size": 8},
            customdata=locations,
            hovertemplate=(
                "%{customdata}<br>Distance: %{x:.2f} m<br>"
                "Energy grade: %{y:.2f} m<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=distance_m,
            y=gauge_pressure_kpa,
            name="Gauge pressure",
            mode="lines+markers",
            line={"color": "#DC2626", "width": 2, "dash": "dot"},
            marker={"symbol": "circle", "size": 7},
            customdata=locations,
            hovertemplate=(
                "%{customdata}<br>Distance: %{x:.2f} m<br>"
                "Gauge pressure: %{y:.2f} kPa<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    figure.update_layout(
        title="Pipeline Pressure and Energy Profile",
        template="plotly_white",
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        margin={"l": 70, "r": 70, "t": 100, "b": 70},
    )
    figure.update_xaxes(title_text="Pipeline distance (m)", showgrid=True, gridcolor="#E5E7EB")
    figure.update_yaxes(
        title_text="Elevation and energy head (m)",
        showgrid=True,
        gridcolor="#E5E7EB",
        secondary_y=False,
    )
    figure.update_yaxes(title_text="Gauge pressure (kPa)", secondary_y=True)
    return figure


def write_pressure_profile_html(
    profile: PressureProfileResult, output_path: Path
) -> Path:
    """Write a self-contained interactive pressure-profile chart to an HTML file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure = build_pressure_profile_figure(profile)
    figure.write_html(
        output_path,
        include_plotlyjs=True,
        full_html=True,
        config={"displaylogo": False, "responsive": True},
    )
    return output_path.resolve()
