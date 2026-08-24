#!/usr/bin/env python3
"""
The k=8 consumption step, in exact rational arithmetic.

Inputs consumed (paper k8 sec 3):
    m1 = 1, m2 = 4/3, m3 = 2, m4 = 13/4          pinned two-sidedly
    m5 >= M5 = 101/18,  m6 <= M6 = 640/63         one-sided (k<=6 chain)
    m7 >= M7,           m8 <= M8                 one-sided (k=8 chain, new)

Output: an exact rational degree-8 sum-of-squares dual certificate P with
P >= 0 on R, P(0) = 1, and coefficient signs y_even > 0 > y_odd, giving

    nu({0}) <= sum_{k<=6} y_k m_k + y_7 M7 + y_8 M8 =: w0 ,
    N0s/N >= 1 - 2 w0 ,   Nd/N >= 1 - w0 .

Sign lemma (two lines, proved in the paper): if g(x) = prod (x - r_i) with all
r_i > 0 then the coefficients of g alternate, so every term of the convolution
(g^2)_j = sum_{a+b=j} g_a g_b carries the same sign (-1)^j; hence P = g^2/g(0)^2
has y_j of sign (-1)^j.  So a perfect square with positive roots ALWAYS consumes
odd moments from below and even moments from above -- the tower's natural
direction.  There is no one-sided premium.

Usage:
    python3 certify_k8.py                 # uses M7,M8 from ../data/model_constants.json
    python3 certify_k8.py M7 M8           # rationals or decimals
    python3 certify_k8.py --table         # payoff table over (M7,M8)
"""
from fractions import Fraction as F
import sys, os, json

# r129 (38th conversion): the {2,2,2} bundle was mis-classified -- crossing
# number is not a complete invariant of chord diagrams on a circle.  The nested
# three-chord class is 17/420, not 3/70, so {2,2,2} = 32/105 and M6 = 640/63.
M = {0: F(1), 1: F(1), 2: F(4, 3), 3: F(2), 4: F(13, 4), 5: F(101, 18), 6: F(640, 63)}


# ---------- exact linear algebra over Q ----------------------------------
def solve(Amat, b):
    n = len(b)
    A = [row[:] + [b[i]] for i, row in enumerate(Amat)]
    for i in range(n):
        p = next((r for r in range(i, n) if A[r][i] != 0), None)
        if p is None:
            raise ZeroDivisionError("singular")
        A[i], A[p] = A[p], A[i]
        piv = A[i][i]
        A[i] = [v / piv for v in A[i]]
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i]
                A[r] = [x - f * y for x, y in zip(A[r], A[i])]
    return [A[i][n] for i in range(n)]


def det(Amat):
    A = [row[:] for row in Amat]
    n = len(A); d = F(1)
    for i in range(n):
        p = next((r for r in range(i, n) if A[r][i] != 0), None)
        if p is None:
            return F(0)
        if p != i:
            A[i], A[p] = A[p], A[i]; d = -d
        d *= A[i][i]; inv = F(1) / A[i][i]
        for r in range(i + 1, n):
            f = A[r][i] * inv
            for c in range(i, n):
                A[r][c] -= f * A[i][c]
    return d


def hankel(mom, n):
    return [[mom[i + j] for j in range(n + 1)] for i in range(n + 1)]


def psd(Amat):
    """leading principal minors all > 0  <=>  positive definite (exact)."""
    return all(det([r[:k] for r in Amat[:k]]) > 0 for k in range(1, len(Amat) + 1))


def christoffel(mom, n):
    """lambda_n(0) = det H_n / det (H_n with row0,col0 deleted)  -- the exact optimum."""
    H = hankel(mom, n)
    minor = [[H[i][j] for j in range(1, n + 1)] for i in range(1, n + 1)]
    return det(H) / det(minor)


def kernel_poly(mom, n):
    """coefficients of K_n(x,0) = sum_j p_j(0) p_j(x); c = H_n^{-1} e_0, w0 = 1/c_0."""
    return solve(hankel(mom, n), [F(1)] + [F(0)] * n)


# ---------- the certificate ----------------------------------------------
def square_from_roots(roots):
    """P(x) = prod (x-r)^2 / prod r^2 ; returns exact coefficients y_0..y_8."""
    g = [F(1)]                                    # g[j] = coefficient of x^j, ascending
    for r in roots:
        g = [(g[i - 1] if i else F(0)) - r * (g[i] if i < len(g) else F(0))
             for i in range(len(g) + 1)]
    d = len(g) - 1
    y = [F(0)] * (2 * d + 1)
    for a in range(d + 1):
        for b in range(d + 1):
            y[a + b] += g[a] * g[b]
    c = y[0]
    return [v / c for v in y]


def evaluate(y, M7, M8):
    """w0 = sum y_k m_k with m5 at its lower bound, m6/m8 upper, m7 lower."""
    mom = dict(M); mom[7] = M7; mom[8] = M8
    return sum(y[k] * mom[k] for k in range(9))


def rationalise(x, den):
    return F(round(x * den), den)


# ---------------------------------------------------------------------------
# Archived witnesses (AUDIT_R177 2.10).
#
# The only step in build() that needs a third party is finding the roots of
# K_4(x,0): numpy PROPOSES four floats, which are then rationalised into exact
# atoms.  Nothing about the proof depends on how those atoms were found -- the
# certificate y is rebuilt from them in exact rational arithmetic and its value
# w0 is compared against the exact Christoffel optimum lam.  numpy is a search
# heuristic, never a premise.
#
# So the atoms are a WITNESS, and a witness should be checkable without the
# tool that produced it.  They are archived in k8_atoms.json, and build()
# prefers the archive: the shipped verification path then runs on the standard
# library alone -- which is what REPRODUCTION.md promises.  The archived atoms
# are still CHECKED, not trusted: a wrong atom makes w0 - lam exceed the
# tolerance and build() raises.  Regenerate with --emit-atoms (needs numpy).
_ATOMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k8_atoms.json")


def _atom_key(M7, M8):
    return f"{M7}|{M8}"


def _load_atoms(M7, M8):
    """Return (atoms, expected_w0) or (None, None)."""
    if not os.path.exists(_ATOMS):
        return None, None
    try:
        rec = json.load(open(_ATOMS)).get(_atom_key(M7, M8))
    except Exception:
        return None, None
    if not rec:
        return None, None
    return [F(a) for a in rec["atoms"]], F(rec["w0"]) if "w0" in rec else None


def _save_atoms(M7, M8, ratr, den, w0):
    db = {}
    if os.path.exists(_ATOMS):
        try:
            db = json.load(open(_ATOMS))
        except Exception:
            db = {}
    db[_atom_key(M7, M8)] = {"M7": str(M7), "M8": str(M8), "den": den,
                             "atoms": [str(a) for a in ratr],
                             # w0 is stored so the replay can check the atoms
                             # EXACTLY, not just within the 1e-7 rationalisation
                             # tolerance -- see the note in build().
                             "w0": str(w0)}
    db["_note"] = ("Rationalised extremal atoms (roots of K_4(x,0)) for the k=8 "
                   "Christoffel certificate.  A WITNESS, not an input: build() "
                   "rebuilds the certificate from these in exact rational "
                   "arithmetic and rejects them if w0 - lambda_4(0) exceeds "
                   "1e-7.  Archived so the verification path needs no numpy "
                   "(AUDIT_R177 2.10).  Regenerate: certify_k8.py --emit-atoms")
    json.dump(db, open(_ATOMS, "w"), indent=1)


def build(M7, M8, den=10 ** 5, verbose=True, emit=False):
    mom = dict(M); mom[7] = M7; mom[8] = M8
    H = hankel(mom, 4)
    if not psd(H):
        raise ValueError("(M7,M8) lies outside the moment cone over m1..m6")
    lam = christoffel(mom, 4)
    c = kernel_poly(mom, 4)
    # roots of K_4(x,0): monic quartic
    mon = [v / c[4] for v in c]

    rts = None                      # float roots: only ever used for display
    ratr, want_w0 = (None, None) if emit else _load_atoms(M7, M8)
    if ratr is not None:
        # --- stdlib-only path: replay the archived witness and CHECK it ---
        y = square_from_roots(ratr)
        w0 = evaluate(y, M7, M8)
        # Two checks, because the first one alone is too loose.  The
        # rationalisation tolerance only says "this is SOME certificate near
        # the optimum": AUDIT_R177 verified that perturbing one archived atom
        # by 1e-4 still lands inside 1e-7, while changing the delivered
        # headline rational.  So we also require w0 to reproduce EXACTLY the
        # value recorded when the witness was emitted.  (The exact headline is
        # pinned independently by gate g_certify84; this makes the artifact
        # self-checking rather than relying on the gate to notice.)
        if not (w0 - lam < F(1, 10 ** 7)):
            raise ValueError(f"archived atoms for ({M7}, {M8}) do not certify: "
                             f"w0 - lambda_4(0) = {float(w0 - lam):.3e} exceeds 1e-7. "
                             f"Regenerate with --emit-atoms.")
        if want_w0 is not None and w0 != want_w0:
            raise ValueError(f"archived atoms for ({M7}, {M8}) are inconsistent with "
                             f"the recorded w0: rebuilt {w0}, archived {want_w0}. "
                             f"The witness has been altered; regenerate with "
                             f"--emit-atoms.")
        src = "archived witness (k8_atoms.json), no numpy"
    else:
        # --- search path: numpy proposes, exact arithmetic disposes ---
        try:
            import numpy as np
        except ImportError:
            raise SystemExit(
                "certify_k8: no archived atoms for this (M7, M8) and numpy is "
                "unavailable.  numpy is needed only to PROPOSE the roots of "
                "K_4(x,0); the certificate itself is exact.  Either install "
                "numpy, or run a point whose atoms are archived in "
                "k8_atoms.json (see AUDIT_R177 2.10).")
        rts = np.sort(np.roots([1.0, float(mon[3]), float(mon[2]),
                                float(mon[1]), float(mon[0])]).real)
        # coarsest denominator that still certifies within tol of the optimum
        for den in (10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7, 10 ** 8, 10 ** 9, 10 ** 10):
            ratr = [rationalise(float(r), den) for r in rts]
            y = square_from_roots(ratr)
            w0 = evaluate(y, M7, M8)
            if w0 - lam < F(1, 10 ** 7):
                break
        src = f"numpy root search, denominator {den}"
        if emit:
            _save_atoms(M7, M8, ratr, den, w0)
            print(f"  atoms archived        : {_ATOMS}")

    if verbose:
        print("  moment cone           : (M7,M8) admissible, H_4 positive definite")
        print(f"  Christoffel optimum   : lambda_4(0) = {lam} = {float(lam):.10f}")
        print(f"  atom source           : {src}")
        if rts is not None:
            print(f"  extremal atoms (roots of K_4(x,0)) : {[round(float(r),8) for r in rts]}")
        print(f"  rationalised atoms    : {[str(r) for r in ratr]}")
        print("  certificate signs     : " + " ".join(
            f"y{k}{'+' if y[k] > 0 else '-'}" for k in range(9)))
        ok = all((y[k] > 0) == (k % 2 == 0) for k in range(9))
        print(f"  sign lemma satisfied  : {ok}   (y_even>0>y_odd, required for one-sided consumption)")
        print(f"  delivered w0          : {float(w0):.10f}   (rationalisation cost "
              f"{float(w0-lam):.2e})")
        print(f"  N0s/N >= 1-2w0        = {w0.numerator and 1-2*w0}  = {float(1-2*w0):.8f}")
        print(f"  Nd /N >= 1- w0        = {1-w0}  = {float(1-w0):.8f}")
    return dict(lam=lam, atoms=ratr, y=y, w0=w0)


def table():
    print("payoff of the k=8 rung: headline 1-2w0 as a function of the two new inputs")
    print("(exact Christoffel optimum; '--' = outside the moment cone over m1..m6)\n")
    m8s = [F(3675, 100), F(3700, 100), F(3707, 100), F(3720, 100), F(3750, 100), F(3800, 100)]
    print("        M7 \\ M8 " + "".join(f"{float(v):>10.3f}" for v in m8s))
    for M7f in [19.071225, 19.08, 19.09, 19.10, 19.1055, 19.11, 19.12, 19.15]:
        M7 = F(round(M7f * 10 ** 6), 10 ** 6); row = ""
        for M8 in m8s:
            mom = dict(M); mom[7] = M7; mom[8] = M8
            try:
                if not psd(hankel(mom, 4)):
                    row += "        --"; continue
                row += f"{float(1-2*christoffel(mom,4)):>10.5f}"
            except Exception:
                row += "        --"
        print(f"        {M7f:8.6f} " + row)
    # AUDIT_R177 2.10: this trailing block is DISPLAY ONLY -- it locates the
    # cone vertex numerically for the reader's orientation and nothing above
    # (or in gate g_certify84, which only reads the k<=6 corner from this
    # table) depends on it.  It was the last numpy dependency on the
    # certification path, so it now degrades to a one-line notice instead of
    # taking the whole certificate chain down with it on a numpy-less host.
    print("\ncone vertex over m1..m6 (the extremal measure's own m7,m8):")
    try:
        import numpy as np
    except ImportError:
        print("  (skipped: numpy unavailable -- display only, nothing above "
              "depends on it)")
        return
    c = kernel_poly(M, 3)
    mon = [v / c[3] for v in c]
    r = np.sort(np.roots([1.0, float(mon[2]), float(mon[1]), float(mon[0])]).real)
    at = np.concatenate([[0.0], r])
    V = np.vander(at, 7, increasing=True).T
    w = np.linalg.solve(V[:4, :], [float(M[k]) for k in range(4)])
    print(f"  m7_vertex = {(w*at**7).sum():.6f},  m8_vertex = {(w*at**8).sum():.6f}")


if __name__ == "__main__":
    if "--table" in sys.argv:
        table(); sys.exit()
    if len(sys.argv) >= 3:
        M7, M8 = F(sys.argv[1]), F(sys.argv[2])
    else:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                         "model_constants.json")
        d = json.load(open(p))
        M7, M8 = F(d["M7"]), F(d["M8"])
    print(f"k=8 certificate at M7 = {M7} = {float(M7):.6f}, M8 = {M8} = {float(M8):.6f}\n")
    # AUDIT_R177 2.10: --emit-atoms re-runs the numpy root search and archives
    # the rationalised atoms as a witness, so that ordinary runs (and gate
    # g_certify84) can verify on the standard library alone.
    build(M7, M8, emit=("--emit-atoms" in sys.argv))
