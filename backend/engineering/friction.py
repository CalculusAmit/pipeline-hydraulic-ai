"""Darcy friction-factor calculations for circular-pipe flow."""

from __future__ import annotations

from math import log10, sqrt

from .models import FlowRegime, FrictionFactorMethod

LAMINAR_LIMIT = 2_300.0
TURBULENT_LIMIT = 4_000.0


def flow_regime(reynolds_number: float) -> FlowRegime:
    """Classify flow using conventional Reynolds-number limits."""

    if reynolds_number <= 0:
        raise ValueError("reynolds_number must be greater than zero.")
    if reynolds_number <= LAMINAR_LIMIT:
        return FlowRegime.LAMINAR
    if reynolds_number < TURBULENT_LIMIT:
        return FlowRegime.TRANSITIONAL
    return FlowRegime.TURBULENT


def haaland_friction_factor(reynolds_number: float, relative_roughness: float) -> float:
    """Return Darcy friction factor using the explicit Haaland correlation."""

    if reynolds_number < TURBULENT_LIMIT:
        raise ValueError("Haaland correlation requires Reynolds number >= 4000.")
    if relative_roughness < 0:
        raise ValueError("relative_roughness cannot be negative.")

    denominator = -1.8 * log10(
        (relative_roughness / 3.7) ** 1.11 + 6.9 / reynolds_number
    )
    return 1.0 / denominator**2


def colebrook_friction_factor(
    reynolds_number: float,
    relative_roughness: float,
    tolerance: float = 1e-10,
    max_iterations: int = 100,
) -> float:
    """Solve the Colebrook-White equation by fixed-point iteration.

    The Haaland correlation supplies a reliable initial estimate. The result is a
    Darcy friction factor, not a Fanning friction factor.
    """

    if reynolds_number < TURBULENT_LIMIT:
        raise ValueError("Colebrook equation requires Reynolds number >= 4000.")
    if relative_roughness < 0:
        raise ValueError("relative_roughness cannot be negative.")
    if tolerance <= 0 or max_iterations <= 0:
        raise ValueError("tolerance and max_iterations must be greater than zero.")

    friction_factor = haaland_friction_factor(reynolds_number, relative_roughness)
    for _ in range(max_iterations):
        inverse_sqrt_factor = -2.0 * log10(
            relative_roughness / 3.7
            + 2.51 / (reynolds_number * sqrt(friction_factor))
        )
        next_factor = 1.0 / inverse_sqrt_factor**2
        if abs(next_factor - friction_factor) <= tolerance:
            return next_factor
        friction_factor = next_factor

    raise RuntimeError("Colebrook solver did not converge within max_iterations.")


def darcy_friction_factor(
    reynolds_number: float,
    relative_roughness: float,
    method: FrictionFactorMethod = FrictionFactorMethod.AUTO,
) -> float:
    """Return a Darcy friction factor across laminar, transition, and turbulent flow.

    Transitional flow does not have one universally reliable friction-factor
    correlation. The solver therefore linearly blends the laminar value at Re=2300
    with the selected turbulent correlation at Re=4000 and reports a warning.
    """

    if reynolds_number <= 0:
        raise ValueError("reynolds_number must be greater than zero.")
    if relative_roughness < 0:
        raise ValueError("relative_roughness cannot be negative.")

    regime = flow_regime(reynolds_number)
    if regime is FlowRegime.LAMINAR:
        return 64.0 / reynolds_number

    selected_method = (
        FrictionFactorMethod.HAALAND
        if method is FrictionFactorMethod.AUTO
        else method
    )

    def turbulent_factor(reynolds: float) -> float:
        if selected_method is FrictionFactorMethod.HAALAND:
            return haaland_friction_factor(reynolds, relative_roughness)
        if selected_method is FrictionFactorMethod.COLEBROOK:
            return colebrook_friction_factor(reynolds, relative_roughness)
        raise ValueError(f"Unsupported friction-factor method: {selected_method}")

    if regime is FlowRegime.TURBULENT:
        return turbulent_factor(reynolds_number)

    laminar_at_limit = 64.0 / LAMINAR_LIMIT
    turbulent_at_limit = turbulent_factor(TURBULENT_LIMIT)
    blend = (reynolds_number - LAMINAR_LIMIT) / (TURBULENT_LIMIT - LAMINAR_LIMIT)
    return laminar_at_limit + blend * (turbulent_at_limit - laminar_at_limit)
