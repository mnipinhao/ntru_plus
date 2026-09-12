#!/usr/bin/env python3
"""Generate call-site instrumented KEM source without changing arithmetic objects."""

from __future__ import annotations

import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text()
gt = sys.argv[2] == "gt"
groups = [
    "Forward", "BaseInv", "BaseMul_R0", "BaseMul_Rinv", "BaseMulAdd",
    "Inverse", "ToBytes_full", "ToBytes_small", "FromBytes_checked", "CBD",
    "SOTP_encode", "SOTP_decode", "Triple", "Sub", "Crepmod3", "hash_f",
    "hash_g", "hash_h", "SHAKE_sampling", "RNG", "cleanup", "Inverse_to_ternary",
]
mapping = {
    "poly_ntt": ("Forward", "gt_d1_poly_ntt" if gt else "poly_ntt", False),
    "poly_baseinv": ("BaseInv", "gt864_native_poly_baseinv" if gt else "poly_baseinv", True),
    "poly_basemul": ("BaseMul_R0", "gt_d1_poly_basemul" if gt else "poly_basemul", False),
    "poly_basemul_add": ("BaseMulAdd", "gt_d1_poly_basemul_add" if gt else "poly_basemul_add", False),
    "poly_cbd1": ("CBD", "poly_cbd1", False),
    "poly_sotp_encode": ("SOTP_encode", "poly_sotp_encode", False),
    "poly_sotp_decode": ("SOTP_decode", "poly_sotp_decode", True),
    "poly_triple": ("Triple", "poly_triple", False),
    "poly_sub": ("Sub", "poly_sub", False),
    "poly_crepmod3": ("Crepmod3", "poly_crepmod3", False),
    "hash_f": ("hash_f", "hash_f", False),
    "hash_g": ("hash_g", "hash_g", False),
    "hash_h": ("hash_h", "hash_h", False),
    "shake256": ("SHAKE_sampling", "shake256", False),
    "randombytes": ("RNG", "randombytes", False),
    "secure_clear": ("cleanup", "secure_clear", False),
}
if gt:
    mapping.update({
        "gt864_native_inverse_ternary": ("Inverse_to_ternary", "gt864_native_inverse_ternary", False),
        "gt864_native_basemul_for_inverse": ("BaseMul_Rinv", "gt864_native_basemul_for_inverse", False),
        "gt864_native_inverse": ("Inverse", "gt864_native_inverse", False),
        "gt864_fr0_tobytes_full": ("ToBytes_full", "gt864_fr0_tobytes_full", False),
        "gt864_fr0_tobytes_small": ("ToBytes_small", "gt864_fr0_tobytes_small", False),
        "gt864_fr0_frombytes_checked": ("FromBytes_checked", "gt864_fr0_frombytes_checked", True),
    })
else:
    mapping.update({
        "poly_basemul_scale": ("BaseMul_Rinv", "poly_basemul_scale", False),
        "poly_invntt_scale": ("Inverse", "poly_invntt_scale", False),
        "poly_tobytes": ("ToBytes_full", "poly_tobytes", False),
        "poly_frombytes": ("FromBytes_checked", "poly_frombytes", True),
    })

header = "\n#include <stdint.h>\nuint64_t prof_start(void);\nvoid prof_end(int,uint64_t);\n"
if gt:
    header += '#include "gt864_poly_api.h"\n'
for name, (group, real, returns_int) in mapping.items():
    if returns_int:
        body = f"uint64_t _pt=prof_start(); int _pr={real}(__VA_ARGS__); prof_end({groups.index(group)},_pt); _pr;"
        header += f"#define {name}(...) ({{ {body} }})\n"
    else:
        body = f"uint64_t _pt=prof_start(); {real}(__VA_ARGS__); prof_end({groups.index(group)},_pt);"
        header += f"#define {name}(...) do {{ {body} }} while(0)\n"

marker = "\n/*************************************************" if gt else "\n#ifdef SUPERCOP"
position = source.index(marker)
print(source[:position] + header + source[position:])
