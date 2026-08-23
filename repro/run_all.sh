#!/usr/bin/env bash
# REPRO_SPEC r139 sec 5 -- layered reproduction driver.
#   ./run_all.sh gates   all gate scripts + certify84          (<= 2 min)
#   ./run_all.sh light   full recompute of the light classes   (<= 1 day, 1 node)
#   ./run_all.sh heavy   C_7/C_8/C_9/{8,2}/{6,4}/{5,5}         (needs --confirm)
#   ./run_all.sh o5      high-statistics model measurement     (fixed seed)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=1 RATBACKEND="${RATBACKEND:-gmpy2}"
PY="${PY:-python3}"

gates() {
  local fail=0
  for g in g_ledger g_fcyc_counts g_totals g_pure_orbits g_p24 g_v52 g_v25 \
           g_vjoints g_o5 g_pred_rat g_seq g_logdet g_bias g_ncc g_tt \
           g_certify84 g_certify91 g_be; do
    echo "=== $g"
    "$PY" "$HERE/gates/$g.py" || { fail=1; echo "  ^^ GATE FAILED: $g"; }
  done
  echo; [ $fail -eq 0 ] && echo "ALL GATES GREEN" || echo "*** SOME GATES FAILED ***"
  return $fail
}

light() {   # ascending cost -- the 3bis scheduling lesson: never queue the
            # heaviest class first, its memo tables decide the worker cap
  set -e
  "$PY" "$HERE/engines/t222_exact.py"
  "$PY" "$HERE/engines/p24_exact.py"
  "$PY" "$HERE/engines/run_class.py" '{5,2}'   --jobs 8
  "$PY" "$HERE/engines/run_k10.py" '{2^5}'     10 2,2,2,2,2 --jobs 110
  "$PY" "$HERE/engines/run_class.py" '{2,2,4}' --jobs 24
  "$PY" "$HERE/engines/run_class.py" '{4,4}'   --jobs 24
  "$PY" "$HERE/engines/run_class.py" '{6,2}'   --jobs 24
  "$PY" "$HERE/engines/run_k10.py" '{4,2,2,2}' 10 4,2,2,2 --jobs 110
  "$PY" "$HERE/engines/run_k10.py" '{2,2,5}'    9 2,2,5   --jobs 110
  # last and non-fatal (AUDIT_R149 2.1): sympy-only slow gate; on
  # hosts without sympy it prints NOT-APPLICABLE and must not kill
  # the eight class recomputes above.
  "$PY" "$HERE/gates/g_span_t222.py" \
    || echo "  ^^ g_span_t222 NOT-APPLICABLE or failed (non-fatal in light)"
}

heavy() {
  cat <<'TAB'
  cost table (measured; core-hours, gmpy2, one 24-64 core node)

    class      F-CYC terms   dihedral orbits   ambient   measured wall
    C_7             9366            685          R^6     3.5 min @ 24 cores
    C_8            94586           6027          R^7      63 min @ 60 cores
    C_9          1091670          60648          R^8      3-5 DAYS  (est.)
    {8,2}          94586/orbit       21          R^9      days      (probe)
    {6,4}          28132/orbit       28         R^11      days      (probe)
    {5,5}          22500/orbit       15         R^10      days      (probe)

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
  gates) gates ;;  light) light ;;  heavy) heavy "$@" ;;  o5) o5 ;;
  *) sed -n '2,7p' "$0"; exit 2 ;;
esac
