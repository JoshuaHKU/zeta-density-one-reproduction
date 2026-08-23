#!/usr/bin/env python3
"""Ledger enumeration gate: two independent enumerators must agree, every orbit
size must divide 2b (the D20 invariant that caught the {5,2}/{2,2,4}/{6,2}
under-count), and the orbit sizes must sum to the closed-form partition count."""
import os, sys, json
from math import comb, factorial
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, check, require_count, finish

def pr(n):                       # (n-1)!! = perfect matchings of n labelled points
    return 1 if n <= 1 else (n - 1) * pr(n - 2)

CLOSED = {                       # independent closed forms, hand-derived
    "t222": ("{2,2,2}", 6, pr(6)),
    "p24":  ("{2^4}",   8, pr(8)),
    "j52":  ("{5,2}",   7, comb(7, 2)),
    "j62":  ("{6,2}",   8, comb(8, 2)),
    "j44":  ("{4,4}",   8, comb(8, 4) // 2),
    "j224": ("{2,2,4}", 8, comb(8, 4) * pr(4)),
    "p25":  ("{2^5}",  10, pr(10)),
    "j225": ("{2,2,5}", 9, comb(9, 5) * pr(4)),
    "j4222":("{4,2,2,2}",10, comb(10, 4) * pr(6)),
    "j54":  ("{5,4}",    9, comb(9, 5)),
    "j622": ("{6,2,2}", 10, comb(10, 6) * pr(4)),
    # r148: the enumerator's "smallest element goes in the first block" dedup is
    # valid only AMONG EQUAL-SIZE blocks.  For {4,4,2} it forced element 0 into a
    # 4-block, silently dropping every partition with 0 in the PAIR: 9*35 = 315
    # of 1575.  This entry was missing from the table, so the gate could not
    # catch it -- a gate only protects what it is told to protect.
    "j442": ("{4,4,2}", 10, factorial(10) // (24 * 24 * 2) // 2),
}
n_ok = 0
WITHHELD = {"j442": "r148: enumerator dropped 315 of 1575 placements; value "
                    "4051/124740 is WRONG and is deliberately NOT in the package "
                    "until the class is re-enumerated and recomputed"}
for cls, (lab, n, want) in CLOSED.items():
    f = os.path.join(CONST, cls, "orbits.json")
    if not os.path.exists(f):
        why = WITHHELD.get(cls, "constant absent from the package")
        print(f"  WITHHELD  ledger {lab:<10} {why}")
        continue
    o = json.load(open(f))
    tot = sum(e["size"] for e in o["orbit_list"])
    sc = o["self_check"]
    good = (o["cycle"] == n and tot == want == o["partitions"]
            and sc["sum_of_orbit_sizes_equals_partitions"]["pass"]
            and sc["every_orbit_size_divides_2b"]["pass"]
            and all((2 * n) % e["size"] == 0 for e in o["orbit_list"]))
    n_ok += check(f"ledger {lab:<10}", good,
                  f"{o['orbits']} orbits, {tot} placements (closed form {want})")
require_count("ledger coverage", n_ok, len(CLOSED) - len(WITHHELD))
finish("F-LEDGER")
