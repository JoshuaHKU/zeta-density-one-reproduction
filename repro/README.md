# preprint-0.84 -- reproduction package

Built to `compute/REPRO_SPEC.md` (round 139).  One standard: **every number in
the paper has one path from the command line to the text, no hidden state, and
an executable assertion.**

Two consumers: a reader re-running everything, and a referee spot-checking one
value.  Both start here.

## Quick start

```bash
export OMP_NUM_THREADS=1 RATBACKEND=gmpy2
./run_all.sh gates
```
Ten gate scripts, under two minutes, no GPU, no cluster.  `exit 0` iff all pass.

Then any single constant:

```bash
cat constants/j224/RUN.md      # environment, one command, expected output, wall clock
python3 gates/g_totals.py      # rebuild every bundle from its per-orbit rows
```

## Layout

    engines/        the integrators, no constant-specific logic
    constants/<c>/  orbits.json, values.json, RUN.md, (term_orbits.json for c7/c8)
    measurements/   o5/ (200000 x 12 per-sample central moments, 19 MB)
                    ladder/ (midpoint-ladder checkpoints, the second numeric path)
    gates/          one script per F-gate; exit 0 iff pass
    certification/  certify_k8.py, recentring.py
    data/           model_constants.json (the r129-corrected model side)
    logs/           append-only raw logs, incidents preserved
    MANIFEST.json   sha256 of everything + engine hashes + host table
    run_all.sh      gates | light | heavy --confirm | o5

## What is exact and what is not

Exact rationals, certified symbolically:

| constant | value | second path |
|---|---|---|
| `{2,2,2}` | `32/105` | two independent exact methods |
| `{2^4}` | `1661/3780` | r129 ladder (dev -8.1e-7) |
| `{2,2,4}` | `-127/840` | GPU ladder, 22/22 orbits, 1.07e-6 |
| `{4,4}` | `23/4536` | GPU ladder, 7/7 orbits, 3.85e-7 |
| `{6,2}` | `-563/11340` | GPU ladder, 4/4 orbits, 9.42e-7 |
| `{5,2}` | `1/8` | GPU ladder, 3/3 orbits, 1.04e-6 |
| `C_7` | `-17/360` | identification ladder (r121-124 Romberg, registered *before* the symbolic run) |
| `C_8` | `157/4032` | **model-side bound only** -- see below |
| `{2^5}` | `10531/13860` | GPU ladder, 79/79 orbits 2.04e-6, bundle -4.22e-6 |
| `{4,2,2,2}` | `-208771/498960` | cross-host replication, 12/12 overlapping orbits identical |
| `{2,2,5}` | `2263/5040` | PENDING |
| `Sigma_7` | `7/90` | `= {5,2} + C_7` |
| `Sigma_8` | `633/2240` | `= {2^4}+{2,2,4}+{4,4}+{6,2}+C_8` |
| `m_7` | `3439/180` | re-centring, F-PRED-RAT-7 |
| `m_8` | `747361/20160` | re-centring, F-PRED-RAT-8 |

**C_8 has no independent symbolic path.**  Its `second_path` field says
`model-side-ABC` and means exactly that: the model bounds it, it does not
confirm it.  The pre-registered small-denominator candidate `7/180` MISSED the
true value by 4.96e-5.  The brute-force 94586-term recheck was started and
stopped (logs/README.md, incident 5); restarting costs ~14 h with no checkpoint.

One caveat on `{4,2,2,2}`: cross-host replication is the *same code* on two
machines.  It rules out a machine-local fault, not a method-level one.  The
label says `cross-host-replication`, never "independently confirmed".

**Sigma_9 = 0.172618190 +- 6.07e-4** and **Sigma_10 = 0.400778101 +- 1.08e-3**
are measurements, not rationals.  Anything downstream of them -- the k=10
pricing, the 0.877 projection -- is conditional on the measurement, and the
paper must grade it that way.

Headline, from exact constants only:

    N0s/N >= 1 - 2 w0 = 4483782896209867992189972451657/5278903382744981072330819894343 = 0.84937772
    Nd /N >= 1 -   w0 = 4881343139477424532260396173000/5278903382744981072330819894343 = 0.92468886

and the unconditional k<=6 corner `2025/2519 = 0.8038904327` / `2272/2519 = 0.9019452164`.

## Two rules that cost us the most to learn

**Key on content, never on index.**  Every orbit key in this package is the
dihedral canonical form `min(orbit(placement))`.  The ladder chain and the exact
chain enumerate orbits in different orders and pick different representatives;
matching by index falsely FAILed two of three classes in round 136.  Building
this package, the same mistake surfaced once more -- phase 0 labels its five
D_6 orbits in its own order, and zipping by index gave `551/1260` instead of
`32/105`.  It was caught by `gates/g_totals.py`, which is why that gate exists.

**A comparison that matched nothing is not a pass.**  Every gate asserts
`matches == expected`; a short match prints `NOT-APPLICABLE` and exits non-zero.
