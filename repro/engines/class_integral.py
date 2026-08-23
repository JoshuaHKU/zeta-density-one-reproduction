#!/usr/bin/env python3
"""
STEP 4 -- the general block-partition class integral, via F-CYC + facet recursion.

Structure (recovered in Phase 0 and generalised here).  A class {b_1..b_r} of
m_k is a partition of the k EDGES of the k-cycle into blocks.  Writing v_0..v_{k-1}
for the edge frequencies:

  * each block carries a connected factor C_{b_j}(its frequencies), which is
    supported on "block frequencies sum to zero" -- so the free dimension is
    sum_j (b_j - 1) = k - r;
  * the cycle carries the walk overlap O_k = (1 - spread(partial sums))_+ ;
  * val = int O_k * prod_j C_{b_j} dv .

F-CYC (paper sec 5.5(ii), cyclic_cumulant.py):

    C_b(v) = sum_{P |- block} (-1)^{|P|-1} sum_{cyclic orders sigma of P}
             ov(0, w_{s1}, w_{s1}+w_{s2}, ...),      w_p = sum of v over part p

with ov(...) = (1 - spread)_+ .  Check at b=2: the two partitions give
1 - (1-|v|)_+ = min(|v|,1).  Since every edge frequency is a difference of two
walk positions, |v| <= spread < 1 on the support, so a SIZE-2 BLOCK may be
carried as the monomial factor |v| instead of two overlap factors -- one fewer
auxiliary dimension per pair.  Blocks of size >= 3 are expanded by F-CYC.

Each resulting term is therefore
    (product of signs) * int (product of overlaps) * (monomial) dv
= a signed monomial integral over a rational polytope with one auxiliary
variable per overlap factor -- exactly what facet_recursion.py evaluates.

Usage:
    python3 class_integral.py --validate      # C5, {4,2}, {6}, {2,2,2}, {2^4}
    python3 class_integral.py --time          # cost probe for the unknown classes
    python3 class_integral.py CLASS [--jobs N]
"""
import itertools, sys, os, time
from ratbackend import F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from facet_recursion import Polytope


# ---------------------------------------------------------------- F-CYC
def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]
        yield [[first]] + part


def fcyc_terms(block):
    """[(sign, [part, part, ...] in cyclic order)] for the connected factor."""
    out = []
    for P in set_partitions(block):
        m = len(P)
        sign = (-1) ** (m - 1)
        first = next(i for i, blk in enumerate(P) if min(block) in blk)
        others = [i for i in range(m) if i != first]
        for perm in itertools.permutations(others):
            out.append((sign, [P[first]] + [P[i] for i in perm]))
    return out


# ---------------------------------------------------------------- geometry
def edge_forms(blocks, k):
    """v_i as a vector over the free variables (one per block, minus the last)."""
    free_of = {}
    nfree = 0
    for blk in blocks:
        for e in sorted(blk)[:-1]:
            free_of[e] = nfree; nfree += 1
    forms = {}
    for blk in blocks:
        srt = sorted(blk)
        for e in srt[:-1]:
            f = [0] * nfree; f[free_of[e]] = 1
            forms[e] = f
        last = [0] * nfree
        for e in srt[:-1]:
            last[free_of[e]] -= 1
        forms[srt[-1]] = last
    return forms, nfree, free_of


def cycle_walk(forms, k, nfree):
    """positions of the k-cycle walk: 0 and the partial sums."""
    pos = [tuple([0] * nfree)]
    acc = [0] * nfree
    for i in range(k - 1):
        acc = [a + b for a, b in zip(acc, forms[i])]
        pos.append(tuple(acc))
    return pos


def term_walk(parts, forms, nfree):
    """positions of one F-CYC term: partial sums of the merged block sums."""
    ws = []
    for p in parts:
        w = [0] * nfree
        for e in p:
            w = [a + b for a, b in zip(w, forms[e])]
        ws.append(w)
    pos = [tuple([0] * nfree)]
    acc = [0] * nfree
    for w in ws[:-1]:
        acc = [a + b for a, b in zip(acc, w)]
        pos.append(tuple(acc))
    return pos


# ---------------------------------------------------------------- integration
def one_term(args):
    walks, cols, nfree = args
    naux = len(walks)
    n = nfree + naux
    mono = tuple(1 if i in cols else 0 for i in range(n))
    total = F(0)
    # sigma <-> -sigma folding.  The integrand is invariant under the global
    # reflection v -> -v: walk positions negate, so the spread (and hence every
    # overlap factor) is unchanged, and |v| is unchanged.  That reflection maps
    # the orthant sigma onto the orthant -sigma, and the signed monomial
    # sgn(sigma) * prod x_c equals prod |x_c| on BOTH.  So the two orthants
    # contribute equally and exactly half of them need to be integrated.
    # Exact factor 2 whenever the class has at least one size-2 block.
    orthants = list(itertools.product((1, -1), repeat=len(cols)))
    if cols:
        orthants = [s for s in orthants if s[0] == 1]
        fold = 2
    else:
        fold = 1
    for sigma in orthants:
        rows = []
        for c, s in zip(cols, sigma):
            e = [0] * n; e[c] = -s
            rows.append((e, 0))
        for w, wk in enumerate(walks):
            t = nfree + w
            for p in wk:
                a1 = [-c for c in p] + [0] * naux; a1[t] = 1
                rows.append((a1, 0))
                a2 = [c for c in p] + [0] * naux; a2[t] = -1
                rows.append((a2, 1))
        sgn = 1
        for s in sigma:
            sgn *= s
        total += sgn * Polytope(rows, n).integrate({mono: F(1)})
    return fold * total


def class_terms(blocks, k):
    """[(sign, walks, cols, nfree)] -- one entry per F-CYC term tuple."""
    forms, nfree, free_of = edge_forms(blocks, k)
    base = cycle_walk(forms, k, nfree)
    cols = [free_of[sorted(b)[0]] for b in blocks if len(b) == 2]
    big = [b for b in blocks if len(b) >= 3]
    per = [fcyc_terms(sorted(b)) for b in big]
    out = []
    for combo in itertools.product(*per) if per else [()]:
        sign = 1
        walks = [base]
        for s, parts in combo:
            sign *= s
            w = term_walk(parts, forms, nfree)
            if len(w) > 1:                     # a single-position walk is ov = 1
                walks.append(w)
        out.append((sign, walks, cols, nfree))
    return out


def class_integral(blocks, k, jobs=1, verbose=False):
    terms = class_terms(blocks, k)
    if verbose:
        print(f"    {len(terms)} F-CYC term tuples, free dim {terms[0][3]}, "
              f"monomial cols {terms[0][2]}")
    tot = F(0)
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            for s, v in zip((t[0] for t in terms),
                            ex.map(one_term, [(t[1], t[2], t[3]) for t in terms])):
                tot += s * v
    else:
        for s, walks, cols, nfree in terms:
            tot += s * one_term((walks, cols, nfree))
    return tot


# ---------------------------------------------------------------- driver
# --validate targets.  BUNDLE = True means the target is the class bundle
# (sum over dihedral placement classes with multiplicity), so the driver must
# enumerate the orbits; BUNDLE = False means a single placement.
# The {4,2} entry used to carry the BUNDLE value -23/420 while the driver
# evaluated ONE placement (-2/315), so this self-test had been failing silently
# since it was written -- it was never wired into run_all.sh gates.  For a PURE
# class the two agree (one placement), which is why C5 and {6} passed and hid it.
CLASSES = {
    "C5":      ([[0, 1, 2, 3, 4]], 5, F(1, 36), False),
    "{6}":     ([[0, 1, 2, 3, 4, 5]], 6, F(-1, 126), False),
    "{4,2}":   ([[0, 1, 2, 3], [4, 5]], 6, F(-23, 420), True),
    "{2,2,2}": ([[0, 1], [2, 3], [4, 5]], 6, F(32, 105), True),
}


def bundle(blocks, k, jobs=1):
    """sum over the dihedral placement classes of the class of `blocks`"""
    import sys as _s, os as _o
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    from block_classes import set_partitions_by_sizes, orbit
    sizes = sorted((len(b) for b in blocks), reverse=True)
    o = {}
    for p in set_partitions_by_sizes(k, sizes):
        o.setdefault(orbit(p, k), []).append(p)
    tot = F(0)
    for members in o.values():
        rep = [list(b) for b in members[0]]
        tot += len(members) * class_integral(rep, k, jobs=jobs)
    return tot

if __name__ == "__main__":
    jobs = 1
    if "--jobs" in sys.argv:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1])
    if "--validate" in sys.argv:
        ok = True
        for nm, (blocks, k, tgt, bun) in CLASSES.items():
            t0 = time.time()
            print(f"  {nm}{' (bundle)' if bun else ''}: ", end="", flush=True)
            v = (bundle(blocks, k, jobs) if bun
                 else class_integral(blocks, k, jobs=jobs, verbose=True))
            g = (v == tgt); ok &= g
            print(f"    = {v}  target {tgt}  "
                  f"{'MATCH' if g else '*** MISMATCH ***'}   {time.time()-t0:.0f}s")
        print("\n" + ("F-CYC LAYER VALIDATED" if ok else "*** FAIL ***"))
        raise SystemExit(0 if ok else 1)
    if "--time" in sys.argv:
        for nm, blocks, k in [("{2,2,4}", [[0, 1], [2, 3], [4, 5, 6, 7]], 8),
                              ("{5,2}", [[0, 1, 2, 3, 4], [5, 6]], 7),
                              ("{6,2}", [[0, 1, 2, 3, 4, 5], [6, 7]], 8),
                              ("{4,4}", [[0, 1, 2, 3], [4, 5, 6, 7]], 8)]:
            terms = class_terms(blocks, k)
            t0 = time.time()
            one_term((terms[0][1], terms[0][2], terms[0][3]))
            dt = time.time() - t0
            n = terms[0][3] + len(terms[0][1])
            print(f"  {nm:<9} terms {len(terms):<6} ambient R^{n}  "
                  f"first term {dt:6.2f}s  -> ~{len(terms)*dt/3600:8.2f} core-hours")
        raise SystemExit
