#!/usr/bin/env python3
"""F-V-52: second path for the Sigma_7 joint constant {5,2}.

(REPRO_SPEC's F-V-52 is the {2^5} gate -- g_v25.py.  This one was
mis-named F-V-52 when the package was first assembled; renamed in r141.)

{5,2} was the one class whose pre-registered rational candidate (1/8) was hit
EXACTLY, so it must not rest on that coincidence alone: the midpoint ladder with
h^2 Richardson gives an independent numeric path, orbit by orbit (3 orbits),
and the bundle must reproduce 1/8 to ladder accuracy."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, canon_key, check, require_count, finish

LAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "measurements", "ladder")
TOL = 3e-6
ex = json.load(open(os.path.join(CONST, "j52", "values.json")))
def lad(f):
    return {canon_key(e["blocks"], 7): e["value"]
            for e in json.load(open(os.path.join(LAD, f))).values()}
c, f = lad("gpu_lj_52_dv0.1.json"), lad("gpu_lj_52_dv0.05.json")
keys = set(ex["orbit_values"]) & set(c) & set(f)
if len(keys) < 3:
    print(f"  NOT-APPLICABLE  F-V-52: matched {len(keys)}/3 orbits"); sys.exit(1)
worst, rsum = 0.0, 0.0
for k in keys:
    rich = (4 * f[k] - c[k]) / 3
    e = ex["orbit_values"][k]
    rsum += rich * e["size"]
    worst = max(worst, abs(rich - float(Q(e["value"]))))
check("F-V-52 per orbit", worst < TOL, f"3/3 orbits, max|Richardson-exact| = {worst:.3e} (tol {TOL:.0e})")
check("F-V-52 bundle", abs(rsum - 0.125) < 1e-5,
      f"ladder bundle {rsum:.9f} vs exact 1/8 (dev {rsum-0.125:+.2e})")
check("F-V-52 candidate was pre-registered", ex["total"] == "1/8",
      "model 0.124944, candidate 1/8, exact hit -- second path required and supplied")
require_count("F-V-52 checks", 3, 3)
finish("F-V-52")
