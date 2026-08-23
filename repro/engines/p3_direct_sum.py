# -*- coding: utf-8 -*-
"""Toeplitz--trace route, math-side reference engine (direct summation).

迹路线数学侧参考实现（直和）。Paper: sec "conv" item (vii).

Independence note / 独立性说明
------------------------------
This is the MATH-SIDE reference implementation.  The compute-side
implementation (``tt_moments.py``, multiset aggregation + span-DP,
written from the spec alone) is the independent twin; gate F-IMPL-b
requires bitwise agreement of the two on overlap tables.  Do NOT
"unify" the two engines: their disagreement surface is the point.

Mathematics
-----------
Spectral identity: the Vandermonde--Gram matrix G = W W*/N at the
eigenangles of a Haar-random U in U(N) is isospectral to the Toeplitz
matrix G'_{mn} = t_{m-n}, t_k = (1/N) tr U^k.  Expanding tr (G')^b
over index walks:

  m_b(N) = N^{-(b+1)} * sum_{k_1+...+k_b = 0}
             (N - span(0, S_1, ..., S_{b-1}))_+        [walk weight]
           * N^{#zeros}                                 [t_0 = 1]
           * E[ prod_{k_i != 0} tr U^{k_i} ],           [trace moment]

with S_j the prefix sums.  The trace moment is exact at every finite
N by Schur orthogonality:

  E[ p_mu conj(p_nu) ] = sum_{lambda |- K, len(lambda) <= N}
                           chi^lambda(mu) chi^lambda(nu),

evaluated by Murnaghan--Nakayama on beta-numbers (first-column hook
lengths): removing a border strip of length r means lowering one
beta-number by r onto an unoccupied value; the sign is (-1)^(number
of occupied betas jumped over).

Everything is exact rational arithmetic (fractions.Fraction); there
is no floating point anywhere in this module.

Validation ladder (run before trusting any new value; see gate g_tt):
  1. textbook characters;
  2. E|tr U^k|^2 = min(k, N) for all k (exact at every N);
  3. in-range Diaconis--Shahshahani values and vanishing;
  4. the out-of-range hand value E|p_{2,2}|^2 (N=3) = 7;
  5. closed forms m_2(N) = 4/3 - 1/(3N^2), m_3(N) = 2 - 1/N^2.

Usage:
  from p3_direct_sum import m_b
  m_b(4, 6)         # exact Fraction, m_4 at N = 6

Provenance: r147 (five gates F-TT-2..6, blind D19 hit), r148
(F-TT-7..10 + Sigma_9/Sigma_10); receipts in the package root.
"""
import itertools
from fractions import Fraction
from functools import lru_cache

# ---------------------------------------------------------------------------
# Murnaghan-Nakayama characters on beta-numbers
# ---------------------------------------------------------------------------


def _betas(lam, n):
    """Beta-set (first-column hook lengths) of ``lam`` padded to n rows."""
    return tuple(sorted((lam[i] + (n - 1 - i) if i < len(lam)
                         else (n - 1 - i) for i in range(n)), reverse=True))


@lru_cache(maxsize=None)
def character(lam, rho):
    """chi^lam(rho) for partitions given as weakly-decreasing tuples.

    Recursive Murnaghan-Nakayama over the cycles of ``rho``; border
    strips are enumerated as legal beta-number moves.  Exact integer.
    """
    if not rho:
        return 1 if not lam else 0
    r, rest = rho[0], rho[1:]
    n = len(lam)
    beta = set(_betas(lam, n))
    total = 0
    for b in beta:
        if b - r >= 0 and (b - r) not in beta:
            moved = sorted((beta - {b}) | {b - r}, reverse=True)
            height = sum(1 for x in beta if b - r < x < b)
            child = tuple(x for x in (moved[i] - (n - 1 - i)
                                      for i in range(n)) if x > 0)
            total += (-1) ** height * character(child, rest)
    return total


def partitions(k, cap=None):
    """Yield the partitions of ``k`` as weakly-decreasing tuples."""
    cap = cap or k
    if k == 0:
        yield ()
        return
    for first in range(min(k, cap), 0, -1):
        for rest in partitions(k - first, first):
            yield (first,) + rest


@lru_cache(maxsize=None)
def trace_moment(mu, nu, n):
    """E[ p_mu(U) conj(p_nu(U)) ] over CUE(n), exact (Schur orthogonality).

    ``mu``/``nu`` are the positive/negative frequency multisets as
    sorted tuples.  Zero unless the total windings agree.
    """
    if sum(mu) != sum(nu):
        return 0
    return sum(character(lam, mu) * character(lam, nu)
               for lam in partitions(sum(mu)) if len(lam) <= n)


# ---------------------------------------------------------------------------
# The moment lattice sum
# ---------------------------------------------------------------------------


def _span(steps):
    """Span of the prefix-sum walk 0, S_1, ..., S_{b-1} (last step closes)."""
    s = mx = mn = 0
    for k in steps[:-1]:
        s += k
        if s > mx:
            mx = s
        elif s < mn:
            mn = s
    return mx - mn


def m_b(b, n):
    """Exact m_b(N=n) = E (1/N) tr (G')^b, as a Fraction.

    Direct summation over all k-vectors with |k_i| <= n-1 summing to
    zero.  Cost (2n-1)^(b-1) lattice points; fine for the gate-sized
    overlap tables, use the compute-side sharded engine for frontier
    points.
    """
    total = Fraction(0)
    grid = range(-(n - 1), n)
    for head in itertools.product(grid, repeat=b - 1):
        tail = -sum(head)
        if abs(tail) > n - 1:
            continue
        steps = head + (tail,)
        weight = n - _span(steps)
        if weight <= 0:
            continue
        nonzero = [k for k in steps if k != 0]
        mu = tuple(sorted((k for k in nonzero if k > 0), reverse=True))
        nu = tuple(sorted((-k for k in nonzero if k < 0), reverse=True))
        expect = trace_moment(mu, nu, n) if nonzero else 1
        if expect:
            total += Fraction(weight) * n ** (b - len(nonzero)) * expect
    return total / Fraction(n ** (b + 1))
