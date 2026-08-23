#!/usr/bin/env python3
"""Assemble Sigma_8 from the five level-8 classes, then m_7/m_8 and the k=8
certificate.  Usage: python3 assemble_sigma8.py  C8_as_fraction"""
import sys, os, json
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "certification"))
import certify_k8 as C

CLASSES = {"{2^4}": F(1661, 3780), "{2,2,4}": F(-127, 840),
           "{6,2}": F(-563, 11340), "{4,4}": F(23, 4536)}
SIGMA7 = F(1, 8) + F(-17, 360)          # {5,2} + C7  = 7/90
R7, R8 = F(685, 36), F(217, 6)          # re-centring rational parts

if __name__ == "__main__":
    C8 = F(sys.argv[1])
    print("level-8 classes")
    for k, v in CLASSES.items():
        print(f"   {k:<9} = {str(v):<14} = {float(v):+.10f}")
    print(f"   {'C_8':<9} = {str(C8):<14} = {float(C8):+.10f}")
    S8 = sum(CLASSES.values()) + C8
    print(f"   {'':<9}   {'-'*14}")
    print(f"   Sigma_8   = {S8} = {float(S8):.10f}   (model 0.282490)")
    print(f"   Sigma_7   = {SIGMA7} = {float(SIGMA7):.10f}   (model 0.077722)")
    m7 = R7 + SIGMA7
    m8 = R8 + 8 * SIGMA7 + S8
    print(f"\n   m7 = 685/36 + Sigma_7          = {m7} = {float(m7):.10f}")
    print(f"   m8 = 217/6 + 8 Sigma_7 + Sigma_8 = {m8} = {float(m8):.10f}")
    print(f"\n   F-SIGMA7  Sigma_7 >= 0.074844 : "
          f"{'PASS' if float(SIGMA7) >= 0.074844 else 'FAIL'}")
    print(f"   F-SIGMA8  Sigma_8 <= 0.290506 : "
          f"{'PASS' if float(S8) <= 0.290506 else 'FAIL'}"
          f"   (margin {0.290506-float(S8):+.6f})")
    print("\nk=8 certificate at the now-exact (M7, M8)")
    mom = dict(C.M); mom[7] = m7; mom[8] = m8
    if not C.psd(C.hankel(mom, 4)):
        print("   *** (m7,m8) outside the moment cone over m1..m6"); raise SystemExit(1)
    lam = C.christoffel(mom, 4)
    print(f"   lambda_4 = {lam} = {float(lam):.10f}")
    print(f"   N0s/N >= {1-2*lam} = {float(1-2*lam):.8f}")
    print(f"   Nd /N >= {1-lam} = {float(1-lam):.8f}")
    b = C.build(m7, m8, verbose=False)
    print(f"   rationalised certificate: w0 = {float(b['w0']):.10f}"
          f"  (cost {float(b['w0']-b['lam']):.2e})")
    print(f"   delivered  N0s/N >= {float(1-2*b['w0']):.8f}"
          f"   Nd/N >= {float(1-b['w0']):.8f}")
    json.dump({"classes": {k: str(v) for k, v in CLASSES.items()}, "C8": str(C8),
               "Sigma_8": str(S8), "Sigma_7": str(SIGMA7), "m7": str(m7), "m8": str(m8),
               "lambda_4": str(lam), "headline": str(1-2*lam), "distinct": str(1-lam)},
              open(os.path.join(HERE, "sigma8_assembly.json"), "w"), indent=1)
