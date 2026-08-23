#!/usr/bin/env python3
"""O-BE-5, corrected to the r163 coefficient spec.

    m_b(N)*N^(b+1) = sum_{m in [0,N)^b} sum_{P |- [b]} prod_{B in P} kappa_B ,
    k_i = m_i - m_{i+1 mod b}

    kappa_B = delta[sum_{i in B} k_i = 0] *
              sum_{Q |- B} (-1)^(|Q|-1)
              sum_{sigma = cyclic orders of Q's CLASSES} (N - span_sigma(g))_+

with g_C = sum_{i in C} k_i the merged frequency of class C.  Coefficient is the
pure sign (-1)^(|Q|-1); there is no factorial factor.

My first attempt indexed terms by slot permutations (73 of them at b=4) -- that
is the O-BE-4 WALL-system family, not the assembly family.  The correct count is
the Fubini number (75 at b=4): the two sequences agree at b=3 and diverge from
b=4, which is exactly where the trap sat.  The assembly gate caught it at b=4 in
0.1 s, before any GPU time was spent.
"""
import sys, json, time, itertools
sys.path.insert(0, ".")
from be_tu_scan import set_partitions


def cyclic_orders(n):
    """(n-1)! orders of n classes: fix class 0 first, permute the rest"""
    if n == 0:
        return [()]
    return [(0,) + p for p in itertools.permutations(range(1, n))]


def kappa(B, kvals, N):
    """kappa_B for one block, given the k values as a dict i -> k_i"""
    if sum(kvals[i] for i in B) != 0:
        return 0
    tot = 0
    for Q in set_partitions(list(B)):
        sign = (-1) ** (len(Q) - 1)
        g = [sum(kvals[i] for i in C) for C in Q]
        sub = 0
        for order in cyclic_orders(len(Q)):
            acc = mx = mn = 0
            for c in order:
                acc += g[c]
                mx = max(mx, acc); mn = min(mn, acc)
            sub += max(N - (mx - mn), 0)
        tot += sign * sub
    return tot


def assemble(b, N):
    """sum over m and over P of prod kappa_B -- the full assembly"""
    tot = 0
    parts = [[list(B) for B in P] for P in set_partitions(range(b))]
    for m in itertools.product(range(N), repeat=b):
        k = {i: m[i] - m[(i + 1) % b] for i in range(b)}
        for P in parts:
            pr = 1
            for B in P:
                pr *= kappa(B, k, N)
                if pr == 0:
                    break
            tot += pr
    return tot


if __name__ == "__main__":
    from math import comb, factorial
    print("SELF-CHECK 1 (spec sec 3): |B|=1 -> kappa = N*delta_{k=0}")
    ok = all(kappa([0], {0: kk}, 7) == (7 if kk == 0 else 0) for kk in (-2, 0, 3))
    print(f"   {'OK' if ok else '*** FAIL ***'}")
    print("SELF-CHECK 2: |B|=2, k!=0 -> kappa = min(|k|,N);  k=0 -> 0")
    bad = []
    for N in (5, 9):
        for kk in range(-6, 7):
            got = kappa([0, 1], {0: kk, 1: -kk}, N)
            want = 0 if kk == 0 else min(abs(kk), N)
            if got != want:
                bad.append((N, kk, got, want))
    print(f"   {'OK' if not bad else '*** FAIL *** ' + str(bad[:3])}")
    print("SELF-CHECK 3: q(s) = sum_m S(s,m)(m-1)! = 1,2,6,26,150")
    def q(s):
        return sum(len(cyclic_orders(len(Q))) for Q in set_partitions(list(range(s))))
    got = [q(s) for s in range(1, 6)]
    print(f"   {got}  {'OK' if got == [1, 2, 6, 26, 150] else '*** FAIL ***'}")
    print("SELF-CHECK 4: sum_P prod q(|B|) = Fubini(b) = 13,75,541,4683,47293")
    fub = []
    for b in range(3, 8):
        fub.append(sum(__import__("math").prod(q(len(B))) for B in [[list(x) for x in P]
                   for P in set_partitions(range(b))] for B in [B]) if False else
                   sum(__import__("math").prod([q(len(x)) for x in P])
                       for P in set_partitions(range(b))))
    print(f"   {fub}  {'OK' if fub == [13, 75, 541, 4683, 47293] else '*** FAIL ***'}")
