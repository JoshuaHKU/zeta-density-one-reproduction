#!/usr/bin/env python3
"""F-V-25: second path for {2^5}, the Sigma_10 component whose second_path was
PENDING through r140.

All five blocks are pairs, so the ladder integrand is R^5 with a |v| monomial
per pair and no F-CYC expansion -- cheap enough on the V100 that the full
79-orbit table runs at three step sizes in seconds.  Both levels are checked:

  * per orbit, h^2 Richardson (4 L(dv/2) - L(dv))/3 against the exact rational,
    criterion 3e-6 (the same criterion as F-V-JOINTS);
  * at bundle level, against 10531/13860.

The bundle deviation -4.22e-6 reproduces the math-side r136 figure (-4.2e-6),
which until r141 lived only in a log and not in the package."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, canon_key, check, require_count, finish

LAD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "measurements", "ladder")
TOL, BTOL, NORB = 3e-6, 1e-5, 79
v = json.load(open(os.path.join(CONST, "p25", "values.json")))
ex, exact = v["orbit_values"], float(Q(v["total"]))

def lad(f):
    return {canon_key(e["blocks"], 10): e["value"]
            for e in json.load(open(os.path.join(LAD, f))).values()}
c, f = lad("gpu_lj_2p5_dv0.1.json"), lad("gpu_lj_2p5_dv0.05.json")
keys = set(ex) & set(c) & set(f)
if len(keys) < NORB:
    print(f"  NOT-APPLICABLE  F-V-25: matched {len(keys)}/{NORB} orbits")
    sys.exit(1)
worst, bundle = 0.0, 0.0
for k in keys:
    r = (4 * f[k] - c[k]) / 3
    bundle += r * ex[k]["size"]
    worst = max(worst, abs(r - float(Q(ex[k]["value"]))))
check("F-V-25 per orbit", worst < TOL,
      f"{len(keys)}/{NORB} orbits, max|Richardson-exact| = {worst:.3e} (tol {TOL:.0e})")
check("F-V-25 bundle", abs(bundle - exact) < BTOL,
      f"ladder {bundle:.9f} vs exact {v['total']} = {exact:.9f}  "
      f"dev {bundle-exact:+.2e}  (math-side r136 reported -4.2e-6)")
check("F-V-25 Richardson is what buys the accuracy",
      abs(bundle - exact) < abs(sum(f[k] * ex[k]["size"] for k in keys) - exact) / 100,
      "single-level dv=0.05 is off by +8.4e-3; the h^2 extrapolation is not cosmetic")
require_count("F-V-25 checks", 3, 3)
finish("F-V-25")
