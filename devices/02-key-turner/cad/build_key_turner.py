"""Key turner v0.1 - Fusion API build script (untested v0.1, not a medical device).
Run inside Fusion (Scripts and Add-Ins, or the Fusion MCP script executor). Builds the M preset;
change user parameters (Modify > Change Parameters) for S/L - see ../README.md."""
import adsk.core, adsk.fusion, math, os

VI = adsk.core.ValueInput
P3 = adsk.core.Point3D
FO = adsk.fusion.FeatureOperations

def ctx():
    app = adsk.core.Application.get()
    des = adsk.fusion.Design.cast(app.activeDocument.products.itemByProductType('DesignProductType'))
    return app, des, des.rootComponent

def new_design(name):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(app.activeProduct)
    des.designType = adsk.fusion.DesignTypes.ParametricDesignType
    des.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    return app, des, des.rootComponent

def set_params(des, plist):
    """plist: [(name, expr, unit, comment)] ; create or update."""
    up = des.userParameters
    for name, expr, unit, comment in plist:
        p = up.itemByName(name)
        if p:
            p.expression = expr
        else:
            up.add(name, VI.createByString(expr), unit, comment)

def offset_plane(comp, base, expr, name):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(base, VI.createByString(expr))
    pl = comp.constructionPlanes.add(pi)
    pl.name = name
    return pl

def circle(sk, dia_expr, cx=0.0, cy=0.0, guess=1.0):
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(P3.create(cx, cy, 0), guess)
    if cx == 0 and cy == 0:
        sk.geometricConstraints.addCoincident(c.centerSketchPoint, sk.originPoint)
    d = sk.sketchDimensions.addDiameterDimension(c, P3.create(cx + guess, cy + guess, 0))
    d.parameter.expression = dia_expr
    return c

def center_rect(sk, w_expr, h_expr, gw=1.0, gh=0.5):
    """Rectangle centred on sketch origin, width along sketch X."""
    L = sk.sketchCurves.sketchLines
    r = L.addTwoPointRectangle(P3.create(-gw/2, -gh/2, 0), P3.create(gw/2, gh/2, 0))
    gc = sk.geometricConstraints
    for i in range(4):
        ln = r.item(i)
        s, e = ln.startSketchPoint.geometry, ln.endSketchPoint.geometry
        if abs(s.y - e.y) < 1e-9:
            gc.addHorizontal(ln)
        else:
            gc.addVertical(ln)
    diag = L.addByTwoPoints(r.item(0).startSketchPoint, r.item(2).startSketchPoint)
    diag.isConstruction = True
    gc.addMidPoint(sk.originPoint, diag)
    hl = [r.item(i) for i in range(4) if abs(r.item(i).startSketchPoint.geometry.y - r.item(i).endSketchPoint.geometry.y) < 1e-9][0]
    vl = [r.item(i) for i in range(4) if abs(r.item(i).startSketchPoint.geometry.x - r.item(i).endSketchPoint.geometry.x) < 1e-9][0]
    d1 = sk.sketchDimensions.addDistanceDimension(hl.startSketchPoint, hl.endSketchPoint, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, P3.create(0, gh, 0))
    d1.parameter.expression = w_expr
    d2 = sk.sketchDimensions.addDistanceDimension(vl.startSketchPoint, vl.endSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, P3.create(gw, 0, 0))
    d2.parameter.expression = h_expr
    return r

def extrude(comp, prof, dist_expr, op=FO.NewBodyFeatureOperation, name=None, symmetric=False, bodies=None):
    ex = comp.features.extrudeFeatures
    inp = ex.createInput(prof, op)
    if symmetric:
        inp.setSymmetricExtent(VI.createByString(dist_expr), True)
    else:
        inp.setDistanceExtent(False, VI.createByString(dist_expr))
    if bodies:
        inp.participantBodies = bodies
    f = ex.add(inp)
    if name: f.name = name
    return f

def loft(comp, profs, op, name=None):
    lf = comp.features.loftFeatures
    inp = lf.createInput(op)
    for p in profs:
        inp.loftSections.add(p)
    inp.isSolid = True
    f = lf.add(inp)
    if name: f.name = name
    return f

def edges_where(body, fn):
    oc = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if fn(e):
            oc.add(e)
    return oc

def fillet(comp, edges, r_expr, name=None):
    ff = comp.features.filletFeatures
    inp = ff.createInput()
    inp.isRollingBallCorner = True
    inp.edgeSetInputs.addConstantRadiusEdgeSet(edges, VI.createByString(r_expr), True)
    f = ff.add(inp)
    if name: f.name = name
    return f

def chamfer(comp, edges, d_expr, name=None):
    cf = comp.features.chamferFeatures
    inp = cf.createInput2()
    inp.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, VI.createByString(d_expr), True)
    f = cf.add(inp)
    if name: f.name = name
    return f

def timeline_report(des):
    bad = 0
    tl = des.timeline
    for i in range(tl.count):
        it = tl.item(i)
        if it.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            bad += 1
            print("  UNHEALTHY:", it.name, "|", it.errorOrWarningMessage)
    print("timeline items:", tl.count, "unhealthy:", bad)
    return bad

def body_report(comp, um=None):
    for b in comp.bRepBodies:
        bb = b.boundingBox
        pp = b.physicalProperties
        print("body '%s' solid=%s faces=%d edges=%d vol_cm3=%.4f area_cm2=%.3f bbox_mm=(%.2f x %.2f x %.2f) zmin_mm=%.3f" % (
            b.name, b.isSolid, b.faces.count, b.edges.count, b.volume, b.area,
            (bb.maxPoint.x-bb.minPoint.x)*10, (bb.maxPoint.y-bb.minPoint.y)*10, (bb.maxPoint.z-bb.minPoint.z)*10, bb.minPoint.z*10))

# ---------- material + simulation helpers ----------
PLA_NAME = "PLA FDM (Prusament TDS, interlayer yield)"

def ensure_pla(des):
    """PLA from Prusament PLA TDS v1.1 (2022-02-16): density 1.24 g/cm3, tensile modulus 2.3 GPa (horizontal),
    yield set to interlayer adhesion 17 MPa (weakest direction), UTS field set to horizontal tensile yield 51 MPa.
    Poisson 0.36 is an assumption (not in the TDS)."""
    m = des.materials.itemByName(PLA_NAME)
    if not m:
        app = adsk.core.Application.get()
        src = app.materialLibraries.itemByName("Fusion Material Library").materials.itemByName("ABS Plastic")
        m = des.materials.addByCopy(src, PLA_NAME)
    E, nu = 2300000.0, 0.36
    vals = {"structural_Density": 1240.0, "structural_Young_modulus": E, "structural_Poisson_ratio": nu,
            "structural_Shear_modulus": E / (2 * (1 + nu)), "structural_Minimum_yield_stress": 17000.0,
            "structural_Minimum_tensile_strength": 51000.0}
    for k, v in vals.items():
        m.materialProperties.itemById(k).value = v
    return m

def mat_report(m):
    ids = ["structural_Density", "structural_Young_modulus", "structural_Poisson_ratio", "structural_Shear_modulus", "structural_Minimum_yield_stress", "structural_Minimum_tensile_strength"]
    print("material:", m.name, {i.replace("structural_", ""): round(m.materialProperties.itemById(i).value, 3) for i in ids})

def sim_study(name):
    import adsk.sim
    app = adsk.core.Application.get()
    sim = adsk.sim.Simulations.get(app.activeDocument)
    model = sim.simulationModels.item(0)
    st = model.studies.itemByName(name)
    if st:
        st.deleteMe()
    st = model.studies.add(adsk.sim.StudyTypes.LinearStaticStressStudyType, name)
    return sim, model, st

def get_study(name=None):
    import adsk.sim
    app = adsk.core.Application.get()
    sim = adsk.sim.Simulations.get(app.activeDocument)
    model = sim.simulationModels.item(0)
    return model.studies.itemByName(name) if name else model.studies.item(model.studies.count - 1)

def face_info(f):
    g = f.geometry
    bb = f.boundingBox
    t = type(g).__name__
    ext = "bb=(%.2f..%.2f, %.2f..%.2f, %.2f..%.2f)mm" % (bb.minPoint.x*10, bb.maxPoint.x*10, bb.minPoint.y*10, bb.maxPoint.y*10, bb.minPoint.z*10, bb.maxPoint.z*10)
    n = ""
    if t == "Plane":
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = " n=(%.3f,%.3f,%.3f)" % (nv.x, nv.y, nv.z)
    return "%s area=%.3fmm2 %s%s" % (t, f.area*100, ext, n)

def plane_normal(f):
    if not isinstance(f.geometry, adsk.core.Plane):
        return None
    ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
    return nv

def oc(items):
    c = adsk.core.ObjectCollection.create()
    for i in items:
        c.add(i)
    return c

def apply_params(des, d):
    for n, e in d.items():
        des.userParameters.itemByName(n).expression = e
    adsk.doEvents()

def min_wall_axisym(body, R_cm):
    """Min distance between outer skin faces and inner (bore/slot) faces of a sleeve-like body. cm in, mm out."""
    app = adsk.core.Application.get()
    mm = app.measureManager
    inner, outer = [], []
    for f in body.faces:
        n = plane_normal(f)
        if n is not None and abs(abs(n.z) - 1) < 1e-6:
            continue
        bb = f.boundingBox
        ext = max(abs(bb.minPoint.x), abs(bb.maxPoint.x), abs(bb.minPoint.y), abs(bb.maxPoint.y))
        (inner if ext < R_cm - 0.05 else outer).append(f)
    best = (1e9, None)
    for a in outer:
        for b in inner:
            r = mm.measureMinimumDistance(a, b)
            if r.value < best[0]:
                best = (r.value, r)
    v, r = best
    p1, p2 = r.positionOne, r.positionTwo
    return v * 10, (p1.x*10, p1.y*10, p1.z*10), (p2.x*10, p2.y*10, p2.z*10), len(outer), len(inner)

def render_prep(des, root, appearance_hint="Plastic - Matte (Blue)"):
    """Hide sketches/construction geometry, apply a visual appearance, fit view. Returns appearance name."""
    app = adsk.core.Application.get()
    for s in root.sketches:
        s.isVisible = False
    for p in root.constructionPlanes:
        p.isLightBulbOn = False
    lib = app.materialLibraries.itemByName("Fusion Appearance Library")
    ap = None
    if lib:
        try:
            ap = lib.appearances.itemByName(appearance_hint)
        except Exception:
            ap = None
        if not ap:
            for i in range(lib.appearances.count):
                a = lib.appearances.item(i)
                if "Plastic" in a.name and "Matte" in a.name:
                    ap = a
                    break
    name = None
    if ap:
        local = des.appearances.itemByName(ap.name) or des.appearances.addByCopy(ap, ap.name)
        for b in root.bRepBodies:
            b.appearance = local
        name = local.name
    try:
        app.executeTextCommand("NaViewCube.Hide")
    except Exception:
        pass
    app.activeViewport.fit()
    return name

def faces_share_vertex(a, b):
    va = set()
    for v in a.vertices:
        p = v.geometry; va.add((round(p.x, 6), round(p.y, 6), round(p.z, 6)))
    for v in b.vertices:
        p = v.geometry
        if (round(p.x, 6), round(p.y, 6), round(p.z, 6)) in va:
            return True
    return False

def min_dist_groups(ga, gb):
    """Min distance (mm) between two face groups, skipping face pairs that touch. Returns (mm, p1, p2)."""
    mm = adsk.core.Application.get().measureManager
    best = (1e9, None, None)
    for a in ga:
        for b in gb:
            if a == b or faces_share_vertex(a, b):
                continue
            r = mm.measureMinimumDistance(a, b)
            if r.value * 10 < best[0]:
                best = (r.value * 10, r.positionOne, r.positionTwo)
    return best

def fmt_pt(p):
    return "(%.2f, %.2f, %.2f)" % (p.x * 10, p.y * 10, p.z * 10) if p else "-"

def activate_doc(name):
    app = adsk.core.Application.get()
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name == name:
            d.activate()
            adsk.doEvents()
            des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
            return app, des, des.rootComponent
    raise RuntimeError("document not open: " + name)
def poly_xy(sk, root, pts):
    """Closed polygon on an XY-plane sketch. pts = [(x_expr, y_expr), ...] (mm expressions using user params).
    Each vertex is dimensioned from the origin in X and Y, so the sketch is fully constrained and parametric."""
    des = adsk.fusion.Design.cast(root.parentDesign)
    um = des.unitsManager
    ev = lambda e: um.evaluateExpression(e, "mm")  # returns cm
    L = sk.sketchCurves.sketchLines
    d = sk.sketchDimensions
    xs = sk.project(root.yConstructionAxis).item(0)  # x = 0 line
    ys = sk.project(root.xConstructionAxis).item(0)  # y = 0 line
    xs.isConstruction = True; ys.isConstruction = True
    P = [P3.create(ev(x), ev(y), 0) for x, y in pts]
    lines = []
    for i in range(len(P)):
        a = lines[-1].endSketchPoint if lines else P[i]
        b = P[(i + 1) % len(P)] if i < len(P) - 1 else lines[0].startSketchPoint
        lines.append(L.addByTwoPoints(a, b))
    for i, (xe, ye) in enumerate(pts):
        sp = lines[i].startSketchPoint
        g = sp.geometry
        if abs(g.x) < 1e-7:
            sk.geometricConstraints.addCoincident(sp, xs)
        else:
            try:
                dm = d.addDistanceDimension(sk.originPoint, sp, adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation, P3.create(g.x / 2, g.y + 0.5, 0))
                dm.parameter.expression = "abs(" + xe + ")"
            except Exception:
                j = next(k for k in range(i) if pts[k][0] == xe)
                cl = L.addByTwoPoints(lines[j].startSketchPoint, sp); cl.isConstruction = True
                sk.geometricConstraints.addVertical(cl)
        if abs(g.y) < 1e-7:
            sk.geometricConstraints.addCoincident(sp, ys)
        else:
            try:
                dm = d.addDistanceDimension(sk.originPoint, sp, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, P3.create(g.x + 0.5, g.y / 2, 0))
                dm.parameter.expression = "abs(" + ye + ")"
            except Exception:
                j = next(k for k in range(i) if pts[k][1] == ye)
                cl = L.addByTwoPoints(lines[j].startSketchPoint, sp); cl.isConstruction = True
                sk.geometricConstraints.addHorizontal(cl)
    return lines



def add_slot_fillets(des, root):
    """v0.1 rev: round the key-slot inside corners (stress concentration found in FE)."""
    set_params(des, [
        ("slot_end_r", "key_t / 2 - 0.1 mm", "mm", "Radius on the slot's vertical end corners (rev: FE showed a sharp-corner stress peak)"),
        ("slot_floor_r", "1 mm", "mm", "Fillet between slot floor and slot walls (cup-shaped floor, prints without support)"),
    ])
    P = lambda n: des.userParameters.itemByName(n).value
    body = root.bRepBodies.item(0)
    H, Kd, Wk, Tk, li = P("paddle_h"), P("key_slot_d"), P("key_slot_w"), P("key_t"), P("slot_leadin")
    def vert_end(e):
        g = e.geometry
        if not isinstance(g, adsk.core.Line3D):
            return False
        s, t = e.startVertex.geometry, e.endVertex.geometry
        return (abs(s.x - t.x) < 1e-6 and abs(s.y - t.y) < 1e-6 and abs(abs(s.x) - Wk/2) < 1e-6
                and abs(abs(s.y) - Tk/2) < 1e-6 and min(s.z, t.z) >= H - Kd - 1e-6)
    ve = edges_where(body, vert_end)
    print("slot vertical end edges:", ve.count)
    fillet(root, ve, "slot_end_r", "SlotEndRounds")
    def floor_edge(e):
        bb = e.boundingBox
        return abs(bb.minPoint.z - (H - Kd)) < 1e-6 and abs(bb.maxPoint.z - (H - Kd)) < 1e-6
    fe_ = edges_where(body, floor_edge)
    print("slot floor edges:", fe_.count)
    fillet(root, fe_, "slot_floor_r", "SlotFloorFillet")


def _rect_on_xz(sk, w_expr, h_expr, W, H):
    """Rectangle in model XZ plane: bottom edge centred on origin, from z=0 to z=H. Fully constrained."""
    L = sk.sketchCurves.sketchLines
    gc = sk.geometricConstraints
    m2s = sk.modelToSketchSpace
    p = [m2s(P3.create(-W/2, 0, 0)), m2s(P3.create(W/2, 0, 0)), m2s(P3.create(W/2, 0, H)), m2s(P3.create(-W/2, 0, H))]
    ln = [L.addByTwoPoints(p[0], p[1])]
    ln.append(L.addByTwoPoints(ln[0].endSketchPoint, p[2]))
    ln.append(L.addByTwoPoints(ln[1].endSketchPoint, p[3]))
    ln.append(L.addByTwoPoints(ln[2].endSketchPoint, ln[0].startSketchPoint))
    gc.addHorizontal(ln[0]); gc.addHorizontal(ln[2]); gc.addVertical(ln[1]); gc.addVertical(ln[3])
    gc.addMidPoint(sk.originPoint, ln[0])
    d = sk.sketchDimensions
    dw = d.addDistanceDimension(ln[0].startSketchPoint, ln[0].endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, m2s(P3.create(0, 0, -1)))
    dw.parameter.expression = w_expr
    dh = d.addDistanceDimension(ln[1].startSketchPoint, ln[1].endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, m2s(P3.create(W/2 + 1, 0, H/2)))
    dh.parameter.expression = h_expr
    return ln


def _teardrop_on_xz(sk, dia_expr, zc_expr, R, ZC):
    """Teardrop (circle + 45 deg roof) in model XZ plane, centred on x=0. Fully constrained."""
    gc = sk.geometricConstraints
    d = sk.sketchDimensions
    m2s = sk.modelToSketchSpace
    c = sk.sketchCurves.sketchCircles.addByCenterRadius(m2s(P3.create(0, 0, ZC)), R)
    s2 = math.sqrt(2)
    t1 = m2s(P3.create(R/s2, 0, ZC + R/s2)); t2 = m2s(P3.create(-R/s2, 0, ZC + R/s2)); a = m2s(P3.create(0, 0, ZC + R*s2))
    L = sk.sketchCurves.sketchLines
    l1 = L.addByTwoPoints(t1, a)
    l2 = L.addByTwoPoints(l1.endSketchPoint, t2)
    l3 = L.addByTwoPoints(l2.endSketchPoint, l1.startSketchPoint)
    gc.addCoincident(l1.startSketchPoint, c)
    gc.addCoincident(l2.endSketchPoint, c)
    gc.addTangent(l1, c)
    gc.addTangent(l2, c)
    gc.addHorizontal(l3)
    axis = L.addByTwoPoints(sk.originPoint, m2s(P3.create(0, 0, ZC)))
    axis.isConstruction = True
    gc.addVertical(axis)
    gc.addCoincident(axis.endSketchPoint, c.centerSketchPoint)
    dd = d.addDiameterDimension(c, m2s(P3.create(R, 0, ZC - R)))
    dd.parameter.expression = dia_expr
    dz = d.addDistanceDimension(axis.startSketchPoint, axis.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, m2s(P3.create(-R - 2, 0, ZC / 2)))
    dz.parameter.expression = zc_expr
    # apex at r*sqrt(2) above the centre <=> roof lines at 45 deg to horizontal
    da = d.addDistanceDimension(c.centerSketchPoint, l1.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, m2s(P3.create(R + 2, 0, ZC + R)))
    da.parameter.expression = dia_expr + " / 2 * sqrt(2)"
    return c


def run(_context: str):
    app, des, root = ctx()
    if root.bRepBodies.count or des.userParameters.count:
        app, des, root = new_design("Key turner")
    set_params(des, [
        ("paddle_w", "95 mm", "mm", "Paddle length gripped by the hand = ANSUR II hand breadth + 8-9 mm, rounded to 5 mm (M: all-subjects median 86 mm)"),
        ("paddle_h", "66 mm", "mm", "Paddle height: holds key slot + finger hole with >= 7 mm web between them (design estimate)"),
        ("paddle_t", "18 mm", "mm", "Paddle thickness (rev3: 14 -> 18 mm after FE showed slot-wall bending across layers; design estimate)"),
        ("key_t", "2.4 mm", "mm", "Key slot thickness = 2.0 mm KW1 blade thickness (single retailer listing) + 0.4 mm clearance. MEASURE YOUR KEY"),
        ("key_slot_w", "32 mm", "mm", "Key slot width, fits the bow of common house keys (design estimate - measure your key)"),
        ("key_slot_d", "18 mm", "mm", "Key slot depth (rev2: 24 -> 18 mm to shorten the slot-wall lips; design estimate)"),
        ("slot_leadin", "1 mm", "mm", "45 deg chamfer around slot opening for easier insertion"),
        ("finger_d", "22 mm", "mm", "Finger hole diameter (design estimate; no finger-breadth data in ANSUR II)"),
        ("finger_z", "finger_d / 2 + 6 mm", "mm", "Finger hole centre height: 6 mm of material under the hole"),
        ("top_r", "8 mm", "mm", "Top corner radius"),
        ("base_ch", "3 mm", "mm", "45 deg chamfer on bottom corners (a round here would overhang near the bed)"),
        ("edge_r", "2 mm", "mm", "Comfort fillet on all non-bed outer edges"),
        ("hole_r", "1.5 mm", "mm", "Comfort fillet on finger-hole edges"),
    ])
    P = lambda n: des.userParameters.itemByName(n).value
    W, H, T = P("paddle_w"), P("paddle_h"), P("paddle_t")
    xz = root.xZConstructionPlane

    sk = root.sketches.add(xz); sk.name = "PaddleProfile"
    _rect_on_xz(sk, "paddle_w", "paddle_h", W, H)
    body_f = extrude(root, sk.profiles.item(0), "paddle_t", name="Paddle", symmetric=True)
    body = body_f.bodies.item(0); body.name = "KeyTurner"

    def y_edge_at(x, z):
        def f(e):
            g = e.geometry
            if not isinstance(g, adsk.core.Line3D):
                return False
            s, t = e.startVertex.geometry, e.endVertex.geometry
            return abs(s.x - t.x) < 1e-6 and abs(s.z - t.z) < 1e-6 and abs(s.x - x) < 1e-6 and abs(s.z - z) < 1e-6
        return f
    tops = adsk.core.ObjectCollection.create()
    for x in (W/2, -W/2):
        for e in edges_where(body, y_edge_at(x, H)):
            tops.add(e)
    fillet(root, tops, "top_r", "TopCornerRounds")
    bots = adsk.core.ObjectCollection.create()
    for x in (W/2, -W/2):
        for e in edges_where(body, y_edge_at(x, 0)):
            bots.add(e)
    chamfer(root, bots, "base_ch", "BaseCornerChamfers")

    sf = root.sketches.add(xz); sf.name = "FingerHole"
    _teardrop_on_xz(sf, "finger_d", "finger_z", P("finger_d")/2, P("finger_z"))
    profs = adsk.core.ObjectCollection.create()
    for i in range(sf.profiles.count):
        profs.add(sf.profiles.item(i))
    ex = root.features.extrudeFeatures
    hi = ex.createInput(profs, FO.CutFeatureOperation)
    hi.setSymmetricExtent(VI.createByString("paddle_t + 2 mm"), True)
    hf = ex.add(hi); hf.name = "TeardropFingerHole"

    top_pl = offset_plane(root, root.xYConstructionPlane, "paddle_h", "TopPlane")
    ss = root.sketches.add(top_pl); ss.name = "KeySlot"
    center_rect(ss, "key_slot_w", "key_t", 3.2, 0.24)
    si = ex.createInput(ss.profiles.item(0), FO.CutFeatureOperation)
    si.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(VI.createByString("key_slot_d")), adsk.fusion.ExtentDirections.NegativeExtentDirection)
    sf_ = ex.add(si); sf_.name = "KeySlotCut"

    # lead-in chamfer around slot opening: slot edges lying in the top plane z=H
    Wk, Tk = P("key_slot_w"), P("key_t")
    def slot_top(e):
        s, t = e.startVertex.geometry, e.endVertex.geometry
        return abs(s.z - H) < 1e-6 and abs(t.z - H) < 1e-6 and max(abs(s.x), abs(t.x)) <= Wk/2 + 1e-6 and max(abs(s.y), abs(t.y)) <= Tk/2 + 1e-6
    chamfer(root, edges_where(body, slot_top), "slot_leadin", "SlotLeadIn")

    # comfort fillets: edges on the two big faces (|y| = T/2), excluding bed edges and finger-hole edges
    def big_face_outer(e):
        bb = e.boundingBox
        on_face = abs(abs(bb.minPoint.y) - T/2) < 1e-6 and abs(abs(bb.maxPoint.y) - T/2) < 1e-6
        if not on_face or bb.maxPoint.z < 1e-6:
            return False
        inside_hole = max(abs(bb.minPoint.x), abs(bb.maxPoint.x)) < P("finger_d") and bb.maxPoint.z < P("finger_z") + P("finger_d")
        return not inside_hole
    fillet(root, edges_where(body, big_face_outer), "edge_r", "OuterComfortFillets")
    def hole_edge(e):
        bb = e.boundingBox
        on_face = abs(abs(bb.minPoint.y) - T/2) < 1e-6 and abs(abs(bb.maxPoint.y) - T/2) < 1e-6
        return on_face and max(abs(bb.minPoint.x), abs(bb.maxPoint.x)) < P("finger_d") and bb.maxPoint.z < P("finger_z") + P("finger_d") and bb.minPoint.z > 1e-6
    fillet(root, edges_where(body, hole_edge), "hole_r", "FingerHoleFillets")
    add_slot_fillets(des, root)

    for s in root.sketches:
        print("sketch", s.name, "fullyConstrained=", s.isFullyConstrained)
    timeline_report(des)
    body_report(root)
    app.activeViewport.fit()
