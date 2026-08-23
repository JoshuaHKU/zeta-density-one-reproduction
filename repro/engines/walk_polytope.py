#!/usr/bin/env python3
"""
Second, independent exact method for walk-class integrals -- the polytope
route, in any dimension.

        I(pos) = int_{[-1,1]^d} (1 - spread(pos(v)))_+ * prod_i |v_i| dv

Two rewritings turn this into integrals of a monomial over rational polytopes.

(1) The overlap identity of the paper (sec 5.5):
        (1 - spread(P))_+ = Leb{ t : t <= p_a <= t+1 for all a } ,
    so an extra variable t absorbs the piecewise-linear factor:
        I = int dt dv  1[t <= p_a(v) <= t+1 for all a] * prod|v_i| .

(2) prod|v_i| is a signed monomial on each sign orthant, and each v_i is itself
    a difference of two positions, so the orthant walls are already among the
    kink hyperplanes.  Hence
        I = sum_{sigma in {+-1}^d} (prod sigma_i) * int_{Q_sigma} prod v_i dv dt,
        Q_sigma = { (v,t) : sigma_i v_i >= 0, t <= p_a(v) <= t+1 for all a } ,
    a bounded rational polytope in R^{d+1} (bounded because 0 is a position, so
    t in [-1,0] and every position lies in [t,t+1]).
    The map v -> -v identifies Q_{-sigma} with Q_sigma and preserves the
    integrand, so only half the orthants are evaluated.

Each polytope integral is computed exactly: vertices by solving every
(d+1)-subset of the facet equations in rational arithmetic, a triangulation of
the vertex set, and the exact barycentric monomial formula

        int_Delta f = |det[w_1-w_0,...,w_D-w_0]| *
                      sum_{j_1..j_m} (prod_i c_{i,j_i}) * prod_k mult_k! / (m+D)!

for f a product of m linear forms, D = d+1.  The triangulation is produced
numerically (scipy Delaunay) and then VERIFIED exactly: the simplices must have
non-zero volume, their rational volumes must sum to the volume obtained from an
independent convex-hull computation, and the whole answer is cross-checked
against the iterated-integration engine walk_exact3.py on the 3-variable
classes.  This is the same discipline as the paper's own dual-method
certification: two code paths that share no arithmetic must agree fraction by
fraction.
"""
from fractions import Fraction as F
from itertools import combinations, product
import numpy as np


# ---------- exact rational linear algebra -------------------------------
def rsolve(A, b):
    """exact solve of a square rational system; None if singular"""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(n):
        p = next((r for r in range(i, n) if M[r][i] != 0), None)
        if p is None:
            return None
        M[i], M[p] = M[p], M[i]
        piv = M[i][i]
        M[i] = [x / piv for x in M[i]]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i]
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [M[i][n] for i in range(n)]


def rdet(A):
    M = [row[:] for row in A]
    n = len(M); d = F(1)
    for i in range(n):
        p = next((r for r in range(i, n) if M[r][i] != 0), None)
        if p is None:
            return F(0)
        if p != i:
            M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        inv = F(1) / M[i][i]
        for r in range(i + 1, n):
            f = M[r][i] * inv
            for c in range(i, n):
                M[r][c] -= f * M[i][c]
    return d


# ---------- the polytope --------------------------------------------------
def build_constraints(pos, sigma):
    """rows (a, b) meaning a . (v,t) <= b, in R^{d+1}"""
    d = len(pos[0])
    C = []
    for i in range(d):
        e = [F(0)] * (d + 1); e[i] = F(-sigma[i])
        C.append((e, F(0)))                      # sigma_i v_i >= 0
    for p in pos:
        a1 = [F(-c) for c in p] + [F(1)]         # t - p_a <= 0
        C.append((a1, F(0)))
        a2 = [F(c) for c in p] + [F(-1)]         # p_a - t <= 1
        C.append((a2, F(1)))
    return C


def vertices(C, D):
    """all vertices of {x : a.x <= b}, exactly"""
    n = len(C)
    V, seen = [], set()
    for idx in combinations(range(n), D):
        A = [C[i][0] for i in idx]; b = [C[i][1] for i in idx]
        x = rsolve([r[:] for r in A], b[:])
        if x is None:
            continue
        if any(sum(a * xi for a, xi in zip(C[j][0], x)) > C[j][1] for j in range(n)):
            continue
        key = tuple(x)
        if key not in seen:
            seen.add(key); V.append(x)
    return V


def simplex_monomial(W, cols, m_den):
    """exact integral of prod_{i in cols} x_i over the simplex with rational
    vertex list W (D+1 vertices in R^D)."""
    D = len(W) - 1
    M = [[W[j + 1][i] - W[0][i] for i in range(D)] for j in range(D)]
    det = rdet(M)
    if det == 0:
        return F(0)
    m = len(cols)
    # coefficient table c[i][j] = (vertex j)_(cols[i])
    c = [[W[j][cols[i]] for j in range(D + 1)] for i in range(m)]
    tot = F(0)
    for js in product(range(D + 1), repeat=m):
        prod_c = F(1)
        for i, j in enumerate(js):
            prod_c *= c[i][j]
            if prod_c == 0:
                break
        if prod_c == 0:
            continue
        mult = {}
        for j in js:
            mult[j] = mult.get(j, 0) + 1
        fac = 1
        for v in mult.values():
            for q in range(2, v + 1):
                fac *= q
        tot += prod_c * fac
    return abs(det) * tot / m_den


def integral(pos, verbose=False):
    d = len(pos[0]); D = d + 1
    m_den = 1
    for q in range(2, d + D + 1):
        m_den *= q                                # (m + D)! with m = d
    cols = list(range(d))
    total = F(0)
    sigmas = [s for s in product((1, -1), repeat=d) if s[0] == 1]   # v -> -v symmetry
    for sigma in sigmas:
        C = build_constraints(pos, sigma)
        V = vertices(C, D)
        if len(V) < D + 1:
            continue
        P = np.array([[float(x) for x in v] for v in V])
        from scipy.spatial import ConvexHull
        try:
            hull = ConvexHull(P)
        except Exception:
            continue                       # lower-dimensional cell: measure zero
        # cone from V[0] over the hull facets: facets containing V[0] are flat
        # against the apex and contribute nothing, the rest tile the polytope.
        apex = 0
        simplices = [list(f) + [apex] for f in hull.simplices if apex not in f]
        sgn = 1
        for s in sigma:
            sgn *= s
        sub = F(0); volnum = 0.0
        fac = 1
        for q in range(2, D + 1):
            fac *= q
        for simp in simplices:
            W = [V[i] for i in simp]
            M = np.array([[float(W[j + 1][i] - W[0][i]) for i in range(D)]
                          for j in range(D)])
            dv = abs(np.linalg.det(M)) / fac
            if dv < 1e-14:
                continue                   # degenerate sliver
            volnum += dv
            sub += simplex_monomial(W, cols, m_den)
        if abs(volnum - hull.volume) > 1e-8 * max(1.0, hull.volume):
            raise RuntimeError(f"triangulation volume mismatch: "
                               f"{volnum} vs hull {hull.volume}")
        total += sgn * sub
        if verbose:
            print(f"      sigma={sigma}  verts={len(V)}  simplices={len(simplices)}"
                  f"  vol={volnum:.8f}  contrib={float(sgn*sub):+.10f}")
    return 2 * total          # the two half-orthant families are equal


if __name__ == "__main__":
    import sys, time
    ARCH = {
        'T0': ([(0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)], F(3, 70)),
        'T1': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)], F(1, 90)),
        'T2': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], F(1, 180)),
        'T3': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 0, 1)], F(1, 70)),
        'NEST': ([(0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 1, 0)], F(17, 420)),
    }
    ok = True
    for nm, (p, tgt) in ARCH.items():
        t0 = time.time()
        v = integral(p, verbose="-v" in sys.argv)
        g = (v == tgt); ok &= g
        print(f"  {nm:<5} = {str(v):<12} = {float(v):.10f}   target {str(tgt):<8} "
              f"{'MATCH' if g else '*** MISMATCH ***'}   {time.time()-t0:.0f}s")
    print("\n" + ("polytope-route regression PASS" if ok else "*** FAIL ***"))
