#!/usr/bin/env python3
"""Bundle gate: for every constant, sum(size * orbit value) must equal the
recorded total, every key must BE the canonical form of its own rep (R1), and
values.json must agree with orbits.json orbit-by-orbit.
This is the gate that caught the phase0 D0..D4 vs block_classes index
misalignment during packaging (551/1260 instead of 32/105)."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, canon_key, check, require_count, finish

WANT = {"t222": "32/105", "p24": "1661/3780", "j224": "-127/840",
        "j44": "23/4536", "j62": "-563/11340", "j52": "1/8",
        "p25": "10531/13860", "j54": "-257/10080", "j622": "-120139/498960", "j4222": "-208771/498960", "j225": "2263/5040",
        "c7": "-17/360", "c8": "157/4032"}
n = 0
for cls, want in WANT.items():
    v = json.load(open(os.path.join(CONST, cls, "values.json")))
    o = json.load(open(os.path.join(CONST, cls, "orbits.json")))
    nn = v["cycle"]
    tot = sum(Q(e["value"]) * e["size"] for e in v["orbit_values"].values())
    keys_ok = all(k == canon_key(e["rep"], nn) for k, e in v["orbit_values"].items())
    join_ok = ({e["canon"] for e in o["orbit_list"]} == set(v["orbit_values"])
               and all(e["size"] == v["orbit_values"][e["canon"]]["size"]
                       for e in o["orbit_list"]))
    sp_ok = all("second_path" in e for e in v["orbit_values"].values())   # R3
    n += check(f"total {v['class']:<10}",
               str(tot) == want and keys_ok and join_ok and sp_ok,
               f"{tot} (want {want}), {len(v['orbit_values'])} orbits, "
               f"keys {'ok' if keys_ok else 'BAD'}, join {'ok' if join_ok else 'BAD'}, "
               f"second_path {'ok' if sp_ok else 'MISSING'}")
require_count("constants covered", n, len(WANT))
finish("F-TOTALS")
