#!/usr/bin/env python3
"""Generate constants/<class>/RUN.md to REPRO_SPEC r139 sec 4:
environment line, ONE command (with a justified --jobs ceiling), expected
output excerpt, and the checkpoint policy."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

ENV_FACET = ("python3 >= 3.9; `gmpy2` STRONGLY recommended (8x over "
             "`fractions.Fraction`; set `RATBACKEND=frac` to fall back and "
             "reproduce without it); numpy NOT required.\n"
             "   Runs on 220/230/231/238.  **220 has no numpy**: the facet chain "
             "runs there, the ladder chain does not.")
ENV_LAD = ("python3 >= 3.9 + numpy; CuPy 12.x + a **V100** for the GPU path "
           "(`LADDER_GPU=<dev>`).  fp64 on GeForce is 1:32 and unusably slow -- "
           "the RTX 3080 Ti in 238 is dev 0, the V100 is dev 1.\n"
           "   220 cannot run this chain (no numpy).")

C = {
 "t222": dict(lab="{2,2,2}", k=6, eng="phase0 polytope", cmd="python3 ../../engines/t222_exact.py",
   jobs="8", why="5 orbits in R^3; memory negligible", wall="~1 min",
   head="D0 size 2  3/70", tot="32/105 = 0.3047619048", env=ENV_FACET, ck="none"),
 "p24": dict(lab="{2^4}", k=8, eng="phase0 polytope", cmd="python3 ../../engines/p24_exact.py",
   jobs="8", why="17 orbits in R^4, ~10 s each; trivial memory", wall="~3 min",
   head="P0 size 16  11/6048", tot="1661/3780 = 0.4394179894", env=ENV_FACET, ck="none"),
 "j52": dict(lab="{5,2}", k=7, eng="facet recursion", cmd="python3 ../../engines/run_class.py '{5,2}' --jobs 8",
   jobs="8", why="150 F-CYC terms x 3 orbits in R^7; memo table ~0.2 GB/worker", wall="~90 s",
   head="Q0 size 7 rep [[0,1,2,3,4],[5,6]] = 5/504", tot="1/8", env=ENV_FACET, ck="none"),
 "j224": dict(lab="{2,2,4}", k=8, eng="facet recursion", cmd="python3 ../../engines/run_class.py '{2,2,4}' --jobs 24",
   jobs="24", why="1082 terms x 22 orbits in R^7; memo ~0.4 GB/worker, so <= 24 workers on a 32 GB node",
   wall="~2 h on 24 cores", head="O0 size 16  -5/18144", tot="-127/840 = -0.1511904762", env=ENV_FACET,
   ck="`values_2_2_4.json` is written once at the end; a partial run leaves nothing behind."),
 "j44": dict(lab="{4,4}", k=8, eng="facet recursion", cmd="python3 ../../engines/run_class.py '{4,4}' --jobs 24",
   jobs="24", why="1082^2/quotient terms in R^7; memo ~0.6 GB/worker", wall="~3 h on 24 cores",
   head="O0 size 8", tot="23/4536 = 0.0050705467", env=ENV_FACET, ck="none"),
 "j62": dict(lab="{6,2}", k=8, eng="facet recursion", cmd="python3 ../../engines/run_class.py '{6,2}' --jobs 24",
   jobs="24", why="9366 terms x 4 orbits in R^8; memo ~0.9 GB/worker", wall="~4 h on 24 cores",
   head="O0 size 8", tot="-563/11340 = -0.0496472663", env=ENV_FACET, ck="none"),
 "p25": dict(lab="{2^5}", k=10, eng="facet recursion (r136)", cmd="python3 ../../engines/run_k10.py '{2^5}' 10 2,2,2,2,2 --jobs 110",
   jobs="110", why="only size-2 blocks, so no F-CYC expansion: 1 term/orbit in R^5. Memo ~0.05 GB/worker; 110 workers fit a 128-core/250 GB node",
   wall="~25 min on 110 cores", head="O0 size 20  149/118800", tot="10531/13860 = 0.7598845598", env=ENV_FACET,
   ck="none"),
 "j4222": dict(lab="{4,2,2,2}", k=10, eng="facet recursion (r136)", cmd="python3 ../../engines/run_k10.py '{4,2,2,2}' 10 4,2,2,2 --jobs 110",
   jobs="110", why="1082 terms x 190 orbits in R^7; memo ~0.4 GB/worker -> **<= 110 workers/node**",
   wall="~3 h on 110 cores", head="O0 size 20  -61/285120", tot="-208771/498960 = -0.4184423400", env=ENV_FACET,
   ck="none; this class is the cross-host duplicate (220 and 231 independently returned identical rationals)."),
 "j225": dict(lab="{2,2,5}", k=9, eng="facet recursion (r136)", cmd="python3 ../../engines/run_k10.py '{2,2,5}' 9 2,2,5 --jobs 110",
   jobs="110", why="9366 terms x 30 orbits in R^8; memo ~0.9 GB/worker -> **<= 110 workers/node**",
   wall="~5 h on 110 cores", head="O0 size 18  289/302400", tot="2263/5040 = 0.4489087302", env=ENV_FACET,
   ck="none"),
 "j54": dict(lab="{5,4}", k=9, eng="facet recursion (r136)", cmd="python3 ../../engines/run_k10.py '{5,4}' 9 5,4 --jobs 160",
   jobs="160", why="1082x26 terms x 10 orbits in R^9; measured 0.9 GB/worker on the pre-r141 engine", wall="~13 h on 160 cores (238)",
   head="O0 size 18  -11/151200", tot="-257/10080 = -0.0254960317", env=ENV_FACET,
   ck="none for this run (it predates the r141 checkpoint patch); later runs write ck_5_4.json"),
 "j622": dict(lab="{6,2,2}", k=10, eng="facet recursion (r136, r141-optimised)", cmd="python3 ../../engines/run_k10.py '{6,2,2}' 10 6,2,2 --jobs 16",
   jobs="16", why="1082 terms x 46 orbits in R^9; **size the job by memo x worker, not by cores** -- the r141 engine uses MORE memory per worker (LP cache), and 65 workers x 3.6 GB OOM-killed a sibling run on a 251 GB node",
   wall="~14 h on 16 cores (230), including a restart", head="O0 size 20  -19/30800", tot="-120139/498960 = -0.2407788199", env=ENV_FACET,
   ck="ck_6_2_2.json, written after every orbit; delete it to force a full recompute. It saved this run twice."),
 "c7": dict(lab="{7} = C_7", k=7, eng="facet recursion + dihedral quotient",
   cmd="python3 ../../engines/run_pure_rows.py 7 --jobs 24 --out c7_orbit_values.json",
   jobs="24", why="9366 F-CYC terms -> 685 D_7 orbits (13.7x); memo ~0.9 GB/worker",
   wall="~3.5 min on 24 cores", head="685 term orbits, free dim 6", tot="-17/360 = -0.0472222222", env=ENV_FACET,
   ck="`c7_orbit_values.json` is the deliverable; no intermediate checkpoint."),
 "c8": dict(lab="{8} = C_8", k=8, eng="facet recursion + dihedral quotient",
   cmd="python3 ../../engines/run_pure_rows.py 8 --jobs 32 --out c8_orbit_values.json",
   jobs="32", why="94586 F-CYC terms -> 6027 D_8 orbits (15.7x) in R^8; memo ~1.8 GB/worker -- **this is the class that caused the 3bis swap incident**: 120 workers x 1.8 GB = 216 GB on a 251 GB box drove the node into swap and produced 0 orbits in 87 min. Size the job by memo x worker, NOT by core count.",
   wall="~63 min on 60 cores (238); ~1.8 h on 32", head="6027 term orbits, free dim 7",
   tot="157/4032 = 0.0389384921", env=ENV_FACET,
   ck="`c8_orbit_values.json` is written once at the end; there is no resume, so a killed run restarts from zero."),
}
LAD_NOTE = {"j224": "22", "j44": "7", "j62": "4", "j52": "3"}

for cls, d in C.items():
    p = os.path.join(HERE, "constants", cls)
    v = json.load(open(os.path.join(p, "values.json")))
    sp = list(v["orbit_values"].values())[0]["second_path"]
    txt = f"""# RUN.md -- {d['lab']}  (repro/constants/{cls})

Exact value **{v['total']}** = {float(__import__('fractions').Fraction(v['total'])):.10f},
{len(v['orbit_values'])} dihedral orbits on the {d['k']}-cycle, {v['class']}.
Engine: {d['eng']}.

## 1. Environment

   {d['env']}
   Always `export OMP_NUM_THREADS=1` -- the workers are processes; letting each
   spawn BLAS threads only oversubscribes the node (measured: no speedup, since
   numpy threads only BLAS and this chain is elementwise/rational).
   `RATBACKEND=gmpy2` (default) or `RATBACKEND=frac`.

## 2. Command (one line)

```bash
export OMP_NUM_THREADS=1 RATBACKEND=gmpy2
{d['cmd']}
```

**--jobs ceiling {d['jobs']}**: {d['why']}.

## 3. Expected output

```
backend gmpy2 ...
  {d['head']} ...
  total = {d['tot']}
```
Expected wall clock: {d['wall']}.

## 4. Checkpoints

{d['ck']}
Nothing in this directory is a checkpoint: `orbits.json` and `values.json` are
the delivered artefacts, keyed by dihedral canonical form (never by index).

## 5. Second path

`{json.dumps(sp)}`
"""
    if cls in LAD_NOTE:
        txt += f"""
Reproduce it with the midpoint ladder (needs numpy, and CuPy+V100 for the GPU path):

```bash
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py {cls.replace('j','').replace('p','')} 0.1
LADDER_GPU=1 OMP_NUM_THREADS=1 python3 ../../engines/ladder_joints_sw.py {cls.replace('j','').replace('p','')} 0.05
python3 ../../gates/{'g_v52.py' if cls == 'j52' else 'g_vjoints.py'}
```
h^2 Richardson `(4 L(dv/2) - L(dv))/3` must match all {LAD_NOTE[cls]} orbits within 3e-6.
**Match on the canonical form, never on orbit index** -- the ladder and the exact
chain enumerate orbits in different orders and pick different representatives;
index matching produced a false FAIL in round 136.
"""
    open(os.path.join(p, "RUN.md"), "w").write(txt)
    print("  wrote", os.path.join("constants", cls, "RUN.md"))
