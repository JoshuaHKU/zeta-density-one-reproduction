#!/usr/bin/env python3
"""Per-term-orbit gate for the pure classes C_7 and C_8.

run_pure.py originally persisted only the bundle value; REPRO_SPEC sec 7 requires
the 685 + 6027 per-orbit rows so a referee can spot-check one F-CYC term orbit
instead of only the total.  They were recomputed with run_pure_rows.py, which
re-derives the same dihedral quotient.  This gate reconstitutes the bundle from
the rows and checks the term bookkeeping."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, check, require_count, finish

WANT = {"c7": ("-17/360", 685, 9366), "c8": ("157/4032", 6027, 94586)}
n = 0
for cls, (tot, norb, nterm) in WANT.items():
    f = os.path.join(CONST, cls, "term_orbits.json")
    if not os.path.exists(f):
        print(f"  NOT-APPLICABLE  {cls} term orbits: {f} absent (run still out)")
        check(f"{cls} term orbits", False); continue
    d = json.load(open(f))
    rec = sum(Q(v["value"]) * v["weight"] for v in d["orbit_values"].values())
    ok = (str(rec) == tot == d["total"] and len(d["orbit_values"]) == norb
          and d["fcyc_terms"] == nterm
          and all(v["weight"] != 0 for v in d["orbit_values"].values()))
    n += check(f"{cls} term orbits", ok,
               f"{len(d['orbit_values'])}/{norb} orbits from {d['fcyc_terms']}/{nterm} "
               f"F-CYC terms rebuild {rec} (want {tot}), {d['wall_s']}s")
    check(f"{cls} signed weights sum to 0",
          sum(v["weight"] for v in d["orbit_values"].values()) == 0,
          "sum of F-CYC signs over all terms vanishes")
require_count("pure classes with per-orbit rows", n, len(WANT))
finish("F-PURE-ORBITS")
