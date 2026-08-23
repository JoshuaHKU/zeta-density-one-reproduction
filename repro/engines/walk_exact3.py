#!/usr/bin/env python3
"""
Exact rational integrator for 3-variable walk classes.

        I(pos) = int_{[-1,1]^3} (1 - spread(pos(v,w,u)))_+ * |v||w||u| dv dw du

Method and breakpoint enumeration are those of
preprint-0.8/certification/exact_t222.py (Proposition p:t222), refactored here
to accept an ARBITRARY position list so that every dihedral class can be run
through the same code path.  Nothing about the method is changed; the only
difference is that the class list is supplied by the caller.

Self-checks retained from the source: every piece is integrated twice (whole
piece, and the two halves) with a closed Newton-Cotes rule of order exceeding
the polynomial degree on the piece; for a genuine piece the two exact rationals
must coincide, and a missed kink forces a disagreement, which aborts.
"""
from fractions import Fraction as F

ONE, ZERO = F(1), F(0)

NC5 = [F(7, 90), F(32, 90), F(12, 90), F(32, 90), F(7, 90)]
NC7 = [F(41, 840), F(216, 840), F(27, 840), F(272, 840), F(27, 840),
       F(216, 840), F(41, 840)]
NC9 = [F(989, 28350), F(5888, 28350), F(-928, 28350), F(10496, 28350),
       F(-4540, 28350), F(10496, 28350), F(-928, 28350), F(5888, 28350),
       F(989, 28350)]


def nc_int(g, x0, x1, wts):
    n = len(wts) - 1
    h = x1 - x0
    return sum(wt * g(x0 + h * F(i, n)) for i, wt in enumerate(wts)) * h


def nc_int_checked(g, x0, x1, wts, tag):
    a = nc_int(g, x0, x1, wts)
    xm = (x0 + x1) / 2
    b = nc_int(g, x0, xm, wts) + nc_int(g, xm, x1, wts)
    if a != b:
        raise RuntimeError(f"scheme disagreement at {tag}: [{x0},{x1}]")
    return a


def make_f(pos):
    def f(v, w, u):
        vals = [cv * v + cw * w + cu * u for (cv, cw, cu) in pos]
        spread = max(vals) - min(vals)
        if spread >= 1:
            return ZERO
        return (1 - spread) * abs(v) * abs(w) * abs(u)
    return f


def pair_diffs(pos):
    ds = set()
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            d = tuple(a - b for a, b in zip(pos[i], pos[j]))
            if any(d):
                ds.add(d); ds.add(tuple(-x for x in d))
    return sorted(ds)


def cap_never_binds(pos):
    """every variable must be a difference of two positions, so that
    spread < 1 forces |var| < 1 and min(|.|,1) = |.| on the support."""
    ds = set(pair_diffs(pos))
    d = len(pos[0])
    for k in range(d):
        e = tuple(1 if i == k else 0 for i in range(d))
        if e not in ds and tuple(-x for x in e) not in ds:
            return False
    return True


def integral(pos, verbose=False):
    assert len(pos[0]) == 3, "this module is the 3-variable case"
    if not cap_never_binds(pos):
        raise RuntimeError("min(|.|,1) cap may bind: refusing to use |var|")
    f = make_f(pos)
    diffs = pair_diffs(pos)
    uforms = [(d, c) for d in diffs if d[2] != 0 for c in (-1, 0, 1)]

    def u_breaks(v, w):
        bs = {F(-1), F(0), F(1)}
        for (cv, cw, cu), c in uforms:
            bs.add(F(c - cv * v - cw * w, cu))
        return sorted(b for b in bs if -1 <= b <= 1)

    def I_u(v, w):
        bs = u_breaks(v, w); tot = ZERO
        for x0, x1 in zip(bs, bs[1:]):
            if x1 > x0:
                tot += nc_int_checked(lambda u: f(v, w, u), x0, x1, NC5, 'u')
        return tot

    wlin = set()
    for (cv, cw, cu), c in uforms:
        for e in (-1, 0, 1):
            if cw:
                wlin.add((cw, c - cu * e, -cv))
    ufl = list(uforms)
    for i in range(len(ufl)):
        for j in range(i + 1, len(ufl)):
            (d1, c1), (d2, c2) = ufl[i], ufl[j]
            aw = d1[1] * d2[2] - d2[1] * d1[2]
            if aw:
                wlin.add((aw, c1 * d2[2] - c2 * d1[2],
                          -(d1[0] * d2[2] - d2[0] * d1[2])))
    for d in diffs:
        if d[2] == 0 and d[1] != 0:
            for c in (-1, 0, 1):
                wlin.add((d[1], c, -d[0]))
    wlin = sorted(wlin)

    def w_breaks(v):
        bs = {F(-1), F(0), F(1)}
        for aw, b0, bv in wlin:
            bs.add(F(b0 + bv * v, aw))
        return sorted(b for b in bs if -1 <= b <= 1)

    def I_w(v):
        bs = w_breaks(v); tot = ZERO
        for x0, x1 in zip(bs, bs[1:]):
            if x1 > x0:
                tot += nc_int_checked(lambda w: I_u(v, w), x0, x1, NC7, 'w')
        return tot

    vset = {F(-1), F(0), F(1)}
    for i in range(len(wlin)):
        a1, b1, c1v = wlin[i]
        if c1v:
            for e in (-1, 0, 1):
                r = F(a1 * e - b1, c1v)
                if -1 < r < 1:
                    vset.add(r)
        for j in range(i + 1, len(wlin)):
            a2, b2, c2v = wlin[j]
            den = c1v * a2 - c2v * a1
            if den:
                r = F(b2 * a1 - b1 * a2, den)
                if -1 < r < 1:
                    vset.add(r)
    for d in diffs:
        if d[1] == 0 == d[2] and d[0] != 0:
            for c in (-1, 0, 1):
                r = F(c, d[0])
                if -1 < r < 1:
                    vset.add(r)
    vs = sorted(vset)
    tot = ZERO
    for x0, x1 in zip(vs, vs[1:]):
        if x1 > x0:
            tot += nc_int_checked(I_w, x0, x1, NC9, 'v')
    if verbose:
        print(f"    pieces: v {len(vs)-1}, w-forms {len(wlin)}, diffs {len(diffs)}")
    return tot


if __name__ == "__main__":
    # regression against the four archived classes of Proposition p:t222
    ARCHIVE = {
        'T0': ([(0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)], F(3, 70)),
        'T1': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0), (0, 0, 1)], F(1, 90)),
        'T2': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)], F(1, 180)),
        'T3': ([(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1), (0, 0, 1)], F(1, 70)),
    }
    ok = True
    for nm, (pos, tgt) in ARCHIVE.items():
        v = integral(pos)
        good = (v == tgt)
        ok &= good
        print(f"  {nm} = {v} = {float(v):.10f}   archived {tgt}   "
              f"{'MATCH' if good else '*** MISMATCH ***'}")
    print("\n" + ("regression PASS" if ok else "*** regression FAIL ***"))
