#!/usr/bin/env python3
"""O-TT-1 / O-TT-2 (r148): exact finite-N trace moments m_b(N), written from the
r147 spec -- no math-side code reused.

    m_b(N) = N^-(b+1) sum_{k_1+..+k_b=0} (N - span(prefix sums))_+ * N^#{zeros}
             * E[prod_i tr U^{k_i}]

Schur orthogonality gives the expectation exactly, at every finite N:

    E[p_mu conj(p_nu)] = sum_{lambda |- K, len(lambda) <= N} chi^lambda(mu) chi^lambda(nu)

with mu = multiset of positive steps, nu = multiset of |negative steps|, K their
common size.  Characters come from Murnaghan-Nakayama with memoisation.

The expectation depends only on (mu, nu); the span weight depends only on the
ORDER of the steps.  So the sum factorises: enumerate (mu, nu) pairs, compute the
character sum once each, and multiply by the span-weighted count of distinct
arrangements, obtained by a DP over (multiset used, current position) inside a
sliding window -- this is the "multiset aggregation + span-DP" the spec asks for.
"""
import os
import sys
from fractions import Fraction as Q
from functools import lru_cache
from itertools import product


# ---------------------------------------------------------------- partitions
def partitions_exact(n, parts, cap):
    """partitions of n into EXACTLY `parts` parts, each <= cap.

    The first version of mu_nu_terms() enumerated partitions(K, N-1) and then
    dropped everything whose length was wrong.  For b=12, N=8 that means walking
    all partitions of K <= 84 into parts <= 7 -- astronomically many -- to keep a
    handful.  It is why m_12(8) sat on ONE core for over an hour before the pool
    could even start: the bottleneck was this serial enumeration, not the sum."""
    if parts == 0:
        if n == 0:
            yield ()
        return
    if n < parts or n > parts * cap:
        return
    for first in range(min(cap, n - parts + 1), 0, -1):
        for rest in partitions_exact(n - first, parts - 1, first):
            yield (first,) + rest


def partitions(n, cap=None):
    if cap is None: cap = n
    if n == 0:
        yield (); return
    for first in range(min(n, cap), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


# ------------------------------------------------- Murnaghan-Nakayama characters
# BOUNDED caches (r150).  These were maxsize=None.  Each worker accumulated its
# own unbounded copy of the character table, so total RSS grew with progress:
# on 240 a 12-worker m_13(9) run went 29.9 GB -> 39.1 GB while advancing only
# 41% -> 48%, and an earlier 30-worker attempt exhausted RAM *and* the page file,
# killing Windows services and wedging the RDP session stack.  The memory has to
# be bounded, not merely watched.  Tune with TT_CHI_CACHE / TT_SCHUR_CACHE.
_CHI_CACHE = int(os.environ.get("TT_CHI_CACHE", 1_000_000))
_SCHUR_CACHE = int(os.environ.get("TT_SCHUR_CACHE", 200_000))


@lru_cache(maxsize=_CHI_CACHE)
def chi(lam, mu):
    """character chi^lam(mu); lam, nu given as weakly decreasing tuples"""
    if not mu:
        return 1 if not lam else 0
    r, rest = mu[0], mu[1:]
    tot = 0
    # border strips of size r: use the beta-number (first-column hook) encoding,
    # where removing an r-strip = moving one beta down by r into a free slot.
    n = len(lam)
    beta = [lam[i] + (n - 1 - i) for i in range(n)]        # strictly decreasing
    bset = set(beta)
    for i, b in enumerate(beta):
        c = b - r
        if c < 0 or c in bset:
            continue
        nb = sorted([x for x in beta if x != b] + [c], reverse=True)
        # height = number of beta values jumped over
        ht = sum(1 for x in beta if c < x < b)
        m = len(nb)
        new = tuple(nb[i] - (m - 1 - i) for i in range(m))
        new = tuple(x for x in new if x > 0)
        tot += (-1) ** ht * chi(new, rest)
    return tot


@lru_cache(maxsize=_SCHUR_CACHE)
def schur_pair(mu, nu, N):
    """E[p_mu conj(p_nu)] = sum over lambda |- K with at most N rows"""
    K = sum(mu)
    if K != sum(nu):
        return 0
    return sum(chi(lam, mu) * chi(lam, nu)
               for lam in partitions(K) if len(lam) <= N)


# ------------------------------------------------------- span-weighted counting
def span_weight(steps, N):
    """sum over DISTINCT arrangements of the multiset `steps` of (N - span)_+ ,
    where span = max - min of the prefix sums (0 included).

    (N - span)_+ = #{ t in Z : the whole walk lies in [t, t+N-1] }, so the sum is
    counted window by window: for each window offset the DP counts arrangements
    whose walk never leaves it.  Anchoring the window by its lowest point that the
    walk actually touches would double-count, so we instead fix lo and require
    min = lo exactly, by inclusion-exclusion over the two窗口 of width N and N-1."""
    vals = sorted(set(steps))
    cnt0 = tuple(steps.count(v) for v in vals)
    if not steps:
        return N

    def walks_in_band(width):
        """arrangements whose prefix sums all lie in some fixed band of `width`
        consecutive integers, summed over all placements of that band"""
        if width <= 0:
            return 0
        total = 0
        # the lowest prefix sum can never go below the sum of the negative steps,
        # and p_0 = 0 must lie in the band, so lo ranges over [sum_neg, 0].
        # An earlier version derived this range wrongly and dropped the deepest
        # windows -- span_weight([2,-2],3) came out 1 instead of 2.
        sum_neg = sum(s for s in steps if s < 0)
        # ... and the band may sit as much as (width-1) BELOW that, as long as it
        # still covers p_0 = 0.  Clipping at sum_neg was the second version of this
        # bug: span_weight([1,-1],3) then gave 3 instead of 4.
        for lo in range(min(0, sum_neg) - (width - 1), 1):
            hi = lo + width - 1
            if hi < 0:
                continue
            from functools import lru_cache as _lc
            @_lc(maxsize=None)
            def dp(used, pos):
                if all(u == c for u, c in zip(used, cnt0)):
                    return 1 if pos == 0 else 0
                t = 0
                for i, v in enumerate(vals):
                    if used[i] < cnt0[i]:
                        np_ = pos + v
                        if lo <= np_ <= hi:
                            nu = list(used); nu[i] += 1
                            t += dp(tuple(nu), np_)
                return t
            total += dp(tuple(0 for _ in vals), 0)
            dp.cache_clear()
        return total

    # #{(arrangement, t)} with walk inside [t, t+N-1]  =  sum over arrangements of
    # (N - span)_+ , which is exactly what we want.
    return walks_in_band(N)


def mu_nu_terms(b, N):
    """[(z, mu, nu)] -- the independent summands of m_b(N).  Each contributes
    N^z * span_weight(steps) * schur_pair(mu, nu, N) and knows nothing about the
    others, so this list is the natural unit of parallelism: sharding HERE (not
    merely across (b,N) points) is what makes the b=14 table reachable, since the
    single most expensive point would otherwise set the wall clock on its own."""
    out = []
    for z in range(b + 1):
        rem = b - z
        for npos in range(rem + 1):
            nneg = rem - npos
            if npos == 0 and nneg == 0:
                if z == b:
                    out.append((z, (), ()))
                continue
            for K in range(max(npos, nneg), (N - 1) * min(npos, nneg) + 1):
                for mu in partitions_exact(K, npos, N - 1):
                    for nu in partitions_exact(K, nneg, N - 1):
                        out.append((z, mu, nu))
    return out


def term_value(args):
    z, mu, nu, b, N = args
    e = schur_pair(mu, nu, N)
    if e == 0:
        return 0
    steps = list(mu) + [-x for x in nu] + [0] * z
    w = span_weight(steps, N)
    return N ** z * w * e if w else 0


def m_b_parallel(b, N, jobs=1, shard=0, nshard=1):
    """m_b(N) summed over a shard of the (mu, nu) terms.  With nshard > 1 the
    return value is a PARTIAL numerator: sum the shards, then divide by N^(b+1)."""
    terms = [t for i, t in enumerate(mu_nu_terms(b, N)) if i % nshard == shard]
    args = [(z, mu, nu, b, N) for z, mu, nu in terms]
    if jobs > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            tot = sum(ex.map(term_value, args, chunksize=16))
    else:
        tot = sum(term_value(a) for a in args)
    return tot if nshard > 1 else Q(tot, N ** (b + 1))


def m_b(b, N, verbose=False):
    """exact m_b(N) as a Fraction"""
    tot = 0
    # a step multiset is (mu, nu, z): positive parts mu, negatives nu, z zeros
    for z in range(b + 1):
        rem = b - z
        for npos in range(rem + 1):
            nneg = rem - npos
            if npos == 0 and nneg == 0:
                if z == b:
                    tot += N ** z * span_weight([], N) * schur_pair((), (), N)
                continue
            maxK = (N - 1) * npos
            for K in range(1, maxK + 1):
                for mu in partitions(K, N - 1):
                    if len(mu) != npos: continue
                    for nu in partitions(K, N - 1):
                        if len(nu) != nneg: continue
                        e = schur_pair(mu, nu, N)
                        if e == 0: continue
                        steps = list(mu) + [-x for x in nu] + [0] * z
                        w = span_weight(steps, N)
                        if w:
                            tot += N ** z * w * e
    return Q(tot, N ** (b + 1))
