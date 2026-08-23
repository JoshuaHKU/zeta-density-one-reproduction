#!/usr/bin/env python3
"""
Exact integration of a polynomial over a rational polytope by the Lasserre
facet recursion, with the irrational facet normalisations cancelled by
coordinate projection and with memoisation on tight constraint sets.

        (d + k) int_P f  =  sum_i  (b_i / |a_{i,j_i}|) int_{pi_{j_i}(F_i)} f(x(y)) dy

for f homogeneous of degree d about the origin of the current coordinate
system; see phase3/FACET_RECURSION_LOG.md step 1 for the derivation.

Canonical keys.  A face is the tight set T; the pivot columns of the reduced
row echelon form of {a_i : i in T} depend only on the row SPAN, hence only on
T, so free(T) = complement(pivots(T)) is canonical, and adding one constraint
adds exactly one pivot -- which is the projection direction.  Memo key is
therefore (T, alpha) with alpha a monomial over free(T).

Two corrections that the unit tests forced (log steps 2.2-2.4): faces that are
not full-dimensional must be detected and returned as 0 (exact_lp.py), and the
reduced constraints must be deduplicated at EVERY face, because distinct
original half-spaces can reduce to the same hyperplane on a face.

API
    P = Polytope(rows, n)         rows = [(coeff tuple, const)] meaning a.x <= b
    P.integrate(poly)             poly = {exponent tuple over R^n : Fraction}
"""
from ratbackend import F
from exact_lp import full_dimensional


# ---------------------------------------------------------------- polynomials
def poly_mul_affine(poly, var, aff, nvars):
    """substitute x_var = aff (a dict {exponent tuple over the REMAINING vars:
    coeff}) into a polynomial over nvars variables, dropping coordinate `var`.
    Returns a polynomial over nvars-1 variables."""
    out = {}
    for exp, c in poly.items():
        p = exp[var]
        rest = exp[:var] + exp[var + 1:]
        term = {rest: c}
        for _ in range(p):
            new = {}
            for e1, c1 in term.items():
                for e2, c2 in aff.items():
                    e = tuple(x + y for x, y in zip(e1, e2))
                    new[e] = new.get(e, F(0)) + c1 * c2
            term = new
        for e, c1 in term.items():
            if c1:
                out[e] = out.get(e, F(0)) + c1
    return {e: c for e, c in out.items() if c}


def by_degree(poly):
    d = {}
    for e, c in poly.items():
        d.setdefault(sum(e), {})[e] = c
    return d


# ---------------------------------------------------------------- the polytope
class Polytope:
    def __init__(self, rows, n):
        # The recursion SUMS over constraints, so a half-space listed twice would
        # be counted twice (a unit test on the square with a duplicated facet
        # returned 2).  Walks repeat positions, so duplicates really occur.
        # Normalise each row by the unique positive scaling that makes the
        # coefficient vector a primitive integer vector, then deduplicate.
        # Redundant PARALLEL rows (same a, larger b) are harmless: their face is
        # empty and contributes 0.
        from math import gcd
        seen, norm = set(), []
        for a, b in rows:
            a = [F(x) for x in a]; b = F(b)
            if all(x == 0 for x in a):
                if b < 0:
                    norm = [((0,) * n, F(-1))]      # infeasible
                    break
                continue                            # trivially true: drop
            L = 1
            for x in list(a) + [b]:
                L = L * x.denominator // gcd(L, x.denominator)
            ai = [int(x * L) for x in a]; bi = F(b * L)
            g = 0
            for x in ai:
                g = gcd(g, abs(x))
            ai = tuple(x // g for x in ai); bi = bi / g
            if (ai, bi) not in seen:
                seen.add((ai, bi)); norm.append((tuple(F(x) for x in ai), bi))
        self.rows = norm
        self.n = n
        self._red = {}
        self._memo = {}
        self._dim = {}
        self._fac = {}
        self.nodes = 0
        # NOT called by default: measured on the walk polytopes it removes ZERO
        # rows (the descriptions are already irredundant after dedup) and costs
        # one LP per row.  Kept for constraint families where it may pay.
        # self._prune()

    def _prune(self):
        """Drop constraints that define no facet.  A globally redundant
        half-space contains P, hence contains every face of P, so it can only
        ever be tight on a lower-dimensional (measure-zero) face: dropping it
        changes nothing and removes its whole subtree from the recursion.
        Test: the face {i} must be full-dimensional in its own affine hull."""
        keep = []
        for i in range(len(self.rows)):
            T = frozenset([i])
            red = self.reduce(T)
            if red is None:
                continue
            pivots, free, const, coef = red
            k = len(free)
            if k == 0:
                keep.append(i); continue
            rws = []
            for j in range(len(self.rows)):
                if j == i:
                    continue
                rr = self.reduce_row(T, j)
                if rr is None:
                    continue
                g, d = rr
                rws.append(({free.index(f): v for f, v in g.items()}, d))
            if full_dimensional(rws, k):
                keep.append(i)
        if len(keep) != len(self.rows):
            self.rows = [self.rows[i] for i in keep]
            self._red = {}; self._memo = {}; self._dim = {}; self._fac = {}

    # ---- canonical reduction of the tight set -----------------------------
    def reduce(self, T):
        """returns (pivots, free, const, coef) where for x in aff(F_T):
        x[p] = const[p] + sum_{f in free} coef[p][f] * x[f]."""
        if T in self._red:
            return self._red[T]
        rows = [(list(self.rows[i][0]), self.rows[i][1]) for i in sorted(T)]
        n = self.n
        pivots = []
        r = 0
        for c in range(n):
            piv = None
            for rr in range(r, len(rows)):
                if rows[rr][0][c] != 0:
                    piv = rr; break
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            a, b = rows[r]
            s = a[c]
            rows[r] = ([x / s for x in a], b / s)
            for rr in range(len(rows)):
                if rr != r and rows[rr][0][c] != 0:
                    f = rows[rr][0][c]
                    rows[rr] = ([x - f * y for x, y in zip(rows[rr][0], rows[r][0])],
                                rows[rr][1] - f * rows[r][1])
            pivots.append(c); r += 1
            if r == len(rows):
                break
        # inconsistent system (0 = nonzero) -> empty face
        for rr in range(r, len(rows)):
            if all(x == 0 for x in rows[rr][0]) and rows[rr][1] != 0:
                self._red[T] = None
                return None
        free = [c for c in range(n) if c not in pivots]
        const = {}; coef = {}
        for idx, p in enumerate(pivots):
            a, b = rows[idx]
            const[p] = b
            coef[p] = {f: -a[f] for f in free}
        out = (tuple(pivots), tuple(free), const, coef)
        self._red[T] = out
        return out

    def reduce_row(self, T, i):
        """constraint i expressed in the free coordinates of T: (gamma, delta)"""
        red = self.reduce(T)
        if red is None:
            return None
        pivots, free, const, coef = red
        a, b = self.rows[i]
        delta = b - sum(a[p] * const[p] for p in pivots)
        gamma = {}
        for f in free:
            g = a[f] + sum(a[p] * coef[p][f] for p in pivots)
            if g:
                gamma[f] = g
        return gamma, delta

    # ---- per-face facet list, deduplicated AFTER reduction ------------------
    def facets(self, T):
        """distinct reduced facets of the face T.
        Two DIFFERENT original constraints can reduce to the SAME hyperplane on a
        face (on x=1 of the square [-1,1]^2 the rows (0,1)<=1 and (1,2)<=3 both
        become y<=1).  Summing over original indices then counts that facet
        twice -- this was the last bug: it inflated the square's area to 5.
        So the reduced rows are normalised to primitive integer form and
        deduplicated here, at every face."""
        if T in self._fac:
            return self._fac[T]
        from math import gcd
        red = self.reduce(T)
        seen, out = {}, []
        for i in range(len(self.rows)):
            if i in T:
                continue
            rr = self.reduce_row(T, i)
            if rr is None:
                continue
            g, d = rr
            if not g:
                out.append((i, g, d)); continue
            L = 1
            for x in list(g.values()) + [d]:
                L = L * x.denominator // gcd(L, x.denominator)
            gi = {f: int(v * L) for f, v in g.items()}; di = F(d * L)
            q = 0
            for v in gi.values():
                q = gcd(q, abs(v))
            key = (tuple(sorted((f, v // q) for f, v in gi.items())), di / q)
            if key in seen:
                continue
            seen[key] = i
            out.append((i, g, d))
        self._fac[T] = out
        return out

    # ---- the recursion -----------------------------------------------------
    def M(self, T, alpha):
        """integral of the monomial alpha (over free(T)) on the projected face"""
        key = (T, alpha)
        if key in self._memo:
            return self._memo[key]
        self.nodes += 1
        red = self.reduce(T)
        if red is None:
            self._memo[key] = F(0); return F(0)
        pivots, free, const, coef = red
        k = len(free)
        # A face that is NOT full-dimensional in its own affine hull has
        # k-measure zero and must return 0.  Summing over all constraints
        # otherwise injects spurious terms whenever a redundant constraint is
        # tangent to the face (unit cube + tangent plane returned volume 2).
        if k > 0:
            if T not in self._dim:
                rows = [({free.index(f): v for f, v in g.items()}, d)
                        for _, g, d in self.facets(T)]
                self._dim[T] = full_dimensional(rows, k)
            if not self._dim[T]:
                self._memo[key] = F(0); return F(0)
        if k == 0:
            x = [F(0)] * self.n
            for p in pivots:
                x[p] = const[p]
            ok = all(sum(a[t] * x[t] for t in range(self.n)) <= b
                     for a, b in self.rows)
            v = F(1) if ok else F(0)
            self._memo[key] = v; return v
        d = sum(alpha)
        tot = F(0)
        for i, gamma, delta in self.facets(T):
            if not gamma:
                # constant on the affine hull: 0 <= delta.  delta < 0 means the
                # whole face is EMPTY -- skipping it here (as a first version of
                # this file did) leaves a spurious non-zero value.
                if delta < 0:
                    self._memo[key] = F(0); return F(0)
                continue                       # redundant on this face
            if delta == 0:
                continue                       # facet through the origin: prefactor 0
            j = min(gamma)                     # canonical new pivot
            jpos = free.index(j)
            # x_j = (delta - sum_{f != j} gamma_f x_f)/gamma_j
            aff = {}
            zero = tuple([0] * (k - 1))
            aff[zero] = delta / gamma[j]
            for f, g in gamma.items():
                if f == j:
                    continue
                fpos = free.index(f)
                fpos2 = fpos if fpos < jpos else fpos - 1
                e = [0] * (k - 1); e[fpos2] = 1
                e = tuple(e)
                aff[e] = aff.get(e, F(0)) - g / gamma[j]
            sub = poly_mul_affine({alpha: F(1)}, jpos, aff, k)
            T2 = T | frozenset([i])
            # free(T2) must be free(T) minus j -- guaranteed by canonicity
            inner = F(0)
            for deg, part in by_degree(sub).items():
                for e, c in part.items():
                    inner += c * self.M(T2, e)
            tot += delta / abs(gamma[j]) * inner
        v = tot / (d + k)
        self._memo[key] = v
        return v

    def integrate(self, poly):
        """poly = {exponent tuple over R^n : coeff}"""
        tot = F(0)
        for e, c in poly.items():
            tot += c * self.M(frozenset(), e)
        return tot


# ---------------------------------------------------------------- walk classes
def walk_integral(pos, extra_walks=(), weight_cols=None):
    """
        int (1-spread(pos))_+ * prod_{i in weight_cols} |v_i|
              * prod_w (1-spread(w))_+   dv
    computed as a signed sum over sign orthants of monomial integrals over
    rational polytopes: one auxiliary variable per overlap factor.
    """
    from itertools import product as iproduct
    d = len(pos[0])
    walks = [pos] + [list(w) for w in extra_walks]
    naux = len(walks)
    n = d + naux
    cols = list(range(d)) if weight_cols is None else list(weight_cols)
    mono = tuple(1 if i in cols else 0 for i in range(n))
    total = F(0)
    sigmas = [s for s in iproduct((1, -1), repeat=d) if s[0] == 1]
    for sigma in sigmas:
        rows = []
        for i in range(d):
            e = [0] * n; e[i] = -sigma[i]
            rows.append((e, 0))                       # sigma_i v_i >= 0
        for w, wk in enumerate(walks):
            t = d + w
            for p in wk:
                a1 = [-c for c in p] + [0] * naux; a1[t] = 1
                rows.append((a1, 0))                  # t <= p_a
                a2 = [c for c in p] + [0] * naux; a2[t] = -1
                rows.append((a2, 1))                  # p_a <= t+1
        P = Polytope(rows, n)
        sgn = 1
        for s in sigma:
            sgn *= s
        total += sgn * P.integrate({mono: F(1)})
    return 2 * total


if __name__ == "__main__":
    import sys, time, json, os
    HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(HERE, "..", "phase0"))
    ARCH = {
        'T0':   ([(0,0,0),(1,0,0),(0,0,0),(0,1,0),(0,0,0),(0,0,1)], F(3,70)),
        'NEST': ([(0,0,0),(1,0,0),(0,0,0),(0,1,0),(0,1,1),(0,1,0)], F(17,420)),
        'T1':   ([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,0),(0,0,1)], F(1,90)),
        'T2':   ([(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,1,1),(0,0,1)], F(1,180)),
        'T3':   ([(0,0,0),(1,0,0),(1,1,0),(1,1,1),(0,1,1),(0,0,1)], F(1,70)),
    }
    ok = True
    for nm, (p, tgt) in ARCH.items():
        t0 = time.time()
        v = walk_integral([tuple(q) for q in p])
        g = (v == tgt); ok &= g
        print(f"  {nm:<5} = {str(v):<10} target {str(tgt):<9} "
              f"{'MATCH' if g else '*** MISMATCH ***'}   {time.time()-t0:5.1f}s")
    print("\n" + ("step-3 partial (Phase 0 set) PASS" if ok else "*** FAIL ***"))
