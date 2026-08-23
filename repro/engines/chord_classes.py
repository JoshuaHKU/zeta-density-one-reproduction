#!/usr/bin/env python3
"""
PHASE 0.2 -- complete dihedral audit of the {2,2,2} bundle.

Setting (recovered from certification/exact_t222.py of preprint-0.8).  The
{2,2,2} class of m_6 is a pairing of the SIX EDGES of the hexagon, not of its
vertices: writing s_0..s_5 for the cyclic steps (s_i = x_{i+1} - x_i, sum 0), a
pairing {i,j} sets s_i = +var, s_j = -var, and the walk positions are the
partial sums x_0 = 0, x_{k+1} = x_k + s_k.  The class value is

        val(matching) = int_{[-1,1]^3} (1 - spread(x))_+ |v||w||u| dv dw du ,

the min(|.|,1) caps never binding because every variable is a difference of two
positions, so |var| <= spread < 1 on the support.

r129 found that the archived assembly selected class representatives by
CROSSING NUMBER, which is not a complete invariant of chord diagrams on a
circle: two inequivalent dihedral classes both have crossing number 0.  This
file re-derives the classification from scratch:

  * enumerate all 15 perfect matchings of the 6 slots;
  * compute the orbit decomposition under the dihedral group D_6 (order 12)
    -- rotations x -> x+r and reflections x -> -x on the slot circle, which are
    exactly the symmetries of the cyclic trace (rotation of the cycle and
    reversal);
  * record crossing number per orbit, exhibiting the collision;
  * emit the position list (walk) of every matching, for exact integration.

No value is computed here -- see t222_exact.py.  This file is pure
combinatorics and is fully deterministic.
"""
from itertools import permutations
import json, os

SLOTS = 6


def matchings(items):
    """all perfect matchings of a list, as sorted tuples of sorted pairs"""
    if not items:
        yield ()
        return
    a, rest = items[0], items[1:]
    for i, b in enumerate(rest):
        for m in matchings(rest[:i] + rest[i + 1:]):
            yield tuple(sorted(((a, b),) + m))


def crossings(m, n=SLOTS):
    """number of crossing pairs of chords on the circle 0..n-1"""
    c = 0
    for i in range(len(m)):
        for j in range(i + 1, len(m)):
            a, b = m[i]; p, q = m[j]
            inside_p = a < p < b
            inside_q = a < q < b
            if inside_p != inside_q:
                c += 1
    return c


def rot(m, r, n=SLOTS):
    return tuple(sorted(tuple(sorted(((a + r) % n, (b + r) % n))) for a, b in m))


def ref(m, n=SLOTS):
    return tuple(sorted(tuple(sorted(((-a) % n, (-b) % n))) for a, b in m))


def dihedral_orbit(m, n=SLOTS):
    o = set()
    for r in range(n):
        x = rot(m, r, n)
        o.add(x); o.add(ref(x, n))
    return frozenset(o)


def walk(m, n=SLOTS):
    """position list: x_0 = 0, x_{k+1} = x_k + s_k, with s_i = +var / -var.
    Variables are numbered in order of first appearance."""
    var = {}
    for i, j in sorted(m, key=lambda p: p[0]):
        var.setdefault(i, len(var))
    idx = {}
    for a, b in m:
        k = var[min(a, b)]
        idx[min(a, b)] = (k, +1)
        idx[max(a, b)] = (k, -1)
    d = len(var)
    pos, cur = [], [0] * d
    for k in range(n):
        pos.append(tuple(cur))
        v, sgn = idx[k]
        cur = list(cur); cur[v] += sgn
    return pos


def main():
    ms = sorted(matchings(list(range(SLOTS))))
    assert len(ms) == 15, len(ms)
    orbits = {}
    for m in ms:
        orbits.setdefault(dihedral_orbit(m), []).append(m)
    # order orbits by (crossing number, size) for a stable report
    items = sorted(orbits.items(), key=lambda kv: (crossings(kv[1][0]), len(kv[1])))
    print(f"perfect matchings of {SLOTS} cyclic slots: {len(ms)}")
    print(f"dihedral (D_{SLOTS}, order {2*SLOTS}) orbits: {len(items)}\n")
    print(f"{'orbit':<6}{'size':<6}{'cr':<4}  representative        walk")
    out = []
    for k, (orb, mem) in enumerate(items):
        rep = mem[0]; cr = crossings(rep)
        assert all(crossings(x) == cr for x in mem), "crossing number not constant on an orbit"
        w = walk(rep)
        name = f"D{k}"
        print(f"{name:<6}{len(mem):<6}{cr:<4}  {str(rep):<22}{w}")
        out.append(dict(name=name, size=len(mem), crossings=cr,
                        representative=[list(p) for p in rep],
                        members=[[list(p) for p in x] for x in mem],
                        walk=[list(p) for p in w]))
    tot = sum(o["size"] for o in out)
    assert tot == 15, tot
    print(f"\nsizes: {' + '.join(str(o['size']) for o in out)} = {tot}")
    bycr = {}
    for o in out:
        bycr.setdefault(o["crossings"], []).append(o["name"])
    print("crossing number -> orbits:")
    for cr in sorted(bycr):
        tag = "   <-- COLLISION: crossing number does not separate these" \
              if len(bycr[cr]) > 1 else ""
        print(f"   cr = {cr}: {', '.join(bycr[cr])}{tag}")
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "t222_classes.json"), "w"), indent=1)
    print(f"\nwritten: {os.path.join(here,'t222_classes.json')}")
    return out


if __name__ == "__main__":
    main()
