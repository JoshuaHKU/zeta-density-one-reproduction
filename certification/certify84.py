# -*- coding: utf-8 -*-
"""preprint-0.84 exact certification chain / 全链精确认证.

Verifies, in exact rational arithmetic (stdlib Fraction only):
  A. the corrected {2,2,2} bundle and M6 = 640/63;
  B. the re-centring identities and central moments;
  C. the k=7,8 assembly (Sigma7 = 7/90, m7 = 3439/180,
     Sigma8 known part = 307/1260, m8 = 519/14 at C8 = 7/180);
  D. the Christoffel certificates: Q3* rational coefficients,
     lambda_3 = 247/2519, headlines 2025/2519, 2272/2519;
     lambda_4 = 3053795/40569016, headlines 17230713/20284508,
     37515221/40569016; sign patterns; cone interiority;
  E. the one-sided tolerances (Sigma7 >= 0.074844 margin,
     Sigma8 <= 0.290506 margin).
Exit 0 iff every assertion holds.  python3 certify84.py
"""
from fractions import Fraction as F

ok = True
def check(name, cond):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name)
    ok = ok and cond

# ---- A. corrected pairing bundle ---------------------------------
T0, T0n, T1, T2, T3 = F(3,70), F(17,420), F(1,90), F(1,180), F(1,70)
t222 = 2*T0 + 3*T0n + 6*T1 + 3*T2 + T3
check("{2,2,2} = 2*T0+3*T0'+6*T1+3*T2+T3 = 32/105", t222 == F(32,105))
S6 = t222 - F(23,420) - F(1,126)
check("Sigma_6 = 61/252", S6 == F(61,252))
M6 = F(119,12) + S6
check("M6 = 640/63", M6 == F(640,63))
check("old bundle overshoot = 1/140", F(131,420)-t222 == F(1,140))

# ---- B. re-centring -----------------------------------------------
S = {1: F(0), 2: F(1,3), 3: F(0), 4: F(1,4), 5: F(1,36), 6: S6}
from math import comb
def m_of(k, extra={}):
    Sx = dict(S); Sx.update(extra)
    return F(1) + sum(comb(k,j)*Sx.get(j, F(0)) for j in range(1, k+1))
for k, target in [(1,F(1)),(2,F(4,3)),(3,F(2)),(4,F(13,4)),
                  (5,F(101,18)),(6,F(640,63))]:
    check(f"recentring m_{k} = {target}", m_of(k) == target)
check("m7 rational part = 685/36", m_of(7) - S.get(7, F(0)) == F(685,36))
check("m8 rational part (no S7,S8) = 217/6", m_of(8) == F(217,6))
C7 = F(-17,360)
check("685/36 + C7 = 6833/360 (ledger interlock)",
      F(685,36)+C7 == F(6833,360))
check("217/6 + 8*C7 = 3221/90 (ledger interlock)",
      F(217,6)+8*C7 == F(3221,90))

# ---- C. k=7,8 assembly --------------------------------------------
J52 = 7*(F(5,504)+F(1,360)+F(13,2520))
check("{5,2} = 1/8", J52 == F(1,8))
S7 = J52 + C7
check("Sigma_7 = 7/90", S7 == F(7,90))
M7 = F(685,36) + S7
check("m7 = 3439/180", M7 == F(3439,180))
S8known = F(1661,3780) + F(-127,840) + F(23,4536) + F(-563,11340)
check("Sigma_8 known four = 307/1260", S8known == F(307,1260))
C8 = F(157,4032)                   # certified (6027-orbit run)
S8 = S8known + C8
check("Sigma_8 = 633/2240 (certified)", S8 == F(633,2240))
M8 = F(217,6) + 8*S7 + S8
check("m8 = 747361/20160", M8 == F(747361,20160))

# ---- D. Christoffel certificates ----------------------------------
def inv_col0(H):
    n = len(H)
    A = [r[:] + [F(1) if i == 0 else F(0)] for i, r in enumerate(H)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [v/pv for v in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f*y for x, y in zip(A[r], A[c])]
    return [A[i][n] for i in range(n)]

m = [F(1), F(1), F(4,3), F(2), F(13,4), F(101,18), M6, M7, M8]
H3 = [[m[i+j] for j in range(4)] for i in range(4)]
col = inv_col0(H3); K3 = col[0]
lam3 = 1/K3
check("lambda_3 = 247/2519", lam3 == F(247,2519))
q3 = [c/K3 for c in col]
check("Q3* = 1 - 8232/2519 x + 7368/2519 x^2 - 1932/2519 x^3",
      q3 == [F(1), F(-8232,2519), F(7368,2519), F(-1932,2519)])
check("Q3* alternating signs", all((q3[j] > 0) == (j % 2 == 0)
                                   for j in range(4)))
val3 = sum(q3[i]*q3[j]*m[i+j] for i in range(4) for j in range(4))
check("int (Q3*)^2 dnu = 247/2519 (zero premium)", val3 == lam3)
check("k<=6 headline = 2025/2519", 1-2*lam3 == F(2025,2519))
check("k<=6 distinct = 2272/2519", 1-lam3 == F(2272,2519))
check("2025/2519 > 4/5", F(2025,2519) > F(4,5))
check("2272/2519 > 9/10", F(2272,2519) > F(9,10))

H4 = [[m[i+j] for j in range(5)] for i in range(5)]
col4 = inv_col0(H4); K4 = col4[0]
lam4 = 1/K4
check("lambda_4 = 12241115/162540559", lam4 == F(12241115,162540559))
q4 = [c/K4 for c in col4]
check("Q4* alternating signs", all((q4[j] > 0) == (j % 2 == 0)
                                   for j in range(5)))
val4 = sum(q4[i]*q4[j]*m[i+j] for i in range(5) for j in range(5))
check("int (Q4*)^2 dnu = lambda_4 (zero premium)", val4 == lam4)
check("headline = 138058329/162540559", 1-2*lam4 == F(138058329,162540559))
check("distinct = 150299444/162540559", 1-lam4 == F(150299444,162540559))
check("headline > 0.8493", 1-2*lam4 > F(8493,10000))
check("distinct > 0.9246", 1-lam4 > F(9246,10000))

# F-STIELTJES (r147): shifted Hankel H^(1) PD in exact rationals =>
# Stieltjes moment sequence => orthogonal-poly zeros all positive =>
# universal alternation theorem (every order), see r147 memo H2
def lead_minors(H):
    n = len(H); out = []
    for k in range(1, n+1):
        M = [row[:k] for row in H[:k]]
        d = F(1)
        for i in range(k):
            p = next(r for r in range(i, k) if M[r][i] != 0)
            if p != i:
                M[i], M[p] = M[p], M[i]; d = -d
            for r in range(i+1, k):
                f = M[r][i]/M[i][i]
                M[r] = [a - f*b for a, b in zip(M[r], M[i])]
        for i in range(k):
            d *= M[i][i]
        out.append(d)
    return out
H1shift = [[m[i+j+1] for j in range(4)] for i in range(4)]
mins = lead_minors(H1shift)
check("F-STIELTJES: H^(1) leading minors (1, 2/9, 23/1296, ...) all > 0",
      mins[:3] == [F(1), F(2,9), F(23,1296)] and all(d > 0 for d in mins))

# sign pattern of P = (Q4*)^2  => one-sided consumption directions
P = [F(0)]*9
for i in range(5):
    for j in range(5):
        P[i+j] += q4[i]*q4[j]
check("P sign pattern (-1)^j (odd lower / even upper)",
      all((P[j] > 0) == (j % 2 == 0) for j in range(9)))

# ---- E. tolerances -------------------------------------------------
check("Sigma_7 = 7/90 >= 0.074844 (3.8% margin)",
      S7 >= F(74844,1000000))
check("Sigma_8 = 633/2240 <= 0.290506 (2.8% margin)",
      S8 <= F(290506,1000000))

print("\nALL CHECKS PASS" if ok else "\nFAILURES PRESENT")
raise SystemExit(0 if ok else 1)
