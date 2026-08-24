#!/usr/bin/env python3
"""
PHASE 0.1 + 0.2 -- exact value of every dihedral class of the {2,2,2} bundle,
and the assembled bundle value.

Runs the 5 dihedral orbits found by chord_classes.py through the exact
rational integrator, and additionally verifies DIHEDRAL INVARIANCE by running
several distinct members of the same orbit: rotation of the cycle translates
all positions (spread is translation invariant) and reversal negates them, so
members of one orbit must return the SAME rational.  That is an independent
check on the class construction itself, not just on the integration.

Gates:
  F-NEST      the nested class D1 must return 17/420 (r129's claim)
  F-ORBIT     members of an orbit must return identical rationals
  F-BUNDLE    sum over orbits, weighted by orbit size, must be 32/105
  F-ARCHIVE   the four archived representatives must reproduce 3/70, 1/90,
              1/180, 1/70

Usage:  OMP_NUM_THREADS=1 python3 t222_exact.py [--full]
        --full also runs every one of the 15 matchings (slow, ~10 min)
"""
import json, os, sys, time
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from walk_polytope import integral as integral_poly
from walk_exact3 import integral as integral_iter

# AUDIT_R164 2.3: the integration method must travel WITH each task, not
# through a module-level global -- under the spawn start method workers
# re-import this module and silently fall back to the default, so
# "--iterated" ran the polytope engine twice and reported the two-method
# cross-check as passing when it compared a method against itself.
_METHODS = {"poly": integral_poly, "iter": integral_iter}
import chord_classes as CC


def job(args):
    tag, pos, method_name = args
    t0 = time.time()
    v = _METHODS[method_name]([tuple(p) for p in pos])
    return tag, v, time.time() - t0


def main():
    classes = json.load(open(os.path.join(HERE, "t222_classes.json"))) \
        if os.path.exists(os.path.join(HERE, "t222_classes.json")) else CC.main()
    full = "--full" in sys.argv
    method_name = "iter" if "--iterated" in sys.argv else "poly"

    tasks = [(c["name"], c["walk"], method_name) for c in classes]
    # one extra member per orbit (where the orbit has one) for F-ORBIT
    extra = []
    for c in classes:
        for mem in c["members"][1:3]:
            extra.append((c["name"] + "*", CC.walk(tuple(tuple(p) for p in mem)), method_name))
    if full:
        extra = []
        for c in classes:
            for i, mem in enumerate(c["members"]):
                extra.append((f"{c['name']}#{i}", CC.walk(tuple(tuple(p) for p in mem)), method_name))

    print(f"exact integration of {len(tasks)} orbit representatives"
          f" + {len(extra)} invariance checks\n")
    with ProcessPoolExecutor(max_workers=8) as ex:
        res = dict()
        times = dict()
        for tag, v, dt in ex.map(job, tasks + extra):
            res[tag] = v; times[tag] = dt

    ok = True
    print(f"{'orbit':<7}{'size':<6}{'cr':<4}{'exact value':<16}{'decimal':<14}{'s':<6}")
    total = F(0)
    for c in classes:
        v = res[c["name"]]
        total += c["size"] * v
        print(f"{c['name']:<7}{c['size']:<6}{c['crossings']:<4}"
              f"{str(v):<16}{float(v):<14.9f}{times[c['name']]:<6.0f}")
    print(f"\nF-BUNDLE  {{2,2,2}} = sum size*value = {total} = {float(total):.9f}")
    good = (total == F(32, 105))
    ok &= good
    print(f"          r129 claims 32/105 = {float(F(32,105)):.9f}   "
          f"{'PASS' if good else '*** FAIL ***'}")
    print(f"          superseded value    131/420 = {float(F(131,420)):.9f}"
          f"   (difference {total - F(131,420)})")

    d1 = res["D1"]
    g = (d1 == F(17, 420)); ok &= g
    print(f"\nF-NEST    nested class D1 = {d1}   r129 claims 17/420   "
          f"{'PASS' if g else '*** FAIL ***'}")
    d0 = res["D0"]
    print(f"          sequential class D0 = {d0}  (the archived T0 = 3/70)")
    print(f"          the archived assembly used D0's value for all 5 cr=0 "
          f"matchings;\n          the true split is {classes[0]['size']} x {d0} + "
          f"{classes[1]['size']} x {d1}, an error of "
          f"{classes[1]['size']*(d0-d1)} in the bundle")

    print("\nF-ORBIT   dihedral invariance")
    for tag in sorted(t for t in res if t.endswith("*") or "#" in t):
        base = tag.split("*")[0].split("#")[0]
        g = (res[tag] == res[base]); ok &= g
        print(f"          {tag:<8} = {str(res[tag]):<14} vs {base} "
              f"{'PASS' if g else '*** FAIL ***'}")

    print("\nF-ARCHIVE the four archived representatives")
    ARCH = {'T0': (classes[0], F(3, 70)), 'T2': (classes[3], F(1, 180)),
            'T3': (classes[4], F(1, 70))}
    for nm, (c, tgt) in ARCH.items():
        g = (res[c["name"]] == tgt); ok &= g
        print(f"          {nm} ~ {c['name']}: {res[c['name']]} vs {tgt}  "
              f"{'PASS' if g else '*** FAIL ***'}")
    g = (res["D2"] == F(1, 90)); ok &= g
    print(f"          T1 ~ D2: {res['D2']} vs 1/90  {'PASS' if g else '*** FAIL ***'}")

    json.dump({k: [str(v), float(v)] for k, v in res.items()},
              open(os.path.join(HERE, "t222_values.json"), "w"), indent=1)
    print("\n" + ("ALL PHASE-0 GATES PASS" if ok else "*** SOME GATES FAILED ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
