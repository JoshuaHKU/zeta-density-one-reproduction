# RUN.md -- {2,2,2}  (repro/constants/t222)

Exact value **32/105** = 0.3047619048,
5 dihedral orbits on the 6-cycle, {2,2,2}.
Engine: phase0 polytope.

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
python3 ../../engines/t222_exact.py
```

**--jobs ceiling 8**: 5 orbits in R^3; memory negligible.

## 3. Expected output

```
backend gmpy2 ...
  D0 size 2  3/70 ...
  total = 32/105 = 0.3047619048
```
Expected wall clock: ~1 min.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "newton-cotes-ladder", "note": "phase0 exact_t222 iterated NC, method A vs B agree"}`
