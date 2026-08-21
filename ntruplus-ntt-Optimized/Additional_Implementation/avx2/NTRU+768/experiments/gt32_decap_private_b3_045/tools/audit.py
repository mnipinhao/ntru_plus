#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

SYMBOLS = ("ntruplus768_basemul_scale_m_avx2",
           "ntruplus768_basemul_general_m_avx2",
           "ntruplus768_basemul_general_m_decap_avx2",
           "ntruplus768_unpack_m_body_avx2", "ntruplus768_dec_impl",
           "ntruplus768_enc_derand_impl")

def nm(path: Path) -> dict[str, int]:
    text = subprocess.check_output(["nm", "-n", str(path)], text=True)
    return {f[2]: int(f[0], 16) for line in text.splitlines()
            if len((f := line.split())) == 3 and f[2] in SYMBOLS}

def sizes(path: Path) -> dict[str, int]:
    text = subprocess.check_output(["size", "-A", str(path)], text=True)
    return {f[0]: int(f[1]) for line in text.splitlines()
            if len((f := line.split())) >= 2 and f[0] in (".text", ".rodata")}

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--control",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args(); out={"control":{"addresses":nm(a.control),"sections":sizes(a.control)},
                           "candidate":{"addresses":nm(a.candidate),"sections":sizes(a.candidate)}}
    if out["control"] != out["candidate"]: raise SystemExit(json.dumps(out,indent=2))
    a.output.write_text(json.dumps(out,indent=2)+"\n"); print("geometry: PASS")
if __name__ == "__main__": main()

