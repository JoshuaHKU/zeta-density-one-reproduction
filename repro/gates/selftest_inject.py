#!/usr/bin/env python3
"""Gate self-test by error injection (AUDIT_R164 5.4, extended AUDIT_R177 2.8).

Principle: a gate that stays green after a deliberate corruption of the
data it claims to check is a fake gate.  Run before every release.
Exit 0 iff every injection was caught.

TWO injection classes, because they catch different defects:

  CASES    -- CORRUPTION.  Mutate a value inside a JSON artifact and require
              the gate to exit non-zero.  Catches "the gate reads the data
              but does not really compare it" (AUDIT_R164 2.2: g_totals
              computed the bundle total and never compared it to the `total`
              field, so a corrupted field passed 14/14).

  ABSENCE  -- DELETION.  Move the data out of the way entirely and require
              the gate to exit non-zero.  Catches a defect that corruption
              CANNOT reach: an expectation derived from the same glob as the
              data vanishes together with the data, so the gate compares an
              empty set against an empty expectation and reports success.
              This was AUDIT_R164 2.1 -- g_logdet printed
              "PASS F-LOGDET pools matched 0/0" and exited 0 with every pool
              file removed.  Adding this class was AUDIT_R177 2.8: the very
              gate whose fake-green started this discipline had no permanent
              regression test, because no value-mutation can reproduce it.
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable

def run_gate(name):
    return subprocess.run([PY, os.path.join(HERE, name)],
                          capture_output=True, text=True).returncode

def inject(path, mutate):
    J = json.load(open(path))
    mutate(J)
    json.dump(J, open(path, "w"), indent=1)

CASES = [
    ("constants/p24/values.json", "g_totals.py",
     lambda J: J.__setitem__("total", "999/1000"),
     "g_totals catches corrupted total field"),
    ("constants/p24/values.json", "g_totals.py",
     lambda J: list(J["orbit_values"].values())[0].__setitem__("value", "1/7"),
     "g_totals catches corrupted orbit value"),
    ("constants/be/parity_scan_b4.json", "g_be.py",
     lambda J: J["total"].__setitem__(0, str(int(J["total"][0]) + 1)),
     "g_be catches corrupted Moebius assembly total"),
    ("constants/be/sigma_scan_b4.json", "g_be.py",
     lambda J: list(J["T"].values())[0].__setitem__(2, "999999"),
     "g_be catches corrupted fine-term value (signed assembly)"),
    ("constants/c9/term_orbits.json", "g_be.py",
     lambda J: list(J["orbit_values"].values())[0].__setitem__("weight", "3"),
     "g_be BE7 catches corrupted c9 orbit weight"),
    ("constants/j72/values.json", "g_be.py",
     lambda J: J["orbit_values"]["O0"].__setitem__("value", "-1/2"),
     "g_be BE7 catches corrupted j72 orbit"),
    ("constants/tt/m_tables_ext.json", "g_be.py",
     lambda J: J["values"]["9"].__setitem__("8", "1/2"),
     "g_be BE5 catches corrupted extension point"),
]

# AUDIT_R177 2.8 -- absence injections: (files to hide, gate, label).
# Paths are relative to ROOT.  All listed files are moved aside together, the
# gate must exit non-zero, and everything is restored in a finally block.
ABSENCE = [
    (["data/eigs_N128.npy", "data/eigs_N256.npy", "data/eigs_N512.npy",
      "data/ev_400.npy", "data/ev_800.npy", "data/ev_1600.npy"],
     "g_logdet.py",
     "g_logdet catches MISSING pools (the 0/0 fake-green of AUDIT_R164 2.1)"),
    (["measurements/o5/o5_central_N128_s0.npy"],
     "g_o5.py",
     "g_o5 catches a MISSING measurement pool"),
]

fails = []
for rel, gate, mutate, label in CASES:
    path = os.path.join(ROOT, rel)
    bak = path + ".selftest.bak"
    shutil.copy2(path, bak)
    try:
        inject(path, mutate)
        rc = run_gate(gate)
        caught = (rc != 0)
        print(f"  [{'CAUGHT' if caught else 'MISSED'}] {label} (exit {rc})")
        if not caught:
            fails.append(label)
    finally:
        shutil.move(bak, path)

# --- absence class -------------------------------------------------------
HOLD = os.path.join(ROOT, ".selftest_absence")
for rels, gate, label in ABSENCE:
    os.makedirs(HOLD, exist_ok=True)
    moved = []
    try:
        for rel in rels:
            src = os.path.join(ROOT, rel)
            if os.path.exists(src):
                dst = os.path.join(HOLD, rel.replace(os.sep, "__"))
                shutil.move(src, dst)
                moved.append((src, dst))
        rc = run_gate(gate)
        caught = (rc != 0)
        print(f"  [{'CAUGHT' if caught else 'MISSED'}] {label} (exit {rc})")
        if not caught:
            fails.append(label)
    finally:
        for src, dst in moved:
            shutil.move(dst, src)
        if os.path.isdir(HOLD) and not os.listdir(HOLD):
            try:
                os.rmdir(HOLD)
            except OSError:
                # Restricted filesystems (sandboxed mounts) may forbid rmdir.
                # The artifacts themselves are already moved back at this
                # point; a leftover empty holding directory is harmless and
                # must not abort the verdict.  (Portability fix, r177.)
                pass

# sanity: gates green again on restored data
for gate in sorted({g for _, g, _, _ in CASES} | {g for _, g, _ in ABSENCE}):
    rc = run_gate(gate)
    ok = (rc == 0)
    print(f"  [{'PASS' if ok else 'FAIL'}] restored data: {gate} green again (exit {rc})")
    if not ok:
        fails.append(f"restore {gate}")

print()
if fails:
    print(f"*** selftest_inject: {len(fails)} FAKE-GREEN or restore failures: {fails}")
    sys.exit(1)
print("selftest_inject: ALL INJECTIONS CAUGHT, ALL GATES GREEN ON RESTORE")
