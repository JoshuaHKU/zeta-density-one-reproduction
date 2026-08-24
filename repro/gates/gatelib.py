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
    """R3 of sec 3: matching fewer items than expected is NOT a pass.
    AUDIT_R164 2.1: a non-positive expectation is NOT a pass either --
    an expectation derived from the same glob as the data vanishes with
    the data, and 0 == 0 must never green-light a gate."""
    if want <= 0:
        print(f"  NOT-APPLICABLE  {name}   expected count is {want} (<=0): "
              f"empty comparison is not a pass")
        _res.append((name, False)); return False
    if got < want:
        print(f"  NOT-APPLICABLE  {name}   matched {got}/{want} {detail}")
        _res.append((name, False)); return False
    return check(name, got == want, f"matched {got}/{want} {detail}")

def finish(title):
    bad = [n for n, ok in _res if not ok]
    print(f"\n{title}: {len(_res)-len(bad)}/{len(_res)} pass"
          + (f"   FAILED: {', '.join(bad)}" if bad else ""))
    sys.exit(1 if bad else 0)


def need(*modules):
    """AUDIT_R164 1.3: third-party dependency guard (pattern lifted from
    g_span_t222).  A gate whose dependencies are absent prints
    NOT-APPLICABLE and exits 3 -- never an unhandled ImportError."""
    import importlib
    missing = []
    for m in modules:
        try:
            importlib.import_module(m)
        except Exception:
            missing.append(m)
    if missing:
        # AUDIT_R177 2.10: the old wording claimed "certification does not
        # need them", which is false for the k=8 chain (certify_k8.py).  Only
        # certify84.py / certify91.py are genuinely stdlib-only.
        print(f"  NOT-APPLICABLE  missing third-party module(s): "
              f"{', '.join(missing)}  (this gate needs them; the exact-rational "
              f"constant gates and certify84.py / certify91.py do not)")
        sys.exit(3)
