#!/usr/bin/env python3
"""F-V-JOINTS: the three Sigma_8 joint constants {2,2,4}/{4,4}/{6,2} must be
reproduced orbit-by-orbit by an INDEPENDENT numeric path -- the midpoint ladder
with two-level h^2 Richardson extrapolation (4 L(dv/2) - L(dv))/3.

Criterion 3e-6.  Expected match count 22 + 7 + 4 = 33.

Matching is on the DIHEDRAL CANONICAL FORM of the block set, never on orbit
index: the ladder enumerates orbits in its own order and picks its own
representatives, and index matching produced a false FAIL in round 136."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, canon_key, check, require_count, finish

LAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "measurements", "ladder")
TOL = 3e-6
JOBS = [("j224", 8, "lj_224_dv0.1.json",     "lj_224_dv0.05.json",     22),
        ("j44",  8, "gpu_lj_44_dv0.1.json",      "gpu_lj_44_dv0.05.json",   7),
        ("j62",  8, "gpu_lj_62_dv0.1.json",  "gpu_lj_62_dv0.05.json",   4)]

def load_lad(f, n):
    d = json.load(open(os.path.join(LAD, f)))
    return {canon_key(e["blocks"], n): e["value"] for e in d.values()}

matched = 0
for cls, n, f_coarse, f_fine, want in JOBS:
    ex = json.load(open(os.path.join(CONST, cls, "values.json")))["orbit_values"]
    try:
        c, f = load_lad(f_coarse, n), load_lad(f_fine, n)
    except FileNotFoundError as e:
        print(f"  NOT-APPLICABLE  {cls}: missing ladder file {e.filename}")
        check(f"F-V-JOINTS {cls}", False); continue
    keys = set(ex) & set(c) & set(f)
    worst, wk = 0.0, None
    for k in keys:
        rich = (4 * f[k] - c[k]) / 3
        d = abs(rich - float(Q(ex[k]["value"])))
        if d > worst: worst, wk = d, k
    if len(keys) < want:
        print(f"  NOT-APPLICABLE  F-V-JOINTS {cls}: matched {len(keys)}/{want} orbits")
        check(f"F-V-JOINTS {cls}", False); continue
    matched += len(keys)
    check(f"F-V-JOINTS {cls:<6}", worst < TOL,
          f"{len(keys)}/{want} orbits, max|Richardson-exact| = {worst:.3e} "
          f"(tol {TOL:.0e}) at {wk}")
require_count("F-V-JOINTS orbit coverage", matched, 33)
finish("F-V-JOINTS")
