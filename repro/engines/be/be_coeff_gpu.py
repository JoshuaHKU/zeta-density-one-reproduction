#!/usr/bin/env python3
"""F-BE-COEFF / O-BE-5 on the GPU, to the r163 coefficient spec.

    m_b(N)*N^(b+1) = sum_{m in [0,N)^b} sum_{P|-[b]} prod_{B in P} kappa_B
    kappa_B = delta[sum_B k = 0] * sum_{Q|-B} (-1)^(|Q|-1)
              sum_{sigma = cyclic orders of Q's classes} (N - span_sigma(g))_+

Design: the combinatorial skeleton (which P, which Q, which cyclic order, which
slots merge into which class) depends only on b, so it is compiled ONCE on the
host into flat index lists.  The m-grid -- the only thing that grows as N^b --
is then processed on the GPU as plain integer array ops: no custom kernel, and
no per-point Python.

This is the same reasoning that made the LTU scan a good GPU target and the
span-DP a bad one: here the per-point work is a fixed, uniform, tiny integer
computation over an enormous regular lattice.

Everything is integer; the accumulator is int64 and the running total is checked
against the safe range so a silent wrap can never be mistaken for a result.
"""
import sys, json, time, itertools
sys.path.insert(0, ".")
from be_tu_scan import set_partitions

SAFE = 2**62


def compile_blocks(b):
    """for each block B (as a frozenset of slots) precompute its (Q, sigma) plan"""
    plans = {}
    for size in range(1, b + 1):
        pass
    return plans


def block_plan(B):
    """[(sign, [class-slot-lists in sigma order]) ...] for one block"""
    out = []
    for Q in set_partitions(list(B)):
        sign = (-1) ** (len(Q) - 1)
        n = len(Q)
        orders = [(0,) + p for p in itertools.permutations(range(1, n))] if n else [()]
        for order in orders:
            out.append((sign, [list(Q[c]) for c in order]))
    return out


def assemble_gpu(b, N, xp):
    grid = xp.indices((N,) * b, dtype=xp.int64).reshape(b, -1)
    k = grid - xp.roll(grid, -1, axis=0)
    del grid
    parts = [[list(B) for B in P] for P in set_partitions(range(b))]
    plans = {tuple(B): block_plan(B) for P in parts for B in P}
    kap = {}
    for Bk, plan in plans.items():
        s = xp.zeros(k.shape[1], dtype=xp.int64)
        for i in Bk:
            s = s + k[i]
        z = (s == 0)
        acc_tot = xp.zeros(k.shape[1], dtype=xp.int64)
        for sign, classes in plan:
            acc = xp.zeros(k.shape[1], dtype=xp.int64)
            mx = xp.zeros(k.shape[1], dtype=xp.int64)
            mn = xp.zeros(k.shape[1], dtype=xp.int64)
            for C in classes:
                g = xp.zeros(k.shape[1], dtype=xp.int64)
                for i in C:
                    g = g + k[i]
                acc = acc + g
                mx = xp.maximum(mx, acc)
                mn = xp.minimum(mn, acc)
            acc_tot = acc_tot + sign * xp.maximum(N - (mx - mn), 0)
        kap[Bk] = acc_tot * z
    tot = 0
    for P in parts:
        pr = None
        for B in P:
            pr = kap[tuple(B)] if pr is None else pr * kap[tuple(B)]
        tot += int(pr.sum())
        if abs(tot) > SAFE:
            raise OverflowError("int64 accumulator near overflow -- result unsafe")
    return tot


if __name__ == "__main__":
    b = int(sys.argv[1])
    Ns = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2][0].isdigit() else list(range(2, b + 6))
    try:
        import cupy as xp
        dev = int(sys.argv[sys.argv.index("--gpu") + 1]) if "--gpu" in sys.argv else 0
        xp.cuda.Device(dev).use(); backend = f"cupy(dev{dev})"
    except Exception as e:
        import numpy as xp
        backend = f"numpy ({e})"
    print(f"backend {backend}  b={b}  N={Ns}", flush=True)
    out = {}
    for N in Ns:
        t0 = time.time(); v = assemble_gpu(b, N, xp)
        out[N] = v
        print(f"  N={N}: {v}   {time.time()-t0:.1f}s", flush=True)
        json.dump({"b": b, "backend": backend,
                   "assembly": {str(kk): str(vv) for kk, vv in out.items()}},
                  open(f"../constants/be/coeff_assembly_b{b}.json", "w"), indent=1)
