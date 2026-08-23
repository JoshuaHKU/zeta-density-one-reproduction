#!/usr/bin/env python3
"""Exact value of a block-partition class, summed over its dihedral placement
classes with multiplicities.  Usage:
    python3 run_class.py '{2,2,4}' [--jobs N] [--probe]
--probe times ONE F-CYC term of the first placement class and stops."""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ratbackend import F, BACKEND
from class_integral import class_integral, class_terms, one_term

CYCLE = {"{2,2,4}": 8, "{4,4}": 8, "{6,2}": 8, "{2^4}": 8, "{5,2}": 7, "{8}": 8}

def load(label):
    if label == "{8}":
        return [{"size": 1, "rep": [[0, 1, 2, 3, 4, 5, 6, 7]]}], 1
    for cand in (os.environ.get("BLOCK_CLASSES"),
                 os.path.join(HERE, "..", "data", "block_classes.json"),
                 os.path.join(HERE, "block_classes.json"),
                 os.path.join(os.environ.get("OUTDIR", HERE), "block_classes.json")):
        if cand and os.path.exists(cand):
            cls = json.load(open(cand)); break
    else:
        raise SystemExit("block_classes.json not found; set BLOCK_CLASSES")
    c = [x for x in cls if x["label"] == label][0]
    return c["orbits"], c["total"]

if __name__ == "__main__":
    label = sys.argv[1]
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    orbits, total = load(label)
    k = CYCLE[label]
    print(f"backend {BACKEND}   {label} on the {k}-cycle: "
          f"{len(orbits)} placement classes, {total} placements", flush=True)
    if "--probe" in sys.argv:
        for oi, o in enumerate(orbits[:1]):
            ts = class_terms([list(b) for b in o["rep"]], k)
            n = ts[0][3] + len(ts[0][1])
            print(f"  {len(ts)} F-CYC terms, free {ts[0][3]}, mono cols {ts[0][2]}, "
                  f"ambient R^{n}", flush=True)
            t0 = time.time(); one_term((ts[0][1], ts[0][2], ts[0][3]))
            dt = time.time() - t0
            nterm = len(ts) * max(1, 2 ** len(ts[0][2]))
            print(f"  first term {dt:.2f}s -> class ~{len(ts)*dt/60:.1f} min single-core"
                  f", all {len(orbits)} classes ~{len(orbits)*len(ts)*dt/3600/jobs:.2f} h "
                  f"on {jobs} cores", flush=True)
        raise SystemExit
    tot = F(0); rows = []
    for oi, o in enumerate(orbits):
        t0 = time.time()
        v = class_integral([list(b) for b in o["rep"]], k, jobs=jobs)
        tot += o["size"] * v
        rows.append([oi, o["size"], str(v), float(v)])
        print(f"  R{oi:<3} size {o['size']:<3} {str(v):<18} {float(v):+.10f}  "
              f"{o['rep']}  {time.time()-t0:.0f}s", flush=True)
    print(f"\n  {label} = {tot} = {float(tot):.10f}", flush=True)
    out = os.path.join(os.environ.get("OUTDIR", HERE),
                       f"values_{label.replace('{','').replace('}','').replace(',','_')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"label": label, "orbits": rows, "total": str(tot)}, open(out, "w"), indent=1)
    print(f"  written {out}")
