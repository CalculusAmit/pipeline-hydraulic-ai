"""Unit tests for the single-pipe hydraulic solver."""

import unittest
from math import pi

from backend.cli import build_hydraulic_input
from backend.engineering import FrictionFactorMethod, HydraulicInput, solve_hydraulics


class HydraulicSolverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_input = HydraulicInput(
            flow_rate_m3_s=0.010,
            pipe_diameter_m=0.100,
            pipe_length_m=100.0,
            absolute_roughness_m=0.000045,
            density_kg_m3=998.0,
            dynamic_viscosity_pa_s=0.001002,
            elevation_change_m=10.0,
            total_minor_loss_coefficient=2.0,
            pump_efficiency=0.70,
            operating_hours=24.0,
        )

    def test_calculates_expected_core_quantities(self) -> None:
        result = solve_hydraulics(self.sample_input)

        self.assertAlmostEqual(result.cross_sectional_area_m2, 0.007854, places=5)
        self.assertAlmostEqual(result.velocity_m_s, 1.273, places=3)
        self.assertGreater(result.reynolds_number, 100_000)
        self.assertGreater(result.major_head_loss_m, 0)
        self.assertGreater(result.minor_head_loss_m, 0)
        self.assertGreater(result.required_pump_head_m, 10.0)
        self.assertGreater(result.pump_input_power_w, result.hydraulic_power_w)
        self.assertGreater(result.operating_energy_kwh, 0)

    def test_downhill_system_requires_no_pump_head(self) -> None:
        result = solve_hydraulics(
            HydraulicInput(
                flow_rate_m3_s=0.010,
                pipe_diameter_m=0.100,
                pipe_length_m=0.0,
                absolute_roughness_m=0.0,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                elevation_change_m=-10.0,
            )
        )

        self.assertEqual(result.required_pump_head_m, 0.0)
        self.assertEqual(result.pump_input_power_w, 0.0)
        self.assertTrue(result.warnings)

    def test_laminar_pressure_drop_matches_hagen_poiseuille(self) -> None:
        """Independently validate Darcy-Weisbach against laminar-flow theory."""
        flow_rate_m3_s = 1e-5
        pipe_diameter_m = 0.010
        pipe_length_m = 10.0
        dynamic_viscosity_pa_s = 0.001
        result = solve_hydraulics(
            HydraulicInput(
                flow_rate_m3_s=flow_rate_m3_s,
                pipe_diameter_m=pipe_diameter_m,
                pipe_length_m=pipe_length_m,
                absolute_roughness_m=0.0,
                density_kg_m3=1_000.0,
                dynamic_viscosity_pa_s=dynamic_viscosity_pa_s,
            )
        )

        # Hagen-Poiseuille: delta_p = 128 * mu * L * Q / (pi * D^4)
        expected_pressure_drop_pa = (
            128.0
            * dynamic_viscosity_pa_s
            * pipe_length_m
            * flow_rate_m3_s
            / (pi * pipe_diameter_m**4)
        )

        self.assertLess(result.reynolds_number, 2_300.0)
        self.assertAlmostEqual(
            result.friction_pressure_drop_pa, expected_pressure_drop_pa, places=8
        )

    def test_rejects_invalid_pump_efficiency(self) -> None:
        with self.assertRaises(ValueError):
            HydraulicInput(
                flow_rate_m3_s=0.010,
                pipe_diameter_m=0.100,
                pipe_length_m=100.0,
                absolute_roughness_m=0.000045,
                density_kg_m3=998.0,
                dynamic_viscosity_pa_s=0.001002,
                pump_efficiency=1.1,
            )

    def test_converts_user_friendly_units_to_solver_units(self) -> None:
        user_input = build_hydraulic_input(
            flow_rate_l_s=10.0,
            pipe_diameter_mm=100.0,
            pipe_length_m=100.0,
            absolute_roughness_mm=0.045,
            density_kg_m3=998.0,
            dynamic_viscosity_mpa_s=1.002,
            elevation_change_m=10.0,
            total_minor_loss_coefficient=2.0,
            pump_efficiency_percent=70.0,
            operating_hours=24.0,
            friction_factor_method=FrictionFactorMethod.AUTO,
        )

        self.assertAlmostEqual(user_input.flow_rate_m3_s, 0.010)
        self.assertAlmostEqual(user_input.pipe_diameter_m, 0.100)
        self.assertAlmostEqual(user_input.absolute_roughness_m, 0.000045)
        self.assertAlmostEqual(user_input.dynamic_viscosity_pa_s, 0.001002)
        self.assertAlmostEqual(user_input.pump_efficiency, 0.70)


if __name__ == "__main__":
    unittest.main()
