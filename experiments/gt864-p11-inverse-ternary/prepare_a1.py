#!/usr/bin/env python3
"""Create an isolated P11-A1 package from the frozen P10 baseline."""

import hashlib
import shutil
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
BUILD = P / "build"
subprocess.run(["python3", str(P / "prepare.py")], check=True)
subprocess.run(["python3", str(P / "generate_a1.py")], check=True)
subprocess.run(["python3", str(P / "model_a1.py")], check=True)
source = BUILD / "baseline"
candidate = BUILD / "candidate-a1"
if candidate.exists():
    shutil.rmtree(candidate)
shutil.copytree(source, candidate)
shutil.copyfile(P / "candidate-main-a1.S", candidate / "gt864_p11_inverse16_lazy.S")
shutil.copyfile(P / "candidate-tail.S", candidate / "gt864_p11_inverse_tail_lazy.S")
shutil.copyfile(P / "candidate-route-a1.alloc.S", candidate / "gt864_p11_route_ternary.S")

makefile = candidate / "Makefile"
text = makefile.read_text().replace(
    "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    "NATIVE_OBJECTS += gt864_p11_inverse16_lazy.o gt864_p11_inverse_tail_lazy.o gt864_p11_route_ternary.o gt864_crepmod3_raw.o",
    1,
)
makefile.write_text(text)

wrapper = candidate / "gt864_native_public.S"
text = wrapper.read_text()
start = text.index(".global C(gt864_inverse_ternary_asm)")
prefix, block = text[:start], text[start:]
old_address = "    add x0, x19, x26, lsl #1\n    mov x8, #24\n    madd x0, x27, x8, x0"
new_address = "    mov x8, #16\n    madd x0, x26, x8, x19\n    add x0, x0, x27, lsl #3"
assert old_address in block
block = block.replace(old_address, new_address, 1)
block = block.replace("bl C(lazy_i16)", "bl C(p11_lazy_i16)")
block = block.replace("bl C(lazy_itail)", "bl C(p11_lazy_itail)")
old = "    // P8: one raw-to-ternary pass; constants stay resident.\n    mov x0, x19\n    bl C(gt864_crepmod3_raw)"
new = "    // P11-A1: reverse-consume in-place main records; tail remains in scratch.\n    mov x0, x19\n    mov x1, x19\n    mov x2, x25\n    bl C(p11_route_ternary)"
assert old in block
block = block.replace(old, new, 1)
wrapper.write_text(prefix + block)

manifest = candidate / "SOURCE-MANIFEST.sha256"
paths = [line.split(None, 1)[1] for line in manifest.read_text().splitlines() if line.strip()]
for path in ("gt864_p11_inverse16_lazy.S", "gt864_p11_inverse_tail_lazy.S", "gt864_p11_route_ternary.S"):
    if path not in paths:
        paths.append(path)
manifest.write_text("".join(f"{hashlib.sha256((candidate/path).read_bytes()).hexdigest()}  {path}\n" for path in paths))
print(candidate)
