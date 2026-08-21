"""Tests for engineering chart generation."""

import tempfile
import unittest
from pathlib import Path

from backend.charts import build_pressure_profile_figure, write_pressure_profile_html
from backend.engineering import (
    PipeSection,
    PipelineProfileInput,
    calculate_pressure_profile,
)


class PressureProfileChartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = calculate_pressure_profile(
            PipelineProfileInput(
                flow_rate_m3_s=0.010,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                inlet_gauge_pressure_kpa=250.0,
                sections=(
                    PipeSection("Section 1", 50.0, 0.100, 0.000045, 5.0, 1.0),
                    PipeSection("Section 2", 50.0, 0.100, 0.000045, -2.0, 2.0),
                ),
            )
        )

    def test_chart_contains_expected_engineering_series(self) -> None:
        figure = build_pressure_profile_figure(self.profile)

        self.assertEqual(len(figure.data), 4)
        self.assertEqual(
            [trace.name for trace in figure.data],
            [
                "Pipeline elevation",
                "Hydraulic grade line",
                "Energy grade line",
                "Gauge pressure",
            ],
        )

    def test_writes_self_contained_html_chart(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = write_pressure_profile_html(
                self.profile, Path(temporary_directory) / "pressure_profile.html"
            )

            self.assertTrue(output_path.is_file())
            chart_html = output_path.read_text(encoding="utf-8")
            self.assertIn("Pipeline Pressure and Energy Profile", chart_html)
            self.assertIn("plotly.js", chart_html)
