"""Section-based pipeline modelling and pressure-profile calculations."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, pi

from .models import FrictionFactorMethod, HydraulicInput
from .solver import GRAVITY_M_S2, solve_hydraulics


def _require_finite(name: str, value: float) -> None:
    if not isfinite(value):
        raise ValueError(f"{name} must be a finite number.")


def _require_positive(name: str, value: float) -> None:
    _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def _require_non_negative(name: str, value: float) -> None:
    _require_finite(name, value)
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


@dataclass(frozen=True)
class PipeSection:
    """One constant-diameter pipe segment in a pipeline route.

    `elevation_change_m` is the outlet elevation minus the inlet elevation of
    this section. Positive values represent uphill flow.
    """

    name: str
    length_m: float
    diameter_m: float
    absolute_roughness_m: float
    elevation_change_m: float = 0.0
    total_minor_loss_coefficient: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Section name cannot be blank.")
        _require_non_negative("length_m", self.length_m)
        _require_positive("diameter_m", self.diameter_m)
        _require_non_negative("absolute_roughness_m", self.absolute_roughness_m)
        _require_finite("elevation_change_m", self.elevation_change_m)
        _require_non_negative(
            "total_minor_loss_coefficient", self.total_minor_loss_coefficient
        )


@dataclass(frozen=True)
class PipelineProfileInput:
    """Fluid, inlet condition, and pipe sections for a pressure-profile analysis."""

    flow_rate_m3_s: float
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    inlet_gauge_pressure_kpa: float
    sections: tuple[PipeSection, ...]
    friction_factor_method: FrictionFactorMethod = FrictionFactorMethod.AUTO

    def __post_init__(self) -> None:
        _require_positive("flow_rate_m3_s", self.flow_rate_m3_s)
        _require_positive("density_kg_m3", self.density_kg_m3)
        _require_positive("dynamic_viscosity_pa_s", self.dynamic_viscosity_pa_s)
        _require_finite("inlet_gauge_pressure_kpa", self.inlet_gauge_pressure_kpa)
        if not self.sections:
            raise ValueError("At least one pipe section is required.")
        if not all(isinstance(section, PipeSection) for section in self.sections):
            raise ValueError("sections must contain only PipeSection values.")
        if not isinstance(self.friction_factor_method, FrictionFactorMethod):
            raise ValueError(
                "friction_factor_method must be a FrictionFactorMethod value."
            )


@dataclass(frozen=True)
class PressureProfilePoint:
    """Hydraulic state at the inlet or outlet of one pipeline section."""

    location: str
    distance_m: float
    elevation_m: float
    velocity_m_s: float
    pressure_head_m: float
    gauge_pressure_kpa: float
    total_energy_head_m: float
    cumulative_friction_loss_m: float


@dataclass(frozen=True)
class PressureProfileResult:
    """All points and summary values from a section-based pressure simulation."""

    points: tuple[PressureProfilePoint, ...]
    total_length_m: float
    total_elevation_change_m: float
    total_friction_head_loss_m: float
    outlet_gauge_pressure_kpa: float
    warnings: tuple[str, ...]


def _velocity_head_m(flow_rate_m3_s: float, diameter_m: float) -> tuple[float, float]:
    """Return average velocity and velocity head for a circular pipe."""

    area_m2 = pi * diameter_m**2 / 4.0
    velocity_m_s = flow_rate_m3_s / area_m2
    return velocity_m_s, velocity_m_s**2 / (2.0 * GRAVITY_M_S2)


def calculate_pressure_profile(inputs: PipelineProfileInput) -> PressureProfileResult:
    """Calculate gauge pressure at the inlet and after every pipe section.

    The calculation applies the energy equation using an inlet gauge pressure and
    a reference inlet elevation of zero. Pipe-friction losses reduce total energy;
    elevation and velocity-head changes determine the resulting local pressure.
    Sudden diameter-change losses must be supplied by the user through a section's
    total minor-loss coefficient.
    """

    first_velocity_m_s, first_velocity_head_m = _velocity_head_m(
        inputs.flow_rate_m3_s, inputs.sections[0].diameter_m
    )
    inlet_pressure_head_m = (
        inputs.inlet_gauge_pressure_kpa * 1_000.0
        / (inputs.density_kg_m3 * GRAVITY_M_S2)
    )
    total_energy_head_m = inlet_pressure_head_m + first_velocity_head_m

    points = [
        PressureProfilePoint(
            location="Inlet",
            distance_m=0.0,
            elevation_m=0.0,
            velocity_m_s=first_velocity_m_s,
            pressure_head_m=inlet_pressure_head_m,
            gauge_pressure_kpa=inputs.inlet_gauge_pressure_kpa,
            total_energy_head_m=total_energy_head_m,
            cumulative_friction_loss_m=0.0,
        )
    ]
    warnings: list[str] = []
    distance_m = 0.0
    elevation_m = 0.0
    cumulative_friction_loss_m = 0.0

    for section in inputs.sections:
        section_result = solve_hydraulics(
            HydraulicInput(
                flow_rate_m3_s=inputs.flow_rate_m3_s,
                pipe_diameter_m=section.diameter_m,
                pipe_length_m=section.length_m,
                absolute_roughness_m=section.absolute_roughness_m,
                density_kg_m3=inputs.density_kg_m3,
                dynamic_viscosity_pa_s=inputs.dynamic_viscosity_pa_s,
                total_minor_loss_coefficient=section.total_minor_loss_coefficient,
                friction_factor_method=inputs.friction_factor_method,
            )
        )
        total_energy_head_m -= section_result.total_friction_head_loss_m
        distance_m += section.length_m
        elevation_m += section.elevation_change_m
        cumulative_friction_loss_m += section_result.total_friction_head_loss_m
        velocity_m_s, velocity_head_m = _velocity_head_m(
            inputs.flow_rate_m3_s, section.diameter_m
        )
        pressure_head_m = total_energy_head_m - elevation_m - velocity_head_m
        gauge_pressure_kpa = (
            pressure_head_m * inputs.density_kg_m3 * GRAVITY_M_S2 / 1_000.0
        )

        if section_result.warnings:
            for warning in section_result.warnings:
                warnings.append(f"{section.name}: {warning}")
        if gauge_pressure_kpa < 0:
            warnings.append(
                f"{section.name}: calculated gauge pressure is negative "
                f"({gauge_pressure_kpa:.2f} kPa). Check inlet pressure and NPSH."
            )

        points.append(
            PressureProfilePoint(
                location=f"After {section.name}",
                distance_m=distance_m,
                elevation_m=elevation_m,
                velocity_m_s=velocity_m_s,
                pressure_head_m=pressure_head_m,
                gauge_pressure_kpa=gauge_pressure_kpa,
                total_energy_head_m=total_energy_head_m,
                cumulative_friction_loss_m=cumulative_friction_loss_m,
            )
        )

    return PressureProfileResult(
        points=tuple(points),
        total_length_m=distance_m,
        total_elevation_change_m=elevation_m,
        total_friction_head_loss_m=cumulative_friction_loss_m,
        outlet_gauge_pressure_kpa=points[-1].gauge_pressure_kpa,
        warnings=tuple(warnings),
    )
