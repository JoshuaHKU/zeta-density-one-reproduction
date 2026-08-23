# -*- coding: utf-8 -*-
"""Slow gate F-SPAN: elementary closed forms for all five b=6 classes.

span 分解门（慢门，约 2--4 分钟，属 light 层，不在快门列表中）。

Derives, by the span decomposition of r146 (paper sec conv (v),
"companion span decomposition"), every b=6 dihedral pairing class as
an explicit iterated polynomial integral (sympy, exact):

    T0 = 3/70    T0' = 17/420    T1 = 1/90    T2 = 1/180    T3 = 1/70
    bundle 2*T0 + 3*T0' + 6*T1 + 3*T2 + T3 = 32/105   (the D19 value)

Method: class value = int prod|x_j| (1 - span(prefix positions))_+
over R^3; per orthant the span reduces to an explicit piecewise-
linear form (documented inline), each piece a Dirichlet-type
polytope integral.  This is the third independent path to
Prop. p:t222 (after facet recursion and the 1310-term symbolic
verification); the trace route added a fourth at the m_6 level.

Runtime note: sympy integration dominates; keep out of the <=2 min
fast-gate layer (REPRO_SPEC sec 5), run via ./run_all.sh light or
directly.  Exit 0 iff all six identities hold exactly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gatelib import check, finish                     # noqa: E402

# Dependency guard (AUDIT_R149 sec 2.1): sympy is the only
# third-party dependency in the whole light layer; on hosts without
# it (e.g. 220, facet-chain only) this gate must self-report and
# step aside rather than kill the layer.  NOT-APPLICABLE exits
# non-zero per REPRO_SPEC sec 3; the light() driver treats this
# gate as non-fatal.
try:
    import sympy as sp
    from sympy import Rational as R, integrate as I
except ImportError:
    print("  NOT-APPLICABLE  F-SPAN needs sympy (absent on this "
          "host); the six checks were last verified on a "
          "sympy-equipped host -- see AUDIT_R149 sec 4.1")
    sys.exit(3)

u, v, w, t, x = sp.symbols('u v w t x', positive=True)


def dirich(*a):
    """Dirichlet integral over the simplex, exact."""
    return sp.prod([sp.gamma(k) for k in a]) / sp.gamma(sum(a))


# ---- T0, positions {0,u,v,w} --------------------------------------
# +++ : span = max(u,v,w);  ++- : span = max(u,v) + s.
A1 = 3 * I(u * (1 - u) * (u ** 2 / 2) ** 2, (u, 0, 1))
A2 = 2 * I(u * (u ** 2 / 2) * (1 - u) ** 3 / 6, (u, 0, 1))
T0 = 2 * (A1 + 3 * A2)

# ---- T0', positions {0,u,v,v+w}  (diagram (0,1)(2,5)(3,4)) --------
# +++ : span = max(u, v+w);  ++- : span = max(u,v) + (s-v)_+ ;
# +-+ : span = t + max(u, w-t);  -++ : span = r+v+w.
B1 = I(u ** 5 * (1 - u) / 24, (u, 0, 1)) + I(x ** 5 * (1 - x) / 12,
                                             (x, 0, 1))
Ia = I(v * (v ** 2 / 2) * (1 - v) * I(u, (u, 0, v)), (v, 0, 1)) \
    + I(u * (1 - u) * I(v * (v ** 2 / 2), (v, 0, u)), (u, 0, 1))
Ib = I(v * (v ** 2 / 2) * (v * (1 - v) ** 2 / 2 + (1 - v) ** 3 / 6),
       (v, 0, 1)) \
    + I(u * I(v * (v * (1 - u) ** 2 / 2 + (1 - u) ** 3 / 6), (v, 0, u)),
        (u, 0, 1))
b3a = I(I(u * t ** 3 / 2 * (1 - u - t), (u, 0, 1 - t)), (t, 0, 1))
b3b1 = I(I(u * t * (t * u + u ** 2 / 2) * (1 - t - u), (u, 0, 1 - t)),
         (t, 0, 1))
b3b2 = I(I(u * t * I((t + x) * (1 - t - x), (x, u, 1 - t)),
           (u, 0, 1 - t)), (t, 0, 1))
B4 = dirich(2, 2, 2, 2)
T0p = 2 * (B1 + (Ia + Ib) + (b3a + b3b1 + b3b2) + B4)

# ---- T1, positions {0,u,v,v+w,w} ----------------------------------
# +++ shares B1's integrand; two mixed orthants are A2-type; -++ is
# the Dirichlet simplex.
T1 = 2 * (B1 + 2 * A2 + B4)

# ---- T2, positions {0,u,u+v,v,v+w,w} ------------------------------
# +++ : span = v + max(u,w) -> u^3 v (1-u-v);  +-+ : A2-type;
# ++- = -++ : Dirichlet.
T2 = 2 * (dirich(4, 2, 2) + A2 + 2 * B4)

# ---- T3, positions {0,u,u+v,u+v+w,v+w,w} --------------------------
# +++/++-/-++ : span = full sum (Dirichlet);  +-+ on u>=w (x2):
# span = u + |w - t|.
Ea1 = 2 * I(I(u * w * I(t * (1 - u - w + t), (t, 0, w)),
              (w, 0, sp.Min(u, 1 - u))), (u, 0, 1))
Ea2 = 2 * I(I(u * w * I(t * (1 - u - w + t), (t, u + w - 1, w)),
              (w, 1 - u, u)), (u, R(1, 2), 1))
Eb = 2 * I(I(u * w * (w * (1 - u) ** 2 / 2 + (1 - u) ** 3 / 6),
             (w, 0, u)), (u, 0, 1))
T3 = 2 * (3 * dirich(2, 2, 2, 2) + (Ea1 + Ea2 + Eb))

for name, val, want in [("T0", T0, R(3, 70)), ("T0'", T0p, R(17, 420)),
                        ("T1", T1, R(1, 90)), ("T2", T2, R(1, 180)),
                        ("T3", T3, R(1, 70))]:
    check(f"{name} = {want} (elementary closed form)",
          sp.simplify(sp.nsimplify(val) - want) == 0)
bundle = sp.simplify(2 * T0 + 3 * T0p + 6 * T1 + 3 * T2 + T3)
check("bundle = 32/105 (D19 corrected, third path)",
      sp.simplify(bundle - R(32, 105)) == 0)

finish("F-SPAN (b=6 elementary closed forms)")
