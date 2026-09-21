#!/usr/bin/env python3
"""Create non-overwriting reversed-placement clones for fixed-ELF controls."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path
from supercop_workflow import read_lock, sha256_file, sha256_tree

HOT = {
    "768": ("ntt.s", "ntt_m.s", "ntt_p.s", "basemul.s", "invntt.s", "pack.s"),
    "1152": ("ntt.s", "basemul.s", "invntt.s", "pack.s",
             "zz_native_40_forward.S", "zz_native_41_r_serializer_v2.S",
             "zz_native_42_serializer_v2_hash_g.c", "zz_native_52_h4_pairunpack.S"),
}
def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-root",type=Path,required=True)
    ap.add_argument("--parameter",choices=("768","1152"),required=True)
    ap.add_argument("--source-implementation",required=True)
    ap.add_argument("--implementation",required=True)
    a=ap.parse_args(); root=a.campaign_root.resolve()
    marker=json.loads((root/".ntruplus-campaign.json").read_text())
    if marker.get("supercop_version") != read_lock()["version"]: raise SystemExit("campaign mismatch")
    base=root/"crypto_kem"/f"ntruplus{a.parameter}"; src=base/a.source_implementation; dst=base/a.implementation
    if dst.exists(): raise SystemExit(f"refusing to overwrite {dst}")
    if not src.is_dir(): raise SystemExit(f"missing source {src}")
    source_hash=sha256_tree(src); shutil.copytree(src,dst)
    renamed={}; index=0
    for name in HOT[a.parameter]:
        path=dst/name
        if not path.is_file(): continue
        new=f"zz_place_{index:02d}_{name}"
        path.rename(dst/new); renamed[name]=new; index+=1
    if not renamed: raise SystemExit("no hot sources were found")
    manifest_path=dst/"SOURCE-MANIFEST.json"
    manifest=json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    manifest["fixed_placement_clone"]={"source_implementation":a.source_implementation,
        "source_tree_sha256":source_hash,"policy":"rename hot translation units late",
        "renamed":renamed,"semantic_change":"none"}
    manifest["implementation"]=a.implementation
    manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    files=sorted(p for p in dst.iterdir() if p.is_file() and p.name!="SHA256SUMS")
    (dst/"SHA256SUMS").write_text("\n".join(f"{sha256_file(p)}  {p.name}" for p in files)+"\n")
    print(f"installed {dst}"); return 0
if __name__ == "__main__": raise SystemExit(main())
