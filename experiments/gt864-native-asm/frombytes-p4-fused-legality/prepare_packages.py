#!/usr/bin/env python3
"""Create isolated current-production and P4 FromBytes packages."""

import hashlib
import json
import shutil
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = P / "build"
baseline_region = (P / "baseline-region.c").read_text()
baseline_cluster = baseline_region.split("/* cluster_transpose_frombytes.c */\n", 1)[1].split(
    "\n/* byte_api.c checked wrapper */", 1
)[0]


def source_files(manifest: Path) -> list[str]:
    return [line.split("  ", 1)[1] for line in manifest.read_text().splitlines()]


def write_manifest(package: Path, files: list[str]) -> None:
    lines = [hashlib.sha256((package / file).read_bytes()).hexdigest() + "  " + file for file in files]
    (package / "SOURCE-MANIFEST.sha256").write_text("\n".join(lines) + "\n")


BUILD.mkdir(exist_ok=True)
audit = {}
for name in ("p3a", "p4"):
    package = BUILD / name
    if package.exists():
        shutil.rmtree(package)
    shutil.copytree(
        PROD,
        package,
        ignore=shutil.ignore_patterns("*.o", "*.so", "PQCkemKAT*", "test_kem", "PQCgenKAT_kem"),
    )
    files = source_files(PROD / "SOURCE-MANIFEST.sha256")
    if name == "p3a":
        replacements = {
            "cluster_transpose_frombytes.c": baseline_cluster.encode(),
            "cluster_transpose_frombytes.h": (P / "baseline-cluster.h").read_bytes(),
            "byte_api.c": (P / "baseline-byte-api.c").read_bytes(),
        }
    else:
        replacements = {
            "cluster_transpose_frombytes.c": P / "candidate-cluster.c",
            "cluster_transpose_frombytes.h": P / "candidate-cluster.h",
            "byte_api.c": P / "candidate-byte-api.c",
        }
        replacements = {filename: source.read_bytes() for filename, source in replacements.items()}
    for filename, content in replacements.items():
        (package / filename).write_bytes(content)
    changed = sorted(replacements)
    write_manifest(package, files)
    audit[name] = {
        "source": "current production frame with immutable P3-A boundary" if name == "p3a" else "promoted P4 production",
        "features": [] if name == "p3a" else [
            "legality maximum fused into each decoded vector",
            "no 1728-byte output legality reread",
            "unchanged decode loads, routing stores, FR0 layout and status ABI",
        ],
        "changed": changed,
        "hashes": {
            file: hashlib.sha256((package / file).read_bytes()).hexdigest()
            for file in changed
        },
    }

(P / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
