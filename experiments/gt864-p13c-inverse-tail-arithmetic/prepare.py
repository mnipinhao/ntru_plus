#!/usr/bin/env python3
"""Create frozen P13-B production baseline and isolated P13-C package."""
from pathlib import Path
import hashlib
import io
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
REV = "562a91e6"
PKG = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

if BUILD.exists():
    raise SystemExit(f"refusing to overwrite existing {BUILD}; remove this gitignored directory explicitly")
archive = subprocess.check_output(["git", "archive", REV, PKG], cwd=ROOT)
for label in ("baseline", "candidate"):
    directory = BUILD / label
    directory.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            target = directory / Path(member.name).relative_to(PKG)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tf.extractfile(member).read())

candidate = BUILD / "candidate"
assembly = (HERE / "candidate.opt.S").read_text().replace("p13c_itail", "lazy_itail")
(candidate / "gt864_native_inverse_tail_lazy.S").write_text(
    "/* P13-C Slothy allocated and bounded-window scheduled tail core. */\n" + assembly)
native = candidate / "gt864_native.c"
source = native.read_text()
old = "&gt864_inverse16_tail_scale_barrett[0][0][0]"
assert source.count(old) == 2
native.write_text(source.replace(old, "&gt864_p13b_tail[0][0]"))

manifest = candidate / "SOURCE-MANIFEST.sha256"
names = [line.split(None, 1)[1].strip() for line in manifest.read_text().splitlines()]
manifest.write_text("".join(
    f"{hashlib.sha256((candidate/name).read_bytes()).hexdigest()}  {name}\n"
    for name in names))

for name in ("test.c", "probe.S", "malformed.c", "pi-bench.c", "run_pi5.py"):
    shutil.copyfile(ROOT / "experiments/gt864-p13b-inverse16-arithmetic" / name, HERE / name)
test = HERE / "test.c"
test_source = test.read_text().replace(
    "&gt864_inverse16_tail_scale_barrett[0][0][0])",
    "&gt864_p13b_tail[0][0])")
assert test_source != test.read_text()
test.write_text(test_source)
print(BUILD)
