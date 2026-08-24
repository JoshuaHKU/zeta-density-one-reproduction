# {7,2} = -4313/12600  (j72)
Source: facet chain on host 231 (r148); written receipt RECEIPT_R148_J72.md
(this package).  4 dihedral orbits, size 9 each; bundle value
9 x (-1927/113400 - 251/56700 - 137/15120 - 571/75600) = -4313/12600,
rebuilt bitwise here and gate-checked by g_be BE7 together with the two
identities it participates in:
  C_9 + {7,2} = -75863/302400          (pre-registered before the C_9 run)
  {5,4} + {2,2,5} + C_9 + {7,2} = Sigma_9 = 52207/302400

## Audit notes (AUDIT_R177)

- **2.5 second path.**  `second_path` is `PENDING` / single-path.  A previous
  revision labelled it `pre-registered-identity` on the strength of
  `C_9 + {7,2} = -75863/302400`.  That identity is real and gate-checked, but
  it was consumed certifying `C_9`, and one equation cannot independently
  confirm both of its own terms.  This restores what sec 3 of
  `RECEIPT_R148_J72.md` recorded originally.
- **2.4 no `orbits.json`.**  The receipt archived per-orbit values under the
  labels `O0..O3` only; the orbit representatives were never recorded.  This
  directory is therefore deliberately outside gate `g_totals` (canonical keys
  + orbits/values join) and is covered by `g_be` BE7 instead.  Recovering the
  representatives means re-running the facet chain, ~18 h on 22 workers.
