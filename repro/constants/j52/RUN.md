# RUN.md -- {5,2}  (repro/constants/j52)

Exact value **1/8** = 0.1250000000,
3 dihedral orbits on the 7-cycle, {5,2}.
Engine: facet recursion.

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
python3 ../../engines/run_class.py '{5,2}' --jobs 8
```

**--jobs ceiling 8**: 150 F-CYC terms x 3 orbits in R^7; memo table ~0.2 GB/worker.

## 3. Expected output

```
backend gmpy2 ...
  Q0 size 7 rep [[0,1,2,3,4],[5,6]] = 5/504 ...
  total = 1/8
```
Expected wall clock: ~90 s.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "ladder-gpu", "dev": 1.037e-06, "note": "F-V-25: midpoint ladder + h^2 Richardson on the V100, 3/3 orbits within 1.04e-6, bundle within 7.9e-6 of 1/8; the pre-registered candidate 1/8 also hit exactly (model 0.124944)"}`

Reproduce it with the midpoint ladder (needs numpy, and CuPy+V100 for the GPU path):

```bash
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 52 0.1
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 52 0.05
python3 ../../gates/g_v52.py
```
h^2 Richardson `(4 L(dv/2) - L(dv))/3` must match all 3 orbits within 3e-6.
**Match on the canonical form, never on orbit index** -- the ladder and the exact
chain enumerate orbits in different orders and pick different representatives;
index matching produced a false FAIL in round 136.
