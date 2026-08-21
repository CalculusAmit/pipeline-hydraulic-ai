"""Data models and validation for single-pipe hydraulic calculations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite


class FlowRegime(str, Enum):
    """Flow classification based on Reynolds number."""

    LAMINAR = "laminar"
    TRANSITIONAL = "transitional"
    TURBULENT = "turbulent"


class FrictionFactorMethod(str, Enum):
    """Supported Darcy friction-factor methods for turbulent flow."""

    AUTO = "auto"
    HAALAND = "haaland"
    COLEBROOK = "colebrook"


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
class HydraulicInput:
    """Inputs for steady incompressible flow through one circular pipe.

    The elevation difference is outlet elevation minus inlet elevation. A positive
    value represents a rising pipeline and therefore increases required pump head.
    All inputs use SI units.
    """

    flow_rate_m3_s: float
    pipe_diameter_m: float
    pipe_length_m: float
    absolute_roughness_m: float
    density_kg_m3: float
    dynamic_viscosity_pa_s: float
    elevation_change_m: float = 0.0
    total_minor_loss_coefficient: float = 0.0
    pump_efficiency: float = 0.70
    operating_hours: float = 0.0
    friction_factor_method: FrictionFactorMethod = FrictionFactorMethod.AUTO

    def __post_init__(self) -> None:
        _require_positive("flow_rate_m3_s", self.flow_rate_m3_s)
        _require_positive("pipe_diameter_m", self.pipe_diameter_m)
        _require_non_negative("pipe_length_m", self.pipe_length_m)
        _require_non_negative("absolute_roughness_m", self.absolute_roughness_m)
        _require_positive("density_kg_m3", self.density_kg_m3)
        _require_positive("dynamic_viscosity_pa_s", self.dynamic_viscosity_pa_s)
        _require_finite("elevation_change_m", self.elevation_change_m)
        _require_non_negative(
            "total_minor_loss_coefficient", self.total_minor_loss_coefficient
        )
        _require_non_negative("operating_hours", self.operating_hours)
        _require_finite("pump_efficiency", self.pump_efficiency)

        if not 0 < self.pump_efficiency <= 1:
            raise ValueError("pump_efficiency must be greater than 0 and at most 1.")

        if not isinstance(self.friction_factor_method, FrictionFactorMethod):
            raise ValueError(
                "friction_factor_method must be a FrictionFactorMethod value."
            )


@dataclass(frozen=True)
class HydraulicResult:
    """Results produced by the single-pipe steady-flow hydraulic solver."""

    cross_sectional_area_m2: float
    velocity_m_s: float
    reynolds_number: float
    flow_regime: FlowRegime
    relative_roughness: float
    friction_factor_darcy: float
    major_head_loss_m: float
    minor_head_loss_m: float
    total_friction_head_loss_m: float
    static_head_m: float
    system_head_m: float
    required_pump_head_m: float
    friction_pressure_drop_pa: float
    hydraulic_power_w: float
    pump_input_power_w: float
    operating_energy_kwh: float
    warnings: tuple[str, ...]
