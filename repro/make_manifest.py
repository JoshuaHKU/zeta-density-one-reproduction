#!/usr/bin/env python3
"""MANIFEST.json -- sha256 of every input and output, engine versions, host table."""
import hashlib, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EXTRA_TOP = ["../paper.tex", "../paper.pdf", "../paper-zh.tex", "../paper-zh.pdf"]
EXTRA_DIRS = ["../lean", "../certification"]
SKIP = {"__pycache__", ".DS_Store", "MANIFEST.json"}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def collect(with_hashes=True):
    """The manifest's file set, as {relpath: {sha256, bytes}}.

    AUDIT_R177 2.9bis: factored out of module level so that gate g_manifest
    can verify the manifest against EXACTLY the same walk that produced it.
    Re-implementing the walk in the gate would let the two drift apart, and a
    drifting integrity check is worse than none.  Pass with_hashes=False to
    get just the file set (cheap) when only membership matters.
    """
    out = {}

    def add(path, rel):
        out[rel] = ({"sha256": sha(path), "bytes": os.path.getsize(path)}
                    if with_hashes else {"bytes": os.path.getsize(path)})

    for root, dirs, names in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for n in sorted(names):
            if n in SKIP: continue
            p = os.path.join(root, n)
            add(p, os.path.relpath(p, HERE))
    # AUDIT_R164 4.3: manifest scope extended beyond repro/ -- the paper, the
    # Lean project and the certification layer are hashed too.
    for t in EXTRA_TOP:
        p = os.path.join(HERE, t)
        if os.path.exists(p):
            add(p, t)
    for d in EXTRA_DIRS:
        dd = os.path.join(HERE, d)
        for root, dirs2, names in os.walk(dd):
            dirs2[:] = [x for x in dirs2 if x not in SKIP and x != ".lake"]
            for n in sorted(names):
                if n in SKIP: continue
                p = os.path.join(root, n)
                add(p, os.path.relpath(p, HERE))
    return out



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
 "240": {"cores": 20, "ram_gb": 64, "gpu": None, "numpy": True, "gmpy2": True,
         "role": "tt_moments production points m9(8)/m11(9)/m13(10); parity scan b=6"},
}

def main():
    """Regenerate MANIFEST.json.  AUDIT_R177 2.9bis: guarded behind __main__ so
    that gate g_manifest can `from make_manifest import collect` WITHOUT the
    import rewriting the very file it is about to verify."""
    files = collect()
    ENG = {}
    for n in sorted(os.listdir(os.path.join(HERE, "engines"))):
        if n.endswith(".py"):
            ENG[n] = files[os.path.join("engines", n)]["sha256"][:16]

    TOT = json.load(open(os.path.join(HERE, "constants", "TOTALS.json")))
    json.dump({
      "package": "preprint-0.92 reproduction package (v4)",
      "spec": "REPRO_SPEC r139 rules as excerpted in REPRO_V4_FREEZE.md",
      "rounds_covered": "k8-0.84 (r130-r133), r136-r150 (trace route v3), r158-r164 (branch-equality campaign v4)",
      "python": sys.version.split()[0],
      "engines": ENG,
      "hosts": HOSTS,
      "constants": TOT,
      "grade_note": ("second_path is honest per REPRO_SPEC R3: C_8 carries "
                     "'model-side-ABC', which BOUNDS but does not independently "
                     "re-derive it -- the pre-registered candidate 7/180 missed the "
                     "true value 157/4032 by 4.96e-5, so the model check is not a "
                     "confirmation.  AUDIT_R177 2.9ter: the sentence that used to "
                     "stand here -- 'Sigma_9 and Sigma_10 are high-statistics "
                     "measurements, not exact rationals' -- was a v1 leftover and "
                     "is FALSE since v3.  Both are exact rationals: Sigma_9 = "
                     "52207/302400 and Sigma_10 = 1333891/3326400, in "
                     "constants/tt/m_tables.json, consumed exactly by certify91.py "
                     "and gate-checked (g_be BE7 rebuilds the Sigma_9 partition).  "
                     "Single-path constants are listed in gates/g_totals.py "
                     "SINGLE_PATH and in repro/README.md: {2,2,5}, {5,4}, {6,2,2} "
                     "and (per AUDIT_R177 2.5) {7,2}."),
      "files": files,
    }, open(os.path.join(HERE, "MANIFEST.json"), "w"), indent=1)
    print(f"MANIFEST.json: {len(files)} files, {sum(f['bytes'] for f in files.values())/1e6:.1f} MB")


if __name__ == "__main__":
    main()
