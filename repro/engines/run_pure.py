#!/usr/bin/env python3
"""Pure class {k} = int O_k C_k, via the dihedral quotient of the F-CYC sum.
Validates on C5 = 1/36 and {6} = -1/126 before being used on {8}."""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

def _phase2(probe=False):
    """Output directory for the phase-2 class values, created on demand.

    AUDIT_R164 1.2 created the directory here instead of assuming it exists --
    these runs previously died with FileNotFoundError AFTER hours of compute.
    AUDIT_R177 2.9 adds the other half: call _phase2(probe=True) BEFORE the
    compute starts, so an unwritable parent (read-only mount, full disk, wrong
    owner) fails in the first second rather than the fifth hour.  A long job
    should fail immediately or not at all.
    """
    d = os.path.join(HERE, "..", "phase2")
    os.makedirs(d, exist_ok=True)
    if probe:
        t = os.path.join(d, ".writeprobe")
        with open(t, "w") as f:
            f.write("")
        os.remove(t)
    return d
from ratbackend import F, BACKEND
from class_integral import edge_forms, cycle_walk, term_walk, one_term
from symquot import quotient


def pure_class(k, jobs=1, verbose=True):
    blocks = [list(range(k))]
    forms, nfree, _ = edge_forms(blocks, k)
    base = cycle_walk(forms, k, nfree)
    orbs, nterm = quotient(list(range(k)), k)
    if verbose:
        print(f"  {{{k}}}: {nterm} F-CYC terms -> {len(orbs)} dihedral orbits "
              f"({nterm/len(orbs):.1f}x), free {nfree}", flush=True)
    jobsl = []
    for w, parts in orbs:
        tw = term_walk(parts, forms, nfree)
        walks = [base] + ([tw] if len(tw) > 1 else [])
        jobsl.append((w, (walks, [], nfree)))
    tot = F(0)
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            for (w, _), v in zip(jobsl, ex.map(one_term, [a for _, a in jobsl])):
                tot += w * v
    else:
        for w, a in jobsl:
            tot += w * one_term(a)
    return tot


if __name__ == "__main__":
    # AUDIT_R177 2.9: fail in the first second, not the fifth hour.
    _phase2(probe=True)
    jobs = int(sys.argv[sys.argv.index("--jobs")+1]) if "--jobs" in sys.argv else 8
    print(f"backend {BACKEND}", flush=True)
    if "--validate" in sys.argv:
        ok = True
        for k, tgt in ((5, F(1,36)), (6, F(-1,126))):
            t0=time.time(); v = pure_class(k, jobs)
            g = (v == tgt); ok &= g
            print(f"    = {v}  target {tgt}  {'MATCH' if g else '*** MISMATCH ***'}"
                  f"   {time.time()-t0:.0f}s", flush=True)
        print("QUOTIENT VALIDATED" if ok else "*** FAIL ***")
        raise SystemExit(0 if ok else 1)
    k = int(sys.argv[1])
    t0 = time.time(); v = pure_class(k, jobs)
    print(f"  C_{k} = {{{k}}} = {v} = {float(v):.12f}   {time.time()-t0:.0f}s", flush=True)
    json.dump({"class": f"{{{k}}}", "value": str(v)},
              open(os.path.join(_phase2(), f"values_{k}.json"), "w"), indent=1)
