#!/usr/bin/env python3
"""
PHASE 1/2 (enumeration) -- dihedral classification of every block-partition
class of the seventh and eighth moments.

A class {b_1,...,b_r} of m_k is a set partition of the k cyclic slots into
blocks of the prescribed sizes; each block carries a connected (Ursell) factor.
The symmetry group of the cyclic trace is the dihedral group D_k (rotation of
the cycle and reversal), of order 2k, so the ledger must be organised by
D_k-orbits -- this is exactly the lesson of the r129 conversion, where
selecting representatives by crossing number merged two inequivalent orbits.

This file enumerates, for each class, the full set of partitions, its D_k-orbit
decomposition and the orbit sizes, and compares against the counts recorded in
proof_track_r129.md sec 4:

    {5,2}    on the 7-cycle:  3 placement classes x 7   (total 21)
    {2^4}    on the 8-cycle:  17 dihedral classes       (total 105)
    {2,2,4}  on the 8-cycle:  22 classes                (total 210)
    {4,4}    on the 8-cycle:  7 classes                 (total 35)
    {6,2}    on the 8-cycle:  4 classes, sizes 8/8/8/4  (total 28)

Pure combinatorics; no integration, no model input.

Usage:  python3 block_classes.py
"""
import json, os
from itertools import combinations
from collections import Counter


def set_partitions_by_sizes(n, sizes):
    """all set partitions of {0..n-1} into blocks of the given multiset of sizes"""
    sizes = sorted(sizes, reverse=True)
    assert sum(sizes) == n

    def rec(rem, sizes):
        if not sizes:
            yield ()
            return
        s, rest = sizes[0], sizes[1:]
        rem = sorted(rem)
        # Blocks of EQUAL size are interchangeable, so for those we force the
        # smallest remaining element into the current block (canonical order by
        # minimum).  For a block whose size is unique among the remaining sizes
        # no such quotient is available and every s-subset must be taken --
        # forcing there was the bug that lost {5,2}, {2,2,4} and {6,2}.
        # r148 FIX.  The old condition was `rest[0] == s` -- "the NEXT size
        # equals s".  That is not enough: with sizes [4,4,2] it forced element 0
        # into a 4-block, but 0 may perfectly well live in the 2-block, and every
        # such partition was silently lost (1260 of 1575 for {4,4,2}, a 20% hole).
        # Forcing the smallest remaining element into the current block is valid
        # only when it MUST be in a block of size s, i.e. when ALL remaining
        # blocks have size s.
        force = bool(rest) and all(x == s for x in rest)
        cands = ([(rem[0],) + c for c in combinations(rem[1:], s - 1)] if force
                 else list(combinations(rem, s)))
        for blk in cands:
            newrem = [x for x in rem if x not in blk]
            for tail in rec(newrem, rest):
                yield (tuple(sorted(blk)),) + tail

    seen = set()
    for p in rec(list(range(n)), sizes):
        key = tuple(sorted(p))
        if key not in seen:
            seen.add(key)
            yield key


def act(p, f, n):
    return tuple(sorted(tuple(sorted(f(x) % n for x in blk)) for blk in p))


def orbit(p, n):
    o = set()
    for r in range(n):
        o.add(act(p, lambda x, r=r: x + r, n))
        o.add(act(p, lambda x, r=r: r - x, n))
    return frozenset(o)


def classify(n, sizes, label, expected_total=None, expected_orbits=None,
             expected_sizes=None):
    ps = list(set_partitions_by_sizes(n, sizes))
    orbs = {}
    for p in ps:
        orbs.setdefault(orbit(p, n), []).append(p)
    items = sorted(orbs.items(), key=lambda kv: (-len(kv[1]), kv[1][0]))
    osz = sorted((len(m) for _, m in items), reverse=True)
    print(f"\n{label}  on the {n}-cycle   (D_{n}, order {2*n})")
    print(f"   partitions        : {len(ps)}"
          + (f"   r129 says {expected_total}  "
             f"{'PASS' if expected_total == len(ps) else '*** FAIL ***'}"
             if expected_total else ""))
    print(f"   dihedral orbits   : {len(items)}"
          + (f"   r129 says {expected_orbits}  "
             f"{'PASS' if expected_orbits == len(items) else '*** FAIL ***'}"
             if expected_orbits else ""))
    print(f"   orbit sizes       : {Counter(osz)}")
    if expected_sizes:
        good = sorted(osz, reverse=True) == sorted(expected_sizes, reverse=True)
        print(f"   r129 orbit sizes  : {sorted(expected_sizes, reverse=True)}   "
              f"{'PASS' if good else '*** FAIL ***'}")
    ok = True
    if expected_total: ok &= (expected_total == len(ps))
    if expected_orbits: ok &= (expected_orbits == len(items))
    if expected_sizes:
        ok &= (sorted(osz, reverse=True) == sorted(expected_sizes, reverse=True))
    return dict(label=label, n=n, sizes=list(sizes), total=len(ps),
                orbits=[dict(size=len(m), rep=[list(b) for b in m[0]],
                             members=[[list(b) for b in x] for x in m])
                        for _, m in items]), ok


def main():
    out, allok = [], True
    for args in [
        (7, [5, 2], "{5,2}", 21, 3, [7, 7, 7]),
        (8, [2, 2, 2, 2], "{2^4}", 105, 17, None),
        (8, [4, 2, 2], "{2,2,4}", 210, 22, None),
        (8, [4, 4], "{4,4}", 35, 7, None),
        (8, [6, 2], "{6,2}", 28, 4, [8, 8, 8, 4]),
        (6, [2, 2, 2], "{2,2,2} (phase-0 control)", 15, 5, [6, 3, 3, 2, 1]),
    ]:
        d, ok = classify(*args)
        out.append(d); allok &= ok
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(out, open(os.path.join(here, "block_classes.json"), "w"), indent=1)
    print(f"\nwritten: {os.path.join(here,'block_classes.json')}")
    print("\n" + ("ALL ENUMERATION GATES PASS" if allok
                  else "*** SOME ENUMERATION GATES FAILED ***"))
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
