#!/usr/bin/env python3
"""F-PRED-RAT-7/8/9/10.  The re-centring identity G~/(L l1) = I + P gives
   m_k = sum_j C(k,j) Sigma_j ,   Sigma_0 = 1, Sigma_1 = 0,
so once Sigma_2..Sigma_8 are exact rationals the RATIONAL PART of m_k (all
terms with j <= 8) is pinned exactly, independently of the trace computation.
This gate re-derives it from the constants and compares with the pre-registered
values -- digit for digit."""
import os, sys
from math import comb
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, require_count, finish

S = {0: Q(1), 1: Q(0), 2: Q(1, 3), 3: Q(0), 4: Q(1, 4), 5: Q(1, 36),
     6: Q(61, 252), 7: Q(7, 90), 8: Q(633, 2240)}
WANT = {7: ("3439/180", True), 8: ("747361/20160", True),
        9: ("495107/6720", False), 10: ("199427/1344", False)}
n = 0
for k, (want, complete) in WANT.items():
    v = sum(comb(k, j) * S[j] for j in range(min(k, 8) + 1))
    n += check(f"F-PRED-RAT-{k:<3}", str(v) == want,
               f"{v} = {float(v):.6f}  want {want}"
               + ("  (complete: all Sigma_j exact)" if complete
                  else f"  (rational part only; Sigma_9..Sigma_{k} still measured)"))
require_count("F-PRED-RAT levels", n, len(WANT))
# structural checks on the identity itself
check("re-centring Sigma_1 = 0", S[1] == 0, "flat taper is Nyquist: Phi(tau_k-tau_l)=L delta_kl")
check("F-SIGMA7 = {5,2} + C7", Q(1, 8) + Q(-17, 360) == S[7], f"1/8 - 17/360 = {S[7]}")
check("F-SIGMA8 ledger", Q(1661, 3780) + Q(-127, 840) + Q(23, 4536)
      + Q(-563, 11340) + Q(157, 4032) == S[8],
      "{2^4}+{2,2,4}+{4,4}+{6,2}+C8 = " + str(S[8]))
finish("F-PRED-RAT")
