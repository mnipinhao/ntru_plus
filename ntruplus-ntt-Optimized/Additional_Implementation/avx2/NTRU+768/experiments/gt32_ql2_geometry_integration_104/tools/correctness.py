#!/usr/bin/env python3
"""Run deterministic, KAT, and sanitizer checks for the 104 pair."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
GEN = EXP / "generated"
BUILD = EXP / "build/correctness"
OFFICIAL = ROOT.parents[3] / "third_party/NTRUplus-official-main/Additional_Implementation/avx2/NTRU+768"
TEST = ROOT / "experiments/gt32_hwa_encap_dead_slot_frame_trim_094/tests/deterministic_encap.c"
EXPECTED_KAT = "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8"
COMMON = ["baseinv.c", "consts.c", "decap.c", "fips202.c", "kem.c",
          "keygen.c", "poly.c", "symmetric.c", "add.s", "basemul-ql2.s",
          "batch_inverse.s", "cbd.s", "crepmod3.s", "invntt.s", "ntt.s",
          "ntt-ql2.s", "ntt_p.s", "pack-ql2.s", "KeccakP-1600-AVX2.s"]


def run(command: list[str], cwd: Path | None = None,
        env: dict[str, str] | None = None) -> str:
    return subprocess.check_output(command, cwd=cwd, env=env, text=True)


def common_sources() -> list[Path]:
    return [(GEN / name if name.endswith("-ql2.s") else ROOT / name)
            for name in COMMON]


def build(profile: str, output: Path, flags: list[str], harness: list[Path]) -> None:
    encap = ROOT / "encap.c" if profile == "control" else EXP / "encap-ql2.c"
    run(["gcc", *flags, f"-I{ROOT}", f"-I{OFFICIAL}",
         "-Wl,--gc-sections",
         "-Wl,--undefined=ntruplus768_pack_m_highrange12699_avx2",
         f"-Wl,-T,{GEN / 'tails.ld'}", "-o", str(output),
         *(str(path) for path in harness), str(encap),
         *(str(path) for path in common_sources())])


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    flags = ["-march=native", "-mtune=native", "-O3", "-fwrapv",
             "-fomit-frame-pointer", "-ffunction-sections", "-fdata-sections"]
    deterministic = {}
    for profile in ("control", "ql2"):
        binary = BUILD / f"deterministic-{profile}"
        build(profile, binary, flags, [OFFICIAL / "randombytes.c", TEST])
        deterministic[profile] = run([str(binary)]).strip()
    if len(set(deterministic.values())) != 1:
        raise SystemExit(f"deterministic mismatch: {deterministic}")

    kat = {}
    for profile in ("control", "ql2"):
        binary = BUILD / f"kat-{profile}"
        build(profile, binary, flags + ["-Wno-unused-result"],
              [OFFICIAL / "kat/PQCgenKAT_kem.c", OFFICIAL / "kat/aes.c",
               OFFICIAL / "kat/rng.c"])
        directory = BUILD / f"kat-run-{profile}"
        directory.mkdir()
        run([str(binary)], cwd=directory)
        response = directory / "PQCkemKAT_2336.rsp"
        digest = hashlib.sha256(response.read_bytes()).hexdigest()
        if digest != EXPECTED_KAT:
            raise SystemExit(f"KAT mismatch for {profile}: {digest}")
        kat[profile] = {"bytes": response.stat().st_size, "sha256": digest}

    sanitized = BUILD / "deterministic-ql2-sanitized"
    sanitize_flags = ["-march=native", "-mtune=native", "-O1", "-fwrapv",
                      "-fno-omit-frame-pointer", "-fsanitize=address,undefined",
                      "-fno-sanitize-recover=all", "-ffunction-sections",
                      "-fdata-sections"]
    build("ql2", sanitized, sanitize_flags, [OFFICIAL / "randombytes.c", TEST])
    env = os.environ.copy()
    env["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    sanitizer = run([str(sanitized)], env=env).strip()
    result = {"deterministic": deterministic, "kat": kat,
              "asan_ubsan_ql2": sanitizer}
    (GEN / "correctness.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
