# -*- coding: utf-8 -*-
"""Gate F-TT: the Toeplitz--trace route (paper sec conv (vii)).

迹路线门。Five sections, all exact rational, ~30 s total:
  (a) engine validation ladder (characters, min(k,N), out-of-range
      hand value) on the MATH-SIDE reference engine;
  (b) small-(b,N) recomputation against the canonical tables --
      catches any silent edit of either the engine or the tables;
  (c) every tabulated value against the tabulated 1/N^2 polynomial
      (fit consistency, all b, exact);
  (d) constant terms against the proof-grade tower (m_4..m_8) and
      the re-centring anchors (m_9..m_11);
  (e) central-moment assembly: Sigma_3(N) == 0, Sigma_9/10/11
      extraction, and the full lambda_5 certificate chain
      (PD, Stieltjes, alternation, zero premium, headlines).
Grades are read from the table and reported, not asserted away:
b=11 entries are candidate-pending-acceptance and say so.
Exit 0 iff every check passes (gatelib conventions).
"""
import json
import os
import sys
from fractions import Fraction as Q
from math import comb

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "engines"))
from gatelib import check, finish                     # noqa: E402
from p3_direct_sum import m_b, trace_moment           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = json.load(open(os.path.join(HERE, os.pardir, "constants", "tt",
                                  "m_tables.json")))


def frac(s):
    return Q(s)


def poly_eval(coeffs, n):
    """Evaluate sum_p coeffs[p] / N^(2p) exactly."""
    return sum(frac(c) / Q(n ** (2 * p)) for p, c in enumerate(coeffs))


# ---- (a) engine validation ladder ---------------------------------
check("E|tr U^k|^2 = min(k,N)  (N=3,6; k=1..6)",
      all(trace_moment((k,), (k,), n) == min(k, n)
          for n in (3, 6) for k in range(1, 7)))
check("DS in-range: E[p21 conj p21] = 2, E[p21 conj p3] = 0  (N=6)",
      trace_moment((2, 1), (2, 1), 6) == 2
      and trace_moment((2, 1), (3,), 6) == 0)
check("out-of-range hand value: E|p22|^2 (N=3) = 7 (limit 8)",
      trace_moment((2, 2), (2, 2), 3) == 7)

# ---- (b) small-(b,N) recomputation --------------------------------
check("m_2(N) = 4/3 - 1/(3N^2)  recomputed  (N=2..6)",
      all(m_b(2, n) == Q(4, 3) - Q(1, 3 * n * n) for n in range(2, 7)))
check("m_3(N) = 2 - 1/N^2  recomputed  (N=2..6)",
      all(m_b(3, n) == 2 - Q(1, n * n) for n in range(2, 7)))
small = [(4, n) for n in (2, 3, 4)] + [(5, 2), (5, 3), (6, 2), (6, 3),
                                       (7, 2), (8, 2)]
check("table spot-recompute " + str(small),
      all(m_b(b, n) == frac(TAB["values"][str(b)][str(n)])
          for b, n in small))

# ---- (c) fit consistency: every tabulated value vs polynomial -----
ok = True
for b, vals in TAB["values"].items():
    coeffs = TAB["poly"][b]
    for n, v in vals.items():
        ok &= poly_eval(coeffs, int(n)) == frac(v)
check("all tabulated values equal their 1/N^2 polynomial (exact)", ok)

# ---- (d) constant terms vs tower and anchors ----------------------
tower = {"4": Q(13, 4), "5": Q(101, 18), "6": Q(640, 63),
         "7": Q(3439, 180), "8": Q(747361, 20160)}
check("constant terms re-derive the proof-grade tower m_4..m_8",
      all(frac(TAB["poly"][b][0]) == v for b, v in tower.items()))
S = {j: frac(TAB["sigma_exact"][str(j)]) for j in range(2, 12)}
S[12] = frac(TAB["sigma_exact"]["12"])
S[13] = frac(TAB["sigma_exact"]["13"])
anchors = {9: Q(495107, 6720) + S[9],
           10: Q(199427, 1344) + 10 * S[9] + S[10],
           11: Q(94560551, 302400) + S[11],
           12: Q(199083751, 302400) + 12 * S[11] + S[12],
           13: Q(11694191, 8400) + 78 * S[11] + 13 * S[12] + S[13]}
S[14] = frac(TAB["sigma_exact"]["14"])
anchors[14] = (Q(1264331, 432) + 364 * S[11] + 91 * S[12]
               + 14 * S[13] + S[14])
check("re-centring anchors m_9..m_14 (F-PRED-RAT interlock)",
      all(frac(TAB["poly"][str(b)][0]) == v for b, v in anchors.items()))

# ---- (e) central moments and the lambda_5 chain -------------------
mom = [Q(1), Q(1)] + [frac(TAB["poly"][str(b)][0]) if str(b) in TAB["poly"]
                      else None for b in range(2, 11)]
mom[2], mom[3] = Q(4, 3), Q(2)
check("Sigma_j from binomial assembly of tabulated constants (j=2..10)",
      all(sum(comb(j, i) * (-1) ** (j - i) * mom[i] for i in range(j + 1))
          == S[j] for j in range(2, 11)))
check("Sigma_3(N) == 0 at every N (poly identity)",
      all(poly_eval(TAB["poly"]["3"], n)
          - 3 * poly_eval(TAB["poly"]["2"], n) + 3 - 1 == 0
          for n in range(2, 9)))


def inv_col0(h):
    n = len(h)
    a = [r[:] + [Q(1) if i == 0 else Q(0)] for i, r in enumerate(h)]
    for c in range(n):
        p = next(r for r in range(c, n) if a[r][c] != 0)
        a[c], a[p] = a[p], a[c]
        pv = a[c][c]
        a[c] = [v / pv for v in a[c]]
        for r in range(n):
            if r != c and a[r][c] != 0:
                f = a[r][c]
                a[r] = [x - f * y for x, y in zip(a[r], a[c])]
    return [a[i][n] for i in range(n)]


def minors_positive(h):
    n = len(h)
    out = []
    for k in range(1, n + 1):
        m = [row[:k] for row in h[:k]]
        det = Q(1)
        for i in range(k):
            p = next(r for r in range(i, k) if m[r][i] != 0)
            if p != i:
                m[i], m[p] = m[p], m[i]
                det = -det
            for r in range(i + 1, k):
                f = m[r][i] / m[i][i]
                m[r] = [a2 - f * b2 for a2, b2 in zip(m[r], m[i])]
        for i in range(k):
            det *= m[i][i]
        out.append(det)
    return all(d > 0 for d in out)


h5 = [[mom[i + j] for j in range(6)] for i in range(6)]
col = inv_col0(h5)
lam5 = 1 / col[0]
q5 = [c / col[0] for c in col]
check("lambda_5 = 46970100247159/764967228211380",
      lam5 == frac(TAB["lambda5"]["value"]))
check("zero premium: int (Q5*)^2 dnu == lambda_5",
      sum(q5[i] * q5[j] * mom[i + j] for i in range(6)
          for j in range(6)) == lam5)
check("Q5* alternating (universal sign lemma instance)",
      all((q5[j] > 0) == (j % 2 == 0) for j in range(6)))
check("H5 PD and shifted (m1..m9) PD (Stieltjes)",
      minors_positive(h5) and minors_positive(
          [[mom[i + j + 1] for j in range(5)] for i in range(5)]))
check("k=10 headlines 0.877197/0.938598 (exact fractions)",
      1 - 2 * lam5 == frac(TAB["lambda5"]["headline_simple"])
      and 1 - lam5 == frac(TAB["lambda5"]["headline_distinct"]))
print(f"  note: lambda5 grade = {TAB['lambda5']['grade']}")
print(f"  note: b=11 grade   = {TAB['grade']['11']}")

finish("F-TT (Toeplitz-trace route)")
