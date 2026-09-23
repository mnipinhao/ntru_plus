#!/usr/bin/env python3
"""Release gate: the tree must contain sources and nothing else.

Modelled on NTRU+864's.  The banned-token list is the NTRU+1152 equivalent:
names that belonged to the experiment lane and must not reach a release.
"""
from pathlib import Path
import hashlib, sys

ROOT = Path(__file__).resolve().parents[1]
BANNED_PARTS = {"evidence", "experiment", "experiments", "bench", "archive",
                "slothy", "__pycache__", "build"}
BANNED_SUFFIX = {".o", ".so", ".dylib", ".a", ".log", ".json", ".csv", ".perf", ".map"}
BANNED_NAMES = {"test_kem", "test_abi", "test_canonical", "test_zeroization",
                "test_baseinv_fail", "test_keccak_v84a", "test_shake_prefixed",
                "PQCgenKAT_kem"}
# Only experiment-lane paths.  Gate-numbered labels such as .Lp68_wipe are the
# same convention NTRU+864 uses (.Lp13inv_wipe, .Lp0b_clear_1696) and are not
# references to anything outside the tree.
BANNED_TOKENS = ("gt1152", "GT1152", "experiments/")
EXPECTED_KAT = "2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3"

def fail(s):
    print("release-check:", s, file=sys.stderr)
    raise SystemExit(1)

files = [p for p in ROOT.rglob("*") if p.is_file()]
for p in files:
    r = p.relative_to(ROOT)
    if set(x.lower() for x in r.parts) & BANNED_PARTS: fail(f"banned path: {r}")
    if p.suffix.lower() in BANNED_SUFFIX or p.name in BANNED_NAMES:
        fail(f"generated/result file: {r}")
for p in files:
    if p.suffix not in {".c", ".h", ".S", ".s"} and p.name != "Makefile": continue
    text = p.read_text(encoding="utf-8")
    for token in BANNED_TOKENS:
        if token in text: fail(f"retired token {token!r}: {p.relative_to(ROOT)}")

required = ["Makefile", "api.h", "kem.c", "api_glue.c", "ntt.S", "ntt_tail.S",
            "inverse_ntt.S", "LICENSE",
            "scripts/check_zeroization.py",
            "scripts/export_supercop.py",
            "test/test_abi.c", "test/test_canonical.c", "test/test_zeroization.c",
            "kat/expected/PQCkemKAT_3488.req", "kat/expected/PQCkemKAT_3488.rsp"]
missing = [x for x in required if not (ROOT / x).is_file()]
if missing: fail("missing: " + ", ".join(missing))

got = hashlib.sha256((ROOT / "kat/expected/PQCkemKAT_3488.rsp").read_bytes()).hexdigest()
if got != EXPECTED_KAT: fail(f"KAT hash {got} != {EXPECTED_KAT}")
print(f"release-check: pass ({len(files)} files)")
