#!/usr/bin/env python3
"""Native correctness for P9 public boundaries and complete candidate KEM."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"


def run(arguments: list[object], cwd: Path | None = None) -> None:
    subprocess.run([str(value) for value in arguments], cwd=cwd, check=True)


def main() -> None:
    run([sys.executable, HERE / "prepare.py"])
    direct = BUILD / "mac-direct"
    direct.mkdir(parents=True, exist_ok=True)
    run(["clang", "-O3", "-I" + str(BUILD), "-c",
         BUILD / "gt864_p9_tobytes_full.c", "-o", direct / "full.o"])
    run(["clang", "-O3", "-I" + str(BUILD), "-c",
         BUILD / "gt864_p9_tobytes_small.c", "-o", direct / "small.o"])
    run(["clang", "-O3", "-DP9_BUILD_FULL", "-I" + str(BUILD),
         "-x", "assembler-with-cpp", "-c", BUILD / "p9_tobytes_public.S",
         "-o", direct / "public-full.o"])
    run(["clang", "-O3", "-DP9_BUILD_SMALL", "-I" + str(BUILD),
         "-x", "assembler-with-cpp", "-c", BUILD / "p9_tobytes_public.S",
         "-o", direct / "public-small.o"])
    run(["clang", "-O3", "-I" + str(BUILD), HERE / "test.c",
         direct / "full.o", direct / "small.o", direct / "public-full.o",
         direct / "public-small.o", "-o", direct / "test"])
    run([direct / "test"])

    source = BUILD / "mac-source"
    shutil.copytree(BUILD / "packages/both", source, dirs_exist_ok=True)
    # The production source has a Linux spelling for this internal leaf; this
    # is the inherited Mac-only test shim used by the P8 validation as well.
    numerator = source / "gt864_native_baseinv_num.S"
    numerator.write_text(
        "#ifdef __APPLE__\n#define binv_num_pair _binv_num_pair\n#endif\n" +
        numerator.read_text()
    )
    out = BUILD / "mac-kem"
    run([sys.executable, ROOT / "experiments/gt864-native-asm/verify-production-mac.py",
         source, out])
    response = out / "PQCkemKAT_2624.rsp"
    digest = hashlib.sha256(response.read_bytes()).hexdigest()
    if digest != "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c":
        raise RuntimeError(f"unexpected KAT digest {digest}")
    print(f"p9_mac_kem=pass kat_sha256={digest}")

    production = ROOT / (
        "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
    )
    production_source = BUILD / "mac-production-source"
    shutil.copytree(production, production_source, dirs_exist_ok=True)
    numerator = production_source / "gt864_native_baseinv_num.S"
    numerator.write_text(
        "#ifdef __APPLE__\n#define binv_num_pair _binv_num_pair\n#endif\n" +
        numerator.read_text()
    )
    production_out = BUILD / "mac-production"
    run([sys.executable, ROOT / "experiments/gt864-native-asm/verify-production-mac.py",
         production_source, production_out])
    production_digest = hashlib.sha256(
        (production_out / "PQCkemKAT_2624.rsp").read_bytes()
    ).hexdigest()
    if production_digest != digest:
        raise RuntimeError(f"promoted production KAT mismatch {production_digest}")
    print(f"p9_promoted_mac=pass kat_sha256={production_digest}")


if __name__ == "__main__":
    main()
