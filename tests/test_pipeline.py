"""Tests for section-based pressure-profile calculations."""

import unittest

from backend.engineering import (
    FrictionFactorMethod,
    HydraulicInput,
    PipeSection,
    PipelineProfileInput,
    calculate_pressure_profile,
    solve_hydraulics,
)
from backend.profile_cli import build_profile_input


class PressureProfileTests(unittest.TestCase):
    def test_single_section_matches_single_pipe_pressure_balance(self) -> None:
        section = PipeSection(
            name="Rising main",
            length_m=100.0,
            diameter_m=0.100,
            absolute_roughness_m=0.000045,
            elevation_change_m=10.0,
            total_minor_loss_coefficient=2.0,
        )
        profile_input = PipelineProfileInput(
            flow_rate_m3_s=0.010,
            density_kg_m3=998.0,
            dynamic_viscosity_pa_s=0.001002,
            inlet_gauge_pressure_kpa=250.0,
            sections=(section,),
        )

        result = calculate_pressure_profile(profile_input)
        single_pipe = solve_hydraulics(
            HydraulicInput(
                flow_rate_m3_s=0.010,
                pipe_diameter_m=0.100,
                pipe_length_m=100.0,
                absolute_roughness_m=0.000045,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                elevation_change_m=10.0,
                total_minor_loss_coefficient=2.0,
            )
        )
        expected_outlet_pressure_kpa = 250.0 - (
            998.0 * 9.80665 * single_pipe.system_head_m / 1_000.0
        )

        self.assertEqual(len(result.points), 2)
        self.assertAlmostEqual(result.total_length_m, 100.0)
        self.assertAlmostEqual(result.total_elevation_change_m, 10.0)
        self.assertAlmostEqual(
            result.outlet_gauge_pressure_kpa, expected_outlet_pressure_kpa, places=8
        )

    def test_multiple_sections_accumulate_distance_and_elevation(self) -> None:
        result = calculate_pressure_profile(
            PipelineProfileInput(
                flow_rate_m3_s=0.005,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                inlet_gauge_pressure_kpa=300.0,
                sections=(
                    PipeSection("Section 1", 50.0, 0.080, 0.000045, 5.0, 1.0),
                    PipeSection("Section 2", 75.0, 0.100, 0.000045, -2.0, 2.0),
                ),
            )
        )

        self.assertEqual(len(result.points), 3)
        self.assertAlmostEqual(result.points[-1].distance_m, 125.0)
        self.assertAlmostEqual(result.points[-1].elevation_m, 3.0)
        self.assertGreater(result.total_friction_head_loss_m, 0.0)

    def test_profile_cli_unit_conversion(self) -> None:
        profile_input = build_profile_input(
            flow_rate_l_s=10.0,
            density_kg_m3=998.0,
            dynamic_viscosity_mpa_s=1.002,
            inlet_gauge_pressure_kpa=250.0,
            sections=(PipeSection("Section 1", 10.0, 0.100, 0.000045),),
            friction_factor_method=FrictionFactorMethod.AUTO,
        )

        self.assertAlmostEqual(profile_input.flow_rate_m3_s, 0.010)
        self.assertAlmostEqual(profile_input.dynamic_viscosity_pa_s, 0.001002)

    def test_rejects_profile_without_sections(self) -> None:
        with self.assertRaises(ValueError):
            PipelineProfileInput(
                flow_rate_m3_s=0.010,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                inlet_gauge_pressure_kpa=250.0,
                sections=(),
            )


if __name__ == "__main__":
    unittest.main()
