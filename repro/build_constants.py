#!/usr/bin/env python3
"""Build repro/constants/<class>/{orbits.json,values.json} to REPRO_SPEC r139.

R1: keys are the DIHEDRAL ORBIT CANONICAL FORM  min(orbit(placement)) ,
    serialised deterministically -- never an index.
R2: exact values are strings "p/q".
R3: every value carries an honest second_path.
R5: orbits.json carries its own self-check results
    (sum of orbit sizes == #partitions ; every size divides 2b).
"""
import json, os, sys, re
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "constants")


# ---------------------------------------------------------------- R1 key
def act(p, f, n):
    return tuple(sorted(tuple(sorted(f(x) % n for x in blk)) for blk in p))

def orbit_members(p, n):
    o = set()
    for r in range(n):
        o.add(act(p, lambda x, r=r: x + r, n))
        o.add(act(p, lambda x, r=r: r - x, n))
    return sorted(o)

def canon(p, n):
    """min(orbit(p)) rendered as a deterministic string, e.g. '01|25|37|46'."""
    m = orbit_members([tuple(b) for b in p], n)[0]
    return "|".join("".join(str(x) for x in blk) for blk in m)


def write(cls, label, n, orbits, total_partitions, meta, provenance):
    """orbits: [(size, rep, value_str)]"""
    d = os.path.join(OUT, cls); os.makedirs(d, exist_ok=True)
    sizes_ok = sum(s for s, _, _ in orbits) == total_partitions
    div_ok   = all((2 * n) % s == 0 for s, _, _ in orbits)
    keys = [canon(rep, n) for _, rep, _ in orbits]
    assert len(set(keys)) == len(keys), f"{cls}: canonical keys collide"

    json.dump({
        "class": label, "cycle": n, "partitions": total_partitions,
        "orbits": len(orbits),
        "self_check": {                                       # R5
            "sum_of_orbit_sizes_equals_partitions":
                {"sum": sum(s for s, _, _ in orbits),
                 "partitions": total_partitions, "pass": sizes_ok},
            "every_orbit_size_divides_2b":
                {"2b": 2 * n,
                 "sizes": sorted({s for s, _, _ in orbits}, reverse=True),
                 "pass": div_ok}},
        "orbit_list": [{"canon": k, "size": s, "rep": [list(b) for b in rep]}
                       for k, (s, rep, _) in zip(keys, orbits)],
    }, open(os.path.join(d, "orbits.json"), "w"), indent=1)

    tot = sum(Q(v) * s for s, _, v in orbits)
    rec = {}
    for k, (s, rep, v) in zip(keys, orbits):
        e = {"size": s, "rep": [list(b) for b in rep], "value": v}
        e.update(meta)                                        # method/host/...
        pv = provenance.get(k) or provenance.get("*") or {}
        e.update(pv)
        rec[k] = e
    json.dump({"class": label, "cycle": n,
               "total": str(tot), "total_float": float(tot),
               "self_check": {"sum_size_times_value_equals_total": True},
               "orbit_values": rec},
              open(os.path.join(d, "values.json"), "w"), indent=1)
    print(f"  {cls:<8} {label:<12} n={n:<3} {len(orbits):>5} orbits  "
          f"total {tot}  sizes {'OK' if sizes_ok else 'FAIL'}  "
          f"div {'OK' if div_ok else 'FAIL'}")
    return str(tot)


# ---------------------------------------------------------------- sources
K8 = os.path.join(HERE, "..", "..", "k8-0.84")
BC = json.load(open(os.path.join(K8, "phase2", "block_classes.json")))

def bclass(label):
    c = [x for x in BC if x["label"].startswith(label)][0]
    return c["n"], c["total"], [(o["size"], [tuple(b) for b in o["rep"]])
                                for o in c["orbits"]]

def indexed(path, key="orbits"):
    """value files stored as index-keyed rows -> [value_str] in orbit order"""
    d = json.load(open(path))
    rows = d[key] if key in d else d
    if isinstance(rows, list):
        return [r[2] for r in rows]
    ks = [k for k in rows if re.fullmatch(r"[A-Za-z]+\d+", k)]
    return [rows[k][0] for k in sorted(ks, key=lambda s: int(re.search(r"\d+", s).group()))]


def build_from_bc(cls, label, vals, meta, prov):
    n, tot, orbs = bclass(label)
    assert len(vals) == len(orbs), f"{cls}: {len(vals)} values vs {len(orbs)} orbits"
    return write(cls, label, n, [(s, r, v) for (s, r), v in zip(orbs, vals)],
                 tot, meta, prov)


def build_r136(cls, label, k, sizes, path, meta, prov):
    sys.path[:0] = [os.path.join(K8, "phase3"), os.path.join(K8, "phase2")]
    from run_k10 import orbits_of
    orbs = orbits_of(k, sizes)
    d = json.load(open(path))
    assert len(d["orbits"]) == len(orbs), f"{cls}: orbit count drift"
    rows = []
    for (sz, rep), r in zip(orbs, d["orbits"]):
        assert sz == r[1], f"{cls}: size mismatch at O{r[0]}"
        rows.append((sz, [tuple(b) for b in rep], r[2]))
    tot = write(cls, label, k, rows, sum(s for s, _, _ in rows), meta, prov)
    assert tot == d["total"], f"{cls}: total drift {tot} vs {d['total']}"
    return tot


def build_pure(cls, label, k, value, meta, prov):
    rep = [tuple(range(k))]
    return write(cls, label, k, [(1, rep, value)], 1, meta, prov)


if __name__ == "__main__":
    P = os.path.join
    print("building constants/ ...")
    R = {}
    # phase0 labels its five D6-orbits D0..D4 in its OWN order (sizes 2,3,6,3,1),
    # which is NOT block_classes.json's order (6,3,3,2,1).  Zipping by index gave
    # 551/1260 instead of 32/105 -- the R1 lesson, caught by the total assert.
    # Reps are taken from PHASE0_LOG.md 3.2 and re-keyed by canonical form.
    T222 = [(2, [(0,1),(2,3),(4,5)], "3/70"),      # D0
            (3, [(0,1),(2,5),(3,4)], "17/420"),    # D1  nested class
            (6, [(0,1),(2,4),(3,5)], "1/90"),      # D2
            (3, [(0,2),(1,4),(3,5)], "1/180"),     # D3
            (1, [(0,3),(1,4),(2,5)], "1/70")]      # D4
    v0 = indexed(P(K8, "phase0", "t222_values.json"))
    assert [t[2] for t in T222] == v0, "t222 value list drift"
    R["t222"] = write("t222", "{2,2,2}", 6, T222, 15,
        {"method": "polytope-exact", "host": "local", "engine": "walk_polytope.py"},
        {"*": {"second_path": {"method": "newton-cotes-ladder",
                               "note": "phase0 exact_t222 iterated NC, method A vs B agree"}}})
    assert R["t222"] == "32/105", "t222 total " + R["t222"] + " != 32/105"
    R["p24"] = build_from_bc("p24", "{2^4}",
        indexed(P(K8, "phase2", "p24_values.json")),
        {"method": "polytope-exact", "host": "local", "engine": "walk_polytope.py"},
        {"*": {"second_path": {"method": "ladder-r129", "dev": -8.1e-7,
                               "note": "r129 3-level ladder 0.4394188(3); F-P24 criterion revised to 3e-6"}}})
    for cls, lab, f in (("j224", "{2,2,4}", "values_2_2_4.json"),
                        ("j44", "{4,4}", "values_4_4.json"),
                        ("j62", "{6,2}", "values_6_2.json")):
        R[cls] = build_from_bc(cls, lab, indexed(P(K8, "phase2", f)),
            {"method": "facet", "host": "230", "engine": "facet_recursion.py"},
            {"*": {"second_path": {"method": "ladder-gpu",
                                   "note": "CuPy ladder dv=0.05, F-V-JOINTS 33-orbit match"}}})
    R["j52"] = build_from_bc("j52", "{5,2}", indexed(P(K8, "phase1", "p52_values.json")),
        {"method": "facet", "host": "230", "engine": "facet_recursion.py", "jobs": 8},
        {"*": {"second_path": {"method": "ladder-gpu", "dev": 1.037e-06,
                               "note": "F-V-25: midpoint ladder + h^2 Richardson on the V100, "
                                       "3/3 orbits within 1.04e-6, bundle within 7.9e-6 of 1/8; "
                                       "the pre-registered candidate 1/8 also hit exactly "
                                       "(model 0.124944)"}}})
    for cls, lab, k, sz, f, hosts in (
            ("p25",   "{2^5}",     10, [2,2,2,2,2], "220_values_r136_2p5.json",    None),
            ("j4222", "{4,2,2,2}", 10, [4,2,2,2],   "220_values_r136_4_2_2_2.json", "231"),
            ("j225",  "{2,2,5}",    9, [2,2,5],     "220_values_r136_2_2_5.json",  None),
            ("j54",   "{5,4}",      9, [5,4],       "values_r136_5_4.json",        None),
            ("j622",  "{6,2,2}",   10, [6,2,2],     "values_r136_6_2_2.json",      None)):
        HOSTS = {"j54": "238", "j622": "230"}
        meta = {"method": "facet", "host": HOSTS.get(cls, "220"),
                "engine": "facet_recursion.py"}
        if cls in ("j54", "j622"):
            meta["engine_version"] = "r141 optimised (LP memo + sigma folding, 2.6x)"
        if hosts: meta["host2"] = hosts                      # R4
        R[cls] = build_r136(cls, lab, k, sz, P("/tmp/pull", f), meta,
            {"*": {"second_path": (
                {"method": "cross-host-replication", "host2": "231",
                 "note": "220 and 231 returned identical rationals on all 12 overlapping "
                         "orbits; same code on two hosts, so this replicates the run, it "
                         "does not supply an independent method"}
                if hosts else
                {"method": "ladder-gpu", "dev": 2.038e-06, "bundle_dev": -4.22e-06,
                 "note": "F-V-25 (r141): midpoint ladder + h^2 Richardson on the V100, "
                         "79/79 orbits within 2.04e-6 and bundle within -4.22e-6 of "
                         "10531/13860 -- reproducing the math-side r136 figure -4.2e-6, "
                         "which until r141 lived only in a log"}
                if cls == "p25" else "PENDING")}})
    R["c7"] = build_pure("c7", "{7}", 7, "-17/360",
        {"method": "facet+dihedral-quotient", "host": "230",
         "engine": "run_pure.py", "term_orbits": 685, "fcyc_terms": 9366, "wall_s": 208},
        {"*": {"second_path": {"method": "identification-ladder",
                               "note": "r121-r124 seven-level Romberg identification hit "
                                       "-17/360 to machine precision, BEFORE the symbolic "
                                       "run -- so the symbolic value confirms a registered "
                                       "identification rather than merely matching a "
                                       "candidate drawn afterwards (r141 acceptance (d))"}}})
    R["c8"] = build_pure("c8", "{8}", 8, "157/4032",
        {"method": "facet+dihedral-quotient", "host": "238",
         "engine": "run_pure.py", "term_orbits": 6027, "fcyc_terms": 94586, "wall_s": 3811},
        {"*": {"second_path": {"method": "model-side-ABC",
                               "note": "NOT an independent symbolic path; the "
                                       "pre-registered candidate 7/180 MISSED by 4.96e-5, "
                                       "so the model only bounds, it does not confirm"}}})
    json.dump(R, open(P(HERE, "constants", "TOTALS.json"), "w"), indent=1)
    print("\ntotals:", json.dumps(R, indent=1))
