#!/usr/bin/env python3
"""O-BE-1 fallback for b=8 (r159 orders): full enumeration is uneconomical, so
run the two-legged sampled protocol the orders prescribe and state coverage
honestly:

  LEG A  stratified random sample, >= 100 matrices per PARTITION SHAPE (the
         multiset of block sizes), FULL minor test (all k x k, k <= 8);
  LEG B  ALL matrices, exhaustive minors of order 2, 3 and 4 only.

Neither leg alone is a proof at b=8; together they cover every matrix at low
order and every shape at full order.  The coverage fractions are recorded in
the output so the receipt cannot overstate what was checked.
"""
import sys, json, time, random, itertools
from collections import defaultdict
sys.path.insert(0, ".")
from be_tu_scan import wall_matrices, check_tu

if __name__ == "__main__":
    b = 8
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard")+1].split("/"))
    per_shape = int(sys.argv[sys.argv.index("--per")+1]) if "--per" in sys.argv else 100
    t0 = time.time()
    mats = list(wall_matrices(b))
    print(f"b=8: {len(mats)} deduped wall matrices, enum {time.time()-t0:.0f}s", flush=True)

    by_shape = defaultdict(list)
    for i, (k, rows, prov) in enumerate(mats):
        shape = tuple(sorted((len(B) for B in prov["partition"]), reverse=True))
        by_shape[shape].append(i)
    random.seed(159)
    sample = set()
    for shape, idxs in by_shape.items():
        sample |= set(idxs if len(idxs) <= per_shape else random.sample(idxs, per_shape))
    print(f"  {len(by_shape)} partition shapes; LEG A sample = {len(sample)} matrices "
          f"({100*len(sample)/len(mats):.1f}% of all)", flush=True)

    viol = []
    nA = nB = 0
    for i, (k, rows, prov) in enumerate(mats):
        if i % nshard != shard:
            continue
        full = i in sample
        w = check_tu(rows, b, kmax=(b if full else 4))
        nA += full; nB += 1
        if w:
            w["provenance"] = prov; w["matrix"] = rows; w["leg"] = "A" if full else "B"
            viol.append(w); print(f"  *** VIOLATION i={i} det={w['det']} ***", flush=True)
            break
        if nB % 500 == 0:
            print(f"  {nB} checked ({nA} full)  {time.time()-t0:.0f}s", flush=True)
    res = {"b": 8, "gate": "F-BE-TU-8", "verdict": "PASS" if not viol else "REFUTED",
           "shard": f"{shard}/{nshard}",
           "matrices_total": len(mats), "checked_this_shard": nB,
           "leg_A_full_minors_this_shard": nA,
           "partition_shapes": len(by_shape), "per_shape_target": per_shape,
           "coverage": ("LEG A: >=100 matrices per partition shape, ALL k<=8 minors. "
                        "LEG B: every matrix, minors of order 2,3,4 only. "
                        "NOT a full exhaustive proof at b=8."),
           "violations": viol, "wall_s": round(time.time()-t0, 1)}
    suf = "" if nshard == 1 else f"_s{shard}of{nshard}"
    json.dump(res, open(f"../constants/be/tu_scan_b8{suf}.json", "w"), indent=1)
    print(f"\nF-BE-TU-8 shard {shard}/{nshard}: {res['verdict']}  "
          f"{nB} checked ({nA} full)  {res['wall_s']}s", flush=True)
