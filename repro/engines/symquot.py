#!/usr/bin/env python3
"""Dihedral quotient of the F-CYC term sum.

For a class whose blocks are setwise invariant under a subgroup G of D_k (in
particular the pure class {k}, invariant under all of D_k), the map
v_i -> v_{g(i)} is a coordinate permutation: it preserves Lebesgue measure on
{sum v = 0}, translates the cycle walk (spread invariant) and carries the F-CYC
term (P, cyclic order) to another term with the SAME sign and an equal integral.
So terms may be grouped into G-orbits and only one representative evaluated.

For {8} on the 8-cycle this is a ~16x exact reduction: 94586 terms -> ~6000.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_integral import fcyc_terms


def dihedral_maps(k):
    out = []
    for r in range(k):
        out.append(lambda x, r=r: (x + r) % k)
        out.append(lambda x, r=r: (r - x) % k)
    return out


def canon(parts, k, g):
    """apply g, then re-canonicalise the cyclic order so the part containing 0 is first"""
    P = [tuple(sorted(g(e) for e in p)) for p in parts]
    i0 = next(i for i, p in enumerate(P) if 0 in p)
    rot = P[i0:] + P[:i0]
    return tuple(rot)


def quotient(block, k, group=None):
    """[(total_sign_weight, parts)] -- one entry per orbit, weight = sign * orbit size"""
    maps = group if group is not None else dihedral_maps(k)
    terms = fcyc_terms(sorted(block))
    seen, out = {}, []
    for sign, parts in terms:
        key = min(canon(parts, k, g) for g in maps)
        if key in seen:
            out[seen[key]][0] += sign
        else:
            seen[key] = len(out)
            out.append([sign, parts])
    return [(w, p) for w, p in out if w != 0], len(terms)


if __name__ == "__main__":
    for k in (5, 6, 8):
        q, n = quotient(list(range(k)), k)
        print(f"  block of {k} on the {k}-cycle: {n} terms -> {len(q)} orbits "
              f"({n/max(1,len(q)):.1f}x)")
