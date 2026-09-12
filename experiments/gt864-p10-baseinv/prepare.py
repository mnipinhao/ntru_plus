#!/usr/bin/env python3
"""Create frozen P9 and isolated P10 packages without touching production."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = HERE / "build"


def extract_physical(source: str, candidate: str, public: str) -> str:
    body = source.split(f"{candidate}_slothy_start:", 1)[1].split(f"{candidate}_slothy_end:", 1)[0]
    instructions = []
    for line in body.splitlines():
        code = line.split("//", 1)[0].strip()
        if code and not code.endswith(":"):
            instructions.append("    " + code)
    return "\n".join([
        f"/* P10-A: Slothy A76 allocation from {candidate}; no spill. */",
        "#ifdef __APPLE__",
        f"#define {public} _{public}",
        "#endif",
        ".text",
        f".global {public}",
        f"{public}:",
        *instructions,
        "    ret",
        "",
    ])


def update_manifest(root: Path) -> None:
    lines = []
    for line in (root / "SOURCE-MANIFEST.sha256").read_text().splitlines():
        name = line.split("  ", 1)[1]
        lines.append(hashlib.sha256((root / name).read_bytes()).hexdigest() + "  " + name)
    (root / "SOURCE-MANIFEST.sha256").write_text("\n".join(lines) + "\n")


if BUILD.exists():
    shutil.rmtree(BUILD)
BUILD.mkdir()
ignore = shutil.ignore_patterns("*.o", "*.so", "test_kem", "PQCgenKAT_kem", "PQCkemKAT_*.rsp")
for name in ("p9", "p10"):
    shutil.copytree(PROD, BUILD / name, ignore=ignore)

allocated = (HERE / "candidate.alloc.S").read_text()
p10 = BUILD / "p10"
(p10 / "gt864_native_baseinv_num.S").write_text(extract_physical(allocated, "p10_num_pair", "binv_num_pair"))
(p10 / "gt864_native_baseinv_finish.S").write_text(extract_physical(allocated, "p10_finish_tile", "binv_finish_tile"))
(p10 / "gt864_native_baseinv_inverse.S").write_text(extract_physical(allocated, "p10_inverse3", "binv_inverse3"))

wrapper_path = p10 / "gt864_native_public.S"
wrapper = wrapper_path.read_text()
num_anchor = """    mov x25, #0                // chain
    mov x27, x19
    mov x28, x20
.Lbinv_chain:
"""
num_replacement = """    mov x25, #0                // chain
    mov x27, x19
    mov x28, x20
    // P10 repeated numerator leaf ABI: v30=q and v31=-q^-1 mod 2^16.
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
.Lbinv_chain:
"""
finish_anchor = """    COPY_TRIPLE x22, x24
    mov x25, #0
    mov x27, x19
.Lbinv_finish_chain:
"""
finish_replacement = """    COPY_TRIPLE x22, x24
    mov x25, #0
    mov x27, x19
    // Middle batch kernels clobber volatile SIMD state; reload the finish constants.
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
.Lbinv_finish_chain:
"""
assert wrapper.count(num_anchor) == 1
assert wrapper.count(finish_anchor) == 1
wrapper = wrapper.replace(num_anchor, num_replacement).replace(finish_anchor, finish_replacement)
wrapper_path.write_text(wrapper)
update_manifest(p10)

support = BUILD / "support"
support.mkdir()
native = ROOT / "experiments/gt864-native-asm"
for source in [
    native / "baseinv-p2-two-tile/pi-bench.c",
    native / "integration/test_baseinv.c",
    native / "integration/probe_baseinv.S",
    native / "kem-malformed-transcript.c",
    native / "profile-kem.c",
    ROOT / "experiments/gt864-official-profile-p8/generate_profile_kem.py",
    ROOT / "experiments/gt864-official-profile-p8/full_harness.c",
    ROOT / "experiments/gt864-official-profile-p8/profile_harness.c",
]:
    shutil.copy2(source, support / source.name)
baseinv_test = (native / "integration/test_baseinv.c").read_text()
baseinv_test = baseinv_test.replace(
    "for(int i=0;i<864;i++)in.v[i]=(int16_t)rnd();",
    "/* P10 is the production-KEM BaseInv contract: the proved K1 Forward "
    "producer cube is |x| <= 28765, not arbitrary int16. */\n"
    "        for(int i=0;i<864;i++)in.v[i]=(int16_t)((int32_t)(rnd()%57531u)-28765);",
).replace(
    "(int16_t[]){0,1,-1,32767,-32768,3457,-3457,1728}[t]",
    "(int16_t[]){0,1,-1,28765,-28765,26930,-26930,1728}[t]",
).replace(
    "The proved Keygen-only consumer contract is\n             * [-1972,1972]",
    "The P10 KEM-only consumer closure permits\n             * [-2550,2550]",
).replace(
    "x>=-1972&&x<=1972&&y>=-1972&&y<=1972&&w>=-1972&&w<=1972",
    "x>=-2550&&x<=2550&&y>=-2550&&y<=2550&&w>=-2550&&w<=2550",
)
(support / "test_baseinv_p10.c").write_text(baseinv_test)
shutil.copytree(ROOT / "experiments/gt864-official-profile-p8/compat", support / "compat")

audit = {
    "baseline": "current P9 production snapshot",
    "candidate_changes": {
        name: hashlib.sha256((p10 / name).read_bytes()).hexdigest()
        for name in [
            "gt864_native_baseinv_num.S",
            "gt864_native_baseinv_finish.S",
            "gt864_native_baseinv_inverse.S",
            "gt864_native_public.S",
            "SOURCE-MANIFEST.sha256",
        ]
    },
    "fixed_vector_leaf_abi": {"v30": 3457, "v31": -12929},
    "production_modified": False,
}
(HERE / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
