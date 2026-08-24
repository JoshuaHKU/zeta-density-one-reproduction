#!/usr/bin/env python3
"""Gate g_manifest -- the integrity record must itself be checked.

AUDIT_R177 2.9bis.  MANIFEST.json is the hash root of the whole package, and
until this gate existed it was the ONE artifact nothing verified
(`grep -l MANIFEST gates/*.py` returned nothing, and run_all.sh never invoked
make_manifest.py).  That gap was not theoretical: the working tree's
MANIFEST.json had been COPIED from the published tree, so it recorded 339
entries -- the published tree's count, not its own 348 -- and carried the hash
of the FIXED certification/certify84.py while the tree still held the unfixed
one.  The manifest was, in other words, already stating that a file had not
been synced, and no check was listening.

What this gate asserts:

  1. every manifest entry exists on disk and its sha256 and byte size match;
  2. every file on disk is listed in the manifest  -- the direction that
     catches a shipped-but-unhashed file;
  3. the two counts agree, i.e. the sets are equal, not merely nested.

The disk side comes from `make_manifest.collect()` -- the SAME walk that
generated the file.  Re-implementing the walk here would let the generator and
the checker drift apart, and an integrity check that drifts is worse than
none.  This is also why make_manifest.py's write path now sits behind
`if __name__ == "__main__"`: importing it must not rewrite what we verify.

Cost: about 2 s for 342 files / 62 MB.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from gatelib import check, require_count, finish
from make_manifest import collect

MAN = os.path.join(ROOT, "MANIFEST.json")

if not os.path.exists(MAN):
    print("  NOT-APPLICABLE  MANIFEST.json absent -- run make_manifest.py")
    sys.exit(3)

man = json.load(open(MAN))
recorded = man["files"]
actual = collect()

# --- 1. self-description ---------------------------------------------------
# A manifest copied from another tree is the failure this gate exists for, and
# the cheapest tell is a package string that does not name this package.
check("manifest self-description names v0.92/v4",
      "0.92" in man.get("package", "") and "v4" in man.get("package", ""),
      man.get("package", "<missing>"))

# --- 2. every recorded file is present, correct size, correct hash ----------
missing, bad_hash, bad_size = [], [], []
for rel, rec in recorded.items():
    got = actual.get(rel)
    if got is None:
        missing.append(rel); continue
    if got["sha256"] != rec["sha256"]:
        bad_hash.append(rel)
    if got["bytes"] != rec["bytes"]:
        bad_size.append(rel)

check("no manifest entry missing from disk", not missing,
      f"{len(missing)} missing" + (f": {sorted(missing)[:5]}" if missing else ""))
check("every recorded sha256 matches", not bad_hash,
      f"{len(bad_hash)} mismatched" + (f": {sorted(bad_hash)[:5]}" if bad_hash else ""))
check("every recorded byte size matches", not bad_size,
      f"{len(bad_size)} mismatched" + (f": {sorted(bad_size)[:5]}" if bad_size else ""))

# --- 3. and the other direction: nothing on disk is unhashed ---------------
extra = sorted(set(actual) - set(recorded))
check("no file on disk missing from the manifest", not extra,
      f"{len(extra)} unhashed" + (f": {extra[:5]}" if extra else ""))

# --- 4. sets equal, not merely nested --------------------------------------
check("manifest and disk file sets are equal",
      set(recorded) == set(actual),
      f"manifest {len(recorded)}, disk {len(actual)}")

# A zero-entry manifest must never green-light this gate (AUDIT_R164 2.1: an
# expectation that vanishes with the data is not a pass).
require_count("manifest entries", len(recorded), max(len(actual), 1),
              f"({len(recorded)} recorded / {len(actual)} on disk)")

finish("F-MANIFEST")
