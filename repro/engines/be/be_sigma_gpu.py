#!/usr/bin/env python3
# ============================================================================
# SUPERSEDED -- DO NOT USE FOR VERIFICATION (AUDIT_R164 3.5)
# This is the pre-r163 version with the WRONG term indexing: it enumerates
# per-block slot permutations (Lah counts, terms(4) = 73) instead of the
# correct merged-cluster families (Fubini counts, terms(4) = 75).  It is kept
# only as part of the recorded history of defect D27.  The correct engines are
# be_sigma2.py (CPU) and be_poly_par.py (GPU), whose term counts 13/75/541/4683
# are gate-checked (g_be BE1).
# ============================================================================

"""O-BE-5 (r160): per-(P, sigma) span-product scan, on the GPU.

    T_{P,sigma}(N) = sum_{m in [0,N)^b} prod_B  delta[sum_{i in B} k_i = 0]
                                              * (N - span_sigma(k_B))_+ ,
    k_i = m_i - m_{i+1 mod b},
    span_sigma = max - min of the sigma-ordered partial sums (empty prefix 0 included).

This deliberately does NOT go through the cumulant/Moebius layer, so it is an
independent check of the same objects O-BE-2 reached from the other side.

Why the GPU fits here (unlike the other two chains): the m-grid is a regular
lattice, the work per point is a fixed handful of integer operations, the points
are independent, and the result is a plain sum.  Plain CuPy array ops suffice --
no custom kernel is needed, which is exactly what failed for the span-DP, whose
sub-problems were irregular and individually tiny.

Exactness: every quantity here is an integer.  T can grow large, so the running
sum is kept in int64 and checked against overflow -- if any partial exceeds the
safe range the point is reported rather than silently wrapped.
"""
import sys, json, time, itertools
sys.path.insert(0, ".")
from be_tu_scan import set_partitions

SAFE = 2**62


def terms(b):
    """all (P, sigma-vector) pairs, blocks ordered by least element"""
    out = []
    for P in set_partitions(range(b)):
        blocks = sorted([sorted(B) for B in P], key=lambda B: B[0])
        for perms in itertools.product(*[itertools.permutations(B) for B in blocks]):
            out.append((tuple(map(tuple, blocks)), tuple(map(tuple, perms))))
    return out


def T_of(blocks, perms, b, N, xp):
    """exact T_{P,sigma}(N) as a Python int"""
    if N == 0:
        return 0
    grid = xp.indices((N,) * b, dtype=xp.int64).reshape(b, -1)
    k = grid - xp.roll(grid, -1, axis=0)
    w = xp.ones(grid.shape[1], dtype=xp.int64)
    for B, sig in zip(blocks, perms):
        s = xp.zeros(grid.shape[1], dtype=xp.int64)
        for i in B:
            s = s + k[i]
        w = w * (s == 0)
        if not bool((w != 0).any()):
            return 0
        acc = xp.zeros(grid.shape[1], dtype=xp.int64)
        mx = xp.zeros(grid.shape[1], dtype=xp.int64)
        mn = xp.zeros(grid.shape[1], dtype=xp.int64)
        for i in sig:
            acc = acc + k[i]
            mx = xp.maximum(mx, acc)
            mn = xp.minimum(mn, acc)
        w = w * xp.maximum(N - (mx - mn), 0)
    tot = int(w.sum())
    return tot


if __name__ == "__main__":
    b = int(sys.argv[1])
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard") + 1].split("/"))
    try:
        import cupy as xp
        dev = int(sys.argv[sys.argv.index("--gpu") + 1]) if "--gpu" in sys.argv else 0
        xp.cuda.Device(dev).use(); backend = f"cupy(dev{dev})"
    except Exception as e:
        import numpy as xp
        backend = f"numpy ({e})"
    Ns = list(range(1, b + 8))
    tm = terms(b)
    mine = [t for i, t in enumerate(tm) if i % nshard == shard]
    print(f"backend {backend}  b={b}: {len(tm)} (P,sigma) terms, shard {shard}/{nshard} "
          f"-> {len(mine)}, N={Ns[0]}..{Ns[-1]}", flush=True)
    t0 = time.time(); out = {}
    for n, (blocks, perms) in enumerate(mine):
        key = "|".join("".join(map(str, s)) for s in perms)
        out[key] = [T_of(blocks, perms, b, N, xp) for N in Ns]
        if (n + 1) % 25 == 0:
            print(f"  {n+1}/{len(mine)}  {time.time()-t0:.0f}s", flush=True)
    suf = "" if nshard == 1 else f"_s{shard}of{nshard}"
    json.dump({"b": b, "Ns": Ns, "shard": f"{shard}/{nshard}", "backend": backend,
               "n_terms": len(mine), "T": {k: [str(x) for x in v] for k, v in out.items()},
               "wall_s": round(time.time() - t0, 1)},
              open(f"../constants/be/sigma_scan_b{b}{suf}.json", "w"), indent=1)
    print(f"\nb={b} shard {shard}/{nshard}: {len(mine)} terms  {time.time()-t0:.1f}s  {backend}",
          flush=True)
