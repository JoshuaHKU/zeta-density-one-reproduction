# preprint-0.92 -- reproduction package (v4)

(Original v1 header follows, updated in place for v0.92; the v1/v3/v4
freeze notes REPRO_V4_FREEZE.md record the append-only history.)

Built to the spec REPRO_SPEC.md (round 139; its normative rules are excerpted in REPRO_V4_FREEZE.md and this README -- the internal compute/ tree is not part of this package).  One standard: **every number in
the paper has one path from the command line to the text, no hidden state, and
an executable assertion.**

Two consumers: a reader re-running everything, and a referee spot-checking one
value.  Both start here.

## Quick start

```bash
export OMP_NUM_THREADS=1 RATBACKEND=gmpy2
./run_all.sh gates
```
Eighteen gate scripts (nineteen on disk incl. the optional sympy gate), seconds, no GPU, no cluster.  `exit 0` iff all pass; gates whose optional third-party dependencies (numpy/scipy) are absent print NOT-APPLICABLE and exit 3 rather than crash.

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
| `{2,2,5}` | `2263/5040` | PENDING (single-path: facet chain only) |
| `{5,4}` | `-257/10080` | PENDING (single-path: facet chain only) |
| `{6,2,2}` | `-120139/498960` | PENDING (single-path: facet chain only) |
| `{7,2}` | `-4313/12600` | PENDING (single-path: facet chain only) -- see note below |
| `C_9` | `27649/302400` | facet recursion, second method for `Sigma_9` (g_be BE7) |
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

**Sigma_9 and Sigma_10 are exact rationals since v3**:
Sigma_9 = 52207/302400 (two independent proofs: the Toeplitz-trace route,
now at proof grade via the branch-equality and parity theorems, and the
C_9 facet recursion, constants/c9/), and Sigma_10 = 1333891/3326400.
The v1 text at this spot called them measurements; that snapshot is
preserved in the git history and superseded here.  Per-constant grades
live in constants/tt/m_tables_grades_v4.json (see below).

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


## Grades in v4 (read this before quoting a grade field)

The frozen tables `constants/tt/m_tables.json` and `m_tables_ext.json`
carry the grade tags AS OF THEIR FREEZE (v3 / v4-extension): several say
`exact-candidate` or `pending F-IMPL / joint layers`.  Those files are
append-only and are never edited.  The CURRENT grades live in
`constants/tt/m_tables_grades_v4.json`, which records the regrade rule
explicitly: the branch-equality theorem (single polynomial, every N>=1)
plus the parity theorem close the Toeplitz-trace route, so every m_b
(b<=14) is a proved exact rational and the former second-path items
(C_9 facet, F-IMPL points, joint layers) are redundancy, not
prerequisites.  Items still single-path ({2,2,5}, {5,4}, {6,2,2}) are
marked as such -- their VALUES are consumed via the proved route; the
facet second path for them remains open as optional redundancy.

**Why `{7,2}` is listed as single-path** (AUDIT_R177 2.5).  It was briefly
labelled "pre-registered identity with `C_9`".  That identity,
`C_9 + {7,2} = -75863/302400`, is genuine and gate-checked -- but it has two
facet-side unknowns and it was already *spent* certifying `C_9`: the
pre-registered sum minus the earlier-delivered `{7,2}` is exactly what pinned
the `C_9` target that the facet run then hit.  One equation cannot
independently confirm both of its own terms.  The other identity,
`{5,4}+{2,2,5}+C_9+{7,2} = Sigma_9`, has four facet-side unknowns and
constrains only their sum.  `RECEIPT_R148_J72.md` sec 3 said so from the
start ("second_path currently empty ... no third-party cross-check");
`constants/j72/values.json` has been restored to that reading.  The value is
unaffected and remains gate-checked by `g_be` BE7.

**Why `constants/j72/` has no `orbits.json`** (AUDIT_R177 2.4).  The receipt
archived the per-orbit values under the labels `O0..O3`; the orbit
representatives themselves were never recorded, and recovering them means
re-running the facet chain (~18 h on 22 workers).  Rather than fabricate
representatives, this directory is deliberately outside gate `g_totals` --
which is the gate that checks canonical keys and the orbits/values join --
and is covered by `g_be` BE7 instead.  `C_9`, which does have everything, was
added to `g_totals` in the same audit.

## Gate self-test (error injection)

`./run_all.sh selftest` injects a deliberate corruption into each guarded
constants file (p24 totals and orbit values, parity/sigma scans, c9 orbit
weights, j72, extension table) and requires the corresponding gate to fail,
then restores the file and requires the gate to pass again.  A gate that
stays green under injection is a fake gate.  Run before every release.

## Release scope of per-round process documents (r179)

This release carries every process document that the shipped data, gates,
paper or a retained document's evidence chain cites (receipts anchoring
constants provenance, the adjudications referenced by the value tables,
the freeze records, AUDIT_R149 referenced by gate code).  Fifteen
per-round process documents cited by nothing in the release -- six
acceptances (R148_J72, R148_OTT2, R150_FIMPL_B13, R160_BE, R160_BE2,
R160_C9), ADJUDICATION_R148, BUG_REPORT_ENUM_R148, OPTIMIZATION_r141,
four early receipts (R146, R148_OTT2, R148_OTT3_B11, R148_OTT3_B12),
REPRO_UPDATE_R149 and VERDICT_R153_K14 -- are retained in the program
archive rather than in this release.  Mentions of those filenames inside
the retained historical documents (which are frozen and are not edited)
refer to that archive; copies are available on request.  No value, gate,
log or provenance link depends on the removed files -- verified by a
whole-tree reference scan before removal, and the gate suite plus the
injection self-test were re-run green afterwards.
