"""Single-pipe steady-state hydraulic solver based on Darcy-Weisbach losses."""

from __future__ import annotations

from math import pi

from .friction import darcy_friction_factor, flow_regime
from .models import FlowRegime, HydraulicInput, HydraulicResult

GRAVITY_M_S2 = 9.80665


def solve_hydraulics(inputs: HydraulicInput) -> HydraulicResult:
    """Calculate hydraulic performance for one constant-diameter pipe.

    The model assumes steady, incompressible, single-phase flow in a circular pipe.
    Total system head is the sum of static elevation head and friction losses.
    Required pump head cannot be negative; a negative system head is reported as a
    warning because gravity may be sufficient for the stated operating condition.
    """

    area_m2 = pi * inputs.pipe_diameter_m**2 / 4.0
    velocity_m_s = inputs.flow_rate_m3_s / area_m2
    reynolds_number = (
        inputs.density_kg_m3
        * velocity_m_s
        * inputs.pipe_diameter_m
        / inputs.dynamic_viscosity_pa_s
    )
    relative_roughness = inputs.absolute_roughness_m / inputs.pipe_diameter_m
    regime = flow_regime(reynolds_number)
    friction_factor = darcy_friction_factor(
        reynolds_number, relative_roughness, inputs.friction_factor_method
    )

    velocity_head_m = velocity_m_s**2 / (2.0 * GRAVITY_M_S2)
    major_head_loss_m = (
        friction_factor
        * (inputs.pipe_length_m / inputs.pipe_diameter_m)
        * velocity_head_m
    )
    minor_head_loss_m = inputs.total_minor_loss_coefficient * velocity_head_m
    total_friction_head_loss_m = major_head_loss_m + minor_head_loss_m
    system_head_m = inputs.elevation_change_m + total_friction_head_loss_m
    required_pump_head_m = max(system_head_m, 0.0)

    hydraulic_power_w = (
        inputs.density_kg_m3
        * GRAVITY_M_S2
        * inputs.flow_rate_m3_s
        * required_pump_head_m
    )
    pump_input_power_w = hydraulic_power_w / inputs.pump_efficiency
    operating_energy_kwh = pump_input_power_w * inputs.operating_hours / 1_000.0

    warnings: list[str] = []
    if regime is FlowRegime.TRANSITIONAL:
        warnings.append(
            "Flow is transitional (2300 < Re < 4000); the friction factor is an "
            "interpolated engineering estimate."
        )
    if system_head_m < 0:
        warnings.append(
            "System head is negative; gravity may provide the required head. "
            "Pump head and pump power are reported as zero."
        )

    return HydraulicResult(
        cross_sectional_area_m2=area_m2,
        velocity_m_s=velocity_m_s,
        reynolds_number=reynolds_number,
        flow_regime=regime,
        relative_roughness=relative_roughness,
        friction_factor_darcy=friction_factor,
        major_head_loss_m=major_head_loss_m,
        minor_head_loss_m=minor_head_loss_m,
        total_friction_head_loss_m=total_friction_head_loss_m,
        static_head_m=inputs.elevation_change_m,
        system_head_m=system_head_m,
        required_pump_head_m=required_pump_head_m,
        friction_pressure_drop_pa=(
            inputs.density_kg_m3 * GRAVITY_M_S2 * total_friction_head_loss_m
        ),
        hydraulic_power_w=hydraulic_power_w,
        pump_input_power_w=pump_input_power_w,
        operating_energy_kwh=operating_energy_kwh,
        warnings=tuple(warnings),
    )
