import csv, sys, statistics
d = sys.argv[1]
cols = ["handlength","handbreadth","handcircumference","palmlength","thumbtipreach","wristcircumference"]
def pct(v, p):
    v = sorted(v); k = (len(v)-1)*p/100; f = int(k); c = min(f+1, len(v)-1)
    return v[f] + (v[c]-v[f])*(k-f)
allrows = {c: [] for c in cols}
for s in ["MALE","FEMALE"]:
    with open(f"{d}/ANSUR_II_{s}_Public.csv", encoding="latin-1") as f:
        rows = list(csv.DictReader(f))
    print(s, "n =", len(rows))
    for c in cols:
        if c not in rows[0]:
            print("  missing", c); continue
        v = [float(r[c]) for r in rows]
        allrows[c] += v
        print(f"  {c:20s} p5={pct(v,5):.1f} p50={pct(v,50):.1f} p95={pct(v,95):.1f} mean={statistics.mean(v):.1f}")
print("COMBINED n =", len(allrows["handlength"]))
for c in cols:
    v = allrows[c]
    if v: print(f"  {c:20s} p5={pct(v,5):.1f} p50={pct(v,50):.1f} p95={pct(v,95):.1f}")
