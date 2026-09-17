#!/usr/bin/env python3
"""Install the direct hash-stage Serializer V2 diagnostic non-destructively."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from supercop_workflow import read_lock, sha256_file
REPO = Path(__file__).resolve().parent.parent
EXP = REPO / ("ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
              "NTRU+1152/experiments/avx2_gt9x16_official_001")
def sums(directory: Path) -> None:
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "SHA256SUMS")
    (directory / "SHA256SUMS").write_text("\n".join(f"{sha256_file(p)}  {p.name}" for p in files) + "\n")
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-root", type=Path, required=True)
    ap.add_argument("--source-implementation", required=True)
    ap.add_argument("--implementation", required=True)
    a = ap.parse_args(); root = a.campaign_root.resolve()
    marker = json.loads((root / ".ntruplus-campaign.json").read_text())
    if marker.get("kind") != "disposable-supercop-campaign" or marker.get("supercop_version") != read_lock()["version"]:
        raise SystemExit("campaign marker/lock mismatch")
    base = root / "crypto_kem/ntruplus1152"; src = base / a.source_implementation; dst = base / a.implementation
    if dst.exists(): raise SystemExit(f"refusing to overwrite {dst}")
    shutil.copytree(src, dst)
    for source, name in ((EXP / "src/scale1_r_serializer_v2_hash_g.c", "zz_serializer_v2_hash_g.c"),
                         (EXP / "src/scale1_r_serializer_v2_hash_g.h", "scale1_r_serializer_v2_hash_g.h"),
                         (EXP / "generated/scale1-r-serializer-v2-asm.h", "scale1-r-serializer-v2-asm.h")):
        shutil.copy2(source, dst / name)
    manifest_path = dst / "SOURCE-MANIFEST.json"; manifest = json.loads(manifest_path.read_text())
    manifest["scale1_r_serializer_v2_direct_hash_stage"] = {
        "source_implementation": src.name,
        "boundary": "materialized scale-1 wire state to hash_g output",
        "removed_pass": "1728-byte serializer temporary reload and hash_g staging copy",
        "native_caller_changed": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n"); sums(dst)
    print(f"installed {dst}"); return 0
if __name__ == "__main__": raise SystemExit(main())
