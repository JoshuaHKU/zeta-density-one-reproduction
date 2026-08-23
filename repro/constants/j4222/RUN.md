# RUN.md -- {4,2,2,2}  (repro/constants/j4222)

Exact value **-208771/498960** = -0.4184122976,
190 dihedral orbits on the 10-cycle, {4,2,2,2}.
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
python3 ../../engines/run_k10.py '{4,2,2,2}' 10 4,2,2,2 --jobs 110
```

**--jobs ceiling 110**: 1082 terms x 190 orbits in R^7; memo ~0.4 GB/worker -> **<= 110 workers/node**.

## 3. Expected output

```
backend gmpy2 ...
  O0 size 20  -61/285120 ...
  total = -208771/498960 = -0.4184423400
```
Expected wall clock: ~3 h on 110 cores.

## 4. Checkpoints

none; this class is the cross-host duplicate (220 and 231 independently returned identical rationals).
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{"method": "cross-host-replication", "host2": "231", "note": "220 and 231 returned identical rationals on all 12 overlapping orbits; same code on two hosts, so this replicates the run, it does not supply an independent method"}`
