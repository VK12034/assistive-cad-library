# Key turner

> **untested, v0.1** - This design has not been printed or physically tested.
> It is **not a medical device**. See the
> [repository disclaimer](../../DISCLAIMER.md).

Clamps onto the bow of a key to give a long lever, so the key can be turned with a whole-hand grip instead of a fingertip pinch.

## Who it is for

People who cannot generate a strong lateral pinch or who have painful or restricted wrist rotation, including arthritis and reduced fine motor control.

## Status

Not yet built. The sections below are filled in only from measured sources: the
Fusion model, a simulation result, a slicer run, or a cited publication.

| Stage | State |
|-------|-------|
| Dimensions researched and cited | not started |
| CAD built from named parameters | not started |
| Model checked (dimensions, interference, min wall) | not started |
| Static stress study run | not started |
| STL and STEP exported | not started |
| Sliced and print stats recorded | not started |

## Fit

Designed to fit the bow of a standard house or door key. The source for that dimension is recorded in
[docs/anthropometry-sources.md](../../docs/anthropometry-sources.md).

## Size presets

| Preset | Driving dimension | Value | Basis |
|--------|-------------------|-------|-------|
| Small | TBD | TBD | TBD |
| Medium | TBD | TBD | TBD |
| Large | TBD | TBD | TBD |

## Print settings

Shared defaults are in [docs/print-settings.md](../../docs/print-settings.md).

| Setting | Value |
|---------|-------|
| Material | TBD |
| Layer height | TBD |
| Perimeters | TBD |
| Infill | TBD |
| Supports | none by design |
| Orientation | TBD |

| Preset | Print time | Mass | Slicer |
|--------|-----------|------|--------|
| Small | TBD | TBD | TBD |
| Medium | TBD | TBD | TBD |
| Large | TBD | TBD | TBD |

## How to resize

Every dimension is a named user parameter in the Fusion model. To fit something
this library did not anticipate, open the `.f3d` in `cad/`, go to
Modify, Change Parameters, and edit the parameter rather than the geometry.

| Parameter | Controls |
|-----------|----------|
| TBD | TBD |

## How to use

1. TBD

## Simulation

| Item | Value |
|------|-------|
| Study type | static stress |
| Material | TBD |
| Constraint | TBD |
| Load location | TBD |
| Load magnitude | TBD |
| Reasoning for the load | TBD |
| Minimum safety factor | TBD |

Target: minimum safety factor at or above 2. If a run comes in under 2, the
design is revised and rerun, and both runs are recorded in the changelog.

Simulation predicts the behaviour of an idealised solid, not of a printed part.
FDM parts are anisotropic and are usually weaker across layer lines than the
bulk values used here.

## Known limits

- Never printed, never handled, never tested by a person.
- Simulation uses assumed bulk material properties, not measured properties of
  a printed specimen.
- Further limits are recorded here once the model exists.

## Files

| File | Description |
|------|-------------|
| `cad/` | Fusion source and the build script that generates it |
| `step/` | STEP export per size preset |
| `stl/` | STL export per size preset |
| `renders/` | viewport captures |
| `simulation/` | static stress setup and results |

## Version and changelog

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-11-10 | Model page created. Design not yet built. |
