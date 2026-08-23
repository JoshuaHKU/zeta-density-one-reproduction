#!/usr/bin/env python3
"""MANIFEST.json -- sha256 of every input and output, engine versions, host table."""
import hashlib, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = {"__pycache__", ".DS_Store", "MANIFEST.json"}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

files = {}
for root, dirs, names in os.walk(HERE):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for n in sorted(names):
        if n in SKIP: continue
        p = os.path.join(root, n)
        r = os.path.relpath(p, HERE)
        files[r] = {"sha256": sha(p), "bytes": os.path.getsize(p)}

HOSTS = {
 "230": {"cores": 24, "ram_gb": 188, "gpu": None, "numpy": True, "gmpy2": True,
         "role": "facet chain, CPU ladder checkpoints, C_7"},
 "238": {"cores": 64, "ram_gb": 256, "gpu": ["RTX 3080 Ti (dev 0, fp64 1:32 -- unusable)",
                                             "Tesla V100-SXM2-16GB (dev 1, fp64 1:2 -- the GPU path)"],
         "numpy": True, "cupy": True, "gmpy2": True,
         "role": "GPU ladder, O5 sampling, C_8 (original), {5,4}"},
 "220": {"cores": 128, "ram_gb": 251, "gpu": ["present, unused"], "numpy": False, "gmpy2": True,
         "role": "wide facet chain (r136 classes); NO numpy, so no ladder here"},
 "231": {"cores": 24, "ram_gb": 128, "gpu": None, "numpy": True, "gmpy2": True,
         "role": "cross-host duplicate of {4,2,2,2}"},
}
ENG = {}
for n in sorted(os.listdir(os.path.join(HERE, "engines"))):
    if n.endswith(".py"):
        ENG[n] = files[os.path.join("engines", n)]["sha256"][:16]

TOT = json.load(open(os.path.join(HERE, "constants", "TOTALS.json")))
json.dump({
  "package": "preprint-0.84 reproduction package",
  "spec": "REPRO_SPEC.md (r139)",
  "rounds_covered": "k8-0.84 (r130-r133) and r136-r138",
  "python": sys.version.split()[0],
  "engines": ENG,
  "hosts": HOSTS,
  "constants": TOT,
  "grade_note": ("second_path is honest per REPRO_SPEC R3: C_8 carries "
                 "'model-side-ABC', which BOUNDS but does not independently "
                 "re-derive it -- the pre-registered candidate 7/180 missed the "
                 "true value 157/4032 by 4.96e-5, so the model check is not a "
                 "confirmation.  Sigma_9 and Sigma_10 are high-statistics "
                 "measurements, not exact rationals."),
  "files": files,
}, open(os.path.join(HERE, "MANIFEST.json"), "w"), indent=1)
print(f"MANIFEST.json: {len(files)} files, {sum(f['bytes'] for f in files.values())/1e6:.1f} MB")
