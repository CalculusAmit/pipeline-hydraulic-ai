# Phase 1 - Single-Pipe Hydraulic Calculation Engine

## Objective

Develop and validate a reusable Python solver for steady, incompressible,
single-phase flow in one circular pipe.

## Engineering model

The solver implements:

- cross-sectional area: `A = pi D^2 / 4`
- average velocity: `V = Q / A`
- Reynolds number: `Re = rho V D / mu`
- Darcy-Weisbach major loss: `h_f = f (L/D) (V^2/(2g))`
- minor loss: `h_m = sum(K) (V^2/(2g))`
- system head: `H_system = elevation_change + h_f + h_m`
- hydraulic power: `P_h = rho g Q H_pump`
- pump input power: `P_input = P_h / eta`

## Assumptions and limitations

- The fluid is incompressible and its density and viscosity are constant.
- Flow is steady and fully developed in a circular pipe.
- The pipe has one constant internal diameter and roughness value.
- Minor losses are represented by a user-provided total loss coefficient.
- The model does not yet perform cavitation/NPSH checks, transient analysis,
  pipe-network balancing, or real pump-curve operating-point calculations.
- Transitional-flow friction factors are an engineering interpolation and should
  be treated with care in the final analysis.

## User-entered data

The Phase 1 command-line interface accepts user-friendly units, converts them to
SI units, validates them, and sends only validated data to the calculation engine.
The future FastAPI and React interface will use the same `HydraulicInput` model;
the engineering calculations will not be copied into the user interface.

## Acceptance criteria

The Phase 1 milestone is complete when the demo runs, all automated tests pass,
and the calculation results are manually checked against at least one published
engineering reference or worked example.

## Independent validation case: laminar flow

For fully developed laminar flow in a circular pipe, Darcy-Weisbach with
`f = 64 / Re` is algebraically equivalent to the independent Hagen-Poiseuille
pressure-drop equation:

`delta_p = 128 mu L Q / (pi D^4)`

The automated test uses water-like viscosity with `Q = 1e-5 m^3/s`, `D = 0.01 m`,
and `L = 10 m`. It produces `Re = 1273.24`, so the flow is laminar. Both equations
must give a friction pressure drop of approximately `407.44 Pa`.

This is the first validation check. The next validation stage will compare
turbulent-flow results with a published worked example and document the source
for the final report.
