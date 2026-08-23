# RUN.md -- {8} = C_8  (repro/constants/c8)

Exact value **157/4032** = 0.0389384921,
1 dihedral orbits on the 8-cycle, {8}.
Engine: facet recursion + dihedral quotient.

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
python3 ../../engines/run_pure_rows.py 8 --jobs 32 --out c8_orbit_values.json
```

**--jobs ceiling 32**: 94586 F-CYC terms -> 6027 D_8 orbits (15.7x) in R^8; memo ~1.8 GB/worker -- **this is the class that caused the 3bis swap incident**: 120 workers x 1.8 GB = 216 GB on a 251 GB box drove the node into swap and produced 0 orbits in 87 min. Size the job by memo x worker, NOT by core count..

## 3. Expected output

```
backend gmpy2 ...
  6027 term orbits, free dim 7 ...
  total = 157/4032 = 0.0389384921
```
Expected wall clock: ~63 min on 60 cores (238); ~1.8 h on 32.

## 4. Checkpoints

`c8_orbit_values.json` is written once at the end; there is no resume, so a killed run restarts from zero.
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "model-side-ABC", "note": "NOT an independent symbolic path; the pre-registered candidate 7/180 MISSED by 4.96e-5, so the model only bounds, it does not confirm"}`
