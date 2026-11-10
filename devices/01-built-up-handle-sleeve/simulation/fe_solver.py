"""Linear static stress FE: gmsh (tet mesh from STEP) + scikit-fem (P2 tets).
usage: python fe.py <config.json>   units: mm, N, MPa"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fea"))
import numpy as np
import gmsh
from skfem import MeshTet, Basis, FacetBasis, ElementVector, ElementTetP2, asm, LinearForm, condense, solve
from skfem.models.elasticity import linear_elasticity, lame_parameters
from skfem.helpers import dot


def mesh_step(step, h, out, curv=0):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
    gmsh.model.occ.importShapes(step)
    gmsh.model.occ.synchronize()
    vols = gmsh.model.getEntities(3)
    gmsh.model.addPhysicalGroup(3, [v[1] for v in vols], 1)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.MeshSizeMin", h / 4)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", curv)
    gmsh.option.setNumber("Mesh.Algorithm3D", 1)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.model.mesh.generate(3)
    gmsh.model.mesh.optimize("Netgen")
    gmsh.write(out)
    gmsh.finalize()


def boundary_info(m):
    bf = m.boundary_facets()
    P = m.p[:, m.facets[:, bf]]  # 3 coords x 3 verts x nf
    mid = P.mean(axis=1)
    n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0], axis=0)
    area = 0.5 * np.linalg.norm(n, axis=0)
    n = n / (2 * area)
    t = m.f2t[0, bf]
    cen = m.p[:, m.t[:, t]].mean(axis=1)
    flip = np.sum(n * (mid - cen), axis=0) < 0
    n[:, flip] *= -1
    return bf, mid, n, area


def env(mid, n, extra):
    x, y, z = mid
    e = dict(x=x, y=y, z=z, r=np.hypot(x, y), nx=n[0], ny=n[1], nz=n[2], np=np, abs=np.abs)
    e.update(extra)
    return e


def rigid_modes(ib):
    N = ib.N
    comp = np.zeros(N, dtype=int)
    for k in range(3):
        comp[ib.nodal_dofs[k]] = k
        if ib.edge_dofs.size:
            comp[ib.edge_dofs[k]] = k
    X = ib.doflocs
    B = np.zeros((N, 6))
    for k in range(3):
        B[comp == k, k] = 1.0
    x, y, z = X
    c0, c1, c2 = comp == 0, comp == 1, comp == 2
    B[c0, 3] = -y[c0]; B[c1, 3] = x[c1]          # rot about z
    B[c1, 4] = -z[c1]; B[c2, 4] = y[c2]          # rot about x
    B[c2, 5] = -x[c2]; B[c0, 5] = z[c0]          # rot about y
    return B


def amg_solve(ib, K, f, fixed):
    import pyamg
    A, b, x0, I = condense(K, f, D=fixed)
    B = rigid_modes(ib)[I]
    ml = pyamg.smoothed_aggregation_solver(A.tocsr(), B=B, symmetry="symmetric", max_coarse=500)
    res = []
    xi = ml.solve(b, tol=1e-10, accel="cg", maxiter=800, residuals=res)
    rel = np.linalg.norm(b - A @ xi) / np.linalg.norm(b)
    assert rel < 1e-6, "AMG-CG did not converge: rel residual %.2e after %d its" % (rel, len(res))
    x = x0.copy()
    x[I] = xi
    print("      AMG-CG: %d iterations, rel residual %.1e" % (len(res), rel), flush=True)
    return x


def total_reaction(ib, reac):
    out = []
    for i in range(3):
        s = reac[ib.nodal_dofs[i]].sum()
        if ib.edge_dofs.size:
            s += reac[ib.edge_dofs[i]].sum()
        out.append(float(s))
    return out


def run(cfg):
    E, nu, Y, U = cfg["E"], cfg["nu"], cfg["yield"], cfg["uts"]
    tag = cfg["name"]
    outdir = cfg["outdir"]
    os.makedirs(outdir, exist_ok=True)
    msh = os.path.join(outdir, tag + "_h%.1f.msh" % cfg["h"])
    t0 = time.time()
    mesh_step(cfg["step"], cfg["h"], msh, cfg.get("curv", 0))
    m = MeshTet.load(msh)
    e = ElementVector(ElementTetP2())
    ib = Basis(m, e)
    lam, mu = lame_parameters(E, nu)
    K = asm(linear_elasticity(lam, mu), ib)
    bf, mid, nrm, area = boundary_info(m)
    zmin, zmax = m.p[2].min(), m.p[2].max()
    extra = dict(zmin=zmin, zmax=zmax, **cfg.get("vars", {}))
    E_ = env(mid, nrm, extra)
    results = []
    print("[%s] h=%.2f mm: %d nodes, %d tets, %d DOF (P2), %d boundary facets, z %.2f..%.2f (%.1fs)" % (
        tag, cfg["h"], m.p.shape[1], m.t.shape[1], ib.N, len(bf), zmin, zmax, time.time() - t0))
    for case in cfg["cases"]:
        f = np.zeros(ib.N)
        applied = np.zeros(3)
        notes = []
        for ld in case["loads"]:
            sel = np.asarray(eval(ld["select"], {}, E_), dtype=bool)
            fac = bf[sel]
            A = area[sel].sum()
            assert len(fac) > 0, "empty load selection: " + ld["select"]
            fb = FacetBasis(m, e, facets=fac)
            if "force" in ld:
                tv = np.array(ld["force"], float) / A

                @LinearForm
                def trac(v, w, tv=tv):
                    return tv[0] * v[0] + tv[1] * v[1] + tv[2] * v[2]
                f += asm(trac, fb)
                applied += np.array(ld["force"], float)
                notes.append("force %s N as uniform traction over %.1f mm2 (%d facets) [%s]" % (ld["force"], A, len(fac), ld["select"]))
            elif "squeeze" in ld:
                # each side gets its own pressure so its resultant along the axis is exactly the squeeze force
                ax = np.array(ld["axis"], float)
                ax /= np.linalg.norm(ax)
                proj = np.sum(nrm * ax[:, None], axis=0)
                ps = []
                for side in (proj > 0, proj < 0):
                    s2 = sel & side
                    p = ld["squeeze"] / np.abs(proj[s2] * area[s2]).sum()
                    fb2 = FacetBasis(m, e, facets=bf[s2])

                    # traction -p (n.a) a : directional squeeze, resultant purely along the axis
                    @LinearForm
                    def pres(v, w, p=p, ax=ax):
                        na = w.n[0] * ax[0] + w.n[1] * ax[1] + w.n[2] * ax[2]
                        return -p * na * (ax[0] * v[0] + ax[1] * v[1] + ax[2] * v[2])
                    f += asm(pres, fb2)
                    ps.append(p)
                notes.append("squeeze %.0f N per side along %s -> %.4f / %.4f MPa over %.1f mm2 (%d facets) [%s]" % (
                    ld["squeeze"], ld["axis"], ps[0], ps[1], A, len(fac), ld["select"]))
        fixed = np.array([], dtype=int)
        if "fixed" in case:
            sel = np.asarray(eval(case["fixed"], {}, E_), dtype=bool)
            assert sel.any(), "empty fixed selection"
            fixed = ib.get_dofs(facets=bf[sel]).all()
            notes.append("fixed all DOF on %d facets (%.1f mm2) [%s]" % (sel.sum(), area[sel].sum(), case["fixed"]))
        if case.get("rigid321"):
            bv = np.unique(m.facets[:, bf[np.abs(mid[2] - zmin) < 1e-6]])
            P = m.p[:, bv]
            A_, B_, C_ = bv[np.argmax(P[0])], bv[np.argmin(P[0])], bv[np.argmax(P[1])]
            nd = ib.nodal_dofs
            fixed = np.concatenate([nd[:, A_], nd[1:, B_], nd[2:, C_]])
            notes.append("3-2-1 rigid-body supports at bottom vertices %s, %s, %s" % (
                m.p[:, A_].round(2).tolist(), m.p[:, B_].round(2).tolist(), m.p[:, C_].round(2).tolist()))
        t1 = time.time()
        x = amg_solve(ib, K, f, fixed)
        R = total_reaction(ib, K @ x - f)
        notes.append("solve %.1fs" % (time.time() - t1))
        u = ib.interpolate(x)
        G = u.grad
        eps = 0.5 * (G + np.transpose(G, (1, 0, 2, 3)))
        tr = eps[0, 0] + eps[1, 1] + eps[2, 2]
        S = 2 * mu * eps
        for k in range(3):
            S[k, k] += lam * tr
        vm = np.sqrt(0.5 * ((S[0, 0] - S[1, 1]) ** 2 + (S[1, 1] - S[2, 2]) ** 2 + (S[2, 2] - S[0, 0]) ** 2)
                     + 3 * (S[0, 1] ** 2 + S[1, 2] ** 2 + S[2, 0] ** 2))
        X = ib.mapping.F(ib.X)
        vm_raw = float(vm.max())
        excl = np.zeros(vm.shape, dtype=bool)
        if case.get("rigid321"):
            for node in (A_, B_, C_):
                d = np.sqrt(((X - m.p[:, node][:, None, None]) ** 2).sum(axis=0))
                excl |= d < cfg.get("support_excl", 4.0)
            notes.append("peak reported outside %.1f mm of the 3 point supports (raw peak incl. supports %.3f MPa); %d of %d integration points excluded" % (
                cfg.get("support_excl", 4.0), vm_raw, excl.sum(), excl.size))
        vm = np.where(excl, 0.0, vm)
        i = np.unravel_index(np.argmax(vm), vm.shape)
        loc = X[:, i[0], i[1]]
        s1 = np.linalg.eigvalsh(np.moveaxis(S, (0, 1), (-2, -1)))[..., -1]
        umax = np.sqrt(x[ib.nodal_dofs[0]] ** 2 + x[ib.nodal_dofs[1]] ** 2 + x[ib.nodal_dofs[2]] ** 2).max()
        r = dict(preset=tag, case=case["name"], h=cfg["h"], dofs=int(ib.N), tets=int(m.t.shape[1]),
                 vm_max=float(vm.max()), vm_p999=float(np.percentile(vm, 99.9)),
                 vm_loc=[round(float(v), 2) for v in loc], s1_max=float(np.where(excl, -1e9, s1).max()), umax=float(umax), vm_raw=vm_raw,
                 applied=applied.tolist(), reaction_sum=[round(v, 4) for v in R],
                 SF_yield=float(Y / vm.max()), SF_uts=float(U / vm.max()), notes=notes)
        results.append(r)
        print("  %-34s vm_max=%.3f MPa at %s | p99.9=%.3f | s1_max=%.3f | umax=%.4f mm | SF vs %.0f MPa = %.2f | SF vs %.0f MPa = %.2f | reactions %s" % (
            case["name"], r["vm_max"], r["vm_loc"], r["vm_p999"], r["s1_max"], r["umax"], Y, r["SF_yield"], U, r["SF_uts"], r["reaction_sum"]))
        for nt in notes:
            print("      ", nt)
        if cfg.get("plot"):
            png = os.path.join(outdir, "%s_%s.png" % (tag, case["id"]))
            plot(m, vm, png, "%s - %s\nmax von Mises %.2f MPa, safety factor %.1f vs %.0f MPa" % (tag, case["name"], vm.max(), Y / vm.max(), Y))
    json.dump(results, open(os.path.join(outdir, "%s_h%.1f_results.json" % (tag, cfg["h"])), "w"), indent=1)
    return results


def plot(m, vm, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    bf = m.boundary_facets()
    el_vm = vm.max(axis=1)
    tri = m.facets[:, bf].T
    tv = el_vm[m.f2t[0, bf]]
    pts = m.p.T
    fig = plt.figure(figsize=(8, 7), dpi=110)
    ax = fig.add_subplot(111, projection="3d")
    cmap = plt.get_cmap("jet")
    norm = matplotlib.colors.Normalize(0, el_vm.max())
    ax.add_collection3d(Poly3DCollection(pts[tri], facecolors=cmap(norm(tv)), edgecolor="none"))
    s = (pts.max(0) - pts.min(0)).max() / 2
    for i, lim in enumerate([ax.set_xlim, ax.set_ylim, ax.set_zlim]):
        c = (pts[:, i].max() + pts[:, i].min()) / 2
        lim(c - s, c + s)
    ax.view_init(elev=22, azim=-55)
    ax.set_axis_off()
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    fig.colorbar(sm, ax=ax, shrink=0.6, label="von Mises stress, MPa (element max)")
    ax.set_title(title, fontsize=10)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    cfg = json.load(open(sys.argv[1]))
    allr = []
    for preset in cfg["presets"]:
        c = dict(cfg)
        c.update(preset)
        allr += run(c)
    worst = min(allr, key=lambda r: r["SF_yield"])
    print("WORST: %s / %s h=%.1f vm_max=%.3f MPa SF_yield=%.2f" % (worst["preset"], worst["case"], worst["h"], worst["vm_max"], worst["SF_yield"]))
