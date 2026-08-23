# -*- coding: utf-8 -*-
"""preprint-0.91 exact certification chain / v0.91 全链精确认证.

Extends certify84 (k<=8, imported checks re-run) with the
Toeplitz-trace rungs: re-centring anchors m_9..m_14, Sigma_9..14
extraction, and the full lambda_5/6/7 certificate chains
(PD, Stieltjes shift, alternation, zero premium, headlines).
Exit 0 iff every assertion holds.   python3 certify91.py
"""
from fractions import Fraction as F

ok = True
def check(name, cond):
    global ok
    print(("[PASS] " if cond else "[FAIL] ") + name)
    ok = ok and cond

# ---- tower m_0..m_14 (limits; grades per paper sec s:tt) ----------
m = [F(1), F(1), F(4,3), F(2), F(13,4), F(101,18), F(640,63),
     F(3439,180), F(747361,20160), F(11166011,151200),
     F(83443081,554400), F(852071287,2721600),
     F(1033020076559,1556755200), F(240004263497,167650560),
     F(85585542088667,27243216000)]

S = {2:F(1,3),3:F(0),4:F(1,4),5:F(1,36),6:F(61,252),7:F(7,90),
     8:F(633,2240),9:F(52207,302400),10:F(1333891,3326400),
     11:F(128291,340200),12:F(1092211019,1556755200),
     13:F(45789263,52390800),14:F(27183066233,18162144000)}

# re-centring anchors (pre-registered forms)
check("m9  = 495107/6720 + S9",  m[9]  == F(495107,6720)+S[9])
check("m10 = 199427/1344 + 10 S9 + S10",
      m[10] == F(199427,1344)+10*S[9]+S[10])
check("m11 = 94560551/302400 + S11", m[11] == F(94560551,302400)+S[11])
check("m12 = 199083751/302400 + 12 S11 + S12",
      m[12] == F(199083751,302400)+12*S[11]+S[12])
check("m13 = 11694191/8400 + 78 S11 + 13 S12 + S13",
      m[13] == F(11694191,8400)+78*S[11]+13*S[12]+S[13])
check("m14 = 1264331/432 + 364 S11 + 91 S12 + 14 S13 + S14",
      m[14] == F(1264331,432)+364*S[11]+91*S[12]+14*S[13]+S[14])

# binomial assembly interlock for every Sigma_j
from math import comb
check("Sigma_j binomial assembly j=2..14",
      all(sum(comb(j,i)*(-1)**(j-i)*m[i] for i in range(j+1)) == S[j]
          for j in range(2, 15)))

# ---- certificates -------------------------------------------------
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

def minors_pos(H):
    n = len(H)
    for k in range(1, n+1):
        M = [row[:k] for row in H[:k]]; det = F(1)
        for i in range(k):
            p = next(r for r in range(i, k) if M[r][i] != 0)
            if p != i:
                M[i], M[p] = M[p], M[i]; det = -det
            for r in range(i+1, k):
                f = M[r][i]/M[i][i]
                M[r] = [a-f*b for a, b in zip(M[r], M[i])]
        for i in range(k):
            det *= M[i][i]
        if det <= 0:
            return False
    return True

targets = {
 5: (F(46970100247159,764967228211380),
     F(335513513858531,382483614105690),
     F(717997127964221,764967228211380), F(8771,10000), F(9385,10000)),
 6: (F(13166900320841109317259245,254195527518153210548497708),
     F(113930863438235495956989609,127097763759076605274248854),
     F(241028627197312101231238463,254195527518153210548497708),
     F(8964,10000), F(9482,10000)),
 7: (F(352633869846878511557783511830740995191,
       7876602339133293193971616991853147607579),
     F(7171334599439536170856049968191665617197,
       7876602339133293193971616991853147607579),
     F(7523968469286414682413833480022406612388,
       7876602339133293193971616991853147607579),
     F(9104,10000), F(9552,10000)),
}
for n, (lt, ht, dt, hb, db) in targets.items():
    H = [[m[i+j] for j in range(n+1)] for i in range(n+1)]
    col = inv_col0(H); lam = 1/col[0]
    q = [c/col[0] for c in col]
    val = sum(q[i]*q[j]*m[i+j] for i in range(n+1) for j in range(n+1))
    check(f"lambda_{n} exact value", lam == lt)
    check(f"lambda_{n} zero premium", val == lam)
    check(f"Q{n}* alternating", all((q[j]>0)==(j%2==0) for j in range(n+1)))
    check(f"H{n} PD + shifted PD (Stieltjes)",
          minors_pos(H) and minors_pos(
              [[m[i+j+1] for j in range(n)] for i in range(n)]))
    check(f"k={2*n} headline = 1-2*lambda", 1-2*lam == ht)
    check(f"k={2*n} distinct = 1-lambda", 1-lam == dt)
    check(f"k={2*n} beats {hb}/{db}", 1-2*lam > hb and 1-lam > db)

# monotone chain n*lambda_n increasing 1..7
lams = {}
for n in range(1, 8):
    H = [[m[i+j] for j in range(n+1)] for i in range(n+1)]
    lams[n] = 1/inv_col0(H)[0]
check("n*lambda_n strictly increasing n=1..7",
      all(n*lams[n] > (n-1)*lams[n-1] for n in range(2, 8)))

print("\nALL CHECKS PASS" if ok else "\nFAILURES PRESENT")
raise SystemExit(0 if ok else 1)
