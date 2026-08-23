#!/usr/bin/env python3
"""O-BE-4 (r160): total-unimodularity falsification of the LIFTED system L'.

Coordinates: (m_0..m_{b-1}, c_B for each block B)  ->  b + r columns.
Rows:
  1. m-unit rows      e_i                              (b rows)
  2. whole-block rows dB = sum_{i in B}(e_i - e_{i+1})  (r rows, no c-part)
  3. lifted prefixes  e_{c_B} + dS, S over all sigma_B-prefixes of B
                      (including B itself)              (b rows, since sum|B| = b)
Total (b + r + b) x (b + r).

Test: every k x k minor, k <= b+r, lies in {0, +-1}.  Bareiss exact integer
elimination -- the {0,+-1} test is an integer comparison, never a float one.
A single violation refutes lemma L' and is a real fire alarm.

Blocks are ordered by least element so the c-column assignment is canonical.
Dedup: matrix content canonical form, with the iota-reflection (i -> -1-i mod b)
folded in, as in O-BE-1.
"""
import sys, json, time, itertools
sys.path.insert(0, ".")
from be_tu_scan import set_partitions, det_bareiss


def boundary_m(S, b, ncol):
    v = [0] * ncol
    for i in S:
        v[i] += 1
        v[(i + 1) % b] -= 1
    return v


def lifted_matrices(b):
    seen = {}
    for part in set_partitions(range(b)):
        blocks = sorted([sorted(B) for B in part], key=lambda B: B[0])
        r = len(blocks)
        ncol = b + r
        for perms in itertools.product(*[itertools.permutations(B) for B in blocks]):
            rows = [tuple(1 if j == i else 0 for j in range(ncol)) for i in range(b)]
            for B in blocks:
                rows.append(tuple(boundary_m(B, b, ncol)))
            for bi, sigma in enumerate(perms):
                for t in range(1, len(sigma) + 1):
                    v = boundary_m(sigma[:t], b, ncol)
                    v[b + bi] += 1                    # e_{c_B}
                    rows.append(tuple(v))
            key = tuple(sorted(set(rows)))
            # iota-dedup DISABLED for the lifted system.  On the plain wall system
            # iota (i -> -1-i mod b) is a clean symmetry, but here each block owns
            # a c-column, and reflection permutes the blocks -- so the c-labels
            # must be permuted with them.  A first version left the c-part fixed
            # and over-merged: it gave 11/61 systems at b=3/4 where the sandbox
            # reports 13/73.  Content-only dedup reproduces 13/73 exactly.
            # Over-counting is safe here; under-counting would silently skip
            # matrices the falsification is supposed to test.
            k = key
            if k not in seen:
                seen[k] = ([list(x) for x in key], ncol,
                           {"partition": blocks, "perms": [list(p) for p in perms]})
    return list(seen.items())


def check_tu(rows, ncol, kmax=None):
    R = len(rows)
    kmax = kmax or ncol
    for k in range(1, min(kmax, ncol, R) + 1):
        for ri in itertools.combinations(range(R), k):
            for ci in itertools.combinations(range(ncol), k):
                sub = [[rows[i][j] for j in ci] for i in ri]
                d = det_bareiss(sub) if k > 1 else sub[0][0]
                if d not in (0, 1, -1):
                    return {"rows": list(ri), "cols": list(ci), "det": int(d),
                            "submatrix": sub}
    return None


if __name__ == "__main__":
    b = int(sys.argv[1])
    probe = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 0
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard")+1].split("/"))
    t0 = time.time()
    mats = lifted_matrices(b)
    print(f"b={b}: {len(mats)} deduped lifted matrices   enum {time.time()-t0:.1f}s",
          flush=True)
    if probe:
        t1 = time.time()
        for _, (rows, ncol, _) in mats[:probe]:
            check_tu(rows, ncol)
        dt = (time.time() - t1) / probe
        print(f"  probe: {dt*1000:.0f} ms/matrix -> full level {len(mats)*dt/3600:.2f} core-h",
              flush=True)
        raise SystemExit
    mine = [m for i, m in enumerate(mats) if i % nshard == shard]
    if nshard > 1:
        print(f"  shard {shard}/{nshard}: {len(mine)} matrices", flush=True)
    viol = []
    for n, (key, (rows, ncol, prov)) in enumerate(mine):
        w = check_tu(rows, ncol)
        if w:
            w["provenance"] = prov; w["matrix"] = rows; w["ncol"] = ncol
            viol.append(w); print(f"  *** VIOLATION n={n} det={w['det']} ***", flush=True)
            break
        if (n + 1) % 100 == 0:
            print(f"  {n+1}/{len(mine)}  {time.time()-t0:.0f}s", flush=True)
    res = {"b": b, "gate": f"F-BE-LTU-{b}", "shard": f"{shard}/{nshard}",
           "matrices_deduped_total": len(mats), "checked_this_shard": len(mine),
           "coverage": "exhaustive: all k x k minors, k <= b+r, Bareiss exact integers",
           "violations": viol, "verdict": "PASS" if not viol else "REFUTED",
           "wall_s": round(time.time()-t0, 1)}
    suf = "" if nshard == 1 else f"_s{shard}of{nshard}"
    json.dump(res, open(f"../constants/be/ltu_scan_b{b}{suf}.json", "w"), indent=1)
    print(f"\nF-BE-LTU-{b} shard {shard}/{nshard}: {res['verdict']}  {res['wall_s']}s",
          flush=True)
