# logs/ addendum (v4, 2026-08-22) -- append-only

Audit outcome first: the 24 legacy files indexed in `README.md`
were re-audited against the shipped receipts and REPRO_SPEC
sec 6. **None qualifies for deletion**: every file is either
cited by an acceptance/receipt (e.g. `r150_b14_partial.log` by
`ACCEPTANCE_R150_B14_PARTIAL.md`), or is required incident
evidence (`*_pre_restart.log`, `*_partial.log` document the
recorded incidents narrated in `r136-137-138_compute_log.md`
and the discrepancy register). Per the append-only pledge at
the top of `README.md`, nothing was removed.

What this addendum ADDS: the raw logs of the branch-equality
campaign (v4) and the C_9 facet second method, previously
archived outside the publication tree; and the campaign's
receipts/adjudications trail at `repro/` top level
(`RECEIPT_R159_BE.md`, `RECEIPT_R160_BE.md`,
`ADJUDICATION_R160_BE6.md`, `ACCEPTANCE_R160_BE.md`,
`ACCEPTANCE_R160_BE2.md`, `ACCEPTANCE_R160_C9.md`,
`COMPUTE_ORDERS_BE_R160.md`, `COEFF_SPEC_BE_R163.md`).

| file | round | host | what (consistency-checked against the paper) |
|---|---|---|---|
| `r159_tu_b6.log` | 159 | 230 | m-space TU scan b=6: 2,044 systems, PASS |
| `r159_tu_b7.log` | 159 | 230+231 | m-space TU scan b=7: 18,835 systems in 24 shards, PASS (per-shard ~784) |
| `r159_tu_b8.log` | 159 | 230+231 | b=8 two-leg sampled scan: 197,357 systems, PASS |
| `r159_parity_b5.log` | 159 | local | Moebius parity scan b=5: 52/52 Proposition A |
| `r159_parity_b6.log` | 159 | 240 | Moebius parity scan b=6: 203/203 Proposition A |
| `r160_ltu_b5.log` | 160 | local | lifted TU b=5: 501 systems (= Lah a(5)), PASS |
| `r160_ltu_b6.log` | 160 | 230 | lifted TU b=6: 4,051 systems (= a(6)), PASS |
| `r160_ltu_b7_gpu.log` | 160 | 238+220 | lifted TU b=7: 8 GPU shards, totals sum to 37,633 (= a(7)), all PASS |
| `r163_poly_par_b6.log` | 163 | 220 GPU | fine family b=6: 4,683 terms (= Fubini(6)), F-BE-POLY-6/PAR2-6 PASS |
| `r163_poly_par_b7.log` | 163 | 220 GPU | fine-family b=7 calibration run |
| `r163_coeff_b6.log` | 163 | 220 GPU | signed-assembly gate F-BE-COEFF-6 PASS |
| `r150_238_c9_s0.log` | 150+ | 238 | C_9 shard 0; header notes "resuming from ck0: 31,250 already done" |
| `r150_220_c9_s1.log` | 150+ | 220 | C_9 shard 1 |
| `r150_238_c9_s2.log` | 150+ | 238 | C_9 shard 2 |

Note on the C_9 shard counts: the three checkpoint files report
35,747 + 20,246 + 35,996 = 91,989 cumulative orbit lines; the
excess over the true total is exactly the resumed overlap
declared in the shard-0 header (91,989 - 60,739 = 31,250,
matching "31,250 term orbits already done" from the earlier
230/231 segments). The merged, deduplicated
`constants/c9/term_orbits.json` contains exactly 60,739 signed
orbit rows whose weighted sum equals
C_9 = 27649/302400 bitwise --- the value consumed by the paper.

Everything above is append-only; the legacy `README.md` is
unchanged.
