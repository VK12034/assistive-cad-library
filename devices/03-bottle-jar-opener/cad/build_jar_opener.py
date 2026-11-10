"""Bottle and jar opener v0.1 - Fusion API build script (untested v0.1, not a medical device).
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




def run(_context: str):
    app, des, root = ctx()
    if root.bRepBodies.count or des.userParameters.count:
        app, des, root = new_design("Bottle and jar opener")
    set_params(des, [
        ("cap_max", "82 mm", "mm", "Largest cap the jaw seats: 82 mm, largest regular twist-off lug cap in a closure maker's size list (38-82 mm)"),
        ("cap_min", "28 mm", "mm", "Smallest cap: 28 mm PCO 1881 bottle neck finish (cap outer diameter not published - slightly larger)"),
        ("v_half", "30 deg", "deg", "V half-angle. A cap of diameter D seats D/(2 sin(v_half)) from the apex; 30 deg -> seat distance = D (design choice)"),
        ("jaw_len", "cap_max / (2 * sin(v_half)) + 10 mm", "mm", "V depth: seat of the largest cap + 10 mm of jaw beyond it"),
        ("jaw_wall", "10 mm", "mm", "Jaw arm thickness measured perpendicular to the V wall (design estimate; checked in FE)"),
        ("handle_len", "95 mm", "mm", "Handle length = ANSUR II hand breadth + 8-9 mm, rounded to 5 mm (M: all-subjects median 86 mm)"),
        ("handle_w", "30 mm", "mm", "Handle width (design estimate)"),
        ("plate_t", "10 mm", "mm", "Plate thickness = height of jaw contact on the cap skirt (design estimate)"),
        ("apex_r", "2 mm", "mm", "Radius at the V apex (removes a sharp inside corner)"),
        ("corner_r", "5 mm", "mm", "Radius on outer vertical corners"),
        ("top_r", "1.5 mm", "mm", "Comfort fillet around the top face (bed side stays sharp for adhesion)"),
    ])
    xy = root.xYConstructionPlane
    sk = root.sketches.add(xy); sk.name = "OpenerOutline"
    mouth = "jaw_len * tan(v_half)"                       # half-width of the V at the mouth
    outer = "(jaw_len * tan(v_half) + jaw_wall / cos(v_half))"  # outer arm half-width at the mouth
    xb = "((handle_w / 2 - jaw_wall / cos(v_half)) / tan(v_half))"  # where the outer arm meets the handle edge
    pts = [
        ("jaw_len", outer), ("jaw_len", mouth), ("0 mm", "0 mm"), ("jaw_len", "-" + mouth), ("jaw_len", "-" + outer),
        (xb, "-handle_w / 2"), ("-handle_len", "-handle_w / 2"), ("-handle_len", "handle_w / 2"), (xb, "handle_w / 2"),
    ]
    poly_xy(sk, root, pts)
    print("profiles:", sk.profiles.count, "fullyConstrained:", sk.isFullyConstrained)
    body = extrude(root, sk.profiles.item(0), "plate_t", name="Plate").bodies.item(0)
    body.name = "JarOpener"
    T = des.userParameters.itemByName("plate_t").value

    def vert(e):
        s, t = e.startVertex.geometry, e.endVertex.geometry
        return isinstance(e.geometry, adsk.core.Line3D) and abs(s.x - t.x) < 1e-6 and abs(s.y - t.y) < 1e-6
    apex = edges_where(body, lambda e: vert(e) and abs(e.startVertex.geometry.x) < 1e-6 and abs(e.startVertex.geometry.y) < 1e-6)
    fillet(root, apex, "apex_r", "ApexRadius")
    others = edges_where(body, lambda e: vert(e) and not (abs(e.startVertex.geometry.x) < 1e-3 and abs(e.startVertex.geometry.y) < 1e-3))
    # mouth inner corners (where the V wall meets the mouth face) get the same radius as outer corners
    fillet(root, others, "corner_r", "CornerRadii")
    top = edges_where(body, lambda e: abs(e.boundingBox.minPoint.z - T) < 1e-6 and abs(e.boundingBox.maxPoint.z - T) < 1e-6)
    fillet(root, top, "top_r", "TopComfortFillet")
    timeline_report(des)
    body_report(root)
    app.activeViewport.fit()
