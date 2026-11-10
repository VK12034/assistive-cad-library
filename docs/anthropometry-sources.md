# Sizing sources

Small / medium / large presets are derived from published data, not from
guesswork. This page records every source used and exactly what was taken from
it. Figures that are not yet pinned to a source are marked `TBD` rather than
filled with a plausible number.

## Status

Research in progress. The handle-diameter literature below has been reviewed.
The population percentile tables have not yet been extracted.

## Primary population data

**U.S. Army Anthropometric Survey (ANSUR II), 2012.** The intended primary
source for hand length, hand breadth, and hand circumference percentiles. The
full dataset is published as CSV, so 5th / 50th / 95th percentiles will be
computed directly from the raw records rather than copied from a secondary
site.

- Dimension definitions: <https://mreed.umtri.umich.edu/mreed/downloads/anthro/ansur/ADAS-Dimension_Definitions.pdf>
- Interactive explorer and dataset download: <https://ergoassessment.cam/ansur-2-data-explorer/>

| Measure | 5th %ile | 50th %ile | 95th %ile | Source |
|---------|----------|-----------|-----------|--------|
| Hand length (F) | TBD | TBD | TBD | ANSUR II |
| Hand length (M) | TBD | TBD | TBD | ANSUR II |
| Hand breadth (F) | TBD | TBD | TBD | ANSUR II |
| Hand breadth (M) | TBD | TBD | TBD | ANSUR II |

Caveat to record on every model page that uses it: ANSUR II sampled U.S. Army
personnel, who are not representative of the older and disabled populations
these devices are aimed at. It is the best openly available dataset with full
raw records, not a perfect match for the target users.

## Handle diameter

There is no single agreed optimal cylindrical handle diameter. The literature
splits by method:

| Finding | Value | Method | Source |
|---------|-------|--------|--------|
| Optimum handle diameter, general population | 33 mm | biomechanical hand model | Kong and Lowe, *Optimum Tool Handle Diameter for a Cylinder Grip* |
| Optimum for grip force | 20-30 mm, larger for men | measured grip force | Kong and Lowe, *Optimal cylindrical handle diameter for grip force tasks* |
| Optimum as a fraction of hand length | 19.7% of hand length | measured, 25-50 mm handles tested | NIOSH-described study |
| Most comfortable for maximum grip exertion | 30, 35, 40 mm rated highest | subjective comfort rating | same NIOSH-described study |
| Influence of diameter on total grip force | limited within tested range | measured | CDC-hosted study |

Sources:

- Kong, Y.-K. and Lowe, B. D. *Optimum Tool Handle Diameter for a Cylinder Grip.*
  <https://www.sciencedirect.com/science/article/abs/pii/S0894113003001601>
- Kong, Y.-K. and Lowe, B. D. *Optimal cylindrical handle diameter for grip force
  tasks.* International Journal of Industrial Ergonomics.
  <https://www.sciencedirect.com/science/article/abs/pii/S0169814104002148>
- NIOSH / CDC, *Optimal Cylindrical Handle Diameter for Grip Force Tasks.*
  <https://stacks.cdc.gov/view/cdc/197408>
- CDC, *Effects of handle size and shape on measured grip strength.*
  <https://stacks.cdc.gov/view/cdc/193248/cdc_193248_DS1.pdf>

Design consequence: a built-up handle target in the low-to-mid 30 mm range is
defensible from the model-based literature, and a hand-length-scaled rule of
roughly 18-20% gives the per-size spread. Which rule drives which parameter is
recorded on each model page.

## Object dimensions

Dimensions of the objects these parts fit around: utensil handles, toothbrush
handles, pen barrels, key bows, bottle caps, jar lids, zipper pulls.

| Object | Dimension | Value | Source |
|--------|-----------|-------|--------|
| Utensil handle | cross-section | TBD | TBD |
| Toothbrush handle | cross-section | TBD | TBD |
| Pen barrel | diameter | TBD | TBD |
| Key bow | thickness | TBD | TBD |
| Beverage cap (PCO/PET finish) | diameter | TBD | TBD |
| Jar lid (twist-off finish) | diameter range | TBD | TBD |
