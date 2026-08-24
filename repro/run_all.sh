#!/usr/bin/env bash
# Layered reproduction driver (spec rules excerpted in README.md and
# REPRO_V4_FREEZE.md; the internal REPRO_SPEC.md is not part of this package).
#   ./run_all.sh gates   all gate scripts + certify84          (<= 2 min)
#   ./run_all.sh light   full recompute of the light classes   (<= 1 day, 1 node)
#   ./run_all.sh heavy   C_7/C_8 recompute (C_9 already computed and shipped: constants/c9)         (needs --confirm)
#   ./run_all.sh o5      high-statistics model measurement     (fixed seed)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=1 RATBACKEND="${RATBACKEND:-gmpy2}"
PY="${PY:-python3}"

gates() {
  local fail=0
  # AUDIT_R177 2.9bis: g_manifest runs LAST -- it verifies MANIFEST.json
  # against the tree, so it should see the tree exactly as the other gates
  # left it.
  for g in g_ledger g_fcyc_counts g_totals g_pure_orbits g_p24 g_v52 g_v25 \
           g_vjoints g_o5 g_pred_rat g_seq g_logdet g_bias g_ncc g_tt \
           g_certify84 g_certify91 g_be g_manifest; do
    echo "=== $g"
    "$PY" "$HERE/gates/$g.py" || { fail=1; echo "  ^^ GATE FAILED: $g"; }
  done
  # AUDIT_R164 1.4 / AUDIT_R177 2.7: pre-release self-check -- no
  # user-machine absolute paths anywhere in the shipped SOURCES.
  #
  # Scope was widened twice.  It used to cover only "$HERE"/*.py, which left
  # *.sh, the package-root certification/ and lean/ trees, and the top-level
  # files unscanned -- a hard-coded path in certify91.py or in a shell script
  # would have shipped unnoticed.  It now scans the whole package root.
  #
  # Two deliberate exclusions:
  #   *.log  -- the archived run logs are append-only evidence; they DO contain
  #             the operator's home path in captured tracebacks, and rewriting
  #             them would violate the package's own no-retouch discipline.
  #             Their exposure is a recorded decision, not an oversight.
  #   the pattern itself -- assembled from fragments at run time so that this
  #             script does not match its own source and fail forever.
  local PKG PAT
  PKG="$(cd "$HERE/.." && pwd)"
  PAT="/Us""ers/\|/ho""me/"
  if grep -rn "$PAT" --include="*.py" --include="*.sh" --include="*.lean" \
          --include="*.toml" --include="*.cfg" "$PKG" >/dev/null 2>&1; then
    echo "*** RELEASE SELF-CHECK FAILED: absolute user paths in shipped sources:"
    grep -rn "$PAT" --include="*.py" --include="*.sh" --include="*.lean" \
         --include="*.toml" --include="*.cfg" "$PKG" | head
    fail=1
  fi
  echo; [ $fail -eq 0 ] && echo "ALL GATES GREEN" || echo "*** SOME GATES FAILED ***"
  return $fail
}

light() {   # ascending cost -- the 3bis scheduling lesson: never queue the
            # heaviest class first, its memo tables decide the worker cap
  # AUDIT_R164 1.1: no `set -e` here -- one failing step must not mask
  # the true state of the remaining steps; accumulate and report.
  local lfail=0
  for cmd in \
    "$HERE/engines/t222_exact.py" \
    "$HERE/engines/p24_exact.py"; do
    "$PY" "$cmd" || { lfail=1; echo "  ^^ FAILED: $cmd (continuing)"; }
  done
  "$PY" "$HERE/engines/run_class.py" '{5,2}'   --jobs 8   || { lfail=1; echo "  ^^ FAILED: {5,2}"; }
  "$PY" "$HERE/engines/run_k10.py" '{2^5}'     10 2,2,2,2,2 --jobs 110 || { lfail=1; echo "  ^^ FAILED: {2^5}"; }
  "$PY" "$HERE/engines/run_class.py" '{2,2,4}' --jobs 24  || { lfail=1; echo "  ^^ FAILED: {2,2,4}"; }
  "$PY" "$HERE/engines/run_class.py" '{4,4}'   --jobs 24  || { lfail=1; echo "  ^^ FAILED: {4,4}"; }
  "$PY" "$HERE/engines/run_class.py" '{6,2}'   --jobs 24  || { lfail=1; echo "  ^^ FAILED: {6,2}"; }
  "$PY" "$HERE/engines/run_k10.py" '{4,2,2,2}' 10 4,2,2,2 --jobs 110 || { lfail=1; echo "  ^^ FAILED: {4,2,2,2}"; }
  "$PY" "$HERE/engines/run_k10.py" '{2,2,5}'    9 2,2,5   --jobs 110 || { lfail=1; echo "  ^^ FAILED: {2,2,5}"; }
  # last and non-fatal (AUDIT_R149 2.1): sympy-only slow gate; on
  # hosts without sympy it prints NOT-APPLICABLE and must not kill
  # the eight class recomputes above.
  "$PY" "$HERE/gates/g_span_t222.py" \
    || echo "  ^^ g_span_t222 NOT-APPLICABLE or failed (non-fatal in light)"
  [ $lfail -eq 0 ] && echo "LIGHT: ALL STEPS OK" || echo "*** LIGHT: SOME STEPS FAILED ***"
  return $lfail
}

heavy() {
  cat <<'TAB'
  cost table (measured; core-hours, gmpy2, one 24-64 core node)

    class      F-CYC terms   dihedral orbits   ambient   measured wall
    C_7             9366            685          R^6     3.5 min @ 24 cores
    C_8            94586           6027          R^7      63 min @ 60 cores
    C_9          1091670          60739          R^8      DONE, shipped [1]
    {8,2}          94586/orbit       21          R^9      days      (probe)
    {6,4}          28132/orbit       28         R^11      days      (probe)
    {5,5}          22500/orbit       15         R^10      days      (probe)

  [1] AUDIT_R177 2.9: C_9 is no longer pending -- it is computed and shipped
      (constants/c9, gate g_be BE7).  The row used to read "3-5 DAYS (est.)"
      under a header that says "measured", which is two errors at once.  It is
      NOT replaced by a measured figure here because none was recorded: the run
      was three checkpointed shards across hosts 238/220 (earlier segments on
      230/231) with a declared resume overlap, and no aggregate wall time was
      archived.  Per-shard logs are in logs/.  Lesson for the next frontier
      class: record the aggregate wall time in RUN.md at the time of the run.

  MEMORY, not cores, sets --jobs: memo table ~1.8 GB/worker at C_8 and above.
  120 workers x 1.8 GB on a 251 GB node drove it into 31 GB of swap and returned
  0 orbits in 87 minutes (round 136, incident 3bis).  Size jobs by memo x worker.
TAB
  [ "${2:-}" = "--confirm" ] || { echo; echo "refusing to start a multi-day run without --confirm"; return 1; }
  "$PY" "$HERE/engines/run_pure_rows.py" 7 --jobs 24 --out "$HERE/constants/c7/term_orbits.json"
  "$PY" "$HERE/engines/run_pure_rows.py" 8 --jobs 32 --out "$HERE/constants/c8/term_orbits.json"
}

o5() {      # fixed parameters and seed: N=128, 200000 samples, seed 0
  "$PY" "$HERE/engines/o5_sigma.py" 128 200000 "${JOBS:-8}" 0
}

case "${1:-}" in
  gates) gates ;;  selftest) python3 "$(dirname "$0")/gates/selftest_inject.py" ;;  light) light ;;  heavy) heavy "$@" ;;  o5) o5 ;;
  *) sed -n '2,7p' "$0"; exit 2 ;;
esac
