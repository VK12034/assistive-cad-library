# Printables text

Copy-paste text for the Printables collection and the five model pages. Each model page also needs: the three STLs from that device's `stl/` folder, the renders from `renders/`, the license set to **CC BY 4.0**, and a link back to the GitHub repo.

---

## Collection: Open Assistive CAD Library (untested v0.1)

**Description**

Five simple, parametric assistive aids for everyday tasks: eating and brushing teeth, turning a key, opening jars and bottles, buttons and zippers, and writing. Each one is a single printed piece with no hardware and no supports, and prints in under 2 hours on a standard FDM printer. Each comes in Small, Medium and Large sizes based on published hand-size data (ANSUR II), and the Fusion source with named parameters lets you resize it to fit a specific person or object.

**These designs are untested (v0.1).** They have been modelled, checked and stress-analysed in software, but never printed or used by anyone. They are **not medical devices**. If you're choosing aids for a specific person, involve an occupational therapist. If you print one, please post a make or open an issue on GitHub: real-world feedback is exactly what v0.1 needs.

Source, build scripts, stress studies and full documentation: [GitHub repo link]

License: CC BY 4.0

---

## 1. Built-up handle sleeve (untested v0.1)

**Summary:** Slides over a utensil or toothbrush handle to make it thicker and easier to grip.

**Description**

For people with reduced grip strength or limited finger closing (for example arthritis, neuropathy, or after a stroke) who struggle with thin handles. A tapered round bore (6.4-20 mm) fits round handles. A tapered slot (3.5 mm thick, 12-24 mm wide) fits flat cutlery. The handle wedges in when you push it.

Sizes: grip diameter is 19.7 % of hand length (Kong & Lowe 2005), using ANSUR II hand data.
- S: 32.5 x 80 mm
- M: 37.5 x 95 mm
- L: 41.5 x 105 mm

Print settings: PLA, 0.30 mm layers, 2 perimeters, 10 % infill, no supports, print upright. Slicer estimates (Prusa MK3S profile):
- S: 1 h 07 m, 22.5 g
- M: 1 h 33 m, 31.5 g
- L: 1 h 54 m, 41.0 g

Stress check (open-source FE, solid model): minimum safety factor 5.6 under a 500 N grip squeeze.

Wash by hand: PLA softens at about 55 C. **Untested v0.1, not a medical device.**

---

## 2. Key turner (untested v0.1)

**Summary:** A big paddle that holds a house key, so you can turn it with your whole hand.

**Description**

For people who find gripping and twisting a small key difficult or painful. The key's head pushes into a slot in the top edge. The paddle gives you a longer lever and a large surface to grip, and a teardrop finger hole lets you hook a finger through instead of pinching.

**Measure your key first.** The slot is 2.4 mm thick, built for a key about 2 mm thick, and it holds the key by friction. Change the `key_t` parameter if your key differs.

Sizes (paddle length from ANSUR II hand breadth):
- S: 80 x 62 x 18 mm
- M: 95 x 66 x 18 mm
- L: 105 x 70 x 18 mm

Print settings: PLA, 0.30 mm layers, 2 perimeters, 10 % infill, no supports, print standing on its long edge. Slicer estimates:
- S: 1 h 22 m, 29.0 g
- M: 1 h 41 m, 35.8 g
- L: 1 h 54 m, 41.0 g

Stress check (open-source FE, solid model): minimum safety factor 2.21 for a 5.5 N*m twist. That is a **thin margin**, and the load is a stand-in because I found no published key-turning torque. Don't force a jammed lock with it. **Untested v0.1, not a medical device.**

---

## 3. Bottle and jar opener (untested v0.1)

**Summary:** A flat V-jaw opener for caps from 28 mm bottle caps up to 82 mm jar lids.

**Description**

For people who can't grip or twist a lid hard enough. Slide the V over the cap until both walls touch it, then push the handle. The cap wedges deeper as you turn, and the long handle cuts the force you need. It prints flat, with no overhangs at all.

Sizes (handle length from ANSUR II hand breadth; the jaw is the same on all three):
- S: 172 x 122 x 10 mm
- M: 187 x 122 x 10 mm
- L: 197 x 122 x 10 mm

Print settings: PLA, 0.30 mm layers, 2 perimeters, 10 % infill, no supports, print flat. Slicer estimates:
- S: 55 m, 21.2 g
- M: 59 m, 23.0 g
- L: 1 h 02 m, 24.2 g

Stress check (open-source FE, solid model): minimum safety factor 3.53 at 5.5 N*m, the top of a published typical jar-opening torque range.

The jaw is smooth, so it may slip on greasy lids. **Untested v0.1, not a medical device.**

---

## 4. Zipper and button pull (untested v0.1)

**Summary:** A thick handle with a thin loop for pulling buttons through buttonholes and catching zipper tabs.

**Description**

For people who find small buttons and zipper tabs hard to pinch. To button up: push the loop through the buttonhole, catch the button, and pull it back through. For a zipper: slip the pull tab into the loop and pull. The loop is 11.4 mm wide, which is 18 ligne, a common shirt-button size. Change `loop_ow` for other buttons.

Sizes (handle length from ANSUR II hand breadth):
- S: 153 x 24 x 14 mm
- M: 168 x 24 x 14 mm
- L: 178 x 24 x 14 mm

Print settings: PLA, 0.30 mm layers, 2 perimeters, 10 % infill, no supports, print flat. Slicer estimates:
- S: 32 m, 12.3 g
- M: 37 m, 14.2 g
- L: 40 m, 15.4 g

Stress check (open-source FE, solid model): minimum safety factor 2.42 for a 102 N straight pull on the loop. Out of plane it reaches SF 2 at only about 6 N. **The thin neck is not designed for strong sideways or up-and-down pulls.** **Untested v0.1, not a medical device.**

---

## 5. Pen grip (untested v0.1)

**Summary:** A thick sleeve that slides onto a pen so it can be held with a looser grip.

**Description**

For people who find a standard pen too thin to hold comfortably. Push the pen in tip-first through the wide end. The tapered bore (11 mm down to 7 mm) wedges onto the pen's taper. **Bore sizes are an estimate: measure your pen** and adjust `bore_narrow` if needed.

Sizes:
- S: 22 mm (matches the smaller foam built-up tubing)
- M: 28 mm (matches the larger foam tubing)
- L: 32.5 mm

All are 45 mm long.

Print settings: PLA, 0.30 mm layers, 2 perimeters, 10 % infill, no supports, print upright with the wide end down. Slicer estimates:
- S: 25 m, 7.5 g
- M: 30 m, 9.8 g
- L: 37 m, 12.3 g

Stress check (open-source FE, solid model): minimum safety factor 19.4 under a 102 N pinch. It's hard PLA, not soft foam. **Untested v0.1, not a medical device.**
