#!/usr/bin/env python3
"""
Model-side sampler for the k=8 rung.

Exact finite realisation of the model spectral measure (paper Gabor-Poisson
lemma, flat window, endpoint limit).  With U ~ CUE(N) and eigenangles
theta_j, the unit-circle Vandermonde Gram  Ghat = W W*/N,
W_{jm} = e^{i m theta_j}, has the SAME spectrum as the N x N Toeplitz matrix

        A_{m,m'} = Tr(U^{m-m'}) / N ,      m,m' = 0 .. N-1 ,

because A = (1/N) V* V.  No unfolding, no edge truncation: the whole
construction is exact at finite N and the model measure is the N -> infinity
limit.  Gates: m1 = 1 exactly per sample (diagonal identity); m2(N) =
4/3 - 1/(3N^2) exactly; m3..m6 -> 2, 13/4, 101/18, 640/63.

Saves, per N: a (reps x 12) array of per-sample moments and the pooled
eigenvalue array (per-sample rows kept, so split-sample estimators are
possible downstream).

Usage:  OMP_NUM_THREADS=1 python3 sample_model.py N REPS [OUTDIR]
"""
import numpy as np, math, os, sys, json, time
from scipy.linalg import toeplitz
from concurrent.futures import ProcessPoolExecutor

MAXK = 12


def one(args):
    N, seed = args
    rng = np.random.default_rng(seed)
    # Haar unitary by QR of a complex Ginibre matrix, with the standard phase fix
    Z = (rng.normal(size=(N, N)) + 1j * rng.normal(size=(N, N))) / math.sqrt(2)
    Q, R = np.linalg.qr(Z)
    Q = Q * (np.diag(R) / np.abs(np.diag(R)))
    th = np.angle(np.linalg.eigvals(Q))
    T = np.exp(1j * np.outer(np.arange(N), th)).sum(axis=1)   # T_k = Tr(U^k)
    A = np.tril(toeplitz(T / N))
    A = A + A.conj().T - np.diag(np.diag(A))
    ev = np.linalg.eigvalsh(A)
    return np.array([(ev ** k).mean() for k in range(1, MAXK + 1)]), ev


def main():
    N = int(sys.argv[1]); reps = int(sys.argv[2])
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    chunk = max(1, min(reps, 200))
    Ms, Es, done = [], [], 0
    with ProcessPoolExecutor(max_workers=9) as ex:
        while done < reps:
            n = min(chunk, reps - done)
            res = list(ex.map(one, [(N, 1_000_000 + N * 10_000 + done + i) for i in range(n)]))
            Ms += [r[0] for r in res]; Es += [r[1] for r in res]; done += n
            np.save(f"{out}/mom_{N}.npy", np.array(Ms))
            np.save(f"{out}/ev_{N}.npy", np.array(Es))
            print(f"N={N} {done}/{reps}  {time.time()-t0:.0f}s", flush=True)
    M = np.array(Ms)
    exact = {2: 4 / 3 - 1 / (3 * N ** 2), 3: 2.0, 4: 13 / 4, 5: 101 / 18, 6: 640 / 63}
    print(f"\n### N={N} reps={reps}   ({time.time()-t0:.0f}s)")
    for k in range(1, MAXK + 1):
        mu = M[:, k - 1].mean(); se = M[:, k - 1].std(ddof=1) / math.sqrt(reps)
        s = f"  m{k:2d} = {mu:13.6f} +- {se:.6f}"
        if k == 1:
            s += "   (exact 1 per sample)"
        elif k in exact:
            s += f"   finite-N exact/limit {exact[k]:12.7f}   ({(mu-exact[k])/se:+6.2f} sigma)"
        print(s)


if __name__ == "__main__":
    main()
