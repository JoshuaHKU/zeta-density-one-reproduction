#!/usr/bin/env python3
"""r136 driver: any block-partition class on the k-cycle, by dihedral placement
class.  --probe N calibrates per-orbit cost on N sampled orbits before committing.
Usage: run_k10.py NAME k s1,s2,... [--jobs N] [--probe N]"""
import sys, os, json, time, random
HERE = os.path.dirname(os.path.abspath(__file__))

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
sys.path[:0] = [HERE, os.path.join(HERE, "..", "phase2")]
from ratbackend import F, BACKEND
from class_integral import class_integral, class_terms
from block_classes import set_partitions_by_sizes, orbit

def orbits_of(k, sizes):
    o = {}
    for p in set_partitions_by_sizes(k, sizes):
        o.setdefault(orbit(p, k), []).append(p)
    return sorted(([len(v), [list(b) for b in v[0]]] for v in o.values()),
                  key=lambda x: (-x[0], x[1]))

if __name__ == "__main__":
    # AUDIT_R177 2.9: fail in the first second, not the fifth hour.
    _phase2(probe=True)
    name, k = sys.argv[1], int(sys.argv[2])
    sizes = [int(x) for x in sys.argv[3].split(",")]
    jobs = int(sys.argv[sys.argv.index("--jobs")+1]) if "--jobs" in sys.argv else 8
    orbs = orbits_of(k, sizes)
    print(f"backend {BACKEND}  {name} on the {k}-cycle: {len(orbs)} orbits, "
          f"{sum(o[0] for o in orbs)} placements", flush=True)
    if "--probe" in sys.argv:
        n = int(sys.argv[sys.argv.index("--probe")+1])
        random.seed(1); samp = random.sample(orbs, min(n, len(orbs)))
        tot = 0.0
        for i, (sz, rep) in enumerate(samp):
            ts = class_terms(rep, k)
            t0 = time.time(); class_integral(rep, k, jobs=jobs); dt = time.time()-t0
            tot += dt
            print(f"  probe {i}: size {sz} terms {len(ts)} "
                  f"R^{ts[0][3]+len(ts[0][1])}  {dt:.1f}s", flush=True)
        avg = tot/len(samp)
        print(f"\n  mean {avg:.1f}s/orbit on {jobs} jobs -> full class "
              f"{len(orbs)*avg/3600:.2f} h wall", flush=True)
        raise SystemExit
    # incremental checkpoint: a killed run resumes instead of restarting from
    # zero.  r141 -- the 2.5x engine change made restarts attractive, and the
    # only thing standing in the way was that this driver kept everything in RAM
    # until the last orbit finished.
    ck = os.path.join(HERE, f"ck_{name.replace('{','').replace('}','').replace(',','_').replace('^','p')}.json")
    done = json.load(open(ck)) if os.path.exists(ck) else {}
    if done:
        print(f"  resuming from {ck}: {len(done)} orbits already done", flush=True)
    tot = F(0); rows = []
    for i, (sz, rep) in enumerate(orbs):
        if str(i) in done:
            v = F(done[str(i)]); tot += sz * v; rows.append([i, sz, str(v)]); continue
        t0 = time.time(); v = class_integral(rep, k, jobs=jobs)
        done[str(i)] = str(v); json.dump(done, open(ck, "w"))
        tot += sz * v; rows.append([i, sz, str(v)])
        print(f"  O{i:<4} size {sz:<3} {str(v):<22} {float(v):+.10f}  {time.time()-t0:.0f}s",
              flush=True)
    print(f"\n  {name} = {tot} = {float(tot):.12f}", flush=True)
    json.dump({"class": name, "k": k, "sizes": sizes, "orbits": rows, "total": str(tot)},
              open(os.path.join(_phase2(),
                                f"values_r136_{name.replace('{','').replace('}','').replace(',','_').replace('^','p')}.json"), "w"), indent=1)
