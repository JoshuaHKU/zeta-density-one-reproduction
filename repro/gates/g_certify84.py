#!/usr/bin/env python3
"""Full-chain certificate gate.  Feeds the certifier the two moments that the
exact constants now pin -- m7 = 3439/180 and m8 = 747361/20160 (from
Sigma_7 = 7/90 and Sigma_8 = 633/2240) -- and requires the exact rational
headline of the paper, plus the two structural side conditions (moment cone
admissible / H_4 PD, and the sign lemma) without which the consumption step is
not one-sided.  Also re-runs the unconditional k<=6 corner."""
import os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, require_count, finish

CERT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "certification", "certify_k8.py")
WANT_H = "4483782896209867992189972451657/5278903382744981072330819894343"
WANT_D = "4881343139477424532260396173000/5278903382744981072330819894343"

out = subprocess.run([sys.executable, CERT, "3439/180", "747361/20160"],
                     capture_output=True, text=True).stdout

def grab(pat):
    m = re.search(pat, out)
    return m.group(1) if m else None

n = 0
n += check("moment cone admissible", "(M7,M8) admissible" in out and "H_4 positive definite" in out)
n += check("sign lemma", "sign lemma satisfied  : True" in out,
           "y_even>0>y_odd -- one-sided consumption")
lam = grab(r"lambda_4\(0\) = (\S+)")
n += check("Christoffel optimum", lam == "12241115/162540559", "lambda_4(0) = " + str(lam))
cost = float(grab(r"rationalisation cost ([0-9.e-]+)") or 1)
n += check("rationalisation cost small", cost < 1e-8, f"{cost:.2e}")
n += check("headline 0.84937772", grab(r"N0s/N >= 1-2w0\s+= (\S+)") == WANT_H,
           str(grab(r"N0s/N >= 1-2w0\s+= \S+\s+= (\S+)")))
n += check("distinct 0.92468886", grab(r"Nd /N >= 1- w0\s+= (\S+)") == WANT_D,
           str(grab(r"Nd /N >= 1- w0\s+= \S+\s+= (\S+)")))
require_count("certificate chain", n, 6)

t = subprocess.run([sys.executable, CERT, "--table"], capture_output=True, text=True).stdout
check("unconditional k<=6 corner present", "2025/2519" in t or "0.80389" in t,
      "2025/2519 = 0.8038904327 / 2272/2519 = 0.9019452164")
finish("F-CERT84")
