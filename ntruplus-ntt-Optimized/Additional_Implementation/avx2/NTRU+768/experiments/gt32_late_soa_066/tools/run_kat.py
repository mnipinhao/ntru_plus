#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

rows = {}
outputs = {}
for profile in ("control", "candidate"):
    work = BUILD / f"kat-{profile}-run"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    subprocess.run([str((BUILD / f"kat_{profile}").resolve())], cwd=work,
                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    response_files = sorted(work.glob("*.rsp"))
    if len(response_files) != 1:
        raise RuntimeError(f"{profile}: expected one .rsp, found {response_files}")
    data = response_files[0].read_bytes()
    outputs[profile] = data
    rows[profile] = {
        "file": response_files[0].name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    (RESULTS / f"kat-{profile}.rsp").write_bytes(data)

if outputs["control"] != outputs["candidate"]:
    raise SystemExit("control and candidate KAT responses differ")

out = {
    "status": "byte-exact",
    "profiles": rows,
    "same_response": True,
}
(RESULTS / "kat.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
