#!/usr/bin/env python3
"""Prepare diagnostic no-store cores without touching production sources."""

from pathlib import Path
import json
import hashlib

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = P / "build"
BUILD.mkdir(exist_ok=True)

specs = [
    ("gt864_native_inverse16_lazy.S", "lazy_i16", "p7b0_lazy_i16_nostore", 128),
    ("gt864_native_inverse_tail_lazy.S", "lazy_itail", "p7b0_lazy_itail_nostore", 96),
]
report = {}
for source_name, old, new, expected in specs:
    source = PROD / source_name
    text = source.read_text()
    lines = text.splitlines()
    umov = sum(line.strip().lower().startswith("umov ") for line in lines)
    strh = sum(line.strip().lower().startswith("strh ") for line in lines)
    assert umov == expected and strh == expected
    kept = [line for line in lines if not line.strip().lower().startswith(("umov ", "strh "))]
    generated = ("\n".join(kept) + "\n").replace(old, new)
    output = BUILD / source_name.replace(".S", "_nostore.S")
    output.write_text(generated)
    report[new] = {
        "source": str(source.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "removed_umov": umov,
        "removed_strh": strh,
        "diagnostic_only": True,
    }

(P / "nostore-generation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
