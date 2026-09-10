"""Create isolated P2 and P3-A packages without modifying production."""

import hashlib
import json
import shutil
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = P / "build"

OLD_WRAPPER = """    mov x26, #27
    mov x27, x19
.Linv_center:
    mov x0, x27
    bl C(center32)
    add x27, x27, #64
    subs x26, x26, #1
    b.ne .Linv_center
"""
NEW_WRAPPER = """    // P3-A: one complete normalization pass; constants stay resident.
    mov x0, x19
    bl C(center864)
"""


def source_files(manifest: Path) -> list[str]:
    return [line.split("  ", 1)[1] for line in manifest.read_text().splitlines()]


def write_manifest(package: Path, files: list[str]) -> None:
    lines = [hashlib.sha256((package / file).read_bytes()).hexdigest() + "  " + file for file in files]
    (package / "SOURCE-MANIFEST.sha256").write_text("\n".join(lines) + "\n")


BUILD.mkdir(exist_ok=True)
audit = {}
for name in ("p2", "p3a"):
    package = BUILD / name
    if package.exists():
        shutil.rmtree(package)
    shutil.copytree(
        PRODUCTION,
        package,
        ignore=shutil.ignore_patterns("*.o", "*.so", "PQCkemKAT*", "test_kem", "PQCgenKAT_kem"),
    )
    files = source_files(PRODUCTION / "SOURCE-MANIFEST.sha256")
    changed = []
    if name == "p3a":
        wrapper = (package / "gt864_native_public.S").read_text()
        assert wrapper.count(OLD_WRAPPER) == 1
        (package / "gt864_native_public.S").write_text(wrapper.replace(OLD_WRAPPER, NEW_WRAPPER))
        (package / "gt864_native_center864.S").write_bytes((P / "candidate.opt.S").read_bytes())
        makefile = (package / "Makefile").read_text()
        assert makefile.count("gt864_native_center32.o") == 1
        (package / "Makefile").write_text(
            makefile.replace("gt864_native_center32.o", "gt864_native_center864.o")
        )
        files.remove("gt864_native_center32.S")
        files.append("gt864_native_center864.S")
        changed = ["Makefile", "gt864_native_public.S", "gt864_native_center864.S"]
    write_manifest(package, files)
    audit[name] = {
        "source": "current production P2",
        "features": [] if name == "p2" else ["constant-resident center864"],
        "changed": changed,
        "hashes": {file: hashlib.sha256((package / file).read_bytes()).hexdigest() for file in changed},
    }

(P / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
print(json.dumps(audit, indent=2))
