#!/usr/bin/env python3
"""O-BE-4 on the GPU: batched minor determinants for the lifted-system TU scan.

Why this chain and not the others.  The facet chain is 44% exact simplex with
order comparisons and irregular recursion; tt_moments' span-DP has sub-problems
too small to vectorise (measured: numpy was 20% SLOWER).  This scan is different:
b=7 needs ~4.0e11 INDEPENDENT determinants of k x k matrices with entries in
{-1,0,1}, k <= 14.  Hadamard bounds |det| <= 14^7 ~ 1.05e8, far inside float64's
exact-integer range (2^53 ~ 9e15) and inside int64.  Independent + uniform +
machine-word: the archetypal GPU shape.

Rigour.  float64 LU gives det as a float; we only need to classify it into
{0,+-1} or "other".  Anything not within TOL of 0, +1 or -1 is re-checked on the
CPU with exact Bareiss integer elimination, so a float rounding artefact can
never turn a violation into a pass -- it can only cost an extra exact check.
"""
import sys, json, time, itertools
sys.path.insert(0, ".")
from be_ltu_scan import lifted_matrices, det_bareiss

TOL = 1e-6
# Batch is bounded by BYTES, not by count.  A fixed count of 1e6 means
# 1e6 * k * k * 8 bytes, i.e. 1.57 GB at k=14 -- and with four processes per GPU
# that is 6+ GB of submatrices alone, which OOM'd four shards on a 16 GB V100.
# Size the batch from the element size so memory is flat in k, and remember that
# the driver needs workspace of the same order for the batched factorisation.
BATCH_BYTES = int(__import__("os").environ.get("GPU_BATCH_BYTES", 150_000_000))


def _batch_for(k):
    return max(1024, BATCH_BYTES // (k * k * 8))


_COMB = {}


def _combs(n, k):
    """cached index arrays -- rebuilt per (n,k) once, not per matrix"""
    key = (n, k)
    if key not in _COMB:
        import numpy as np
        _COMB[key] = np.array(list(itertools.combinations(range(n), k)),
                              dtype=np.int64)
    return _COMB[key]


def minors_gpu(rows, ncol, xp, kmax=None):
    """returns list of (k, ri, ci) whose |det| is not clearly in {0,+-1}.

    OPTIMISATION 1 (cross-k batching): the first version launched one kernel per
    (k, chunk) and per matrix, so small k spent more time in launch overhead than
    in arithmetic.  Index combinations are now cached across matrices (they only
    depend on the shape), and the whole (row-subset x col-subset) grid for a given
    k is submitted in one large gather + one batched det.
    """
    import numpy as np
    R = len(rows)
    kmax = kmax or ncol
    A_h = np.array(rows, dtype=np.float64)
    A = xp.asarray(A_h)
    suspicious = []
    for k in range(2, min(kmax, ncol, R) + 1):
        rr = _combs(R, k)
        cc = _combs(ncol, k)
        nr, nc = len(rr), len(cc)
        rr_g = xp.asarray(rr)
        cc_g = xp.asarray(cc)
        step = _batch_for(k)
        for lo in range(0, nr * nc, step):
            hi = min(lo + step, nr * nc)
            idx = xp.arange(lo, hi)
            i_r = idx // nc
            i_c = idx - i_r * nc
            sub = A[rr_g[i_r][:, :, None], cc_g[i_c][:, None, :]]
            d = xp.linalg.det(sub)
            m = xp.minimum(xp.minimum(xp.abs(d), xp.abs(d - 1)), xp.abs(d + 1))
            bad = xp.where(m > TOL)[0]
            if bad.size:
                bad_h = xp.asnumpy(bad) if hasattr(xp, "asnumpy") else bad
                ir_h = xp.asnumpy(i_r) if hasattr(xp, "asnumpy") else i_r
                ic_h = xp.asnumpy(i_c) if hasattr(xp, "asnumpy") else i_c
                for j in bad_h:
                    suspicious.append((k, tuple(rr[ir_h[j]]), tuple(cc[ic_h[j]])))
    return suspicious


def check_tu_gpu(rows, ncol, xp):
    """exact verdict: GPU screens, CPU adjudicates every suspicious minor"""
    for j in range(ncol):
        for i in range(len(rows)):
            if rows[i][j] not in (0, 1, -1):
                return {"rows": [i], "cols": [j], "det": rows[i][j]}
    for k, ri, ci in minors_gpu(rows, ncol, xp):
        sub = [[rows[i][j] for j in ci] for i in ri]
        d = det_bareiss(sub)
        if d not in (0, 1, -1):
            return {"rows": list(ri), "cols": list(ci), "det": int(d),
                    "submatrix": sub}
    return None


if __name__ == "__main__":
    b = int(sys.argv[1])
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard")+1].split("/"))
    lim = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 0
    try:
        import cupy as xp
        dev = int(sys.argv[sys.argv.index("--gpu") + 1]) if "--gpu" in sys.argv else 1
        xp.cuda.Device(dev).use()
        backend = f"cupy(dev{dev})"
    except Exception as e:
        import numpy as xp
        backend = f"numpy ({e})"
    t0 = time.time()
    mats = lifted_matrices(b)
    if lim:
        mats = mats[:lim]
    if nshard > 1:
        mats = [m for i, m in enumerate(mats) if i % nshard == shard]
    print(f"backend {backend}  b={b}: {len(mats)} matrices  enum {time.time()-t0:.1f}s",
          flush=True)
    t1 = time.time(); viol = []
    for n, (key, (rows, ncol, prov)) in enumerate(mats):
        w = check_tu_gpu(rows, ncol, xp)
        if w:
            w["provenance"] = prov; viol.append(w)
            print(f"  *** VIOLATION n={n} det={w['det']} ***", flush=True); break
        if (n + 1) % 50 == 0:
            print(f"  {n+1}/{len(mats)}  {time.time()-t1:.0f}s", flush=True)
    dt = time.time() - t1
    res = {"b": b, "gate": f"F-BE-LTU-{b}", "shard": f"{shard}/{nshard}",
           "checked": len(mats), "violations": viol, "backend": backend,
           "verdict": "PASS" if not viol else "REFUTED", "wall_s": round(dt, 1),
           "method": ("GPU float64 batched screen + exact Bareiss adjudication of "
                      "every suspicious minor; Hadamard bound 14^7 << 2^53 so the "
                      "screen can only cost extra exact checks, never mask a violation")}
    suf = "" if nshard == 1 else f"_g{shard}of{nshard}"
    json.dump(res, open(f"../constants/be/ltu_scan_b{b}{suf}.json", "w"), indent=1)
    print(f"\nb={b} shard {shard}/{nshard}: {res['verdict']}  {len(mats)} matrices  "
          f"{dt:.1f}s  ({1000*dt/max(1,len(mats)):.0f} ms/matrix)  {backend}", flush=True)
