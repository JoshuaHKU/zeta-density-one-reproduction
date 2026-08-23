# RUN.md -- {2^5}  (repro/constants/p25)

Exact value **10531/13860** = 0.7598124098,
79 dihedral orbits on the 10-cycle, {2^5}.
Engine: facet recursion (r136).

## 1. Environment

   python3 >= 3.9; `gmpy2` STRONGLY recommended (8x over `fractions.Fraction`; set `RATBACKEND=frac` to fall back and reproduce without it); numpy NOT required.
   Runs on 220/230/231/238.  **220 has no numpy**: the facet chain runs there, the ladder chain does not.
   Always `export OMP_NUM_THREADS=1` -- the workers are processes; letting each
   spawn BLAS threads only oversubscribes the node (measured: no speedup, since
   numpy threads only BLAS and this chain is elementwise/rational).
   `RATBACKEND=gmpy2` (default) or `RATBACKEND=frac`.

## 2. Command (one line)

```bash
export OMP_NUM_THREADS=1 RATBACKEND=gmpy2
python3 ../../engines/run_k10.py '{2^5}' 10 2,2,2,2,2 --jobs 110
```

**--jobs ceiling 110**: only size-2 blocks, so no F-CYC expansion: 1 term/orbit in R^5. Memo ~0.05 GB/worker; 110 workers fit a 128-core/250 GB node.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 20  149/118800 ...
  total = 10531/13860 = 0.7598845598
```
Expected wall clock: ~25 min on 110 cores.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "ladder-gpu", "dev": 2.038e-06, "bundle_dev": -4.22e-06, "note": "F-V-25 (r141): midpoint ladder + h^2 Richardson on the V100, 79/79 orbits within 2.04e-6 and bundle within -4.22e-6 of 10531/13860 -- reproducing the math-side r136 figure -4.2e-6, which until r141 lived only in a log"}`
