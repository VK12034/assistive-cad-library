# Sizing sources

Small / medium / large presets are derived from published data, not guesswork. This page records every source used and exactly what was taken from it. Where no source could be found, the value is a **design estimate**, labelled that way here and on the model page.

## Primary population data: ANSUR II

**U.S. Army Anthropometric Survey (ANSUR II), 2012**, public release via the Penn State OPEN Design Lab: <https://www.openlab.psu.edu/ansur2/>. Files `ANSUR_II_MALE_Public.csv` (4,082 men) and `ANSUR_II_FEMALE_Public.csv` (1,986 women). Measurements in mm.

Percentiles below were **computed directly from the raw records** (linear interpolation between ranks) with `tools/ansur_stats.py`; the full output is in `tools/ansur_stats_output.txt`. Dimension definitions: <https://mreed.umtri.umich.edu/mreed/downloads/anthro/ansur/ADAS-Dimension_Definitions.pdf>.

| Measure | Group | 5th %ile | 50th %ile | 95th %ile |
|---------|-------|----------|-----------|-----------|
| Hand length | Women | 165.0 | 180.0 | 199.0 |
| Hand length | Men | 177.0 | 193.0 | 210.0 |
| Hand length | All (n = 6,068) | 171.0 | 189.5 | 208.0 |
| Hand breadth | Women | 72.0 | 78.0 | 85.0 |
| Hand breadth | Men | 81.0 | 88.0 | 96.0 |
| Hand breadth | All | 74.0 | 86.0 | 94.0 |

**Preset rule used across the library:** Small = women's 5th percentile, Medium = all-subjects median, Large = men's 95th percentile.

**Caveat:** ANSUR II sampled U.S. Army personnel, who are younger, stronger and healthier than the older and disabled users these devices are aimed at. It is the best openly available dataset with full raw records, not a perfect match.

## Handle diameter

| Finding | Value | Source | Used for |
|---------|-------|--------|----------|
| Most comfortable cylindrical handle diameter | **19.7 % of hand length** | Kong & Lowe (2005), *Int. J. Industrial Ergonomics* 35(6) 495-507; record <https://stacks.cdc.gov/view/cdc/197408> | Handle sleeve S/M/L; pen grip L |
| Optimum diameter, biomechanical model | 33 mm | Kong & Lowe, *Optimum Tool Handle Diameter for a Cylinder Grip* <https://www.sciencedirect.com/science/article/abs/pii/S0894113003001601> | cross-check |
| Pen equivalent diameter with best drawing accuracy | 8 mm | Goonetilleke, Hoffmann & Luximon (2009), *Applied Ergonomics*, <https://doi.org/10.1016/j.apergo.2008.04.015> | pen grip bore |

## Strength data (simulation loads)

| Finding | Value | Source | Used for |
|---------|-------|--------|----------|
| Peak median grip strength, men (ages 29-39) | 51 kg (500 N) | Dodds et al. (2014), *PLoS ONE* 9(12): e113637, <https://doi.org/10.1371/journal.pone.0113637> | handle sleeve squeeze |
| Mean key (lateral) pinch, right hand | men 10.4 kg (102 N), women 6.6 kg | Gunther et al. (2008), *J. Hand Surgery (Eur.)*, <https://doi.org/10.1177/1753193408087031> | sleeve lever, pull, pen squeeze |
| Nominal jar-opening torque range | 2.9-5.5 N*m | Steenbekkers, as cited in Yoxall & Rowson (2015), *Packaging Technology and Science* 28(1) 1-14, <https://shura.shu.ac.uk/9128/> | jar opener; key turner (stand-in) |

No published value was found for the torque needed to turn a key in a residential lock; the jar-opening figure is used as a labelled stand-in.

## Material

| Property | Value | Source |
|----------|-------|--------|
| Density | 1.24 g/cm3 | Prusament PLA technical datasheet v1.1 (2022-02-16), <https://prusament.com/wp-content/uploads/2022/10/PLA_Prusament_TDS_2021_10_EN.pdf> |
| Tensile modulus (printed, horizontal) | 2.3 GPa | same |
| Tensile yield (printed, horizontal) | 51 MPa | same |
| Interlayer adhesion | 17 MPa | same |
| Heat deflection temperature | 55 C | same |
| Poisson's ratio | 0.36 | **assumed**, not in the datasheet |

## Object dimensions

| Object | Dimension | Value | Source / status |
|--------|-----------|-------|-----------------|
| Built-up foam tubing (OT product) | bore x outer diameter | 6 x 22 mm, 10 x 28 mm, 16 x 28 mm (bores 1/4, 3/8, 5/8 in; one seller lists 13/16 in = 20 mm) | Essential Aids, <https://essentialaids.com/children-with-disabilities/children-s-cutlery/closed-cell-foam-tubing.html> |
| Utensil / toothbrush round handles | fit range | 6.4-20 mm (matched to foam tubing bores) | derived from the row above |
| Flat (metal) utensil handles | cross-section | 3.5 mm slot, 12-24 mm wide | **design estimate**, no published flatware standard found |
| Pen barrel | diameter | bore 7-11 mm | **design estimate** bracketing the 8 mm pen above |
| Key blade (KW1) | thickness | 2.0 mm | single retailer listing (Digicom Jamaica); **weak source, measure your key** |
| Key bow | width / depth | 32 / 18 mm slot | **design estimate** |
| Bottle neck (PCO 1881) | finish | 28 mm (lock ring 28.0 mm in patent KR20160000145U) | closure listings, e.g. <https://www.pelliconi.com/product/plastic-caps-28mm-1881/> |
| Twist-off jar lids (lug caps) | diameters | 38, 43, 48, 53, 58, 63, 66, 70, 77, 82 mm | ANT Packaging, <https://www.antpackaging.com/metal-lug-cap.html> |
| Buttons | size unit | 1 ligne = 1/40 in = 0.635 mm; 18 ligne = 11.4 mm | Wikipedia "Ligne", <https://en.wikipedia.org/wiki/Ligne>; button charts e.g. <https://www.purlsoho.com/create/button-conversion-chart/> |
