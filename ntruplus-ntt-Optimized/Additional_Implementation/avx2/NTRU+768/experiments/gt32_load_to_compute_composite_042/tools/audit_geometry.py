#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

def size(path: Path, symbol: str) -> int:
    text = subprocess.run(["nm", "-S", str(path)], check=True,
                          capture_output=True, text=True).stdout
    for line in text.splitlines():
        f = line.split()
        if len(f) >= 4 and f[3] == symbol: return int(f[1], 16)
    raise ValueError((path, symbol))

def addresses(path: Path) -> dict[str, int]:
    text = subprocess.run(["nm", "-n", str(path)], check=True,
                          capture_output=True, text=True).stdout
    wanted = {"gt042_encap_common", "ntruplus768_unpack_m_avx2",
              "gt042d_ntruplus768_unpack_m_avx2",
              "ntruplus768_basemul_general_m_avx2",
              "gt042b_ntruplus768_basemul_general_m_avx2"}
    return {f[2]: int(f[0], 16) for line in text.splitlines()
            if len((f := line.split())) >= 3 and f[2] in wanted}

def main() -> None:
    p = argparse.ArgumentParser()
    for name in ("control-pack", "candidate-pack", "control-b3", "candidate-b3",
                 "normal", "reversed", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    a = p.parse_args()
    normal = addresses(a.normal)
    reversed_ = addresses(a.reversed)
    out = {
        "decode_body_sizes": [
            size(a.control_pack, "ntruplus768_unpack_m_body_avx2"),
            size(a.candidate_pack, "ntruplus768_unpack_m_body_avx2")],
        "decode_wrapper_sizes": [
            size(a.control_pack, "ntruplus768_unpack_m_avx2"),
            size(a.candidate_pack, "ntruplus768_unpack_m_avx2")],
        "b3_sizes": [
            size(a.control_b3, "ntruplus768_basemul_general_m_avx2"),
            size(a.candidate_b3, "ntruplus768_basemul_general_m_avx2")],
        "common_caller_sizes": [size(a.normal, "gt042_encap_common"),
                                size(a.reversed, "gt042_encap_common")],
        "normal_addresses": normal,
        "reversed_addresses": reversed_,
    }
    if out["decode_body_sizes"][0] != out["decode_body_sizes"][1]: raise SystemExit(out)
    if out["decode_wrapper_sizes"][0] != out["decode_wrapper_sizes"][1]: raise SystemExit(out)
    if out["b3_sizes"][0] != out["b3_sizes"][1]: raise SystemExit(out)
    if out["common_caller_sizes"][0] != out["common_caller_sizes"][1]: raise SystemExit(out)
    if normal["gt042_encap_common"] != reversed_["gt042_encap_common"]: raise SystemExit(out)
    if normal["ntruplus768_unpack_m_avx2"] != reversed_["gt042d_ntruplus768_unpack_m_avx2"]: raise SystemExit(out)
    if normal["gt042d_ntruplus768_unpack_m_avx2"] != reversed_["ntruplus768_unpack_m_avx2"]: raise SystemExit(out)
    if normal["ntruplus768_basemul_general_m_avx2"] != reversed_["gt042b_ntruplus768_basemul_general_m_avx2"]: raise SystemExit(out)
    if normal["gt042b_ntruplus768_basemul_general_m_avx2"] != reversed_["ntruplus768_basemul_general_m_avx2"]: raise SystemExit(out)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, indent=2, sort_keys=True))
if __name__ == "__main__": main()
