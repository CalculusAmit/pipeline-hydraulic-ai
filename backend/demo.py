"""Run a realistic Phase 1 water-pipeline example from the command line."""

from .cli import print_hydraulic_result
from .engineering import HydraulicInput, solve_hydraulics


def main() -> None:
    # Water pumped through 100 m of commercial-steel pipe to a tank 10 m higher.
    inputs = HydraulicInput(
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
    result = solve_hydraulics(inputs)

    print_hydraulic_result(result)


if __name__ == "__main__":
    main()
