#!/usr/bin/env python3
"""O-BE-5 per-term gates, on the CORRECTED fine family (r163 spec).

A fine term is indexed by (P, {Q_B}, {sigma_B}) -- partition, per-block merge
partition, and a cyclic order of that block's CLASSES.  Its value is

    T(N) = sum_{m in [0,N)^b} prod_B delta[sum_B k = 0] * (N - span_{sigma_B}(g_B))_+

(the sign prod_B (-1)^(|Q_B|-1) is the assembly COEFFICIENT and is not part of T).
Term count = Fubini(b): 13 / 75 / 541 / 4683 / 47293 for b = 3..7.

Gates:
  F-BE-POLY-b   fit the first b+2 points by exact Lagrange, STARTING AT N=1
                (no N0 exemption); every remaining point must be a digit-for-digit
                holdout hit.
  F-BE-PAR2-b   the fitted polynomial obeys T(-N) = (-1)^(b+1) T(N), checked
                exactly at several negative points.

GPU: the m-grid is the only thing growing as N^b, and per point the work is a
fixed handful of integer ops -- CuPy array ops, no custom kernel.
"""
import sys, json, time, itertools
from fractions import Fraction as Q
sys.path.insert(0, ".")
from be_tu_scan import set_partitions


def fine_terms(b):
    """[(key, [(block_slots, [class-slot-lists in sigma order]) ...])]"""
    out = []
    for P in set_partitions(range(b)):
        blocks = sorted([sorted(B) for B in P], key=lambda B: B[0])
        per = []
        for B in blocks:
            opts = []
            for Qp in set_partitions(list(B)):
                n = len(Qp)
                for order in [(0,) + p for p in itertools.permutations(range(1, n))]:
                    opts.append([list(Qp[c]) for c in order])
            per.append(opts)
        for combo in itertools.product(*per):
            key = "/".join("|".join("".join(map(str, C)) for C in plan)
                           for plan in combo)
            out.append((key, list(zip([tuple(B) for B in blocks], combo))))
    return out


CHUNK = int(__import__("os").environ.get("BE_CHUNK", 1 << 17))
CACHE_MAX = int(__import__("os").environ.get("BE_CACHE_MAX", 256))


def values(b, Ns, xp, shard=0, nshard=1):
    """per-term T(N), computed in CHUNKS of the m-lattice.

    Memory history, because it took two attempts to get right:
      v1 cached one length-N^b array per distinct (block, plan) -> 22 GB, OOM.
      v2 chunked the lattice, which bounded HOW BIG each cached array is but not
         HOW MANY: with ~1000 plans and a 2^21 chunk that is still 16 GB -> OOM
         again, at the same 22 GB.
      v3 (this) bounds BOTH: a small chunk AND a hard cap on the number of cached
         plan arrays.  Peak memory is O(CHUNK * CACHE_MAX), independent of b, N
         and the term count.
    Fixing "how big" without fixing "how many" is not a memory fix.
    """
    tm = fine_terms(b)
    # Fine terms are independent, so a level splits cleanly across GPUs.  Term
    # enumeration is only 0.3 s at b=7, so every shard can build the full list
    # and keep its slice -- no need to distribute the skeleton itself.
    tm = [t for i, t in enumerate(tm) if i % nshard == shard]
    res = {k: [] for k, _ in tm}
    for N in Ns:
        total = N ** b
        acc = {k: 0 for k, _ in tm}
        for lo in range(0, total, CHUNK):
            hi = min(lo + CHUNK, total)
            idx = xp.arange(lo, hi, dtype=xp.int64)
            m = []
            t = idx
            for _ in range(b):
                m.append(t % N); t = t // N
            m = m[::-1]
            k = [m[i] - m[(i + 1) % b] for i in range(b)]
            zc, wc = {}, {}
            for key, spec in tm:
                w = None
                for B, plan in spec:
                    if B not in zc:
                        s = k[B[0]]
                        for i in B[1:]:
                            s = s + k[i]
                        zc[B] = (s == 0)
                    pk = (B, tuple(tuple(C) for C in plan))
                    if pk not in wc:
                        if len(wc) >= CACHE_MAX:
                            wc.clear()
                        acc_s = xp.zeros(hi - lo, dtype=xp.int64)
                        mx = xp.zeros(hi - lo, dtype=xp.int64)
                        mn = xp.zeros(hi - lo, dtype=xp.int64)
                        for C in plan:
                            g = k[C[0]]
                            for i in C[1:]:
                                g = g + k[i]
                            acc_s = acc_s + g
                            mx = xp.maximum(mx, acc_s); mn = xp.minimum(mn, acc_s)
                        wc[pk] = xp.maximum(N - (mx - mn), 0) * zc[B]
                    w = wc[pk] if w is None else w * wc[pk]
                acc[key] += int(w.sum())
            del idx, m, k, zc, wc
        for key in acc:
            res[key].append(acc[key])
    return res


def lagrange(xs, ys, x):
    t = Q(0)
    for i, xi in enumerate(xs):
        term = Q(ys[i])
        for j, xj in enumerate(xs):
            if i != j:
                term *= Q(x - xj, xi - xj)
        t += term
    return t


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
    nfit = b + 2
    t0 = time.time()
    V = values(b, Ns, xp, shard, nshard)
    print(f"backend {backend}  b={b}: {len(V)} fine terms (Fubini), N={Ns[0]}..{Ns[-1]}, "
          f"{time.time()-t0:.1f}s", flush=True)
    sign = (-1) ** (b + 1)
    poly_bad, par_bad = [], []
    for key, ys in V.items():
        fx, fy = Ns[:nfit], ys[:nfit]
        for j in range(nfit, len(Ns)):
            if lagrange(fx, fy, Ns[j]) != ys[j]:
                poly_bad.append((key, Ns[j])); break
        else:
            for N in Ns[:3]:
                if lagrange(fx, fy, -N) != sign * lagrange(fx, fy, N):
                    par_bad.append((key, N)); break
    res = {"b": b, "backend": backend, "shard": f"{shard}/{nshard}", "Ns": Ns, "n_fit_points": nfit,
           "n_fine_terms": len(V), "fubini_expected":
               {3: 13, 4: 75, 5: 541, 6: 4683, 7: 47293}.get(b),
           "F_BE_POLY": "PASS" if not poly_bad else f"FAIL {poly_bad[:3]}",
           "F_BE_PAR2": "PASS" if not par_bad else f"FAIL {par_bad[:3]}",
           "parity_sign": sign, "wall_s": round(time.time() - t0, 1),
           "T": {k: [str(x) for x in v] for k, v in V.items()}}
    suf = "" if nshard == 1 else f"_s{shard}of{nshard}"
    json.dump(res, open(f"../constants/be/sigma_scan_b{b}{suf}.json", "w"), indent=1)
    print(f"  F-BE-POLY-{b}: {res['F_BE_POLY']}")
    print(f"  F-BE-PAR2-{b}: {res['F_BE_PAR2']}  (sign {sign})", flush=True)
