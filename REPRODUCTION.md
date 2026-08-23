# Reproduction checklist / 复现清单 (v0.92)

Recorded outputs on the reference host are quoted; every step is
deterministic exact rational arithmetic unless marked (sampling).

## 0. Requirements

Python 3.9+ (stdlib only for certification; sympy optional for the
slow span gate; numpy/scipy only for re-running measurement pools).
Lean 4 toolchain v4.33.0 via elan for `lake build` (no mathlib).

## 1. Certification chain (~10 s)

    python3 certification/certify91.py
    -> ... ALL CHECKS PASS

Covers: corrected pairing bundle; re-centring identities; k=7/8
assembly; Christoffel certificates lambda_3/lambda_4 (k<=8 layer,
dual-method grade); anchors m_9..m_14; binomial interlocks
Sigma_2..Sigma_14; lambda_5/6/7 certificates (PD, Stieltjes shift,
alternation, zero premium, exact headlines, thresholds); monotone
chain n*lambda_n increasing n=1..7.

## 2. Gate suite (seconds)

    cd repro && ./run_all.sh gates
    -> 18 gates ... ALL GATES GREEN

Includes the trace-route gate g_tt (engine validation ladder,
table recomputation, fit consistency, anchors, lambda_5 chain) run
on the MATH-SIDE engine `repro/engines/p3_direct_sum.py` — code-
independent of the compute-side `repro/engines/tt_moments.py`;
their bitwise agreement on overlap tables is gate F-IMPL.

## 2bis. Branch-equality campaign gate (seconds)

    python3 repro/gates/g_be.py
    -> 31 checks ... g_be: ALL GREEN

Re-verifies, from the archived JSON artifacts alone: the counting
identities (Lah 13/73/501/4051/37633 for the TU wall systems,
Fubini 13/75/541/4683 for the fine cluster-term families, both
proved in the paper); the SIGNED fine assembly
sum prod_B (-1)^{|Q_B|-1} T = m_b(N) N^{b+1} bitwise at b=4/5/6
for every archived N including N=1; the Moebius-layer assembly;
per-term parity spot checks T(-N) = (-1)^{b+1} T(N) by exact
Lagrange interpolation; the odd-b surplus fits (extension points
m9(8), m11(9), m13(10) -- each pre-registered as the unique
prediction of the already-determined fit BEFORE computation, all
HIT bitwise; predictions timestamped in
constants/be/m_odd_ext_PREDICTION.json); and the verdict/violation
integrity of every TU/LTU scan file and the independent
second-implementation assembly gate (b<=7 lifted exhaustive;
260,000+ systems in total across all scans, zero violations). See repro/REPRO_V4_FREEZE.md for the full inventory
and the in-flight items recorded at freeze.

## 3. Lean layer

    cd lean && lake build
    -> builds Certificate84, CertificateK1012, CertificateK14
       (18+ theorems, grind on exact rationals, zero sorry)

## 4. Recompute a frontier value (optional, minutes to hours)

    cd repro/engines
    python3 -c "from p3_direct_sum import m_b; print(m_b(9, 7))"
    -> 2803676131/40353607        (the first pre-registered holdout)

Larger points: use tt_moments.py with sharding; costs and worker
caps in the receipts (`repro/RECEIPT_R150_B14.md` §5–6).

## 5. Measurement tiers (sampling; optional)

The A1 pools (N=128/192/256, 10^7 samples each) are archived as
logs with the derived F-MODEL comparison table
(`repro/measurements/o5/a1_sigma_finiteN.md`, 39+6 comparisons, all
within 3 sd). To re-sample: `repro/engines/o5_sigma.py` (fixed
seeds; see run_all.sh o5).

## 6. What upgrades remain (grade closures)

C_9 facet recursion against pre-registered 27649/302400 (running);
F-IMPL-13 (N=4) and F-IMPL-14 (N=3) delegated points; tenth/
twelfth-layer joint classes; the quasi-polynomiality theorem.
Grade tags update in `repro/constants/tt/m_tables.json` as these
land.
