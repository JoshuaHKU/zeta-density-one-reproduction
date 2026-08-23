# RUN.md -- {6,2}  (repro/constants/j62)

Exact value **-563/11340** = -0.0496472663,
4 dihedral orbits on the 8-cycle, {6,2}.
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
python3 ../../engines/run_class.py '{6,2}' --jobs 24
```

**--jobs ceiling 24**: 9366 terms x 4 orbits in R^8; memo ~0.9 GB/worker.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 8 ...
  total = -563/11340 = -0.0496472663
```
Expected wall clock: ~4 h on 24 cores.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "ladder-gpu", "note": "CuPy ladder dv=0.05, F-V-JOINTS 33-orbit match"}`

Reproduce it with the midpoint ladder (needs numpy, and CuPy+V100 for the GPU path):

```bash
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 62 0.1
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 62 0.05
python3 ../../gates/g_vjoints.py
```
h^2 Richardson `(4 L(dv/2) - L(dv))/3` must match all 4 orbits within 3e-6.
**Match on the canonical form, never on orbit index** -- the ladder and the exact
chain enumerate orbits in different orders and pick different representatives;
index matching produced a false FAIL in round 136.
