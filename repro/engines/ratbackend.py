"""Rational arithmetic backend.

`Fraction` is pure Python; `gmpy2.mpq` wraps GMP and is typically several times
faster on the operand sizes the facet recursion produces.  Set RATBACKEND=frac
to force the stdlib one (used to check that a speed-up does not change a single
value).
"""
import os
_want = os.environ.get("RATBACKEND", "gmpy2")
BACKEND = "fractions"
if _want != "frac":
    try:
        from gmpy2 import mpq as F           # noqa: F401
        BACKEND = "gmpy2"
    except ImportError:
        from fractions import Fraction as F  # noqa: F401
else:
    from fractions import Fraction as F      # noqa: F401
