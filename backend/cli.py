"""Interactive terminal interface for Phase 1 pipeline analysis."""

from __future__ import annotations

from math import isfinite

from .engineering import (
    FrictionFactorMethod,
    HydraulicInput,
    HydraulicResult,
    solve_hydraulics,
)


def build_hydraulic_input(
    *,
    flow_rate_l_s: float,
    pipe_diameter_mm: float,
    pipe_length_m: float,
    absolute_roughness_mm: float,
    density_kg_m3: float,
    dynamic_viscosity_mpa_s: float,
    elevation_change_m: float,
    total_minor_loss_coefficient: float,
    pump_efficiency_percent: float,
    operating_hours: float,
    friction_factor_method: FrictionFactorMethod,
) -> HydraulicInput:
    """Convert user-friendly engineering units into the solver's SI inputs."""

    return HydraulicInput(
        flow_rate_m3_s=flow_rate_l_s / 1_000.0,
        pipe_diameter_m=pipe_diameter_mm / 1_000.0,
        pipe_length_m=pipe_length_m,
        absolute_roughness_m=absolute_roughness_mm / 1_000.0,
        density_kg_m3=density_kg_m3,
        dynamic_viscosity_pa_s=dynamic_viscosity_mpa_s / 1_000.0,
        elevation_change_m=elevation_change_m,
        total_minor_loss_coefficient=total_minor_loss_coefficient,
        pump_efficiency=pump_efficiency_percent / 100.0,
        operating_hours=operating_hours,
        friction_factor_method=friction_factor_method,
    )


def _prompt_number(
    label: str,
    unit: str,
    *,
    default: float | None = None,
    minimum: float | None = None,
    strictly_greater: bool = False,
) -> float:
    """Read one finite numeric value, keeping the prompt open until it is valid."""

    default_text = f" [{default}]" if default is not None else ""
    while True:
        raw_value = input(f"{label} ({unit}){default_text}: ").strip()
        if not raw_value and default is not None:
            return default

        try:
            value = float(raw_value)
        except ValueError:
            print("Please enter a valid number, for example: 10 or 0.045")
            continue

        if not isfinite(value):
            print("Please enter a finite number.")
            continue
        if minimum is not None:
            valid = value > minimum if strictly_greater else value >= minimum
            if not valid:
                operator = ">" if strictly_greater else ">="
                print(f"Value must be {operator} {minimum}.")
                continue
        return value


def _prompt_friction_factor_method() -> FrictionFactorMethod:
    """Read one supported friction-factor method."""

    options = {
        "auto": FrictionFactorMethod.AUTO,
        "haaland": FrictionFactorMethod.HAALAND,
        "colebrook": FrictionFactorMethod.COLEBROOK,
    }
    while True:
        selected = input(
            "Friction-factor method [auto/haaland/colebrook] [auto]: "
        ).strip().lower()
        if not selected:
            return FrictionFactorMethod.AUTO
        if selected in options:
            return options[selected]
        print("Choose auto, haaland, or colebrook.")


def collect_hydraulic_input() -> HydraulicInput:
    """Collect pipeline data in user-friendly units for the Phase 1 solver."""

    print("\nEnter pipeline data. Press Enter to use a value shown in [brackets].")
    return build_hydraulic_input(
        flow_rate_l_s=_prompt_number(
            "Required flow rate", "L/s", minimum=0.0, strictly_greater=True
        ),
        pipe_diameter_mm=_prompt_number(
            "Internal pipe diameter", "mm", minimum=0.0, strictly_greater=True
        ),
        pipe_length_m=_prompt_number("Pipe length", "m", minimum=0.0),
        absolute_roughness_mm=_prompt_number(
            "Absolute roughness", "mm", default=0.045, minimum=0.0
        ),
        density_kg_m3=_prompt_number(
            "Fluid density", "kg/m^3", default=998.0, minimum=0.0, strictly_greater=True
        ),
        dynamic_viscosity_mpa_s=_prompt_number(
            "Dynamic viscosity", "mPa.s", default=1.002, minimum=0.0, strictly_greater=True
        ),
        elevation_change_m=_prompt_number(
            "Outlet elevation minus inlet elevation", "m", default=0.0
        ),
        total_minor_loss_coefficient=_prompt_number(
            "Total fitting-loss coefficient, sum(K)", "-", default=0.0, minimum=0.0
        ),
        pump_efficiency_percent=_prompt_number(
            "Pump efficiency", "%", default=70.0, minimum=0.0, strictly_greater=True
        ),
        operating_hours=_prompt_number(
            "Operating time for energy calculation", "h", default=24.0, minimum=0.0
        ),
        friction_factor_method=_prompt_friction_factor_method(),
    )


def print_hydraulic_result(result: HydraulicResult) -> None:
    """Display hydraulic results in a readable engineering summary."""

    print("\nHydraulic Analysis Result")
    print("=" * 46)
    print(f"Velocity:                 {result.velocity_m_s:.3f} m/s")
    print(f"Reynolds number:          {result.reynolds_number:,.0f}")
    print(f"Flow regime:              {result.flow_regime.value}")
    print(f"Darcy friction factor:    {result.friction_factor_darcy:.5f}")
    print(f"Major head loss:          {result.major_head_loss_m:.3f} m")
    print(f"Minor head loss:          {result.minor_head_loss_m:.3f} m")
    print(f"Total friction loss:      {result.total_friction_head_loss_m:.3f} m")
    print(f"System head:              {result.system_head_m:.3f} m")
    print(f"Required pump head:       {result.required_pump_head_m:.3f} m")
    print(f"Friction pressure drop:   {result.friction_pressure_drop_pa / 1_000:.3f} kPa")
    print(f"Hydraulic power:          {result.hydraulic_power_w / 1_000:.3f} kW")
    print(f"Pump input power:         {result.pump_input_power_w / 1_000:.3f} kW")
    print(f"Operating energy:         {result.operating_energy_kwh:.3f} kWh")

    if result.warnings:
        print("\nWarnings")
        for warning in result.warnings:
            print(f"- {warning}")


def main() -> None:
    """Run interactive calculations until the user chooses to stop."""

    print("AI-Assisted Pipeline Hydraulic Analysis - Phase 1")
    while True:
        try:
            hydraulic_input = collect_hydraulic_input()
            print_hydraulic_result(solve_hydraulics(hydraulic_input))
        except ValueError as error:
            print(f"\nInput error: {error}")
            print("Please start this analysis again with valid values.\n")

        another_run = input("\nAnalyse another pipeline? [y/N]: ").strip().lower()
        if another_run not in {"y", "yes"}:
            print("Analysis finished.")
            return


if __name__ == "__main__":
    main()
