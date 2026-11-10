# How this library is built

## Parametric by construction

No part in this library is drawn by hand. Each one is produced by a Python script that drives the Fusion 360 API through Fusion's local MCP server. Every key dimension is created as a **named user parameter** first, and all sketch geometry and features reference those parameters, so changing one number rebuilds the whole part.

1. Resizing is a parameter edit, not a remodel. The size presets are just different values for the same parameter set.
2. The build script is the real source of truth. Each device's `cad/build_*.py` rebuilds the M preset from an empty Fusion document; the `.f3d` archive is its output.

## Pipeline per device

1. **Dimensions.** Published anthropometry and object dimensions, cited in [anthropometry-sources.md](anthropometry-sources.md), define the S / M / L presets.
2. **CAD.** Fusion model from named parameters: flat base, no overhang over 45 degrees, filleted skin-contact edges. Every sketch is fully constrained.
3. **Check.** Timeline health, sketch constraint status, bounding box per preset, and minimum wall thickness measured with Fusion's `measureMinimumDistance` between opposing faces. Problems found here were fixed before simulation; each fix is in that device's changelog.
4. **Simulation.** Linear static stress study with a hand load taken from published strength data (see below). If the minimum safety factor is under 2, the design is revised and the study rerun; every revision is in the changelog.
5. **Export.** STL (binary, high refinement) and STEP per preset, exported by Fusion from the parametric model, plus viewport captures.
6. **Slicing.** Every STL is sliced from the command line; print time and filament mass are read from the G-code the slicer writes.
7. **Documentation.** The model page.

## Simulation: what was used and why

The plan was Fusion Simulation. On this Fusion install (2706.1.17, Education license) the simulation scripting API (`adsk.sim`, a preview feature) returned no simulation product, even after a study was created by hand and the document was saved and reopened. So every study was run with open-source tools instead:

- **gmsh 4.15.2** meshes the STEP that Fusion exported (tetrahedra, 2-3 mm with local refinement where needed).
- **scikit-fem 12.0.2** solves linear elasticity with quadratic tetrahedra. Algebraic-multigrid CG is used, falling back to a direct sparse solve if it stalls. Converged to a relative residual below 1e-6.
- The solver is `tools/fe_solver.py`. Each device's `simulation/` folder holds its study setup (`study_*.json`) and results (`*_results.json`).

**Results are labelled "not a Fusion Simulation result" on every page.**

How the studies are set up:

- **Material:** PLA from the Prusament PLA datasheet (E = 2.3 GPa). Poisson's ratio 0.36 is assumed.
- **Balanced loads where possible.** A hand squeeze, or a hand twist resisted by a key, balances itself, so the part is held only by three support points (3-2-1). The reactions came out at 0 N, and stresses within 4 mm of those points are excluded as support artifacts.
- **Fixed patches** are used where a rigid object holds the part (the cap in the jar opener, the hand on a handle). Peaks at the edge of a fixed patch are partly artifacts and are flagged.
- **Two failure checks:**
  1. von Mises stress against **17 MPa interlayer adhesion**: the strictest rule, which assumes every stress pulls the layers apart.
  2. **Anisotropic:** tension across layers (sigma_zz, with layers horizontal as printed) against 17 MPa, and von Mises against the **51 MPa in-plane yield**.

  The pass target is SF of at least 2 on the anisotropic check. Each page reports both. Interlayer shear is not checked, because the datasheet gives no value for it.
- **The model is a solid part.** Prints use 2 perimeters and 10 % infill, so a real part is weaker than modelled.

## Rules on numbers

Every figure published in this repository comes from one of four places: a cited publication, the Fusion model, a simulation result, or a slicer run. Anything estimated is labelled as an estimate. Nothing is filled in to look complete.
