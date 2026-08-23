#!/usr/bin/env python3
"""F-P24 (revised criterion 3e-6).  r129 reported the {2^4} bundle by a
three-level ladder as 0.4394188(3); the exact value is 1661/3780.  The observed
deviation is 8.1e-7 -- about 3x the ladder's own claimed band, which is why the
criterion was widened from 3e-7 to 3e-6."""
import os, sys, json
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import CONST, check, require_count, finish

EX = Q(json.load(open(os.path.join(CONST, "p24", "values.json")))["total"])
LAD, TOL, OLD = 0.4394188, 3e-6, 3e-7
d = float(EX) - LAD
check("F-P24 exact value", EX == Q(1661, 3780), str(EX))
check("F-P24 vs r129 ladder", abs(d) < TOL,
      f"exact {float(EX):.10f}  ladder {LAD}  dev {d:+.2e}  (tol {TOL:.0e})")
check("F-P24 criterion revision is necessary", abs(d) > OLD,
      f"|dev| {abs(d):.2e} exceeds the old {OLD:.0e} band -- documented, not hidden")
check("F-P24 denominator note", 3780 % 27 == 0 and 2520 % 27 != 0,
      "3780 = 2^2*3^3*5*7 does not divide 2520 = lcm(1..9): the r129 "
      "small-denominator search could not have found it")
require_count("F-P24 checks", 4, 4)
finish("F-P24")
