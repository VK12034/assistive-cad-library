# Tools

Everything used to build, check, and analyse the library.

## Build scripts (one per device)

Each device's `cad/` folder holds a self-contained Fusion API script that rebuilds the part, Medium preset, from an empty document. Each one defines the standard entry point `def run(_context: str):`. Run it from Fusion's **Scripts and Add-Ins**, or through Fusion's local MCP server (Preferences > General > API > Fusion MCP Server).

| Script | Device |
|--------|--------|
| [`build_handle_sleeve.py`](../devices/01-built-up-handle-sleeve/cad/build_handle_sleeve.py) | 1. Built-up handle sleeve |
| [`build_key_turner.py`](../devices/02-key-turner/cad/build_key_turner.py) | 2. Key turner |
| [`build_jar_opener.py`](../devices/03-bottle-jar-opener/cad/build_jar_opener.py) | 3. Bottle and jar opener |
| [`build_zipper_button_pull.py`](../devices/04-zipper-button-pull/cad/build_zipper_button_pull.py) | 4. Zipper and button pull |
| [`build_pen_grip.py`](../devices/05-pen-grip/cad/build_pen_grip.py) | 5. Pen grip |

## Shared code

| File | What it is |
|------|------------|
| `fusion_lib.py` | Helpers the build scripts share: user parameters, fully constrained sketches (circles, rectangles, parameter-driven polygons, teardrops), features, edge selection, wall-thickness measurement, render setup. Each build script already includes a copy. |
| `fusion_mcp_client.py` | Minimal Python client for Fusion's local MCP server (streamable HTTP at `http://127.0.0.1:27182/mcp`). `python fusion_mcp_client.py script my_script.py` runs a Fusion API script; `shot out.png iso-top-right` saves a viewport capture. |
| `fe_solver.py` | Linear static stress solver (gmsh + scikit-fem + pyamg, matplotlib for plots). `python fe_solver.py study.json`. Study files are in each device's `simulation/` folder. Needs `pip install gmsh scikit-fem meshio numpy scipy pyamg matplotlib`. |
| `ansur_stats.py` | Computes hand-dimension percentiles from the ANSUR II public CSVs. `python ansur_stats.py <folder with the two CSVs>`. Output used in this library: `ansur_stats_output.txt`. |

Study files use paths relative to their own `simulation/` folder (`../step/...`), so run the solver from inside that folder.
