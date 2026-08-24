#!/usr/bin/env python3
"""O5 gate.  Recompute the CUE-model central moments Sigma_j from the ARCHIVED
per-sample file (200000 x 12) and require:
  (a) the six known exact Sigma_j (j=2,4,5,6,7,8) reproduced within 1 sd;
  (b) Sigma_1 = 0 and Sigma_3 = 0 to sampling accuracy (structural);
  (c) Sigma_9 / Sigma_10 measured to at least the precision r138 demands
      (0.009 / 0.015), since the k=10 pricing consumes them."""
import os, sys
from fractions import Fraction as Q
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import need
need("numpy")
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, require_count, finish

NPY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "measurements", "o5", "o5_central_N128_s0.npy")
# AUDIT_R164 2.4: compare against the EXACT FINITE-N law Sigma_j(N=128)
# (polynomials in 1/N^2, same reference as g_bias), not the N->infinity
# limit -- the finite-N term is real and provably so (branch-equality
# theorem); with the limit as reference this gate was one tolerance notch
# away from a wrong verdict.
_POLY = {2: [Q(1,3), Q(-1,3)],
         4: [Q(1,4), Q(-7,12), Q(1,3)],
         5: [Q(1,36), Q(-5,36), Q(1,9)],
         6: [Q(61,252), Q(-35,36), Q(13,9), Q(-5,7)],
         7: [Q(7,90), Q(-91,180), Q(161,180), Q(-7,15)],
         8: [Q(633,2240), Q(-3371,2016), Q(12247,2880), Q(-5545,1008), Q(277,105)]}
_N = 128
EXACT = {j: sum(c / Q(_N) ** (2 * i) for i, c in enumerate(cs))
         for j, cs in _POLY.items()}
NEED = {9: 0.009, 10: 0.015}

M = np.load(NPY)
check("O5 archive shape", M.shape == (200000, 12), f"{M.shape} (want (200000, 12))")
mean = M.mean(0); sd = M.std(0, ddof=1) / np.sqrt(len(M))
n = 0
for j, ex in EXACT.items():
    m, s = mean[j - 1], sd[j - 1]
    dev = m - float(ex)
    n += check(f"F-SIGMA{j} known", abs(dev) <= s,
               f"{m:.9f} +- {s:.2e}  Sigma_j(128) {float(ex):.9f}  dev {dev/s:+.1f} sd")
require_count("O5 known-moment coverage", n, len(EXACT))
check("O5 Sigma_1 = 0", abs(mean[0]) < 1e-12, f"{mean[0]:.3e}")
check("O5 Sigma_3 = 0", abs(mean[2]) <= 2 * sd[2], f"{mean[2]:.3e} +- {sd[2]:.2e}")
for j, need in NEED.items():
    check(f"F-SIGMA{j} precision", sd[j - 1] <= need,
          f"Sigma_{j} = {mean[j-1]:.9f} +- {sd[j-1]:.2e}  (r138 needs {need})")
finish("F-O5")
