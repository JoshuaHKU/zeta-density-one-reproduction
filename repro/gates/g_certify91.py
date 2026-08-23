# -*- coding: utf-8 -*-
"""Gate F-CERT91: run the v0.91 certification chain end to end.

Wraps certification/certify91.py (the k<=14 tower: anchors,
binomial interlocks, lambda_5/6/7 certificate chains, monotone
pricing chain).  Exit code follows the wrapped script.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(HERE, os.pardir, "certification", "certify91.py")
r = subprocess.run([sys.executable, script], capture_output=True, text=True)
tail = r.stdout.strip().splitlines()
for line in tail[-4:]:
    print("  " + line)
print(f"\nF-CERT91: {'PASS' if r.returncode == 0 else 'FAIL'}")
sys.exit(r.returncode)
