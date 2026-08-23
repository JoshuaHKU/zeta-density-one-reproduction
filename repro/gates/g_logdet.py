#!/usr/bin/env python3
"""F-LOGDET (r146 N2): exact reconciliation of every spectral pool.

Morris integral (theorem_harvest_r146.md T1) pins BOTH moments of the
per-sample log-spectral mean L = (1/N) sum_i log lambda_i, exactly, at every N:

    E[L]   = H_N - 1 - log N
    Var[L] = psi'(N+1) - psi'(2)/N

Criterion: |dev| <= 3 sd on each.  The variance error bar MUST be
kurtosis-corrected -- se(V) = V*sqrt((kappa-1)/ns + 2/(ns-1)) -- because the
Gaussian formula narrows the bar by about 1.2x at the measured kappa ~ 2.7-3.6
and would manufacture failures.

This costs nothing and is a free falsification surface: an RNG stream reused
across workers, a Gram normalisation slip or a BLAS precision problem all land
on these two exact lines."""
import os, sys, glob
import numpy as np
from scipy.special import polygamma
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, require_count, finish

POOLS = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "e*_*.npy")))
n = 0
for p in POOLS:
    ev = np.load(p)
    if ev.ndim == 1:
        # r128 pools ship flat; N is in the filename (eigs_N128.npy -> 128).
        import re as _re
        N = int(_re.search(r"N(\d+)", os.path.basename(p)).group(1))
        assert ev.size % N == 0, f"{p}: {ev.size} not divisible by N={N}"
        ev = ev.reshape(-1, N)
    ns, N = ev.shape
    L = np.log(ev).mean(axis=1)
    mE = float(L.mean()); vE = float(L.var(ddof=1))
    H = float(np.sum(1.0 / np.arange(1, N + 1)))
    mX = H - 1.0 - np.log(N)
    vX = float(polygamma(1, N + 1) - polygamma(1, 2) / N)
    se_m = np.sqrt(vE / ns)
    z = (L - mE) / np.sqrt(vE)
    kappa = float((z ** 4).mean())
    se_v = vE * np.sqrt((kappa - 1) / ns + 2.0 / (ns - 1))
    dm, dv = (mE - mX) / se_m, (vE - vX) / se_v
    tag = os.path.basename(p)
    n += check(f"F-LOGDET mean {tag:<12}", abs(dm) <= 3,
               f"N={N} ns={ns}  {mE:.9f} vs {mX:.9f}  {dm:+.2f} sd")
    n += check(f"F-LOGDET var  {tag:<12}", abs(dv) <= 3,
               f"{vE:.6e} vs {vX:.6e}  {dv:+.2f} sd  (kappa {kappa:.2f}, "
               f"Gaussian bar would be {np.sqrt(2.0/(ns-1))*vE/se_v:.2f}x tighter)")
require_count("F-LOGDET pools", n, 2 * len(POOLS))
finish("F-LOGDET")
