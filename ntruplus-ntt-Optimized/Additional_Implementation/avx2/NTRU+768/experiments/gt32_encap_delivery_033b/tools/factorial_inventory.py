#!/usr/bin/env python3
"""Record A/B/C ELF and selected hot-symbol geometry."""

from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

HOT = ["gt033b_factorial_encap", "ntruplus768_unpack_m_body_avx2",
       "ntruplus768_ntt_frontend_avx2", "ntruplus768_ntt_m_avx2",
       "ntruplus768_pack_m_lazy10788_avx2",
       "ntruplus768_pack_m_highrange12699_avx2",
       "ntruplus768_basemul_general_m_avx2", "gt32_032_b3_addm_normal"]

def table(path: Path) -> dict[str, tuple[int, int]]:
    lines = subprocess.check_output(["nm", "-S", "--defined-only", str(path)], text=True)
    return {f[3]: (int(f[0],16), int(f[1],16)) for line in lines.splitlines()
            if len((f := line.split())) >= 4}

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--build",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    out={"schema":"gt32-encap-delivery-033b-factorial-addresses-v1","variants":{}}
    for variant in "abc":
        path=a.build/"factorial"/variant/"bench"; symbols=table(path)
        hot={name:{"start":symbols[name][0],"size":symbols[name][1],
                   "page_offset":symbols[name][0]%4096}
             for name in HOT if name in symbols}
        out["variants"][variant]={"elf_bytes":path.stat().st_size,"hot_symbols":hot}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out["variants"],indent=2,sort_keys=True))
if __name__=="__main__": main()
