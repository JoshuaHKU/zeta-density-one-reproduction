# RUN.md -- {7} = C_7  (repro/constants/c7)

Exact value **-17/360** = -0.0472222222,
1 dihedral orbits on the 7-cycle, {7}.
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
python3 ../../engines/run_pure_rows.py 7 --jobs 24 --out c7_orbit_values.json
```

**--jobs ceiling 24**: 9366 F-CYC terms -> 685 D_7 orbits (13.7x); memo ~0.9 GB/worker.

## 3. Expected output

```
backend gmpy2 ...
  685 term orbits, free dim 6 ...
  total = -17/360 = -0.0472222222
```
Expected wall clock: ~3.5 min on 24 cores.

## 4. Checkpoints

`c7_orbit_values.json` is the deliverable; no intermediate checkpoint.
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "identification-ladder", "note": "r121-r124 seven-level Romberg identification hit -17/360 to machine precision, BEFORE the symbolic run -- so the symbolic value confirms a registered identification rather than merely matching a candidate drawn afterwards (r141 acceptance (d))"}`
