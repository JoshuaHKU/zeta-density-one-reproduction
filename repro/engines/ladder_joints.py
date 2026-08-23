# -*- coding: utf-8 -*-
"""Second-path midpoint ladders for the joint constants
{2,2,4}, {4,4}, {6,2} (and optionally {5,2}) — gate F-V-JOINTS.
联合常数的第二路径中点阶梯（双路径标准）。

Integrand per orbit representative (programme convention, as in
spectator_42_reference.py):  ov_8(joint walk) * prod C_b^{Urs}
(block frequencies) * prod |v_pair|.  All slot frequencies are
bounded by 1 on the ov-support, so the [-1,1]^d midpoint grid is
exact.  Checkpointed per (class, dv, orbit).

Usage:  python3 ladder_joints.py {224|44|62|52} DV
        python3 ladder_joints.py report
Expected wall (single core): 224/44 at dv=0.1: minutes;
62 at dv=0.125/0.1: hours (1082-term C6; use a fat node).
"""
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CK = os.path.join(HERE, "ladder_ck")
os.makedirs(CK, exist_ok=True)


# ---------- enumeration (self-contained, mirrors m78_ledger) ------
def set_partitions(items):
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i + 1:]
        yield [[first]] + part


def canon(blocks, n):
    seq = [None] * n
    for bi, blk in enumerate(blocks):
        for p in blk:
            seq[p] = bi
    best = None
    for refl in (False, True):
        s = seq[::-1] if refl else seq
        for r in range(n):
            rot = s[r:] + s[:r]
            lab, out = {}, []
            for x in rot:
                if x not in lab:
                    lab[x] = len(lab)
                out.append((lab[x], len(blocks[x])))
            t = tuple(out)
            if best is None or t < best:
                best = t
    return best


def orbits(b, sizes_wanted):
    seen = {}
    for P in set_partitions(list(range(b))):
        sizes = tuple(sorted(len(x) for x in P))
        if sizes != sizes_wanted:
            continue
        blocks = sorted(tuple(sorted(x)) for x in P)
        c = canon([tuple(x) for x in blocks], b)
        if c not in seen:
            seen[c] = blocks
    return sorted(seen.values())


CLASSES = {"224": (8, (2, 2, 4)), "44": (8, (4, 4)),
           "62": (8, (2, 6)), "52": (7, (2, 5))}


# ---------- Ursell evaluators -------------------------------------
def compile_terms(b):
    out = []
    for P in set_partitions(list(range(b))):
        m = len(P)
        sign = (-1.0) ** (m - 1)
        first = next(i for i, blk in enumerate(P) if 0 in blk)
        others = [i for i in range(m) if i != first]
        for perm in itertools.permutations(others):
            order = [first] + list(perm)
            masks, cur = [], frozenset()
            for bi in order[:-1]:
                cur = cur | frozenset(P[bi])
                masks.append(tuple(sorted(cur)))
            out.append((sign, masks))
    return out


TERMS = {b: compile_terms(b) for b in (4, 5, 6)}


def C_of(w, b):
    """b-point Ursell at frequency arrays w (sum w = 0)."""
    sub = np.zeros_like(w[0])
    for sign, masks in TERMS[b]:
        if not masks:
            sub = sub + sign
            continue
        mx = np.zeros_like(w[0])
        mn = np.zeros_like(w[0])
        for mk in masks:
            pos = sum(w[j] for j in mk)
            mx = np.maximum(mx, pos)
            mn = np.minimum(mn, pos)
        sub = sub + sign * np.clip(1.0 - (mx - mn), 0.0, None)
    return sub


# ---------- orbit integrand ---------------------------------------
def orbit_value(blocks, bcyc, dv):
    """Midpoint integral for one orbit representative."""
    pairs = [blk for blk in blocks if len(blk) == 2]
    bigs = [blk for blk in blocks if len(blk) > 2]
    nfree = sum(len(blk) - 1 for blk in blocks)  # free dims
    g = np.arange(-1 + dv / 2, 1, dv)
    # variable layout: pair vars first, then per big block its
    # (size-1) free frequencies; outermost variable sliced.
    def freqs(xs):
        f = [None] * bcyc
        k = 0
        for blk in pairs:
            f[blk[0]] = xs[k]
            f[blk[1]] = -xs[k]
            k += 1
        blockfreqs = []
        for blk in bigs:
            fr = xs[k:k + len(blk) - 1]
            last = -sum(fr)
            vals = list(fr) + [last]
            for s, v in zip(blk, vals):
                f[s] = v
            blockfreqs.append(vals)
            k += len(blk) - 1
        return f, blockfreqs
    rest = np.meshgrid(*([g] * (nfree - 1)), indexing="ij")
    tot = 0.0
    for x0 in g:
        xs = [np.full_like(rest[0], x0)] + list(rest) \
            if rest else [np.array([x0])]
        f, bf = freqs(xs)
        p = np.zeros_like(xs[0])
        mx = np.zeros_like(xs[0])
        mn = np.zeros_like(xs[0])
        for s in range(bcyc - 1):
            p = p + f[s]
            mx = np.maximum(mx, p)
            mn = np.minimum(mn, p)
        w = np.clip(1.0 - (mx - mn), 0.0, None)
        for blk, vals in zip(bigs, bf):
            w = w * C_of(vals, len(blk))
        for i in range(len(pairs)):
            w = w * np.abs(xs[i])
        tot += float(w.sum())
    return tot * dv ** nfree


def run(cls, dv):
    bcyc, sizes = CLASSES[cls]
    reps = orbits(bcyc, tuple(sorted(sizes)))
    fn = os.path.join(CK, f"lj_{cls}_dv{dv}.json")
    done = json.load(open(fn)) if os.path.exists(fn) else {}
    for i, blocks in enumerate(reps):
        if str(i) in done:
            continue
        t0 = time.time()
        v = orbit_value(blocks, bcyc, dv)
        done[str(i)] = dict(blocks=[list(b) for b in blocks],
                            value=v, wall=round(time.time() - t0, 1))
        json.dump(done, open(fn, "w"))
        print(f"[{cls}] dv={dv} orbit {i}/{len(reps)}: {v:.8f} "
              f"({done[str(i)]['wall']}s)", flush=True)
    print(f"[{cls}] dv={dv}: {len(reps)} orbits complete")


def report():
    print("Richardson (h2) per class file; compare per-orbit "
          "against the exact tables (gate F-V-JOINTS, |dev|<3e-6):")
    for fn in sorted(os.listdir(CK)):
        print(" ", fn, "->", os.path.join(CK, fn))
    print("(assemble finest-pair (4*v_fine - v_coarse)/3 per orbit;"
          " see COMPUTE_ORDERS.md)")


if __name__ == "__main__":
    if sys.argv[1] == "report":
        report()
    else:
        run(sys.argv[1], float(sys.argv[2]))
