#!/usr/bin/env python3
"""F-SEQ-12/14 (r146 N1): blind recomputation of two pre-registered rationals.

The math side registered, via the NCC closed form seq(2m) = 4^-m int_0^1 (1+x^2)^m dx:
    b=12 sequential orbit  01|23|45|67|89|ab     = 523/192192
    b=14 sequential orbit  01|23|45|67|89|ab|cd  = 119/102960
Method independence is the point of the exercise, so this recomputes them with
the FACET RECURSION -- no NCC, no convolution.  All blocks are pairs, so each
orbit is a single F-CYC term carrying one |v| monomial per pair, in R^6 / R^7."""
import os, sys, time
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "engines"))
from gatelib import check, require_count, finish
from ratbackend import F
from class_integral import class_integral

TGT = {12: "523/192192", 14: "119/102960"}
n = 0
for b, want in TGT.items():
    t0 = time.time()
    v = class_integral([[2 * i, 2 * i + 1] for i in range(b // 2)], b, jobs=1)
    n += check(f"F-SEQ-{b}", str(Q(v)) == want,
               f"facet recursion {v} vs registered {want}  "
               f"(R^{b//2}, {time.time()-t0:.1f}s)")
require_count("F-SEQ levels", n, len(TGT))
finish("F-SEQ")
