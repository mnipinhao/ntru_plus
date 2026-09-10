"""Create isolated P1/P2-A/P2-B/P2-AB packages without touching production."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = P / "build"
BUILD.mkdir(exist_ok=True)

def clean_slothy(path):
    inside = False
    out = []
    for line in path.read_text().splitlines():
        if "binv_num_pair_slothy_start:" in line:
            inside = True
            out += ["/* P2-A: two tiles share q/qinv/R constants; Slothy A76 allocation. */", ".text", ".global binv_num_pair", "binv_num_pair:"]
            continue
        if "binv_num_pair_slothy_end:" in line:
            break
        instruction = line.split("//", 1)[0].strip()
        if inside and instruction and not instruction.endswith(":"):
            out.append("    " + instruction)
    out.append("    ret")
    return "\n".join(out) + "\n"

old_num = """    bl C(binv_num_tile)
    add x27, x27, #48
    add x28, x28, #48
    add x21, x21, #16
    add x26, x26, #1
"""
new_num = """    bl C(binv_num_pair)
    add x27, x27, #96
    add x28, x28, #96
    add x21, x21, #32
    add x26, x26, #2
"""
old_scan = """    add x9, x23, #528
    mov x10, #24
    mov w11, #0
.Lbinv_scan:
    ldrh w8, [x9], #2
    cmp w8, #0
    cset w8, eq
    orr w11, w11, w8
    subs x10, x10, #1
    b.ne .Lbinv_scan
    cbnz w11, .Lbinv_fail
"""
new_scan = """    add x9, x23, #528
    ldp q0, q1, [x9]
    ldr q2, [x9, #32]
    cmeq v0.8h, v0.8h, #0
    cmeq v1.8h, v1.8h, #0
    cmeq v2.8h, v2.8h, #0
    orr v0.16b, v0.16b, v1.16b
    orr v0.16b, v0.16b, v2.16b
    umaxv h0, v0.8h
    umov w11, v0.h[0]
    cbnz w11, .Lbinv_fail
"""

variants = {"p1": set(), "p2a": {"pair"}, "p2b": {"scan"}, "p2ab": {"pair", "scan"}}
audit = {}
for name, features in variants.items():
    out = BUILD / name
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(PROD, out, ignore=shutil.ignore_patterns("*.o", "*.so", "PQCkemKAT*", "test_kem", "PQCgenKAT_kem"))
    # Freeze the baseline at the committed P1 state even after P2 is promoted.
    for file in ["gt864_native_baseinv_num.S", "gt864_native_public.S"]:
        repo_path = (PROD / file).relative_to(ROOT)
        content = subprocess.check_output(["git", "show", f"383a65ac:{repo_path}"], cwd=ROOT)
        (out / file).write_bytes(content)
    changed = []
    wrapper = (out / "gt864_native_public.S").read_text()
    if "pair" in features:
        assert wrapper.count(old_num) == 1
        wrapper = wrapper.replace(old_num, new_num)
        (out / "gt864_native_baseinv_num.S").write_text(clean_slothy(P / "candidate.opt.S"))
        changed.append("gt864_native_baseinv_num.S")
    if "scan" in features:
        assert wrapper.count(old_scan) == 1
        wrapper = wrapper.replace(old_scan, new_scan)
    if features:
        (out / "gt864_native_public.S").write_text(wrapper)
        changed.append("gt864_native_public.S")
    manifest = []
    for line in (PROD / "SOURCE-MANIFEST.sha256").read_text().splitlines():
        file = line.split("  ", 1)[1]
        manifest.append(hashlib.sha256((out / file).read_bytes()).hexdigest() + "  " + file)
    (out / "SOURCE-MANIFEST.sha256").write_text("\n".join(manifest) + "\n")
    audit[name] = {"features": sorted(features), "changed": sorted(changed), "source_hashes": {f: hashlib.sha256((out / f).read_bytes()).hexdigest() for f in changed}}
(P / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
