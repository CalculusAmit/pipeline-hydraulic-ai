# AI-Assisted Pipeline Hydraulic Analysis

Final-year Mechanical Engineering project for hydraulic analysis, pump sizing,
energy estimation, and economic pipe-diameter optimization.

## Current milestone: Phase 1

The current implementation is a validated single-pipe hydraulic calculation
engine. It uses SI units and calculates:

- flow area and velocity
- Reynolds number and flow regime
- Darcy friction factor
- major and minor head loss
- static elevation head and required pump head
- hydraulic power, pump input power, and operating energy

## Run the example

Activate the virtual environment, then run this command from the project root:

```powershell
python -m backend.demo
```

## Analyse your own pipeline

Run the interactive input form from the project root:

```powershell
python -m backend.cli
```

Enter values in the units printed beside each prompt. The interface accepts flow
rate in L/s, pipe diameter and roughness in mm, viscosity in mPa.s, and pump
efficiency as a percentage. It converts them to the SI units used by the solver.

## Simulate pressure along a multi-section pipeline

Run the section-based pressure-profile interface:

```powershell
python -m backend.profile_cli
```

Enter an inlet pressure and each section's geometry, elevation change, and
fitting-loss coefficient. The program prints pressure at the inlet and after
every section. This is the calculation module that will later supply the Plotly
pressure-profile chart in the web dashboard.

The first time you set up the project on another computer, install the pinned
chart dependency inside the activated virtual environment:

```powershell
python -m pip install -r requirements.txt
```

After each pressure-profile calculation, choose `Y` to save a self-contained
interactive chart at `reports/generated/pressure_profile.html`. Open that file
in a browser to inspect values by hovering over the graph.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The Phase 1 engine uses only the Python standard library. Third-party packages
will be added only when they are needed for the API, charts, optimization, and
dashboard phases.

## Unit convention

All Phase 1 inputs use SI units:

| Quantity | Unit |
| --- | --- |
| Flow rate | m^3/s |
| Pipe diameter, length, roughness | m |
| Density | kg/m^3 |
| Dynamic viscosity | Pa.s |
| Head | m |
| Power | W |
| Energy | kWh |

## Project roadmap

1. Validated hydraulic calculation engine
2. Section-based pressure-profile simulator
3. Pump curves, operating point, and pump selection
4. Energy/cost analysis and pipe-diameter optimization
5. FastAPI backend, SQLite storage, and React dashboard
6. PDF report, optional ML screening, final validation, and viva material
