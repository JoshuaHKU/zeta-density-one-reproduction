# constants/be/ -- branch-equality campaign artifacts (v4)

Full-coverage result files (the ones gates consume):
  tu_scan_b{4..7}.json      m-space TU falsification, exhaustive
  tu_scan_b8.json           two-leg SAMPLED coverage (stated, not implied)
  ltu_scan_b{3..7}.json     lifted TU, exhaustive (Lah counts)
  parity_scan_b{4,5,6}.json Moebius-layer parity, complete partitions
  sigma_scan_b{4,5,6}.json  fine (merged-cluster) families, complete (Fubini)
  sigma_scan_b7.json        b=7 summary (47,293 = Fubini(7); COVERAGE PASS);
                            per-term values live in the six shard files
  coeff_assembly*.json      signed-assembly gate, independent 2nd impl
  m_odd_ext*.json           pre-registered odd-b surplus points
  fit_audit_b2_14.json      data-sufficiency audit

Shard / partial files (evidence of runs, NOT standalone results):
  *_s<i>of<n>.json          checkpoint shards; only the merged/summary file
                            is a result.  In particular sigma_scan_b5_s0of3
                            is a 1/3-coverage verification shard of the
                            COMPLETE sigma_scan_b5.json (541 terms).
  tu_scan_b7 shard files    24-shard evidence for the merged b=7 verdict.
