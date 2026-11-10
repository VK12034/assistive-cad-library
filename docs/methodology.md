# How this library is built

## Parametric by construction

No part in this library is drawn by hand. Each one is produced by a Python
script that drives the Fusion 360 API through Fusion's local MCP server. Every
key dimension is created as a **named user parameter** first, and all sketch
geometry and features reference those parameters, so changing one number
rebuilds the whole part.

This has two consequences worth stating plainly:

1. Resizing is a parameter edit, not a remodel. The size presets are just
   different values for the same parameter set.
2. The build script is the real source of truth. The `.f3d` file is an output
   of the script, and the script is committed alongside it.

## Pipeline per device

1. **Dimensions.** Find published anthropometry and object dimensions, cite
   them, and define the small / medium / large presets.
2. **CAD.** Build the part in Fusion from named parameters, designed for a flat
   base, 45 degree overhang limit, sensible wall thickness, and filleted
   contact edges.
3. **Check.** Inspect the built model: screenshots, measured dimensions,
   interference, minimum wall thickness. Fix anything wrong before continuing.
4. **Simulation.** Set up and run a static stress study with a realistic hand
   load. Record the constraints, the load location and magnitude with the
   reasoning behind them, the material, and the minimum safety factor. If the
   safety factor is below 2, revise and rerun.
5. **Export.** STL and STEP for each size preset, plus clean renders.
6. **Slicing.** Slice each STL and record print time, mass, and support needs.
   Where a figure is calculated from model volume rather than sliced, label it
   an estimate.
7. **Documentation.** Write the model page.

## Rules on numbers

Every figure published in this repository comes from one of four places: a
cited publication, the Fusion model, a simulation result, or a slicer run.
Anything estimated is labelled as an estimate. Nothing is filled in to look
complete.
