#!/usr/bin/env python3
"""run_pure.py + per-term-orbit persistence (REPRO_SPEC r139 sec 7).

Same arithmetic as run_pure.py -- it re-derives the SAME dihedral quotient and
must return the same C_k -- but it writes one row per F-CYC term orbit, keyed by
the orbit's canonical form (R1), so an external referee can spot-check a single
term instead of only the bundle.

    python3 run_pure_rows.py K --jobs N [--out FILE]
"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ratbackend import F, BACKEND
from class_integral import edge_forms, cycle_walk, term_walk, one_term, fcyc_terms
from symquot import canon, dihedral_maps


def key_of(parts, k):
    """R1 canonical form of an F-CYC term orbit, as a stable string."""
    best = min(canon(parts, k, g) for g in dihedral_maps(k))
    return "|".join("".join(str(x) for x in p) for p in best)


def quotient_keyed(k):
    """[(key, weight, parts)] -- weight = signed multiplicity of the orbit."""
    maps = dihedral_maps(k)
    seen, out = {}, []
    for sign, parts in fcyc_terms(list(range(k))):
        key = "|".join("".join(str(x) for x in p)
                       for p in min(canon(parts, k, g) for g in maps))
        if key in seen:
            out[seen[key]][1] += sign
        else:
            seen[key] = len(out); out.append([key, sign, parts])
    return [(kk, w, p) for kk, w, p in out if w != 0], len(seen)


if __name__ == "__main__":
    k = int(sys.argv[1])
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 8
    out = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv
           else os.path.join(HERE, f"c{k}_orbit_values.json"))
    # --shard i/n : term orbits are independent, so a class can be split across
    # hosts.  Each shard keeps its own checkpoint and emits its own partial file;
    # merge_shards() recombines them.  C_9 is 1220 core-h, too much for one node.
    shard, nshard = 0, 1
    if "--shard" in sys.argv:
        shard, nshard = (int(x) for x in sys.argv[sys.argv.index("--shard") + 1].split("/"))
    blocks = [list(range(k))]
    forms, nfree, _ = edge_forms(blocks, k)
    base = cycle_walk(forms, k, nfree)
    orbs, nseen = quotient_keyed(k)
    print(f"backend {BACKEND}  C_{k}: {nseen} term orbits, {len(orbs)} with "
          f"nonzero weight, free dim {nfree}, jobs {jobs}", flush=True)
    args = []
    for key, w, parts in orbs:
        tw = term_walk(parts, forms, nfree)
        args.append((([base] + ([tw] if len(tw) > 1 else [])), [], nfree))
    # INCREMENTAL CHECKPOINT (r141).  The original collected every result with a
    # single ex.map and wrote nothing until the last orbit, so a multi-day C_9 run
    # would lose everything if a worker died -- which is exactly what happened to
    # {4,4,2} on 220 (OOM -> BrokenProcessPool).  Results now land on disk as they
    # arrive and a restart resumes.
    # shard-specific checkpoint names: concurrent shards on different hosts must
    # not write the same file, and the merge pass globs them all back together.
    import glob as _glob
    ck = out + (f".ck{shard}" if nshard > 1 else ".ck")
    done = {}
    for f in sorted(_glob.glob(out + ".ck*")):
        done.update(json.load(open(f)))
    if done:
        print(f"  resuming from {ck}: {len(done)} term orbits already done", flush=True)
    todo = [(i, a) for i, (a, (key, w, p)) in enumerate(zip(args, orbs))
            if key not in done and i % nshard == shard]
    t0 = time.time(); nsave = 0
    if jobs > 1 and todo:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            futs = {ex.submit(one_term, a): i for i, a in todo}
            from concurrent.futures import as_completed
            for fut in as_completed(futs):
                i = futs[fut]
                done[orbs[i][0]] = str(fut.result())
                nsave += 1
                if nsave % 50 == 0:
                    json.dump(done, open(ck, "w"))
                    print(f"  {len(done)}/{len(orbs)} term orbits, "
                          f"{time.time()-t0:.0f}s", flush=True)
    else:
        for i, a in todo:
            done[orbs[i][0]] = str(one_term(a))
    json.dump(done, open(ck, "w"))
    if nshard > 1:
        print(f"  shard {shard}/{nshard} complete: {len(done)} term orbits in {ck}",
              flush=True)
        raise SystemExit(0)
    tot = F(0); rows = {}
    for key, w, parts in orbs:
        v = F(done[key])
        tot += w * v
        rows[key] = {"weight": int(w), "value": str(v),
                     "parts": [list(p) for p in parts]}
    dt = time.time() - t0
    print(f"  C_{k} = {tot} = {float(tot):.12f}   {dt:.0f}s", flush=True)
    json.dump({"class": "{%d}" % k, "cycle": k, "term_orbits": len(orbs),
               "fcyc_terms": len(fcyc_terms(list(range(k)))),
               "total": str(tot), "wall_s": round(dt, 1),
               "orbit_values": rows}, open(out, "w"), indent=1)
    print(f"  wrote {out}", flush=True)
