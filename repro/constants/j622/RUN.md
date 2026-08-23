# RUN.md -- {6,2,2}  (repro/constants/j622)

Exact value **-120139/498960** = -0.2407788199,
46 dihedral orbits on the 10-cycle, {6,2,2}.
Engine: facet recursion (r136, r141-optimised).

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
python3 ../../engines/run_k10.py '{6,2,2}' 10 6,2,2 --jobs 16
```

**--jobs ceiling 16**: 1082 terms x 46 orbits in R^9; **size the job by memo x worker, not by cores** -- the r141 engine uses MORE memory per worker (LP cache), and 65 workers x 3.6 GB OOM-killed a sibling run on a 251 GB node.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 20  -19/30800 ...
  total = -120139/498960 = -0.2407788199
```
Expected wall clock: ~14 h on 16 cores (230), including a restart.

## 4. Checkpoints

ck_6_2_2.json, written after every orbit; delete it to force a full recompute. It saved this run twice.
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`"PENDING"`
