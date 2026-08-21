"""Unit tests for Darcy friction-factor calculations."""

import unittest

from backend.engineering.friction import (
    colebrook_friction_factor,
    darcy_friction_factor,
    flow_regime,
    haaland_friction_factor,
)
from backend.engineering.models import FlowRegime, FrictionFactorMethod


class FlowRegimeTests(unittest.TestCase):
    def test_classifies_laminar_transition_and_turbulent_flow(self) -> None:
        self.assertEqual(flow_regime(1_000), FlowRegime.LAMINAR)
        self.assertEqual(flow_regime(3_000), FlowRegime.TRANSITIONAL)
        self.assertEqual(flow_regime(100_000), FlowRegime.TURBULENT)


class FrictionFactorTests(unittest.TestCase):
    def test_laminar_factor_matches_exact_relation(self) -> None:
        self.assertAlmostEqual(darcy_friction_factor(1_000, 0.0), 0.064)

    def test_haaland_matches_known_smooth_pipe_estimate(self) -> None:
        factor = haaland_friction_factor(100_000, 0.0)
        self.assertAlmostEqual(factor, 0.01782, places=4)

    def test_colebrook_matches_known_smooth_pipe_estimate(self) -> None:
        factor = colebrook_friction_factor(100_000, 0.0)
        self.assertAlmostEqual(factor, 0.01799, places=4)

    def test_auto_and_colebrook_are_reasonably_close(self) -> None:
        haaland = darcy_friction_factor(100_000, 0.00045)
        colebrook = darcy_friction_factor(
            100_000, 0.00045, FrictionFactorMethod.COLEBROOK
        )
        self.assertLess(abs(haaland - colebrook), 0.001)


if __name__ == "__main__":
    unittest.main()
