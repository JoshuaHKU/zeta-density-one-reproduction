#!/usr/bin/env python3
"""O-BE-1 (r159): exhaustive falsification of the laminar-family boundary-TU lemma.

Object.  On the b-cycle with edges 0..b-1, edge i has boundary vector
    d{i} = e_i - e_{i+1 mod b}
acting on the b vertex coordinates.  A WALL SYSTEM is the matrix whose rows are
  (1) the unit rows e_i, all i;
  (2) the boundary rows dS = sum_{i in S} (e_i - e_{i+1}), for S in a laminar
      family L built as: partition the edge set [b] into blocks; give each block
      B a permutation sigma_B; L = all sigma_B-prefixes, together with the whole
      blocks B (each whole block is already the last prefix, kept explicitly so
      the construction matches the lemma statement verbatim).

Test.  Total unimodularity: EVERY k x k minor (k <= b) must lie in {0, +-1}.
A single violation refutes the lemma -- report the witness (matrix, row/column
index sets, determinant) and stop that level.

Dedup.  Matrices are keyed by their canonical content (sorted row tuples), and
the iota-reflection (edge i -> -i mod b, which reverses the cycle) is folded in,
per the r159 sandbox finding that iota-partners coincide pointwise.

Exact integer arithmetic throughout -- Bareiss fraction-free elimination, so the
{0,+-1} test is a comparison of integers, never of floats.
"""
import sys, json, time, itertools
from fractions import Fraction as Q


def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i+1:]
        yield [[first]] + part


def boundary(S, b):
    """dS = sum_{i in S} (e_i - e_{i+1 mod b})"""
    v = [0] * b
    for i in S:
        v[i] += 1
        v[(i + 1) % b] -= 1
    return tuple(v)


def wall_matrices(b):
    """yield (canonical_key, rows, provenance) over all (partition, perms)"""
    seen = {}
    units = [tuple(1 if j == i else 0 for j in range(b)) for i in range(b)]
    for part in set_partitions(range(b)):
        for perms in itertools.product(*[itertools.permutations(B) for B in part]):
            L = []
            for sigma in perms:
                for t in range(1, len(sigma) + 1):
                    L.append(tuple(sorted(sigma[:t])))
            for B in part:                       # whole blocks, verbatim
                L.append(tuple(sorted(B)))
            rows = units + [boundary(S, b) for S in sorted(set(L))]
            key = tuple(sorted(set(rows)))
            # iota-reflection: edge i -> (-1-i) mod b reverses the cycle
            iota = tuple(sorted({boundary([(-1 - i) % b for i in S], b) for S in set(L)}
                                | set(units)))
            k = min(key, iota)
            if k not in seen:
                seen[k] = ([list(r) for r in key],
                           {"partition": [list(B) for B in part],
                            "perms": [list(p) for p in perms]})
    for k, (rows, prov) in seen.items():
        yield k, rows, prov


def det_bareiss(M):
    """exact integer determinant, fraction-free (Bareiss)"""
    n = len(M)
    A = [row[:] for row in M]
    sign, prev = 1, 1
    for k in range(n - 1):
        if A[k][k] == 0:
            piv = next((i for i in range(k + 1, n) if A[i][k] != 0), None)
            if piv is None:
                return 0
            A[k], A[piv] = A[piv], A[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j]) // prev
        prev = A[k][k]
    return sign * A[n - 1][n - 1]


def check_tu(rows, b, kmax=None):
    """returns None if TU, else a witness dict"""
    R = len(rows)
    kmax = kmax or b
    for k in range(1, min(kmax, b, R) + 1):
        for ri in itertools.combinations(range(R), k):
            for ci in itertools.combinations(range(b), k):
                sub = [[rows[i][j] for j in ci] for i in ri]
                d = det_bareiss(sub) if k > 1 else sub[0][0]
                if d not in (0, 1, -1):
                    return {"rows": list(ri), "cols": list(ci), "det": int(d),
                            "submatrix": sub}
    return None


if __name__ == "__main__":
    b = int(sys.argv[1])
    probe = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 0
    # --shard i/n : matrices are independent, so a level splits across hosts.
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard")+1].split("/"))
    t0 = time.time()
    mats = list(wall_matrices(b))
    print(f"b={b}: {len(mats)} deduped wall matrices "
          f"(rows {len(mats[0][1])} x cols {b})   enum {time.time()-t0:.1f}s",
          flush=True)
    if probe:
        t1 = time.time()
        for _, rows, _ in mats[:probe]:
            check_tu(rows, b)
        dt = (time.time() - t1) / probe
        print(f"  probe: {dt*1000:.1f} ms/matrix -> full level "
              f"{len(mats)*dt:.1f}s", flush=True)
        raise SystemExit
    viol = []
    mats = [m for i, m in enumerate(mats) if i % nshard == shard]
    if nshard > 1:
        print(f"  shard {shard}/{nshard}: {len(mats)} matrices", flush=True)
    for n, (key, rows, prov) in enumerate(mats):
        w = check_tu(rows, b)
        if w:
            w["provenance"] = prov
            w["matrix"] = rows
            viol.append(w)
            print(f"  *** VIOLATION at matrix {n}: det={w['det']} ***", flush=True)
            break
        if (n + 1) % 200 == 0:
            print(f"  {n+1}/{len(mats)}  {time.time()-t0:.0f}s", flush=True)
    res = {"b": b, "matrices_deduped": len(mats), "rows": len(mats[0][1]),
           "gate": f"F-BE-TU-{b}", "coverage": "exhaustive: all k x k minors, k<=b",
           "violations": viol, "verdict": "PASS" if not viol else "REFUTED",
           "wall_s": round(time.time() - t0, 1)}
    res["shard"] = f"{shard}/{nshard}"
    suf = "" if nshard == 1 else f"_s{shard}of{nshard}"
    json.dump(res, open(f"../constants/be/tu_scan_b{b}{suf}.json", "w"), indent=1)
    print(f"\nF-BE-TU-{b}: {res['verdict']}   {res['wall_s']}s", flush=True)
