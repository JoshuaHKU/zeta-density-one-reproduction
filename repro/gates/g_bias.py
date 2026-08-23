#!/usr/bin/env python3
"""F-BIAS (r148 E): the A1 pools must match the EXACT finite-N central moments.

The P3 Toeplitz-trace route (r147) closes Sigma_j(N) in exact rational form -- a
polynomial in 1/N^2.  The A1 known-moment pre-gate originally compared the
measurement to the N -> infinity LIMIT, which at 10^7 samples fails by 3+ sd for
a reason that is not a bug: the finite-N term is real and now provably so.  The
gate therefore compares against Sigma_j(N), criterion 3 sd, at every N."""
import os, re, sys
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, require_count, finish

# Sigma_j(N) as [c0, c2, c4, c6, c8] with Sigma_j(N) = sum_i c_{2i} / N^(2i)
EXACT = {
 2: [Q(1,3), Q(-1,3)],
 4: [Q(1,4), Q(-7,12), Q(1,3)],
 5: [Q(1,36), Q(-5,36), Q(1,9)],
 6: [Q(61,252), Q(-35,36), Q(13,9), Q(-5,7)],
 7: [Q(7,90), Q(-91,180), Q(161,180), Q(-7,15)],
 8: [Q(633,2240), Q(-3371,2016), Q(12247,2880), Q(-5545,1008), Q(277,105)],
}
def sigma(j, N):
    return sum(c / Q(N) ** (2 * i) for i, c in enumerate(EXACT[j]))

LOGS = {128: "a1_o5_1e7.log", 192: "a1_o5_N192.log", 256: "a1_o5_N256.log"}
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "measurements", "o5")
n = 0
for N, f in LOGS.items():
    p = os.path.join(D, f)
    if not os.path.exists(p):
        print(f"  NOT-APPLICABLE  F-BIAS N={N}: {f} absent"); check(f"F-BIAS N={N}", False); continue
    meas = {}
    for l in open(p):
        m = re.match(r"\s+(\d+)\s+([-\d.]+)\s+([\d.e+-]+)", l)
        if m: meas[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    worst, wj = 0.0, None
    for j in EXACT:
        mu, se = meas[j]
        z = (mu - float(sigma(j, N))) / se
        if abs(z) > abs(worst): worst, wj = z, j
        n += check(f"F-BIAS N={N:<4} j={j}", abs(z) <= 3,
                   f"{mu:.9f} vs exact {float(sigma(j,N)):.9f}  {z:+.2f} sd")
    print(f"    -> N={N}: worst {worst:+.2f} sd at j={wj}")
require_count("F-BIAS checks", n, 3 * len(EXACT))
# and the limit that the old gate used, for contrast
print("\n  for contrast, deviation from the N->infinity LIMIT at N=128:")
for j in (2, 8):
    mu, se = 0, 0
    for l in open(os.path.join(D, LOGS[128])):
        m = re.match(rf"\s+({j})\s+([-\d.]+)\s+([\d.e+-]+)", l)
        if m: mu, se = float(m.group(2)), float(m.group(3))
    print(f"    j={j}: {(mu-float(EXACT[j][0]))/se:+.2f} sd   "
          f"(vs {(mu-float(sigma(j,128)))/se:+.2f} sd against the finite-N value)")
finish("F-BIAS")
