#!/usr/bin/env python3
"""Install normal/reversed shared-ABI same-ELF benchmark implementations."""
from __future__ import annotations
import argparse,json,shutil
from pathlib import Path
from supercop_workflow import read_lock,sha256_file
REPO=Path(__file__).resolve().parent.parent
EXP=REPO/"ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/experiments/avx2_gt9x16_official_001"
def flat(src,dst): dst.write_text(src.read_text().replace('"generated/','"').replace('"asm/','"'))
def sums(d): (d/"SHA256SUMS").write_text("\n".join(f"{sha256_file(p)}  {p.name}" for p in sorted(d.iterdir()) if p.is_file() and p.name!="SHA256SUMS")+"\n")
def install(src,dst,rev):
 if dst.exists(): raise SystemExit(f"refusing to overwrite {dst}")
 shutil.copytree(src,dst)
 flat(EXP/"asm/gt9x16_prod3_aos_branch0.S",dst/"gt9x16_prod3_aos_branch0.S")
 files=[("wire_forward",EXP/"asm/gt9x16_prod3_aos_h4_scale1_lazy_reduce_wire.S"),("natural_serializer",EXP/"asm/direct_serializer_natural.S"),("wire_serializer",EXP/"asm/direct_serializer_wire.S"),("wire_h4",EXP/"asm/encap_h4_m3b_exact_egress_wire.S")]
 order=list(reversed(files)) if rev else files
 prefix="aa_wire" if rev else "zz_wire"
 installed={}
 for n,(role,path) in enumerate(order,20): installed[role]=f"{prefix}_{n:02d}_{role}.S";flat(path,dst/installed[role])
 for name in ("d1-wire-monotone-absorption.inc","gt9x16-prod3-ma2-wire-monotone-constants.inc"):
  shutil.copy2(EXP/"generated"/name,dst/name)
 manifest=json.loads((dst/"SOURCE-MANIFEST.json").read_text());manifest["wire_monotone_shared_abi"]={"placement":"reversed" if rev else "normal","installed_sources":installed,"boundary":"two forwards plus r exact-wire fanout plus PK ingress/MA2/ciphertext exact-wire egress"};(dst/"SOURCE-MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n");sums(dst)
def main():
 p=argparse.ArgumentParser();p.add_argument("--campaign-root",type=Path,required=True);p.add_argument("--normal-source",required=True);p.add_argument("--reversed-source",required=True);p.add_argument("--normal-implementation",required=True);p.add_argument("--reversed-implementation",required=True);a=p.parse_args();root=a.campaign_root.resolve();marker=json.loads((root/".ntruplus-campaign.json").read_text());
 if marker.get("supercop_version")!=read_lock()["version"]:raise SystemExit("campaign lock mismatch")
 base=root/"crypto_kem/ntruplus1152";install(base/a.normal_source,base/a.normal_implementation,False);install(base/a.reversed_source,base/a.reversed_implementation,True);print("installed wire-monotone shared ABI placements")
if __name__=="__main__":main()
