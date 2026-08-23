#!/usr/bin/env python3
"""F-CYC term counts: sum_m S(b,m)(m-1)! must give 150/1082/9366/94586/... and
must equal what class_integral.fcyc_terms actually enumerates (b <= 7)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "engines"))
from gatelib import check, require_count, finish
from math import factorial

def stirling2(n, k):
    return sum((-1) ** (k - j) * factorial(k) // (factorial(j) * factorial(k - j)) * j ** n
               for j in range(k + 1)) // factorial(k)

WANT = {5: 150, 6: 1082, 7: 9366, 8: 94586, 9: 1091670, 10: 14174522}
from class_integral import fcyc_terms
n = 0
for b, w in WANT.items():
    f = sum(stirling2(b, m) * factorial(m - 1) for m in range(1, b + 1))
    ok = (f == w)
    if b <= 7:
        ok &= (len(fcyc_terms(list(range(b)))) == w)
    n += check(f"F-CYC b={b:<3}", ok,
               f"formula {f}, expected {w}" + ("  (+enumerated)" if b <= 7 else ""))
require_count("F-CYC levels", n, len(WANT))
finish("F-CYC")
