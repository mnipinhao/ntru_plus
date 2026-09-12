#!/usr/bin/env python3
"""Create isolated P13 baseline/candidate packages from frozen production."""

from pathlib import Path
import hashlib
import io
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BUILD = HERE / "build"
REVISION = "dd8c3146"
PACKAGE = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

archive = subprocess.check_output(["git", "archive", REVISION, PACKAGE], cwd=REPO)
for label in ("baseline", "candidate"):
    destination = BUILD / label
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            target = destination / Path(member.name).relative_to(PACKAGE)
            target.parent.mkdir(parents=True, exist_ok=True)
            extracted = tar.extractfile(member)
            assert extracted is not None
            target.write_bytes(extracted.read())

wrapper = BUILD / "candidate/gt864_native_public.S"
text = wrapper.read_text()
old_init = """    add x9, sp, #1536
    mov x10, #16
.Lp8inv_init_tail:
    stp xzr, xzr, [x9], #16
    subs x10, x10, #1
    b.ne .Lp8inv_init_tail
"""
new_init = """    // P13-A: exact 256-byte padding clear, eight full-vector stores.
    movi v0.16b, #0
    add x9, sp, #1536
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
"""
old_wipe = """    mov x9, sp
    mov x10, #112
.Lp8inv_wipe:
    stp xzr, xzr, [x9], #16
    subs x10, x10, #1
    b.ne .Lp8inv_wipe
"""
new_wipe = """    // P13-A: exact 1792-byte wipe, 128 bytes per fixed iteration.
    movi v0.16b, #0
    mov x9, sp
    mov x10, #14
.Lp13inv_wipe:
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    stp q0, q0, [x9], #32
    subs x10, x10, #1
    b.ne .Lp13inv_wipe
"""
assert text.count(old_init) == 1
assert text.count(old_wipe) == 1
wrapper.write_text(text.replace(old_init, new_init).replace(old_wipe, new_wipe))

manifest = BUILD / "candidate/SOURCE-MANIFEST.sha256"
lines = []
for line in manifest.read_text().splitlines():
    digest, path = line.split(None, 1)
    path = path.strip()
    if path == "gt864_native_public.S":
        digest = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    lines.append(f"{digest}  {path}")
manifest.write_text("\n".join(lines) + "\n")

for name in ("test.c", "pi-bench.c", "malformed.c"):
    source = REPO / "experiments/gt864-p11-inverse-ternary" / name
    shutil.copyfile(source, HERE / name)
shutil.copyfile(
    REPO / "experiments/gt864-p11-inverse-ternary/build/probe.S",
    HERE / "probe.S",
)

print(BUILD)
