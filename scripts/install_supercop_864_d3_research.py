#!/usr/bin/env python3
"""Install the namespaced 864 D3/MR32 component beside pinned Official."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from supercop_workflow import REPO_ROOT, read_lock, sha256_file
EXP = REPO_ROOT / ("ntruplus-ntt-Optimized/Additional_Implementation/avx2/"
                   "NTRU+864/experiments/avx2_gt9x16_official_001")
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-root",type=Path,required=True)
    ap.add_argument("--implementation",default="avx2-d3-mr32-research")
    a=ap.parse_args(); root=a.campaign_root.resolve()
    marker=json.loads((root/".ntruplus-campaign.json").read_text())
    if marker.get("supercop_version") != read_lock()["version"]: raise SystemExit("campaign mismatch")
    src=root/"crypto_kem/ntruplus864/avx2"; dst=root/"crypto_kem/ntruplus864"/a.implementation
    if dst.exists(): raise SystemExit(f"refusing to overwrite {dst}")
    shutil.copytree(src,dst)
    asm=(EXP/"asm/d3_vpmaddwd_tile.s").read_text().replace(
        '"generated/d3-vpmaddwd-asm-masks.inc"','"d3-vpmaddwd-asm-masks.inc"')
    (dst/"zz_d3_vpmaddwd_tile.s").write_text(asm)
    shutil.copy2(EXP/"generated/d3-vpmaddwd-asm-masks.inc",dst/"d3-vpmaddwd-asm-masks.inc")
    shutil.copy2(EXP/"src/d3_vpmaddwd_tile.h",dst/"d3_vpmaddwd_tile.h")
    manifest={"schema":"ntruplus864-d3-research/v1","supercop_version":read_lock()["version"],
              "implementation":a.implementation,"native_kem_candidate":False,
              "cutpoint":"two packed T3 operands plus zeta to three coefficient planes",
              "status":"research-only; not integrated into KEM"}
    (dst/"SOURCE-MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (dst/"SHA256SUMS").write_text("\n".join(f"{sha256_file(p)}  {p.name}" for p in files)+"\n")
    print(f"installed {dst}"); return 0
if __name__ == "__main__": raise SystemExit(main())
