# RUN.md -- {2^4}  (repro/constants/p24)

Exact value **1661/3780** = 0.4394179894,
17 dihedral orbits on the 8-cycle, {2^4}.
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
python3 ../../engines/p24_exact.py
```

**--jobs ceiling 8**: 17 orbits in R^4, ~10 s each; trivial memory.

## 3. Expected output

```
backend gmpy2 ...
  P0 size 16  11/6048 ...
  total = 1661/3780 = 0.4394179894
```
Expected wall clock: ~3 min.

## 4. Checkpoints

none
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "ladder-r129", "dev": -8.1e-07, "note": "r129 3-level ladder 0.4394188(3); F-P24 criterion revised to 3e-6"}`
