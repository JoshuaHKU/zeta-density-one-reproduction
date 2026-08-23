#!/usr/bin/env python3
"""
The re-centring identity and the collapse of the pair layers at k = 7, 8.

At the endpoint (flat window, lambda -> 1, w/L -> 0) the window is Nyquist:
phi^2 = 1_{[-L/2,L/2]} gives  Phi(2 pi m / L) = L delta_{m0}, so the mean-field
block of G is exactly  l1 * L * I.  Hence

        Gtilde / (L l1)  =  I + P ,        P = the prime-side fluctuation,

and m_k = E[(1+p)^k] = sum_j C(k,j) Sigma_j with Sigma_j := E[p^j].
The k <= 6 chain of the paper therefore PINS the first six central moments:

    Sigma_1 = 0, Sigma_2 = 1/3, Sigma_3 = 0, Sigma_4 = 1/4,
    Sigma_5 = 1/36 (= C_5),  Sigma_6 = 61/252 (= {2,2,2}+{4,2}+{6}),
with the r129-corrected bundle {2,2,2} = 32/105.

Consequences (the point of this file): the ENTIRE pair layer of the seventh and
eighth moments -- Bell(7) = 877 and Bell(8) = 4140 set-partition classes -- is
already determined, and collapses to two rational numbers:

    m_7 = 685/36 + Sigma_7 ,
    m_8 = 217/6  + 8 Sigma_7 + Sigma_8 .

Only the two genuinely new connected sums Sigma_7, Sigma_8 remain.  This is the
k=8 analogue of the paper's anchor-free identities 67/12 and 39/4, and it
supersedes them: it derives them rather than assembling them class by class.

Gates run below: (a) the k<=6 back-substitution reproduces the paper's own
anchor-free constants 67/12 and 39/4 + 6 C_5; (b) Sigma_6 reproduces
{2,2,2} + {4,2} + {6} from the paper's certified rationals.
"""
from fractions import Fraction as F
from math import comb

M = {1: F(1), 2: F(4, 3), 3: F(2), 4: F(13, 4), 5: F(101, 18), 6: F(640, 63)}


def sigmas_from_moments(M, kmax=6):
    """invert m_k = sum_j C(k,j) Sigma_j  (Sigma_0 = 1)."""
    S = {0: F(1)}
    for k in range(1, kmax + 1):
        S[k] = M[k] - sum(comb(k, j) * S[j] for j in range(k))
    return S


def rational_part(S, k, jmax=None):
    """the part of m_k already determined by the known Sigma_0..Sigma_jmax."""
    jmax = k - 1 if jmax is None else jmax
    return sum(comb(k, j) * S[j] for j in range(jmax + 1))


def main():
    S = sigmas_from_moments(M)
    print("central moments of the prime-side operator P, forced by the k<=6 chain:")
    names = {5: "  = C_5 (paper 5.5)", 6: "  = {2,2,2}+{4,2}+{6}"}
    for k in range(1, 7):
        print(f"   Sigma_{k} = {str(S[k]):>12s} = {float(S[k]):.9f}{names.get(k,'')}")

    print("\ngate (a): the paper's anchor-free rational parts, re-derived")
    r5, r6 = rational_part(S, 5, 4), rational_part(S, 6, 4)
    print(f"   m5 rational part  = {r5}   paper: 67/12    {'PASS' if r5==F(67,12) else 'FAIL'}")
    print(f"   m6 rational part  = {r6}   paper: 39/4     {'PASS' if r6==F(39,4) else 'FAIL'}")

    print("\ngate (b): Sigma_6 against the paper's certified connected rationals")
    lhs = F(32, 105) + F(-23, 420) + F(-1, 126)
    print(f"   {{2,2,2}}+{{4,2}}+{{6}} = {lhs} ;  Sigma_6 = {S[6]}   "
          f"{'PASS' if lhs==S[6] else 'FAIL'}")

    print("\nthe k=8 collapse (new):")
    p7, p8 = rational_part(S, 7, 6), rational_part(S, 8, 6)
    print(f"   m7 = {p7} + Sigma_7                = {float(p7):.9f} + Sigma_7")
    print(f"   m8 = {p8} + 8 Sigma_7 + Sigma_8  = {float(p8):.9f} + 8 Sigma_7 + Sigma_8")
    print(f"\n   (Bell(7) = 877 and Bell(8) = 4140 pair classes are entirely "
          f"absorbed into\n    the two rationals {p7} and {p8}.)")
    print("\nrequired consumption directions (sign lemma, paper k8 sec 3):")
    print("   m7 from BELOW  ->  a lower bound on Sigma_7")
    print("   m8 from ABOVE  ->  an upper bound on Sigma_8 (with Sigma_7 from below)")
    return S


if __name__ == "__main__":
    main()
