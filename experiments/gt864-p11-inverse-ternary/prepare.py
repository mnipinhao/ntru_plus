#!/usr/bin/env python3
"""Create isolated P10 baseline and P11 candidate packages."""

import hashlib
import io
import shutil
import subprocess
import tarfile
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BUILD = P / "build"
REV = "dd8c3146"
REL = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

subprocess.run(["python3", str(P / "model.py")], check=True)
subprocess.run(["python3", str(P / "generate.py")], check=True)

for name in ("baseline", "candidate"):
    destination = BUILD / name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    archive = subprocess.check_output(["git", "archive", REV, REL], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            target = destination / Path(member.name).relative_to(REL)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tar.extractfile(member).read())

candidate = BUILD / "candidate"
shutil.copyfile(P / "candidate-main.S", candidate / "gt864_p11_inverse16_lazy.S")
shutil.copyfile(P / "candidate-tail.S", candidate / "gt864_p11_inverse_tail_lazy.S")
shutil.copyfile(P / "candidate-route.alloc.S", candidate / "gt864_p11_route_ternary.S")

makefile = candidate / "Makefile"
text = makefile.read_text()
text = text.replace(
    "NATIVE_OBJECTS += gt864_crepmod3_raw.o",
    "NATIVE_OBJECTS += gt864_p11_inverse16_lazy.o gt864_p11_inverse_tail_lazy.o gt864_p11_route_ternary.o gt864_crepmod3_raw.o",
    1,
)
makefile.write_text(text)

wrapper = candidate / "gt864_native_public.S"
text = wrapper.read_text()
start = text.index(".global C(gt864_inverse_ternary_asm)")
prefix, block = text[:start], text[start:]
block = block.replace("bl C(lazy_i16)", "bl C(p11_lazy_i16)")
block = block.replace("bl C(lazy_itail)", "bl C(p11_lazy_itail)")
old = "    // P8: one raw-to-ternary pass; constants stay resident.\n    mov x0, x19\n    bl C(gt864_crepmod3_raw)"
new = "    // P11: consume scratch-major terminal records and write ternary output.\n    mov x0, x19\n    mov x1, x25\n    bl C(p11_route_ternary)"
assert old in block
block = block.replace(old, new, 1)
wrapper.write_text(prefix + block)


def refresh_manifest(package: Path) -> None:
    manifest = package / "SOURCE-MANIFEST.sha256"
    entries = []
    for line in manifest.read_text().splitlines():
        if not line.strip():
            continue
        path = line.split(None, 1)[1]
        entries.append(path)
    for path in ("gt864_p11_inverse16_lazy.S", "gt864_p11_inverse_tail_lazy.S", "gt864_p11_route_ternary.S"):
        if path not in entries:
            entries.append(path)
    manifest.write_text("".join(f"{hashlib.sha256((package / path).read_bytes()).hexdigest()}  {path}\n" for path in entries))


refresh_manifest(candidate)
shutil.copyfile(P / "test.c", BUILD / "test.c")
shutil.copyfile(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c", P / "malformed.c")
probe = (ROOT / "experiments/gt864-p8-raw-ternary/build/probe.S")
if probe.exists():
    shutil.copyfile(probe, BUILD / "probe.S")
else:
    source = (ROOT / "experiments/gt864-native-asm/integration/probe_inverse.S").read_text()
    (BUILD / "probe.S").write_text(source.replace("gt864_inverse_rinv_asm", "gt864_inverse_ternary_asm"))
print(BUILD)
