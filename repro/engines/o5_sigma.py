#!/usr/bin/env python3
"""
O5 (r138): high-statistics model measurement of Sigma_9 / Sigma_10.

The model spectral measure is the ESD of the unit-circle Vandermonde Gram at
CUE points (identical construction to christoffel_pricing.sample_spectrum).
Sigma_j = E (lambda - 1)^j are the central moments -- exactly the quantities
the re-centring identity Gtilde/(L l1) = I + P pins.

The reference sampler loops samples in one process; since its RNG stream is
per-sample (default_rng((seed, N, k))) the samples are independent and
reproducible, so the loop shards cleanly across processes.  Each worker returns
PER-SAMPLE central moments so the error bars can be bootstrapped over samples
(the eigenvalues inside one sample are strongly dependent -- the effective
sample size is the number of CUE draws, not the number of eigenvalues).

Usage: OMP_NUM_THREADS=1 python3 o5_sigma.py N NSAMP JOBS [SEED]
"""
import sys, time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

PMAX = 14          # r143 A1: Sigma_11..Sigma_14 needed for the k=14 band

def sample_central(args):
    N, seed, k = args
    rng = np.random.default_rng((seed, N, k))
    A = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
    Q, R = np.linalg.qr(A)
    d = np.diagonal(R)
    Q = Q * (d / np.abs(d))[None, :]
    th = np.angle(np.linalg.eigvals(Q))
    x = th * N / (2 * np.pi)
    m = np.arange(N)
    W = np.exp(2j * np.pi * np.outer(x, m) / N)
    s = np.linalg.svd(W, compute_uv=False)
    lam = (s * s) / N
    c = lam - 1.0
    # r148 ruling D: every spectral pool must carry the log-spectral mean so
    # F-LOGDET can be run on it.  (1/N) sum log lambda_i is appended as the LAST
    # column, permanently.  Changed only after the N=128/192/256 A1 sequence
    # finished -- altering the sampler mid-sequence would have broken the
    # like-for-like comparison those three tiers exist to provide.
    return np.array([float(np.mean(c ** p)) for p in range(1, PMAX + 1)]
                    + [float(np.mean(np.log(lam)))])

if __name__ == "__main__":
    N, nsamp, jobs = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        rows = list(ex.map(sample_central, [(N, seed, k) for k in range(nsamp)],
                           chunksize=8))
    M = np.array(rows)                       # nsamp x (PMAX + 1); last col = (1/N) sum log lambda
    mean = M.mean(0)
    se = M.std(0, ddof=1) / np.sqrt(nsamp)
    print(f"N={N}  nsamp={nsamp}  jobs={jobs}  {time.time()-t0:.0f}s", flush=True)
    EX = {2: 1/3, 4: 1/4, 5: 1/36, 6: 61/252, 7: 7/90, 8: 633/2240}
    print(f"{'j':>3} {'Sigma_j':>14} {'+-':>10}   exact / target")
    for p in range(1, PMAX + 1):
        tag = ""
        if p in EX:
            d = mean[p-1] - EX[p]
            tag = f"   exact {EX[p]:+.9f}   dev {d:+.2e} ({d/se[p-1]:+.1f} sd)"
        elif p == 9:
            tag = "   r138 target 0.172 +- 0.009"
        elif p == 10:
            tag = "   r138 target 0.399 +- 0.015"
        print(f"{p:>3} {mean[p-1]:>14.9f} {se[p-1]:>10.2e}{tag}")
    np.save(f"o5_central_N{N}_s{seed}.npy", M)   # SAVE FIRST: an exception in
    # the reporting block below must never cost the pool (it did once, r148).
    # F-LOGDET on this pool, from the new column (r148 D).  No scipy: 238 has
    # none, and trigamma is elementary here --
    #     psi'(n+1) = pi^2/6 - sum_{k<=n} 1/k^2 ,   psi'(2) = pi^2/6 - 1.
    def polygamma(_, n):
        n = int(n)
        return np.pi ** 2 / 6.0 - float(np.sum(1.0 / np.arange(1, n) ** 2))
    L = M[:, PMAX]
    H = float(np.sum(1.0 / np.arange(1, N + 1)))
    mX = H - 1.0 - np.log(N)
    vX = float(polygamma(1, N + 1) - polygamma(1, 2) / N)
    mE, vE = float(L.mean()), float(L.var(ddof=1))
    z = (L - mE) / np.sqrt(vE); kappa = float((z ** 4).mean())
    se_m = np.sqrt(vE / nsamp)
    se_v = vE * np.sqrt((kappa - 1) / nsamp + 2.0 / (nsamp - 1))
    print(f"\nF-LOGDET  mean {mE:.9f} vs {mX:.9f}  {(mE-mX)/se_m:+.2f} sd")
    print(f"F-LOGDET  var  {vE:.6e} vs {vX:.6e}  {(vE-vX)/se_v:+.2f} sd  (kappa {kappa:.2f})")
