"""Sharded exact m_b(N) with CHECKPOINTING (r150 discipline).

The b=14 holdout at N=10 is an overnight run; losing it to a dropped session or
an OOM would cost the whole night, so partial sums land on disk every block and
a restart resumes.  (Same lesson as run_k10/run_pure_rows: a long run without a
checkpoint is one interruption away from zero.)

The __main__ guard is REQUIRED on spawn platforms (Windows/macOS): without it
every worker re-imports and re-executes this file and the pool dies with
BrokenProcessPool.  240 is a Windows box; this bit us once.
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tt_moments import mu_nu_terms, term_value
from fractions import Fraction as Q

BLOCK = 20000

if __name__ == "__main__":
    b, N, jobs = (int(x) for x in sys.argv[1:4])
    shard  = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    nshard = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    tag = f"tt_{b}_{N}_s{shard}of{nshard}"
    ck = tag + ".ck.json"

    t0 = time.time()
    terms = [t for i, t in enumerate(mu_nu_terms(b, N)) if i % nshard == shard]
    print(f"m_{b}({N}) shard {shard}/{nshard}: {len(terms)} terms, "
          f"enumerated in {time.time()-t0:.1f}s", flush=True)

    state = json.load(open(ck)) if os.path.exists(ck) else {"done": 0, "sum": "0"}
    total = int(state["sum"]); start = state["done"]
    if start:
        print(f"  resuming at term {start}", flush=True)

    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for lo in range(start, len(terms), BLOCK):
            blk = terms[lo:lo + BLOCK]
            args = [(z, mu, nu, b, N) for z, mu, nu in blk]
            total += sum(ex.map(term_value, args, chunksize=16))
            json.dump({"done": lo + len(blk), "sum": str(total)}, open(ck, "w"))
            print(f"  {lo+len(blk)}/{len(terms)} terms  {time.time()-t0:.0f}s",
                  flush=True)

    val = total if nshard > 1 else Q(total, N ** (b + 1))
    print(f"m_{b}({N}) shard {shard}/{nshard}: {val}   "
          f"[{len(terms)} terms]  {time.time()-t0:.1f}s", flush=True)
    json.dump({"b": b, "N": N, "shard": shard, "nshard": nshard,
               "value": str(val), "terms": len(terms)}, open(tag + ".json", "w"),
              indent=1)
