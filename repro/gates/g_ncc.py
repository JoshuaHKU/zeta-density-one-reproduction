# -*- coding: utf-8 -*-
"""Gate F-NCC: the non-crossing convolution calculus (paper sec conv (v)).

非交叉卷积演算门。The sequential b-cycle pairing orbit has the
closed form (r146 theorem T2)

    seq(2m) = 4^(-m) * integral_0^1 (1+x^2)^m dx
            = 4^(-m) * sum_{k=0}^m C(m,k) / (2k+1),

a pure rational identity -- no symbolic integration needed.  This
gate checks the closed form against every archived / registered
sequential orbit value:

  m=3 (b= 6): 3/70        archive (T0 of Prop. p:t222)
  m=4 (b= 8): 83/5040     archive ({2^4} largest orbit)
  m=5 (b=10): 73/11088    blind-predicted r144, found in archive
  m=6 (b=12): 523/192192  registered r146, facet-confirmed (g_seq)
  m=7 (b=14): 119/102960  registered r146, facet-confirmed (g_seq)

Complementary to g_seq.py (compute side), which verifies the same
two frontier values by facet recursion: this gate is the closed-form
leg, g_seq is the method-independent leg.  Exit 0 iff all pass.
"""
import os
import sys
from fractions import Fraction as Q
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, finish                     # noqa: E402

TARGETS = {3: Q(3, 70), 4: Q(83, 5040), 5: Q(73, 11088),
           6: Q(523, 192192), 7: Q(119, 102960)}


def seq(m):
    """Closed form 4^(-m) * sum C(m,k)/(2k+1), exact."""
    return Q(1, 4 ** m) * sum(Q(comb(m, k), 2 * k + 1)
                              for k in range(m + 1))


for m, want in TARGETS.items():
    check(f"seq(b={2 * m}) = {want}", seq(m) == want)

# denominator law observation (D21 line): prime 13 enters at b=12
check("denominator of seq(12) divisible by 13 (D21 line)",
      Q(523, 192192).denominator % 13 == 0)

finish("F-NCC (sequential closed forms)")
