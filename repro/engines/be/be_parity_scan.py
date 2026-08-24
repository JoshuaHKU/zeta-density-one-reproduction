#!/usr/bin/env python3
"""O-BE-2 / O-BE-3 (r159): true-cumulant per-term parity scan.

    T_b(N) = sum_{m in [0,N)^b} E[ prod_i tr U^{m_i - m_{i+1}} ]

Expand the expectation over set partitions of the b factors,

    E[prod_{i in [b]} X_i] = sum_{P} prod_{B in P} cum(X_i : i in B),

with the TRUE cumulant obtained by Moebius inversion on the partition lattice,

    cum(X_i : i in B) = sum_{Q |- B} mu(Q) prod_{C in Q} E[prod_{i in C} X_i],
    mu(Q) = (-1)^{|Q|-1} (|Q|-1)! .

The moments E[prod tr U^k] come from the Schur-orthogonality routine already in
tt_moments.py (schur_pair), so this reuses a validated engine rather than a new
one.  Note the r159 sandbox warning: UNSIGNED proxy terms have a different parity
from the true signed assembly, so parity must be adjudicated here, on the true
cumulant terms -- that is the whole point of this scan.

Gates:
  F-BE-ASSEMBLY-b  sum_P T_P(N) == m_b(N) * N^(b+1) digit for digit
  F-BE-PAR-b       Proposition A (strong): every T_P obeys T_P(-N)=(-1)^(b+1) T_P(N)
                   Proposition B (weak):  only the total does
"""
import os, sys, json, time, itertools
from fractions import Fraction as Q
from functools import lru_cache
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tt_moments import schur_pair


def set_partitions(items):
    items = list(items)
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for part in set_partitions(rest):
        for i in range(len(part)):
            yield part[:i] + [[first] + part[i]] + part[i+1:]
        yield [[first]] + part


@lru_cache(maxsize=None)
def moment(ks, N):
    """E[prod_j tr U^{k_j}] for a tuple of signed integers"""
    mu = tuple(sorted((k for k in ks if k > 0), reverse=True))
    nu = tuple(sorted((-k for k in ks if k < 0), reverse=True))
    return schur_pair(mu, nu, N)          # zeros contribute tr U^0 = N


@lru_cache(maxsize=None)
def _fact(n):
    return 1 if n <= 1 else n * _fact(n - 1)


@lru_cache(maxsize=None)
def cumulant(ks, N):
    """true joint cumulant of (tr U^{k}) for k in ks, by Moebius inversion"""
    idx = list(range(len(ks)))
    tot = 0
    for Qp in set_partitions(idx):
        mob = (-1) ** (len(Qp) - 1) * _fact(len(Qp) - 1)
        pr = 1
        for C in Qp:
            kk = tuple(sorted(ks[i] for i in C))
            zeros = sum(1 for i in C if ks[i] == 0)
            pr *= moment(tuple(k for k in kk if k != 0), N) * N ** zeros
        tot += mob * pr
    return tot


def term_values(b, Ns):
    """{partition_key: [T_P(N) for N in Ns]}"""
    parts = [tuple(tuple(sorted(B)) for B in sorted(P, key=min))
             for P in set_partitions(range(b))]
    out = {}
    for P in parts:
        vals = []
        for N in Ns:
            s = 0
            for m in itertools.product(range(N), repeat=b):
                k = tuple(m[i] - m[(i + 1) % b] for i in range(b))
                pr = 1
                for B in P:
                    pr *= cumulant(tuple(k[i] for i in B), N)
                    if pr == 0:
                        break
                s += pr
            vals.append(s)
        out["|".join("".join(map(str, B)) for B in P)] = vals
    return out


def lagrange_at(xs, ys, x):
    """exact Lagrange interpolation of the polynomial through (xs, ys), at x"""
    t = Q(0)
    for i, xi in enumerate(xs):
        term = Q(ys[i])
        for j, xj in enumerate(xs):
            if i != j:
                term *= Q(x - xj, xi - xj)
        t += term
    return t


if __name__ == "__main__":
    b = int(sys.argv[1])
    Ns = list(range(2, b + 6))
    t0 = time.time()
    T = term_values(b, Ns)
    tot = [sum(T[k][i] for k in T) for i in range(len(Ns))]
    print(f"b={b}: {len(T)} partitions, N={Ns[0]}..{Ns[-1]}, {time.time()-t0:.0f}s",
          flush=True)
    sign = (-1) ** (b + 1)
    strong, weak, nonpoly = [], [], []
    for k, ys in T.items():
        # fit through all points, then test T(-N) vs sign*T(N) at a fresh N
        for N in Ns[:3]:
            lhs = lagrange_at(Ns, ys, -N)
            rhs = sign * lagrange_at(Ns, ys, N)
            if lhs != rhs:
                weak.append((k, N, str(lhs), str(rhs)))
                break
        else:
            strong.append(k)
    tl = lagrange_at(Ns, tot, -Ns[0]); tr = sign * lagrange_at(Ns, tot, Ns[0])
    res = {"b": b, "Ns": Ns, "n_partitions": len(T),
           "parity_sign_expected": sign,
           "terms_satisfying_per_term_parity": len(strong),
           "terms_violating": len(weak),
           "violating_examples": weak[:5],
           "total_satisfies_parity": tl == tr,
           "PROPOSITION": ("A" if not weak else "B"),
           "T_P": {k: [str(v) for v in ys] for k, ys in T.items()},
           "total": [str(v) for v in tot], "wall_s": round(time.time()-t0, 1)}
    json.dump(res, open(f"../constants/be/parity_scan_b{b}.json", "w"), indent=1)
    print(f"  per-term parity: {len(strong)}/{len(T)} satisfy, {len(weak)} violate")
    print(f"  total satisfies parity: {tl == tr}")
    print(f"  *** F-BE-PAR-{b}: PROPOSITION {res['PROPOSITION']} ***", flush=True)
