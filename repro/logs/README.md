# logs/ -- append-only

Raw run logs and round logs, archived verbatim.  Nothing here is edited after
the fact; corrections are recorded as later entries, not as edits.

Header convention: `r<round>_<host>_<what>`.

| file | round | host | what |
|---|---|---|---|
| `r131_phase0_log.md` | 131 | local | {2,2,2} ledger error found and fixed; the two independent exact methods |
| `r131_phase1_log.md` | 131 | 230 | {5,2} exact, F-SIGMA7 |
| `r131_phase2_log.md` | 131 | local | full ledger enumeration audit; the "orbit size divides 2b" invariant that caught the under-count; {2^4} exact |
| `r132_facet_recursion_log.md` | 132 | local | the facet-recursion integrator; five bugs and how each was caught |
| `r133_230_run_52.log` | 133 | 230 | {5,2} three orbits, raw |
| `r136_230_ladder_224.log` | 136 | 230 | CPU ladder checkpoint for {2,2,4} |
| `r136-137-138_compute_log.md` | 136-138 | all | the compute campaign: the {6,4} scheduling incident (3bis), the pkill self-match, the 2ter index-matching false FAIL, the 2quater decision to stop D and attack Sigma_9, O5 and the k=10 pricing |
| `r138_238_o5.log` | 138 | 238 | O5 high-statistics run, 200k samples, 152 s on 60 jobs |
| `r139_230_c7_term_orbits.log` | 139 | 230 | C_7 per-term-orbit recovery for this repro package |
| `r139_220_c8_term_orbits.log` | 139 | 220 | C_8 per-term-orbit recovery for this repro package |

## The five incidents REPRO_SPEC sec 6 requires to be preserved

All five are narrated in `r136-137-138_compute_log.md`; pointers:

1. **{6,4} scheduling incident** -- queued the heaviest class first with 120
   workers; 120 x 1.8 GB memo on a 251 GB node -> 31 GB swap, all workers
   blocked, 87 min for 0 orbits.  Fix: ascending-cost ordering and per-class
   job caps sized by memo x worker.  (Registry D22.)
2. **`pkill -f <pattern>` self-match** -- the pattern matched the ssh command
   line carrying it, killing the session six times.  Fix: `pkill -f "[p]attern"`.
3. **230 losing 20 cores** -- and the separate misread where 230 looked
   memory-exhausted; it was 28/188 GB used with 158 available, the rest
   buff/cache.
4. **The 2ter comparison error** -- ladder vs exact matched by orbit INDEX;
   the two toolchains order orbits differently AND pick different
   representatives, so two of three classes falsely FAILed.  Fix: match on the
   dihedral canonical form.  This is the origin of REPRO_SPEC R1.
   A second bug in the same reporter turned 0 matches into `worst = 0.0` and
   hence a spurious PASS; that is the origin of the NOT-APPLICABLE rule.
5. **Stopping D** -- the 94586-term brute-force recheck of C_8 was abandoned
   mid-flight in favour of Sigma_9 work.  It has no checkpoint; restarting it
   costs ~14 h from zero.  Recorded as a decision, not as a completed check:
   C_8's `second_path` says `model-side-ABC`, not "independently re-derived".
