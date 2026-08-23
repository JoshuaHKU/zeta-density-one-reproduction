"""Shared helpers for the F-gates.  REPRO_SPEC r139 sec 3:
a gate exits 0 iff it passes; a gate whose comparison set is SHORTER than
expected prints NOT-APPLICABLE and exits non-zero (empty-comparison false
PASS was a real bug -- 2ter)."""
import json, os, sys
from fractions import Fraction as Q

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONST = os.path.join(ROOT, "constants")
_res = []

def canon_key(blocks, n):
    o = set()
    bl = [tuple(sorted(b)) for b in blocks]
    for r in range(n):
        for f in (lambda x, r=r: x + r, lambda x, r=r: r - x):
            o.add(tuple(sorted(tuple(sorted(f(x) % n for x in b)) for b in bl)))
    return "|".join("".join(str(x) for x in b) for b in sorted(o)[0])

def load(cls):
    return json.load(open(os.path.join(CONST, cls, "values.json")))

def check(name, ok, detail=""):
    _res.append((name, bool(ok)))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    return bool(ok)

def require_count(name, got, want, detail=""):
    """R3 of sec 3: matching fewer items than expected is NOT a pass."""
    if got < want:
        print(f"  NOT-APPLICABLE  {name}   matched {got}/{want} {detail}")
        _res.append((name, False)); return False
    return check(name, got == want, f"matched {got}/{want} {detail}")

def finish(title):
    bad = [n for n, ok in _res if not ok]
    print(f"\n{title}: {len(_res)-len(bad)}/{len(_res)} pass"
          + (f"   FAILED: {', '.join(bad)}" if bad else ""))
    sys.exit(1 if bad else 0)
