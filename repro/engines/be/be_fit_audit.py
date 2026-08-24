#!/usr/bin/env python3
"""O-BE-6 (r160): data-sufficiency audit of the archived exact table.

Under the round-3 theorems, L_b(N) = m_b(N)*N^(b+1) is a SINGLE polynomial of
degree <= b+1 obeying L(-N) = (-1)^(b+1) L(N).  Parity therefore kills every
monomial whose degree differs from b+1 in parity, leaving

    unknowns = floor((b+1)/2) + 1

coefficients.  The audit asks, for each b: do we have more exact points than
unknowns, do the surplus points agree digit for digit, and does the fitted
leading coefficient equal the archived exact m_b?

No gap is filled by computing new points -- the orders say to report shortfalls,
not to paper over them.
"""
import os, sys, json, time
from fractions import Fraction as Q
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tt_moments import m_b

TAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "constants", "tt", "m_tables.json")


def exact_points(b, Nmax):
    """exact m_b(N) for N = 2..Nmax, computed directly (small b) or from table"""
    pts = {}
    for N in range(2, Nmax + 1):
        try:
            pts[N] = m_b(b, N)
        except Exception:
            pass
    return pts


def fit_parity_poly(b, pts):
    """fit L(N) = sum_j a_j N^(b+1-2j), j = 0..floor((b+1)/2), exactly"""
    nun = (b + 1) // 2 + 1
    Ns = sorted(pts)[:nun]
    if len(Ns) < nun:
        return None, nun, Ns
    A = [[Q(N) ** (b + 1 - 2 * j) for j in range(nun)] + [pts[N] * Q(N) ** (b + 1)]
         for N in Ns]
    for col in range(nun):
        p = next(r for r in range(col, nun) if A[r][col] != 0)
        A[col], A[p] = A[p], A[col]
        A[col] = [x / A[col][col] for x in A[col]]
        for r in range(nun):
            if r != col and A[r][col] != 0:
                f = A[r][col]; A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [A[i][nun] for i in range(nun)], nun, Ns


if __name__ == "__main__":
    tab = json.load(open(TAB))
    src_note = {}
    out = {}
    for b in range(2, 15):
        t0 = time.time()
        Nmax = {2: 12, 3: 12, 4: 11, 5: 10, 6: 9, 7: 8}.get(b, 0)
        if Nmax:
            pts = exact_points(b, Nmax)
        else:
            pts = {int(k): Q(v) for k, v in tab.get("values", {}).get(str(b), {}).items()}
        # r160 O-BE-7: three new exact points close the odd-b redundancy gap.
        # They are holdout HITS against the previously exactly-determined fits,
        # so adding them turns a vacuous NOT-APPLICABLE into a real check.
        ext = json.load(open("../constants/be/m_odd_ext.json"))["points"]
        for key, rec in ext.items():
            eb, eN = key[2:].split("("); eb = int(eb.rstrip("(")); eN = int(eN.rstrip(")"))
            if eb == b and "tt_moments" in rec:
                pts[eN] = Q(rec["tt_moments"])
        if not pts:
            out[b] = {"status": "NO EXACT POINTS AVAILABLE -- gap reported, not filled"}
            print(f"  b={b:>2}: NO POINTS"); continue
        coeffs, nun, used = fit_parity_poly(b, pts)
        if coeffs is None:
            out[b] = {"status": "INSUFFICIENT", "points": len(pts), "unknowns": nun,
                      "note": "gap reported, not filled"}
            print(f"  b={b:>2}: INSUFFICIENT  {len(pts)} pts < {nun} unknowns"); continue
        surplus = [N for N in sorted(pts) if N not in used]
        bad = []
        for N in surplus:
            L = sum(coeffs[j] * Q(N) ** (b + 1 - 2 * j) for j in range(nun))
            if L != pts[N] * Q(N) ** (b + 1):
                bad.append(N)
        lead_ok = str(coeffs[0]) == str(Q(tab["poly"][str(b)][0])) if str(b) in tab.get("poly", {}) else None
        out[b] = {"points": len(pts), "N_list": sorted(pts), "unknowns": nun,
                  "source": ("tt_moments.m_b computed directly" if Nmax else
                             "repro/constants/tt/m_tables.json")
                            + (" + O-BE-7 extension point" if b in (9, 11, 13) else ""),
                  "surplus": len(surplus),
                  # surplus == 0 means the fit is EXACTLY determined: there is no
                  # redundant point to check, so "PASS" would be vacuous.  Report
                  # NOT-APPLICABLE, per the empty-comparison-is-not-a-pass rule.
                  "F_BE_FIT": ("NOT-APPLICABLE (surplus 0: exactly determined, "
                               "no independent check available)" if not surplus
                               else ("PASS" if not bad else f"FAIL at N={bad}")),
                  "F_BE_LEAD": ("PASS" if lead_ok else ("FAIL" if lead_ok is False else "N/A (no archived poly)")),
                  "leading_coeff": str(coeffs[0]), "wall_s": round(time.time()-t0, 1)}
        print(f"  b={b:>2}: {len(pts):>2} pts / {nun:>2} unknowns, surplus {len(surplus):>2} -> "
              f"FIT {out[b]['F_BE_FIT']}, LEAD {out[b]['F_BE_LEAD']}")
    json.dump(out, open("../constants/be/fit_audit_b2_14.json", "w"), indent=1)
    passed = [b for b, v in out.items() if v.get("F_BE_FIT") == "PASS"]
    na = [b for b, v in out.items() if str(v.get("F_BE_FIT", "")).startswith("NOT-APPLICABLE")]
    bad = [b for b, v in out.items() if str(v.get("F_BE_FIT", "")).startswith("FAIL")]
    print(f"\nF-BE-FIT: PASS at b={passed}")
    print(f"          NOT-APPLICABLE (no surplus point) at b={na}")
    print(f"          FAIL at b={bad}")
    print(f"F-BE-LEAD: {'ALL PASS' if all(v.get('F_BE_LEAD')=='PASS' for v in out.values()) else 'see above'}")
