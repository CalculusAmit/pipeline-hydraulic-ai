# Phase 2 - Multi-Section Pressure Profile

## Objective

Calculate pressure at the inlet and after every pipeline section, rather than
only reporting one total head-loss value for the complete route.

## Inputs

- constant fluid flow rate, density, and viscosity
- inlet gauge pressure
- one or more pipeline sections
- each section's length, internal diameter, roughness, elevation change, and
  total minor-loss coefficient

## Method

At the inlet, the total energy head is calculated from pressure head and velocity
head. For each section, Darcy-Weisbach and minor losses reduce total energy. The
local gauge-pressure head at the outlet is then calculated using:

`p/(rho g) = H_total - z - V^2/(2g)`

where `z` is cumulative elevation and `V` is the local section velocity.

## Limits

- The model supports steady, incompressible, single-path flow only.
- Branching pipe networks, valves with changing opening, transient effects, and
  cavitation calculations are outside this phase.
- If the diameter changes, the required expansion/contraction loss must be
  included by the user in the section's minor-loss coefficient.
- A negative calculated gauge pressure is a warning, not a cavitation result.
  NPSH and absolute-pressure calculations will be added with the pump module.

## Interactive engineering graph

The simulator writes a self-contained Plotly HTML chart after each calculation.
It plots pipeline elevation, the hydraulic grade line, the energy grade line,
and gauge pressure against distance. This visual evidence is suitable for the
final demonstration and becomes the data source for the future dashboard chart.
