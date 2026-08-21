#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

SYMBOLS = ("ntruplus768_keypair_impl", "ntruplus768_enc_derand_impl",
           "ntruplus768_dec_impl", "ntruplus768_unpack_m_body_avx2",
           "ntruplus768_basemul_scale_m_avx2",
           "ntruplus768_basemul_general_m_avx2")

def addresses(path):
    out = subprocess.check_output(["nm", "-n", str(path)], text=True)
    return {f[2]: int(f[0], 16) for line in out.splitlines()
            if len((f := line.split())) == 3 and f[2] in SYMBOLS}

def sections(path):
    out = subprocess.check_output(["size", "-A", str(path)], text=True)
    return {f[0]: int(f[1]) for line in out.splitlines()
            if len((f := line.split())) >= 2 and f[0] in (".text", ".rodata")}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--control",type=Path,required=True)
    p.add_argument("--candidate",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    data={}
    for name,path in (("A",a.control),("G",a.candidate)):
        data[name]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                    "addresses":addresses(path),"sections":sections(path)}
    if data["A"]["addresses"] != data["G"]["addresses"]: raise SystemExit("address mismatch")
    if data["A"]["sections"] != data["G"]["sections"]: raise SystemExit("section mismatch")
    a.output.write_text(json.dumps({"schema":"gt32-shared-b3-046-geometry-v1","images":data},indent=2)+"\n")
    print("geometry: PASS")
if __name__ == "__main__": main()
