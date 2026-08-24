# REPRO v4 FREEZE (preprint-0.92, r164)

Frozen 2026-08-21. Deltas from v3 (see `REPRO_V3_FREEZE.md`,
which remains valid for everything it covers; v3 files are
unchanged — extensions live in new files only).

## What v4 adds

Paper scope: v0.92 = the density-one revision. New proved
theorems (branch equality t:poly, parity t:parity, lifted TU
l:tu, shift-lift l:lift, moment growth l:growth, determinacy
p:det, no-atom p:noatom, order schema t:schema, density-one
t:dens1). The computational assets behind their verification
campaign enter the package here.

### New constants

- `constants/be/` (96 files): the branch-equality campaign.
  - `tu_scan_b{4..8}*.json` — m-space wall-system TU
    falsification: b<=7 exhaustive (21,171 systems), b=8
    two-leg sampled (197,357 systems; coverage stated in
    file). Zero violations.
  - `ltu_scan_b{3..6}.json` — lifted-system TU falsification,
    exhaustive b<=6 (4,638 systems), zero violations.
    (A 37,633-system b=7 scan was in flight at freezing; its
    result will be recorded as an addendum, not a change.)
  - `parity_scan_b{4,5,6}.json` — true-cumulant (Moebius
    layer) per-term parity: 15/52/203 partitions, all
    satisfying T_P(-N) = (-1)^{b+1} T_P(N); bitwise assembly
    totals included.
  - `sigma_scan_b{4,5,6}.json` — the complete fine
    (merged-cluster) term families, Fubini sizes 75/541/4683,
    with per-term values from N=1; single-polynomial fits,
    per-term parity, and the signed assembly all pass.
  - `m_odd_ext_PREDICTION.json` / `m_odd_ext.json` — the
    pre-registered odd-b surplus points m9(8), m11(9),
    m13(10): predictions recorded before computation
    (timestamp inside), all HIT bitwise.
  - `fit_audit_b2_14.json` — data-sufficiency audit
    (points vs unknowns per b under the proved
    parity-constrained polynomial form).
- `constants/c9/` — the C_9 = 27649/302400 facet-recursion
  second method: `values.json` (pedigree + self-checks),
  `orbits.json`, `term_orbits.json` (60,739 signed orbit
  rows; rebuild sum equals the total exactly).
- `constants/tt/m_tables_ext.json` — the three extension
  points as an EXTENSION file; the frozen v3
  `m_tables.json` is untouched.

### New engines

- `engines/be/` — compute-side sources for the campaign
  (TU/LTU scans, Moebius parity scan, fine-family sigma
  scans incl. GPU variants, fit audit). Math-side
  independent reimplementations live in the session
  archive; the gate below re-verifies everything from the
  JSON artifacts alone, so neither implementation is
  trusted.

### New gate

- `gates/g_be.py` — 29 exact-arithmetic checks recomputed
  from artifacts only (seconds): counting identities
  (Lah 13/73/501/4051/37633, Fubini 13/75/541/4683,
  file-level counts), signed fine assembly b=4/5/6 at every
  archived N including N=1, Moebius-layer assembly, per-term
  parity spots, odd-b surplus fits with leading coefficient
  == archived m_b, and scan verdict integrity. Hooked into
  `run_all.sh gates`.

## Discipline notes

- Append-only: no v3 file was modified; all deltas are new
  files or the run_all gate list.
- In-flight at freeze (recorded, non-blocking, to be
  appended on return): LTU b=7 scan; dual implementation of
  m9(8)/m11(9); optional C_core interval enclosure.
- The registry at freeze: 547 pre-registered checks, 505
  passed, 60 fired-and-converted (matches the paper).

*Math: Claude; program direction: Hongyi Yang.*

## Addendum (2026-08-22): in-flight items landed

- `ltu_scan_b7.json` (+8 shard files): the b=7 lifted-TU scan
  landed PASS -- 37,633 systems (== the predicted Lah count
  a(7)), zero violations; GPU float64 screening with exact
  integer Bareiss adjudication of every flagged minor.
  Lifted falsification now exhaustive for b <= 7
  (42,271 systems total).
- `ltu_scan_b5.json`: re-run and archived after a credential
  gap was self-caught (a receipt row had listed PASS with no
  artifact in the package; register D28).
- `coeff_assembly*.json`: the signed-assembly gate
  F-BE-COEFF-3..6 as an independent second implementation
  written from the r163 coefficient specification (CPU+GPU
  cross-check at b=4), all PASS.
- `gates/g_be.py` extended accordingly (31 checks, ALL GREEN).

Registry at addendum: 571 / 529 / 61 (the paper at freeze time; the
registry has since advanced through the r176/r177 audit rounds -- current
numbers live in the paper's verification section, this line keeps the
freeze-time snapshot).
