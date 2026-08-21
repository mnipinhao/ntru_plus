#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

PROFILES = ("A", "D", "S", "G", "DS", "DG", "SG", "DSG")
SYMBOLS = ("ntruplus768_unpack_m_body_avx2", "ntruplus768_unpack3_m_avx2",
           "ntruplus768_basemul_scale_m_avx2",
           "ntruplus768_basemul_general_m_avx2",
           "ntruplus768_dec_impl")

def addresses(path: Path) -> dict[str, int]:
    out = subprocess.check_output(["nm", "-n", str(path)], text=True)
    values = {}
    for line in out.splitlines():
        f = line.split()
        if len(f) == 3 and f[2] in SYMBOLS:
            values[f[2]] = int(f[0], 16)
    return values

def sections(path: Path) -> dict[str, int]:
    out = subprocess.check_output(["size", "-A", str(path)], text=True)
    return {f[0]: int(f[1]) for line in out.splitlines()
            if len((f := line.split())) >= 2 and f[0] in (".text", ".rodata")}

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--build", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    images = {}
    for profile in PROFILES:
        path = a.build / f"measure-{profile}"
        images[profile] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                           "addresses": addresses(path), "sections": sections(path)}
    reference = images["A"]
    for profile in PROFILES[1:]:
        if images[profile]["addresses"] != reference["addresses"]:
            raise SystemExit(f"address mismatch: {profile}")
        if images[profile]["sections"] != reference["sections"]:
            raise SystemExit(f"section-size mismatch: {profile}")
    a.output.write_text(json.dumps({"schema": "gt32-decap-ltc-044-geometry-v1",
                                    "images": images}, indent=2) + "\n")
    print("geometry: PASS (all selected addresses and section sizes equal)")

if __name__ == "__main__": main()

