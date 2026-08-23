# RUN.md -- {2,2,5}  (repro/constants/j225)

Exact value **2263/5040** = 0.4490079365,
30 dihedral orbits on the 9-cycle, {2,2,5}.
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
python3 ../../engines/run_k10.py '{2,2,5}' 9 2,2,5 --jobs 110
```

**--jobs ceiling 110**: 9366 terms x 30 orbits in R^8; memo ~0.9 GB/worker -> **<= 110 workers/node**.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 18  289/302400 ...
  total = 2263/5040 = 0.4489087302
```
Expected wall clock: ~5 h on 110 cores.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`"PENDING"`
