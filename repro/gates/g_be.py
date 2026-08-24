#!/usr/bin/env python3
"""Gate g_be -- branch-equality campaign verification suite (repro v4).

Recomputes, from the archived JSON artifacts alone (no heavy compute):

  BE1  term-count identities: Lah counts a(b) = sum_P prod|B|! for the
       lifted TU scans (13/73/501/4051), Fubini counts for the fine
       sigma-term families (75/541/4683), Stirling-cyclic q(s) layer;
  BE2  signed assembly: sum over the fine family of
       prod_B (-1)^{|Q_B|-1} * T_{P,Q,sigma}(N)  ==  m_b(N) * N^{b+1}
       bitwise, b = 4,5,6, every archived N (including N = 1);
  BE3  Moebius-layer assembly: parity_scan totals == m_b(N) * N^{b+1};
  BE4  per-term parity spot checks T(-N) = (-1)^{b+1} T(N) by exact
       Lagrange interpolation (fine family and Moebius family);
  BE5  odd-b surplus fits: with the extension points of
       m_tables_ext.json, the parity-constrained fit at b = 9/11/13 is
       overdetermined by one point, consistent bitwise, with leading
       coefficient equal to the archived m_b;
  BE6  TU/LTU scan verdicts and the coefficient-assembly gate: all
       archived scan files report PASS with empty violation lists
       (b <= 7 m-space exhaustive, b = 8 two-leg, lifted b <= 7
       exhaustive = 42,271 systems), and the independent
       second-implementation F-BE-COEFF levels are all PASS.

Every check is exact rational arithmetic; wall time is seconds.
"""
import json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
CB = os.path.join(HERE, "..", "constants", "be")
CT = os.path.join(HERE, "..", "constants", "tt")

fails = []
def check(name, ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        fails.append(name)

def parts(xs):
    xs = list(xs)
    if not xs:
        yield []
        return
    f, r = xs[0], xs[1:]
    for p in parts(r):
        for i in range(len(p)):
            yield p[:i] + [[f] + p[i]] + p[i + 1:]
        yield [[f]] + p

def load(fn, base=CB):
    with open(os.path.join(base, fn)) as fh:
        return json.load(fh)

def mbN(b, N, poly):
    return sum(F(c) / F(N ** (2 * p)) for p, c in enumerate(poly[str(b)])) * N ** (b + 1)

def key_sign(key):
    s = 1
    for block in key.split("/"):
        s *= (-1) ** (len(block.split("|")) - 1)
    return s

def lagrange(vals, Ns, x):
    t = F(0)
    for i, vi in zip(Ns, vals):
        term = F(vi)
        for j in Ns:
            if j != i:
                term *= F(x - j, i - j)
        t += term
    return t

M = load("m_tables.json", CT)
POLY = M["poly"]

# ---- BE1: counting identities -------------------------------------------
lah = {b: sum(math.prod(math.factorial(len(B)) for B in P)
              for P in parts(range(b))) for b in range(3, 8)}
check("BE1 Lah counts a(3..7) = 13/73/501/4051/37633",
      [lah[b] for b in range(3, 8)] == [13, 73, 501, 4051, 37633])
q = {s: sum(math.factorial(len(Q) - 1) for Q in parts(range(s))) for s in range(1, 7)}
fub = {b: sum(math.prod(q[len(B)] for B in P) for P in parts(range(b)))
       for b in range(3, 7)}
check("BE1 Fubini fine counts (3..6) = 13/75/541/4683",
      [fub[b] for b in range(3, 7)] == [13, 75, 541, 4683])
for b in (4, 5, 6):
    S = load(f"sigma_scan_b{b}.json")
    check(f"BE1 sigma_scan_b{b} term count == Fubini({b})",
          len(S["T"]) == fub[b] == S["n_fine_terms"])

# ---- BE2: signed fine assembly ------------------------------------------
for b in (4, 5, 6):
    S = load(f"sigma_scan_b{b}.json")
    ok = all(sum(key_sign(k) * int(v[i]) for k, v in S["T"].items())
             == mbN(b, N, POLY) for i, N in enumerate(S["Ns"]))
    check(f"BE2 signed assembly b={b} over {len(S['Ns'])} N-values", ok)

# ---- BE3: Moebius-layer assembly ----------------------------------------
for b in (4, 5, 6):
    P = load(f"parity_scan_b{b}.json")
    ok = all(F(int(t)) == mbN(b, N, POLY) for N, t in zip(P["Ns"], P["total"]))
    check(f"BE3 Moebius assembly b={b} over {len(P['Ns'])} N-values", ok)

# ---- BE4: parity spot checks --------------------------------------------
import random
random.seed(92)
for b in (4, 5, 6):
    sign = (-1) ** (b + 1)
    for fn, label in ((f"sigma_scan_b{b}.json", "fine"),
                      (f"parity_scan_b{b}.json", "moebius")):
        J = load(fn)
        T = J["T"] if "T" in J else J["T_P"]
        keys = random.sample(list(T.keys()), min(4, len(T)))
        ok = all(lagrange([int(x) for x in T[k]], J["Ns"], -n)
                 == sign * lagrange([int(x) for x in T[k]], J["Ns"], n)
                 for k in keys for n in (3, 5))
        check(f"BE4 parity spots b={b} ({label}, 4 terms x 2 points)", ok)

# ---- BE5: odd-b surplus fits --------------------------------------------
EXT = load("m_tables_ext.json", CT)
for b in (9, 11, 13):
    vals = {int(n): F(v) for n, v in M["values"][str(b)].items()}
    vals.update({int(n): F(v) for n, v in EXT["values"][str(b)].items()})
    Ns = sorted(vals)
    degs = list(range(0, b + 2, 2))
    fitN = Ns[:len(degs)]
    n = len(fitN)
    Mx = [[F(N) ** d for d in degs] + [vals[N] * F(N) ** (b + 1)] for N in fitN]
    for i in range(n):
        p = next(r for r in range(i, n) if Mx[r][i] != 0)
        Mx[i], Mx[p] = Mx[p], Mx[i]
        Mx[i] = [x / Mx[i][i] for x in Mx[i]]
        for r in range(n):
            if r != i and Mx[r][i] != 0:
                Mx[r] = [a - Mx[r][i] * c for a, c in zip(Mx[r], Mx[i])]
    coef = [Mx[i][-1] for i in range(n)]
    surplus = all(sum(c * F(N) ** d for c, d in zip(coef, degs))
                  == vals[N] * F(N) ** (b + 1) for N in Ns[len(degs):])
    lead = coef[-1] == F(POLY[str(b)][0])
    check(f"BE5 b={b} surplus-point consistency + leading == m_{b}",
          surplus and lead and len(Ns) == len(degs) + 1)

# ---- BE6: scan verdicts --------------------------------------------------
for fn in (["tu_scan_b%d.json" % b for b in (4, 5, 6, 7, 8)]
           + ["ltu_scan_b%d.json" % b for b in (3, 4, 5, 6, 7)]):
    try:
        J = load(fn)
        ok = (J.get("verdict", "PASS") == "PASS") and not J.get("violations", [])
        check(f"BE6 {fn} verdict PASS, zero violations", ok)
    except FileNotFoundError:
        check(f"BE6 {fn} present", False)

J = load("coeff_assembly.json")
ok = all(lev.get("verdict") == "PASS" for lev in J["levels"].values())
check("BE6 coeff_assembly.json all levels PASS (independent 2nd impl)", ok)


# ---- BE7: C_9 / {7,2} coverage (AUDIT_R164 3.1/3.2) ----------------------
CC = os.path.join(HERE, "..", "constants")
C9 = json.load(open(os.path.join(CC, "c9", "term_orbits.json")))
tot9 = F(0); wsum = 0
for r in C9["orbit_values"].values():
    tot9 += F(r["weight"]) * F(r["value"]); wsum += F(r["weight"])
check("BE7 c9 rebuild: sum(weight*value) over 60,739 orbits == 27649/302400",
      tot9 == F(27649, 302400) and len(C9["orbit_values"]) == 60739)
check("BE7 c9 signed weights sum to zero", wsum == 0)
J72 = json.load(open(os.path.join(CC, "j72", "values.json")))
j72 = sum(F(e["value"]) * e["size"] for e in J72["orbit_values"].values())
check("BE7 j72 rebuild: 9 x orbit sum == -4313/12600",
      j72 == F(-4313, 12600) == F(J72["total"]))
check("BE7 pre-registered identity C_9 + {7,2} == -75863/302400",
      F(27649, 302400) + F(-4313, 12600) == F(-75863, 302400))
TOT = json.load(open(os.path.join(CC, "TOTALS.json")))
check("BE7 TOTALS.json carries c9 and j72",
      TOT.get("c9") == "27649/302400" and TOT.get("j72") == "-4313/12600")
j54 = F(json.load(open(os.path.join(CC, "j54", "values.json")))["total"])
j225 = F(json.load(open(os.path.join(CC, "j225", "values.json")))["total"])
check("BE7 Sigma_9 partition: {5,4}+{2,2,5}+C_9+{7,2} == 52207/302400",
      j54 + j225 + F(27649, 302400) + F(-4313, 12600) == F(52207, 302400))
S7 = load("sigma_scan_b7.json")
check("BE7 sigma_scan_b7 summary: 47,293 == Fubini(7), POLY/PAR2/COVERAGE PASS",
      int(S7["n_fine_terms"]) == 47293 == int(S7["fubini_expected"])
      and S7["F_BE_POLY"] == "PASS" and S7["F_BE_PAR2"] == "PASS"
      and str(S7["COVERAGE_CHECK"]).startswith("PASS"))
nsh = sum(1 for i in range(6)
          if os.path.exists(os.path.join(CB, f"sigma_scan_b7_s{i}of6.json")))
check("BE7 sigma_scan_b7 shard files present 6/6", nsh == 6)

print()
if fails:
    print(f"*** g_be: {len(fails)} FAILURES: {fails}")
    sys.exit(1)
print("g_be: ALL GREEN")
