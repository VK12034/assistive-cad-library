# Shared print settings

Defaults that apply across the library. Per-device overrides and the measured
print time and mass for each part live on that model page.

## Design rules

Every part in this library is designed to:

- sit on a **flat base** large enough to print without a brim
- keep every overhang within **45 degrees** of vertical, so no supports are needed
- use a **wall thickness** that is a whole multiple of the nozzle width
- carry **filleted edges** on every surface that touches skin

## Suggested slicing defaults

| Setting | Value | Why |
|---------|-------|-----|
| Nozzle | 0.4 mm | the size these wall thicknesses are built around |
| Layer height | 0.2 mm | balances surface finish against print time |
| Perimeters | TBD | set per device from the wall thickness parameter |
| Infill | TBD | set per device from the simulation result |
| Supports | none | required: every part is designed support-free |
| Brim | none | required: every part has a flat base |

## Material

Material choice is recorded per device, together with the property values used
in the simulation and where those values came from. A printed FDM part is
anisotropic and is generally weaker across layer lines than the bulk values
used in analysis, so parts are oriented with load paths running along layers
wherever the geometry allows.

## Measured results

Print time and mass are taken from an actual slicer run, and the model page
names which slicer and which profile produced the number. Where a figure is
calculated from model volume instead of sliced, it is labelled as an estimate.
