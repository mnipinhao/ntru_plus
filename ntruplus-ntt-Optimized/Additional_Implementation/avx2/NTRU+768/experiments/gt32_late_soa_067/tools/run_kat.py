#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_BYTES = 948402
EXPECTED_SHA256 = "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8"

rows = {}
for profile in ("control", "candidate"):
    binary = ROOT / "build" / f"kat_{profile}"
    with tempfile.TemporaryDirectory(prefix=f"late067-{profile}-") as name:
        directory = Path(name)
        subprocess.run([str(binary.resolve())], cwd=directory, check=True,
                       stdout=subprocess.DEVNULL)
        response = directory / "PQCkemKAT_2336.rsp"
        data = response.read_bytes()
    rows[profile] = {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }

if rows["control"] != rows["candidate"]:
    raise SystemExit(f"KAT profiles differ: {rows}")
if rows["control"]["bytes"] != EXPECTED_BYTES \
        or rows["control"]["sha256"] != EXPECTED_SHA256:
    raise SystemExit(f"KAT fingerprint mismatch: {rows}")

output = {
    "schema": "gt32-late-soa-067-kat-v1",
    "expected": {"bytes": EXPECTED_BYTES, "sha256": EXPECTED_SHA256},
    "profiles": rows,
    "exact": True,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "kat.json").write_text(
    json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))
