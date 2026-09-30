#!/usr/bin/env python3
"""Release check: the tree must contain sources and nothing else, the required
files must be present, and the expected KAT must be Official's."""
from pathlib import Path
import hashlib, sys

ROOT=Path(__file__).resolve().parents[1]
BANNED_PARTS={"evidence","experiment","experiments","bench","archive","slothy","__pycache__"}
BANNED_SUFFIX={".o",".so",".dylib",".a",".log",".json",".csv",".perf",".map"}
BANNED_NAMES={"test_kem","test_abi","test_canonical","test_zeroization","test_baseinv_fail","PQCgenKAT_kem"}
EXPECTED_KAT="0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"

def fail(s): print("release-check:",s,file=sys.stderr); raise SystemExit(1)
files=[p for p in ROOT.rglob("*") if p.is_file()]
for p in files:
    r=p.relative_to(ROOT)
    if set(x.lower() for x in r.parts)&BANNED_PARTS: fail(f"banned path: {r}")
    if p.suffix.lower() in BANNED_SUFFIX or p.name in BANNED_NAMES: fail(f"generated/result file: {r}")
required=["Makefile","api.h","kem.c","api_glue.c","ntt_tail.S","scripts/export_supercop.py",
          "test/test_abi.c","test/test_baseinv_fail.c","test/test_canonical.c","test/test_zeroization.c",
          "kat/expected/PQCkemKAT_2624.req","kat/expected/PQCkemKAT_2624.rsp"]
missing=[x for x in required if not (ROOT/x).is_file()]
if missing: fail("missing: "+", ".join(missing))
got=hashlib.sha256((ROOT/"kat/expected/PQCkemKAT_2624.rsp").read_bytes()).hexdigest()
if got!=EXPECTED_KAT: fail(f"KAT hash {got} != {EXPECTED_KAT}")
print(f"release-check: pass ({len(files)} files)")
