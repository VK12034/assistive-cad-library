# Shared print settings

Defaults that apply across the library. Measured print time and mass for each part are on its model page.

## Design rules

Every part in this library is designed to:

- sit on a **flat base** (no brim needed)
- keep every overhang within **45 degrees** of vertical, so **no supports** are needed (checked: the slicer generated no support material for any of the 15 STLs)
- keep the minimum wall at **2.5 mm or more**, five or more 0.50 mm extrusion lines
- have **filleted or chamfered edges** wherever skin touches. Bed edges get a 45 degree chamfer rather than a fillet, because a fillet there would overhang.
- need **no hardware**: every part is one printed piece

## Slicing settings used for every published number

PrusaSlicer was not installed on the machine used, so all parts were sliced with the **ElegooSlicer 1.5.2.2 command line** using its bundled **Prusa MK3S 0.4 nozzle** printer profile and **Prusa Generic PLA** filament profile, with these process settings:

| Setting | Value | Why |
|---------|-------|-----|
| Nozzle | 0.4 mm | standard |
| Layer height | 0.30 mm (first layer 0.20 mm) | keeps every preset under 2 hours; at 0.20 mm the Large handle sleeve took 2 h 14 m |
| Perimeters | 2 (0.50 mm extrusion width) | profile default |
| Top / bottom layers | 4 / 3 | profile default |
| Infill | 10 %, crosshatch | chosen to keep every preset under 2 hours (15-20 % was also sliced for the handle sleeve and took longer) |
| Supports | none | every part is designed support-free |
| Brim | none | every part has a flat base |
| Nozzle / bed temperature | 220 C / 60 C | profile default |

Times are the slicer's estimate for that profile, not a measured print. Other printers and slicers will differ.

## Material

PLA, with the property values from the Prusament PLA datasheet (see [anthropometry-sources.md](anthropometry-sources.md)). FDM parts are anisotropic and weaker across layer lines, so the simulations check tension across layers against the 17 MPa interlayer adhesion. PLA softens at about 55 C: keep these parts out of dishwashers and hot cars.

## Want more strength?

The stress studies model a solid part. If you want more margin than a page reports, raise perimeters to 4 and infill to 20-30 %, and re-slice to check the print time.
