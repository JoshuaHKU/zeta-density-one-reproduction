# RUN.md -- {2,2,4}  (repro/constants/j224)

Exact value **-127/840** = -0.1511904762,
22 dihedral orbits on the 8-cycle, {2,2,4}.
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
python3 ../../engines/run_class.py '{2,2,4}' --jobs 24
```

**--jobs ceiling 24**: 1082 terms x 22 orbits in R^7; memo ~0.4 GB/worker, so <= 24 workers on a 32 GB node.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 16  -5/18144 ...
  total = -127/840 = -0.1511904762
```
Expected wall clock: ~2 h on 24 cores.

## 4. Checkpoints

`values_2_2_4.json` is written once at the end; a partial run leaves nothing behind.
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "ladder-gpu", "note": "CuPy ladder dv=0.05, F-V-JOINTS 33-orbit match"}`

Reproduce it with the midpoint ladder (needs numpy, and CuPy+V100 for the GPU path):

```bash
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 224 0.1
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py 224 0.05
python3 ../../gates/g_vjoints.py
```
h^2 Richardson `(4 L(dv/2) - L(dv))/3` must match all 22 orbits within 3e-6.
**Match on the canonical form, never on orbit index** -- the ladder and the exact
chain enumerate orbits in different orders and pick different representatives;
index matching produced a false FAIL in round 136.
