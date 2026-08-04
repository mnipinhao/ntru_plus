#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


def find_repo(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise SystemExit("cannot locate repository root")


experiment = Path(__file__).resolve().parent.parent
manifest_path = experiment / "contracts" / "prototype-source-closure.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
repo = find_repo(experiment)
prefix = repo / manifest["prefix"]
failures = []
for name, expected in manifest["files"].items():
    path = prefix / name
    if not path.is_file():
        failures.append(f"missing: {path}")
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        failures.append(f"hash mismatch: {name}: {actual} != {expected}")

if failures:
    raise SystemExit("\n".join(failures))
print(f"prototype-source-closure=ok files={len(manifest['files'])} "
      f"revision={manifest['source_revision']}")
