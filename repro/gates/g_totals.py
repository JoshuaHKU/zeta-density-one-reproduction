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

# AUDIT_R164 2.2: the recomputed sum must be compared BOTH against the
# hardcoded want AND against the file's own "total" field (previously
# computed but never compared -- injecting total="999/1000" passed), AND
# against constants/TOTALS.json where present.
TOTALS = json.load(open(os.path.join(CONST, "TOTALS.json")))

WANT = {"t222": "32/105", "p24": "1661/3780", "j224": "-127/840",
        "j44": "23/4536", "j62": "-563/11340", "j52": "1/8",
        "p25": "10531/13860", "j54": "-257/10080", "j622": "-120139/498960", "j4222": "-208771/498960", "j225": "2263/5040",
        "c7": "-17/360", "c8": "157/4032",
        # AUDIT_R177 2.4: C_9 was gate-checked by g_be BE7 (rebuild identities)
        # but was missing from THIS gate, which enforces a different and
        # non-overlapping set of properties: canonical-form keys, the
        # orbits.json <-> values.json join, R3 second_path presence, and
        # three-way total agreement.  constants/c9 satisfies all of them.
        "c9": "27649/302400"}

# {7,2} (constants/j72) is deliberately NOT in WANT.  It is the one constant
# directory with no orbits.json, because RECEIPT_R148_J72.md archived only the
# per-orbit VALUES under the labels O0..O3 -- the orbit representatives
# themselves were never recorded, and recovering them means re-running the
# facet chain (host 231, ~18 h on 22 workers).  Fabricating representatives to
# satisfy this gate would be worse than the gap.  {7,2} is instead covered by
# g_be BE7, which rebuilds 9 x (sum of the four orbit values) == -4313/12600
# and checks the two identities it participates in.  See AUDIT_R177 2.4.
# AUDIT_R177 2.5: the constants that legitimately stand on ONE method.
# Hard-coded on purpose.  If a constant is added to or removed from this set
# without the documentation changing with it, the gate fails -- in BOTH
# directions, so a silent upgrade is caught as well as a silent regression.
#   {2,2,5}, {5,4}, {6,2,2}  facet chain only, long-standing
#   {7,2}                    added by AUDIT_R177 2.5: its former
#                            "pre-registered-identity" label cited
#                            C_9 + {7,2} = -75863/302400, an identity already
#                            spent certifying C_9.  One equation cannot
#                            independently confirm both of its own terms.
#                            RECEIPT_R148_J72.md sec 3 had it right originally.
SINGLE_PATH = {"j225", "j54", "j622", "j72"}

pending_seen = set()   # constants whose second_path method is PENDING
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
    # R3 -- AUDIT_R177 2.5 upgrade.  Presence alone is not enough: a PENDING
    # entry, an empty object and a circular citation all satisfied the old
    # check identically, so a constant could lose (or silently gain) a second
    # path without any gate noticing.  We now also read the METHOD and compare
    # the observed single-path inventory against SINGLE_PATH below -- a
    # hard-coded expectation, deliberately NOT derived from the data it
    # checks (the D30 lesson).
    sp_ok = all("second_path" in e for e in v["orbit_values"].values())
    for e in v["orbit_values"].values():
        sp = e.get("second_path")
        m = sp.get("method") if isinstance(sp, dict) else str(sp)
        if m == "PENDING":
            pending_seen.add(cls)
    tot_field_ok = (Q(v.get("total", "0")) == tot)
    totals_ok = (cls not in TOTALS) or (Q(TOTALS[cls]) == tot)
    n += check(f"total {v['class']:<10}",
               str(tot) == want and tot_field_ok and totals_ok
               and keys_ok and join_ok and sp_ok,
               f"{tot} (want {want}; total field {'ok' if tot_field_ok else 'BAD'}; "
               f"TOTALS.json {'ok' if totals_ok else 'BAD'}), "
               f"{len(v['orbit_values'])} orbits, "
               f"keys {'ok' if keys_ok else 'BAD'}, join {'ok' if join_ok else 'BAD'}, "
               f"second_path {'ok' if sp_ok else 'MISSING'}")
require_count("constants covered", n, len(WANT))

# {7,2} is outside WANT (no orbits.json, see above), so read it separately for
# the single-path inventory; everything else was collected in the loop.
_j72 = json.load(open(os.path.join(CONST, "j72", "values.json")))
for e in _j72["orbit_values"].values():
    sp = e.get("second_path")
    m = sp.get("method") if isinstance(sp, dict) else str(sp)
    if m == "PENDING":
        pending_seen.add("j72")

check("R3 single-path inventory exact",
      pending_seen == SINGLE_PATH,
      f"PENDING = {sorted(pending_seen)}; expected {sorted(SINGLE_PATH)}"
      + ("" if pending_seen == SINGLE_PATH else
         f"; unexpected-PENDING {sorted(pending_seen - SINGLE_PATH)}"
         f"; silently-upgraded {sorted(SINGLE_PATH - pending_seen)}"))
finish("F-TOTALS")
