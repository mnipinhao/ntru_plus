#!/usr/bin/env python3
"""Create isolated production-shaped P3-A and P3-B packages."""

import hashlib
import json
import shutil
from pathlib import Path


P = Path(__file__).resolve().parent
ROOT = P.parents[2]
PRODUCTION = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = P / "build"

CENTER_CALL = """    // P3-A: one complete normalization pass; constants stay resident.
    mov x0, x19
    bl C(center864)
"""
CENTER_FUSED = """    // P3-B: main and tail I16 producers store centered coefficients directly.
"""


def source_files(manifest: Path) -> list[str]:
    return [line.split("  ", 1)[1] for line in manifest.read_text().splitlines()]


def write_manifest(package: Path, files: list[str]) -> None:
    lines = [hashlib.sha256((package / file).read_bytes()).hexdigest() + "  " + file for file in files]
    (package / "SOURCE-MANIFEST.sha256").write_text("\n".join(lines) + "\n")


def portable_source(path: Path, symbol: str) -> bytes:
    preamble = f"#ifdef __APPLE__\n#define {symbol} _{symbol}\n#endif\n\n"
    return (preamble + path.read_text()).encode()


BUILD.mkdir(exist_ok=True)
audit = {}
for name in ("p3a", "p3b"):
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
    if name == "p3b":
        wrapper_path = package / "gt864_native_public.S"
        wrapper = wrapper_path.read_text()
        assert wrapper.count(CENTER_CALL) == 1
        wrapper_path.write_text(wrapper.replace(CENTER_CALL, CENTER_FUSED))
        (package / "gt864_native_inverse16_lazy.S").write_bytes(
            portable_source(P / "main/candidate.opt.S", "lazy_i16")
        )
        (package / "gt864_native_inverse_tail_lazy.S").write_bytes(
            portable_source(P / "tail/candidate.opt.S", "lazy_itail")
        )
        makefile_path = package / "Makefile"
        makefile = makefile_path.read_text()
        assert makefile.count(" gt864_native_center864.o") == 1
        makefile_path.write_text(makefile.replace(" gt864_native_center864.o", ""))
        changed = [
            "Makefile",
            "gt864_native_public.S",
            "gt864_native_inverse16_lazy.S",
            "gt864_native_inverse_tail_lazy.S",
        ]
    write_manifest(package, files)
    audit[name] = {
        "source": "current GT production P3-A",
        "features": [] if name == "p3a" else [
            "producer-side pair packing",
            "producer-side centering",
            "no center864 call or object",
            "fixed-allocation bounded-window Slothy timing",
        ],
        "changed": changed,
        "hashes": {
            file: hashlib.sha256((package / file).read_bytes()).hexdigest()
            for file in changed
        },
    }

(P / "package-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
bench_source = (P.parent / "inverse-p3-center864/pi-bench.c").read_text()
old_label = 'candidate ? "p3a" : "p2"'
new_label = 'candidate ? "p3b" : "p3a"'
assert bench_source.count(old_label) == 2
(P / "pi-bench.c").write_text(bench_source.replace(old_label, new_label))
print(json.dumps(audit, indent=2))
