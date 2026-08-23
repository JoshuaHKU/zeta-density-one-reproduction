# RUN.md -- {5,4}  (repro/constants/j54)

Exact value **-257/10080** = -0.0254960317,
10 dihedral orbits on the 9-cycle, {5,4}.
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
python3 ../../engines/run_k10.py '{5,4}' 9 5,4 --jobs 160
```

**--jobs ceiling 160**: 1082x26 terms x 10 orbits in R^9; measured 0.9 GB/worker on the pre-r141 engine.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 18  -11/151200 ...
  total = -257/10080 = -0.0254960317
```
Expected wall clock: ~13 h on 160 cores (238).

## 4. Checkpoints

none for this run (it predates the r141 checkpoint patch); later runs write ck_5_4.json
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`"PENDING"`
