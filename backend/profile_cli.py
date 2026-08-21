"""Interactive terminal interface for multi-section pressure-profile analysis."""

from __future__ import annotations

from pathlib import Path

from .charts import write_pressure_profile_html
from .cli import _prompt_friction_factor_method, _prompt_number
from .engineering.models import FrictionFactorMethod
from .engineering.pipeline import (
    PipeSection,
    PipelineProfileInput,
    PressureProfileResult,
    calculate_pressure_profile,
)


def build_profile_input(
    *,
    flow_rate_l_s: float,
    density_kg_m3: float,
    dynamic_viscosity_mpa_s: float,
    inlet_gauge_pressure_kpa: float,
    sections: tuple[PipeSection, ...],
    friction_factor_method: FrictionFactorMethod,
) -> PipelineProfileInput:
    """Convert interactive-form units to SI values for a profile calculation."""

    return PipelineProfileInput(
        flow_rate_m3_s=flow_rate_l_s / 1_000.0,
        density_kg_m3=density_kg_m3,
        dynamic_viscosity_pa_s=dynamic_viscosity_mpa_s / 1_000.0,
        inlet_gauge_pressure_kpa=inlet_gauge_pressure_kpa,
        sections=sections,
        friction_factor_method=friction_factor_method,
    )


def _prompt_section(number: int) -> PipeSection:
    default_name = f"Section {number}"
    name = input(f"Section name [{default_name}]: ").strip() or default_name
    print(f"Enter data for {name}.")
    return PipeSection(
        name=name,
        length_m=_prompt_number("  Length", "m", minimum=0.0),
        diameter_m=(
            _prompt_number("  Internal diameter", "mm", minimum=0.0, strictly_greater=True)
            / 1_000.0
        ),
        absolute_roughness_m=(
            _prompt_number("  Absolute roughness", "mm", default=0.045, minimum=0.0)
            / 1_000.0
        ),
        elevation_change_m=_prompt_number(
            "  Outlet elevation minus inlet elevation", "m", default=0.0
        ),
        total_minor_loss_coefficient=_prompt_number(
            "  Total fitting-loss coefficient, sum(K)", "-", default=0.0, minimum=0.0
        ),
    )


def _prompt_section_count() -> int:
    """Read a positive whole number of pipeline sections."""

    while True:
        count = _prompt_number(
            "Number of pipe sections", "-", default=2.0, minimum=1.0
        )
        if count.is_integer():
            return int(count)
        print("Number of pipe sections must be a whole number.")


def collect_profile_input() -> PipelineProfileInput:
    """Collect fluid data, inlet pressure, and multiple pipe sections."""

    print("\nEnter data for the pressure-profile simulator.")
    flow_rate_l_s = _prompt_number(
        "Required flow rate", "L/s", minimum=0.0, strictly_greater=True
    )
    density_kg_m3 = _prompt_number(
        "Fluid density", "kg/m^3", default=998.0, minimum=0.0, strictly_greater=True
    )
    dynamic_viscosity_mpa_s = _prompt_number(
        "Dynamic viscosity", "mPa.s", default=1.002, minimum=0.0, strictly_greater=True
    )
    inlet_gauge_pressure_kpa = _prompt_number(
        "Inlet gauge pressure", "kPa", default=250.0
    )
    number_of_sections = _prompt_section_count()

    sections = tuple(_prompt_section(number) for number in range(1, number_of_sections + 1))
    return build_profile_input(
        flow_rate_l_s=flow_rate_l_s,
        density_kg_m3=density_kg_m3,
        dynamic_viscosity_mpa_s=dynamic_viscosity_mpa_s,
        inlet_gauge_pressure_kpa=inlet_gauge_pressure_kpa,
        sections=sections,
        friction_factor_method=_prompt_friction_factor_method(),
    )


def print_pressure_profile(result: PressureProfileResult) -> None:
    """Print the calculated pressure profile as a station table."""

    print("\nPressure Profile")
    print("=" * 94)
    print(
        f"{'Location':<20}{'Distance (m)':>14}{'Elevation (m)':>16}"
        f"{'Velocity (m/s)':>17}{'Gauge P (kPa)':>17}"
    )
    print("-" * 94)
    for point in result.points:
        print(
            f"{point.location:<20}{point.distance_m:>14.2f}{point.elevation_m:>16.2f}"
            f"{point.velocity_m_s:>17.3f}{point.gauge_pressure_kpa:>17.3f}"
        )

    print("\nProfile summary")
    print(f"Total route length:       {result.total_length_m:.2f} m")
    print(f"Total elevation change:   {result.total_elevation_change_m:.2f} m")
    print(f"Total friction head loss: {result.total_friction_head_loss_m:.3f} m")
    print(f"Outlet gauge pressure:    {result.outlet_gauge_pressure_kpa:.3f} kPa")

    if result.warnings:
        print("\nWarnings")
        for warning in result.warnings:
            print(f"- {warning}")


def main() -> None:
    """Run interactive pressure-profile calculations until the user exits."""

    print("AI-Assisted Pipeline Hydraulic Analysis - Pressure Profile")
    while True:
        try:
            result = calculate_pressure_profile(collect_profile_input())
            print_pressure_profile(result)
            save_chart = input(
                "\nCreate an interactive pressure-profile chart? [Y/n]: "
            ).strip().lower()
            if save_chart not in {"n", "no"}:
                chart_path = write_pressure_profile_html(
                    result, Path("reports/generated/pressure_profile.html")
                )
                print(f"Interactive chart saved to: {chart_path}")
        except ValueError as error:
            print(f"\nInput error: {error}")

        another_run = input("\nAnalyse another pipeline? [y/N]: ").strip().lower()
        if another_run not in {"y", "yes"}:
            print("Analysis finished.")
            return


if __name__ == "__main__":
    main()
