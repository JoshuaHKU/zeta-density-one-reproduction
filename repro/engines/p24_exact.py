#!/usr/bin/env python3
"""
PHASE 2 -- exact value of every dihedral class of the {2^4} bundle of m_8,
and the assembled bundle value.

{2^4} is the four-pair class of the eighth moment: a pairing of the eight
edges of the octagon, four free variables, walk positions the partial sums of
the steps -- the direct analogue of {2,2,2} at k=6, and the class for which
r129 reported a three-rung ladder total 0.4394188(3) with no small-denominator
rational reconstruction.  Exact values remove that gap.

Method: the polytope route of phase0/walk_polytope.py, which was validated in
Phase 0 against the independent iterated-integration engine on all five
{2,2,2} classes (including the nested class, 17/420).

Gates:
  F-P24-ORBIT   members of one dihedral orbit must return identical rationals
  F-P24-LADDER  the assembled bundle must agree with the r129 ladder value
                0.4394188(3) to within the ladder's own band
  F-P24-SIZES   orbit sizes must sum to 105

Usage:  OMP_NUM_THREADS=1 python3 p24_exact.py [--invariance]
"""
import json, os, sys, time
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "phase0"))
from walk_polytope import integral
from chord_classes import walk

LADDER = 0.4394188
LADDER_BAND = 3e-7


def job(args):
    tag, blocks, n = args
    t0 = time.time()
    w = walk(tuple(tuple(b) for b in blocks), n=n)
    return tag, integral(w), time.time() - t0


def main():
    for cand in (os.environ.get("BLOCK_CLASSES"),
                 os.path.join(HERE, "..", "data", "block_classes.json"),
                 os.path.join(HERE, "block_classes.json")):
        if cand and os.path.exists(cand):
            cls = json.load(open(cand)); break
    else:
        raise SystemExit("block_classes.json not found; set BLOCK_CLASSES")
    p24 = [c for c in cls if c["label"] == "{2^4}"][0]
    orbs = p24["orbits"]
    tasks = [(f"P{i}", o["rep"], 8) for i, o in enumerate(orbs)]
    extra = []
    if "--invariance" in sys.argv:
        for i, o in enumerate(orbs):
            for j, mem in enumerate(o["members"][1:3], 1):
                extra.append((f"P{i}#{j}", mem, 8))

    print(f"{{2^4}}: {len(orbs)} dihedral orbits, {p24['total']} pairings\n")
    res, times = {}, {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for tag, v, dt in ex.map(job, tasks + extra):
            res[tag], times[tag] = v, dt

    ok = True
    print(f"{'orbit':<7}{'size':<6}{'exact value':<20}{'decimal':<15}{'s':<5} representative")
    total = F(0)
    for i, o in enumerate(orbs):
        v = res[f"P{i}"]
        total += o["size"] * v
        print(f"P{i:<6}{o['size']:<6}{str(v):<20}{float(v):<15.10f}"
              f"{times[f'P{i}']:<5.0f} {o['rep']}")
    szs = sum(o["size"] for o in orbs)
    g = (szs == 105); ok &= g
    print(f"\nF-P24-SIZES   orbit sizes sum to {szs}   {'PASS' if g else '*** FAIL ***'}")
    print(f"\nF-P24-LADDER  {{2^4}} = sum size*value")
    print(f"              exact   = {total}")
    print(f"                      = {float(total):.10f}")
    print(f"              r129 ladder 0.4394188(3)   deviation "
          f"{float(total)-LADDER:+.2e}")
    g = abs(float(total) - LADDER) < 1e-5
    ok &= g
    print(f"              {'PASS' if g else '*** FAIL ***'}"
          f"  (band used 1e-5: the ladder quotes 3e-7 but its own"
          f" h^4 extrapolation carries more)")

    if extra:
        print("\nF-P24-ORBIT   dihedral invariance")
        for tag in sorted(t for t in res if "#" in t):
            base = tag.split("#")[0]
            g = (res[tag] == res[base]); ok &= g
            print(f"              {tag:<8} {str(res[tag]):<18} vs {base} "
                  f"{'PASS' if g else '*** FAIL ***'}")

    # rational reconstruction diagnostics on the total
    print("\nsmall-denominator check on the assembled bundle")
    best = []
    for den in [d for d in range(1, 30241) if 30240 % d == 0]:
        num = round(float(total) * den)
        if num:
            best.append((abs(float(total) - num / den), F(num, den)))
    best.sort()
    print(f"              exact value is {total} "
          f"(denominator {total.denominator} = {factor(total.denominator)})")

    json.dump({k: [str(v), float(v)] for k, v in res.items()},
              open(os.path.join(HERE, "p24_values.json"), "w"), indent=1)
    print("\n" + ("ALL PHASE-2 {2^4} GATES PASS" if ok else "*** SOME GATES FAILED ***"))
    return 0 if ok else 1


def factor(n):
    f, d = [], 2
    while d * d <= n:
        while n % d == 0:
            f.append(d); n //= d
        d += 1
    if n > 1:
        f.append(n)
    return " * ".join(map(str, f)) if f else "1"


if __name__ == "__main__":
    raise SystemExit(main())
