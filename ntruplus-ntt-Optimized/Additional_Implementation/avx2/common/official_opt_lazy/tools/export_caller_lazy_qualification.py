#!/usr/bin/env python3
"""Create a flat Official-derived caller-lazy qualification source (864/1152).

Port of NTRU+768 avx2_official_opt_001/tools/export_caller_lazy_qualification.py.
The export is the pinned imported Official tree plus exactly two overlays:
`kem.c` (src/kem_lazy.c) and `ntt_caller_lazy.s` (the namespaced lazy Forward).
It refuses to overwrite, verifies the pinned Official tree against
bench/supercop.lock and records every installed source hash in a sibling JSON
manifest.  This is a research export, not a clean-production promotion.

Usage (from the experiment directory):
  export_caller_lazy_qualification.py --param 864 --experiment . \
      --output-root qualification
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from supercop_workflow import read_lock, sha256_file, sha256_tree  # noqa: E402

NAME = "avx2-officialopt-caller-lazy-qual001"


def overlays(param: int) -> dict:
    return {
        "kem.c": "src/kem_lazy.c",
        "ntt_caller_lazy.s": f"asm/ntruplus{param}_officialopt_ntt_caller_lazy.s",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.experiment.resolve()
    output_root = args.output_root.resolve()
    target = output_root / NAME
    manifest_path = output_root / (NAME + ".json")
    if target.exists() or manifest_path.exists():
        raise SystemExit("refusing to overwrite qualification export")

    lock = read_lock(REPO / "bench/supercop.lock")
    key = f"ntruplus{args.param}_avx2_tree_sha256"
    source = root / "upstream/supercop-avx2"
    if sha256_tree(source) != lock[key]:
        raise SystemExit("pinned Official import hash mismatch")
    record = json.loads((root / "upstream/UPSTREAM.json").read_text())
    if record.get("source_tree_sha256") != lock[key]:
        raise SystemExit("UPSTREAM.json does not match the lock")
    lays = overlays(args.param)
    kem = (root / lays["kem.c"]).read_text()
    symbol = f"ntruplus{args.param}_officialopt_ntt_caller_lazy"
    if symbol not in kem or f".global {symbol}" not in (root / lays["ntt_caller_lazy.s"]).read_text():
        raise SystemExit("overlay does not reference the namespaced lazy Forward")

    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, symlinks=False)
    # The imported upstream copy is read-only; the export is a fresh writable
    # copy (content hashes, not modes, are what the manifest pins).
    for path in [target, *target.iterdir()]:
        path.chmod(path.stat().st_mode | 0o200)
    for destination, path in lays.items():
        shutil.copy2(root / path, target / destination)
    if "amd64" not in (target / "architectures").read_text().split():
        raise SystemExit("missing amd64 architecture")
    for goal in ("goal-constbranch", "goal-constindex"):
        if not (target / goal).is_file():
            raise SystemExit(f"missing {goal}")
    files = {str(path.relative_to(target)): sha256_file(path)
             for path in sorted(target.iterdir()) if path.is_file()}
    manifest = {
        "kind": "caller-lazy-qualification-source",
        "implementation": NAME,
        "parameter": str(args.param),
        "supercop_version": lock["version"],
        "official_tree_sha256": lock[key],
        "tree_sha256": sha256_tree(target),
        "overlays": {destination: sha256_file(root / path)
                     for destination, path in lays.items()},
        "files_sha256": files,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(target)


if __name__ == "__main__":
    main()
