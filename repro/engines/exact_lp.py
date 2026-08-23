#!/usr/bin/env python3
"""
Exact rational LP, used by the facet recursion for one decision only: is a face
FULL-DIMENSIONAL in its own affine hull?

Why it is needed.  The Lasserre facet recursion sums over the FACETS of the
current face.  Summing over all constraints instead injects a spurious term
whenever a redundant constraint is tangent to the face in something of
dimension < k-1: the unit cube in R^3 with the tangent plane x+y+z <= 3
appended returns volume 2 instead of 1.  A face that is not full-dimensional
has k-measure 0 and must return 0, so detecting degeneracy is enough -- the
implicit equalities never have to be identified.

Test:  the region {y : gamma_i . y <= delta_i} is full-dimensional iff
       max { t : gamma_i . y + t <= delta_i, t <= 1 } > 0,
since at a relative interior point every constraint is strictly satisfied.

NO PHASE I IS NEEDED.  With tau0 = min(min_i delta_i, 1) the point y = 0,
t = tau0 is feasible, so substituting t = tau0 + u (u >= 0) and splitting the
free y into p - q with p, q >= 0 makes every right-hand side non-negative:
the all-slack basis is feasible and a single phase-II simplex with Bland's rule
suffices.  (A first version of this file used a hand-rolled two-phase simplex
and failed 118 of 300 randomised cross-checks against scipy; the shift removes
the whole failure mode.)
"""
import os as _os
from ratbackend import F


def simplex_max(c, A, b):
    """max c.z  s.t.  A z <= b, z >= 0, ALL b >= 0.
    Returns the optimum, or None if unbounded."""
    m, n = len(A), len(c)
    N = n + m
    T = [[F(x) for x in A[i]] + [F(1) if j == i else F(0) for j in range(m)]
         + [F(b[i])] for i in range(m)]
    T.append([-F(x) for x in c] + [F(0)] * m + [F(0)])
    basis = [n + i for i in range(m)]
    while True:
        col = -1
        for j in range(N):                      # Bland: first negative cost
            if T[m][j] < 0:
                col = j; break
        if col < 0:
            return T[m][N]
        row, best = -1, None
        for i in range(m):
            if T[i][col] > 0:
                r = T[i][N] / T[i][col]
                if best is None or r < best or (r == best and basis[i] < basis[row]):
                    best, row = r, i
        if row < 0:
            return None                         # unbounded
        p = T[row][col]
        T[row] = [x / p for x in T[row]]
        for i in range(m + 1):
            if i != row and T[i][col] != 0:
                f = T[i][col]
                T[i] = [a - f * bb for a, bb in zip(T[i], T[row])]
        basis[row] = col


_FD_MEMO = {}
_FD_CAP = int(_os.environ.get('FD_CAP', 300000))
_FD_STATS = [0, 0, 0]          # [calls, hits, cache flushes]          # [calls, memo hits]

def _fd_key(rows, k):
    """Content-based key.  The rows arrive from reduce_row(), which produces
    each coefficient as an already-reduced rational, so the raw (index, value)
    pairs are canonical enough: two identical constraint systems key identically.
    An earlier version renormalised every row to a primitive integer vector,
    which caught a few more collisions but cost 15% of total runtime -- more
    than the extra hits were worth (measured)."""
    return (k, frozenset((tuple(sorted(g.items())), d) for g, d in rows))


def full_dimensional(rows, k):
    """rows = [(gamma dict over 0..k-1, delta)]"""
    _FD_STATS[0] += 1
    key = _fd_key(rows, k)
    v = _FD_MEMO.get(key)
    if v is not None:
        _FD_STATS[1] += 1
        return v
    v = _full_dimensional(rows, k)
    # BOUNDED.  The first version of this cache had no cap; worker RSS reached
    # 13.5 GB and 90 workers OOM-killed a {4,4,2} run on 220 (BrokenProcessPool,
    # r141).  A hard cap with wholesale clearing keeps almost all of the benefit
    # -- the hit rate is dominated by faces that recur within the current term,
    # not by ancient entries -- at a predictable memory cost.
    if len(_FD_MEMO) >= _FD_CAP:
        _FD_MEMO.clear()
        _FD_STATS[2] += 1
    _FD_MEMO[key] = v
    return v


def _full_dimensional(rows, k):
    if any(not g and d < 0 for g, d in rows):
        return False                # constant-negative on the hull: empty
    # Rows that are CONSTANT on the affine hull (gamma empty, delta >= 0) are
    # redundant, not dimension-reducing.  Leaving them in makes the strictness
    # LP return max t = 0 whenever delta = 0, which wrongly condemned genuine
    # faces (the unit cube with a plane tangent along an edge lost half of two
    # of its facets).  Drop them before testing.
    rows = [(g, d) for g, d in rows if g]
    if k == 0:
        return True
    if not rows:
        return True
    tau0 = min([d for _, d in rows] + [F(1)])
    A, b = [], []
    for g, d in rows:
        r = [F(0)] * (2 * k + 1)
        for f, v in g.items():
            r[f] = F(v); r[k + f] = -F(v)
        r[2 * k] = F(1)
        A.append(r); b.append(F(d) - tau0)
    r = [F(0)] * (2 * k + 1); r[2 * k] = F(1)
    A.append(r); b.append(F(1) - tau0)
    c = [F(0)] * (2 * k) + [F(1)]
    val = simplex_max(c, A, b)
    if val is None:
        return True                             # t unbounded above
    return tau0 + val > 0


if __name__ == "__main__":
    import random
    import numpy as np
    from scipy.optimize import linprog
    print("unit cases")
    print("  square [0,1]^2      :", full_dimensional(
        [({0: F(1)}, F(1)), ({0: F(-1)}, F(0)), ({1: F(1)}, F(1)), ({1: F(-1)}, F(0))], 2))
    print("  point {x=y=1} in R^2:", full_dimensional(
        [({0: F(1)}, F(1)), ({1: F(1)}, F(1)), ({0: F(-1), 1: F(-1)}, F(-2))], 2))
    print("  segment in R^2      :", full_dimensional(
        [({0: F(1)}, F(0)), ({0: F(-1)}, F(0)), ({1: F(1)}, F(1)), ({1: F(-1)}, F(0))], 2))
    print("  empty               :", full_dimensional(
        [({0: F(1)}, F(0)), ({0: F(-1)}, F(-1))], 1))
    random.seed(1); bad = 0; N = 400
    for _ in range(N):
        k = random.randint(1, 4); m = random.randint(2, 7)
        rows = []
        for _ in range(m):
            g = {j: F(random.randint(-3, 3)) for j in range(k) if random.random() < 0.8}
            g = {j: v for j, v in g.items() if v != 0}
            rows.append((g, F(random.randint(-3, 3))))
        mine = full_dimensional(rows, k)
        # the reference must use the SAME semantics: constant rows are dropped
        # (redundant, not dimension-reducing) unless negative (empty)
        if any(not g and d < 0 for g, d in rows):
            ref = False
            if mine != ref:
                bad += 1
            continue
        rw = [(g, d) for g, d in rows if g]
        if not rw:
            if mine is not True:
                bad += 1
            continue
        A = [[float(g.get(j, 0)) for j in range(k)] + [1.0] for g, d in rw] \
            + [[0.0] * k + [1.0]]
        bb = [float(d) for g, d in rw] + [1.0]
        r = linprog([0.0] * k + [-1.0], A_ub=A, b_ub=bb,
                    bounds=[(None, None)] * k + [(None, None)], method="highs")
        ref = bool(r.success and -r.fun > 1e-9)
        if mine != ref:
            bad += 1
            if bad <= 3:
                print("  MISMATCH", k, mine, ref, rows)
    print(f"randomised cross-check vs scipy: {bad}/{N} mismatches")
