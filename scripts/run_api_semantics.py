#!/usr/bin/env python3
"""Build and run KEM API, invalid-input, immutability, and canary checks."""
from __future__ import annotations
import argparse,json,subprocess,tempfile
from datetime import datetime,timezone
from pathlib import Path
from supercop_workflow import REPO_ROOT,read_lock,sha256_file
WIRE_COMMON=("add.s","baseinv.s","basemul.s","cbd.s","crepmod3.s","invntt.s","ntt.s","pack.s",
             "consts.c","kem.c","poly.c","symmetric.c","fips202.c","KeccakP-1600-AVX2.s",
             "top_split_adapter.c","gt9x16_prod3_aos_branch0.S")
def main()->int:
  ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--campaign-root",type=Path,required=True)
  ap.add_argument("--parameter",choices=("768","1152"),required=True); ap.add_argument("--implementation",required=True)
  ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
  if a.output.exists(): raise SystemExit(f"refusing to overwrite {a.output}")
  root=a.campaign_root.resolve(); marker=json.loads((root/".ntruplus-campaign.json").read_text())
  if marker.get("supercop_version")!=read_lock()["version"]: raise SystemExit("campaign mismatch")
  impl=root/"crypto_kem"/f"ntruplus{a.parameter}"/a.implementation
  if a.parameter=="1152":
    man=json.loads((impl/"SOURCE-MANIFEST.json").read_text()); names=list(WIRE_COMMON)
    names+=list(man["wire_monotone_native_rebase2"]["installed_sources"].values())
    names+=list(man.get("exp017_serializer_v2_native",{}).get("installed_sources",{}).values())
    sources=[impl/n for n in dict.fromkeys(names)]
  else:
    sources=sorted(p for p in impl.iterdir() if p.suffix in (".c",".s",".S") and p.name!="ntruplus_bench.c")
  includes=list((root/"bench").glob("*/include")); include=includes[0]
  kat=REPO_ROOT/"ntruplus-ntt-Optimized/Optimized_Implementation/NTRU+768/kat"
  compat=REPO_ROOT/("ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
                    "experiments/avx2_gt9x16_official_001/tests/kat_compat")
  with tempfile.TemporaryDirectory(prefix=f"ntruplus{a.parameter}-api-") as temp:
    binary=Path(temp)/"api-semantics"
    cmd=["cc","-o",str(binary),"-O2","-Wall","-Wextra","-Werror",
         "-Wno-sign-compare","-Wno-unused-parameter","-mavx2","-mbmi2","-mpopcnt","-maes",
         "-march=native","-mtune=native",f"-I{compat}",f"-I{impl}",f"-I{kat}",f"-I{include/'amd64'}",f"-I{include}",
         str(REPO_ROOT/"bench/api_semantics.c"),str(kat/"aes.c"),str(kat/"rng.c"),*(str(p) for p in sources)]
    subprocess.run(cmd,cwd=impl,check=True); run=subprocess.run([str(binary)],text=True,stdout=subprocess.PIPE,check=True)
  source_manifest = impl/"SOURCE-MANIFEST.json"
  rec={"schema":"ntruplus-api-semantics/v1","created_at":datetime.now(timezone.utc).isoformat(),
       "parameter":int(a.parameter),"implementation":a.implementation,"valid_trials":32,"passed":True,
       "checks":["valid roundtrip","tampered ciphertext rejection and zeroization","invalid public-key rejection and zeroization","input immutability","output canaries"],
       "alias_note":"public KEM API does not declare overlapping-buffer support; aliases are not claimed", "stdout":run.stdout.strip(),
       "manifest_sha256":sha256_file(source_manifest) if source_manifest.is_file() else None}
  a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
  print(run.stdout.strip()); return 0
if __name__=="__main__": raise SystemExit(main())
