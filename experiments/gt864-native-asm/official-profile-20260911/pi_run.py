#!/usr/bin/env python3
"""Fresh Pi 5 build, correctness gate, and profiler campaign."""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parent
SC = pathlib.Path("/home/pi/supercop-20260831")
OFFICIAL = SC / "crypto_kem/ntruplus864/aarch64"
GT = ROOT / "gt-source"
BUILD = ROOT / "build"
RAW = ROOT / "raw"
INCLUDE = SC / "bench/pinhao/include/aarch64"
EXPECTED = {
    "kem.c": "acb888a4aa199cc4d1f9a62e4b61921be8d6032b38bd19c8e2afd35aa808937c",
    "symmetric.c": "a9ab4afbb2a9053c75cd959040569e1e705d769021f250d87c3d3f08da1d7053",
    "api.h": "1912c6a38e7f1449321520570020266836a4cace70f7e5901d0e8c172a707865",
}


def run(argv: list[object], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(x) for x in argv], check=True, text=True, **kwargs)


def output(argv: list[object]) -> str:
    return subprocess.check_output([str(x) for x in argv], text=True).strip()


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(root: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.suffix in {".o", ".so"} or path.name in {"test_kem", "PQCgenKAT_kem"}:
            continue
        digest.update(str(path.relative_to(root)).encode() + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def compile_source(source: pathlib.Path, obj: pathlib.Path, includes: list[pathlib.Path], log: object) -> None:
    language = "assembler-with-cpp" if source.suffix in {".s", ".S"} else "c"
    flags: list[object] = [
        "gcc", "-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE",
        "-fPIC", "-ffunction-sections", "-fdata-sections",
    ]
    for include in includes:
        flags.append("-I" + str(include))
    run(flags + ["-x", language, "-c", source, "-o", obj], stdout=log, stderr=subprocess.STDOUT)


def link_shared(objects: list[pathlib.Path], destination: pathlib.Path, log: object) -> None:
    run(
        ["gcc", "-shared", "-Wl,-Bsymbolic", "-Wl,--gc-sections", *objects, "-o", destination],
        stdout=log,
        stderr=subprocess.STDOUT,
    )


def main() -> None:
    process_list = output(["ps", "-eo", "args"])
    if re.search(r"(?:^|/)do-part(?: |$)", process_list, re.MULTILINE):
        raise RuntimeError("a SUPERCOP do-part process is active")
    if not GT.is_dir():
        raise RuntimeError(f"missing uploaded GT source: {GT}")
    for name, expected in EXPECTED.items():
        actual = sha256(OFFICIAL / name)
        if actual != expected:
            raise RuntimeError(f"Official hash mismatch for {name}: {actual}")

    for path in (BUILD, RAW):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
    official_copy = BUILD / "official-source"
    shutil.copytree(OFFICIAL, official_copy)

    environment = {
        "official_source": str(OFFICIAL),
        "official_upstream_latest_verified": False,
        "official_required_hashes": EXPECTED,
        "official_tree_hash": tree_hash(official_copy),
        "gt_tree_hash": tree_hash(GT),
        "uname": output(["uname", "-a"]),
        "gcc": output(["gcc", "--version"]).splitlines()[0],
        "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
        "temperature_before": output(["vcgencmd", "measure_temp"]),
        "throttled_before": output(["vcgencmd", "get_throttled"]),
        "cpu_core": 3,
        "clean_repetitions": {"processes": 6, "samples_per_process": 42, "keygen_inner": 4, "encaps_inner": 20, "decaps_inner": 20},
        "profile_repetitions": {"processes": 6, "samples_per_process": 21, "keygen_inner": 4, "encaps_inner": 20, "decaps_inner": 20},
    }
    (BUILD / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")

    with (BUILD / "gt-build.log").open("w") as log:
        run(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], cwd=GT, stdout=log, stderr=subprocess.STDOUT)
    with (BUILD / "gt-test-kem.log").open("w") as log:
        run(["./test_kem"], cwd=GT, stdout=log, stderr=subprocess.STDOUT)
    for old_rsp in GT.glob("PQCkemKAT_*.rsp"):
        old_rsp.unlink()
    with (BUILD / "gt-kat.log").open("w") as log:
        run(["./PQCgenKAT_kem"], cwd=GT, stdout=log, stderr=subprocess.STDOUT)
    kat_files = sorted(GT.glob("PQCkemKAT_*.rsp"))
    if len(kat_files) != 1:
        raise RuntimeError(f"expected one GT KAT response file, got {kat_files}")
    shutil.copy2(GT / "libgt864.so", BUILD / "gt.so")

    official_objects: list[pathlib.Path] = []
    with (BUILD / "official-build.log").open("w") as log:
        for source in sorted(official_copy.iterdir()):
            if source.suffix not in {".c", ".s", ".S"}:
                continue
            obj = BUILD / (source.name + ".o")
            compile_source(source, obj, [official_copy, ROOT / "compat", INCLUDE], log)
            official_objects.append(obj)
        blocker = BUILD / "optblocker.o"
        compile_source(ROOT / "compat/optblocker.c", blocker, [official_copy, ROOT / "compat", INCLUDE], log)
        official_objects.append(blocker)
        link_shared(official_objects, BUILD / "official.so", log)

    profile_objects: dict[str, list[str]] = {}
    for label, source_root in (("official", official_copy), ("gt", GT)):
        generated = BUILD / f"{label}-profile-kem.c"
        generated.write_text(output([sys.executable, ROOT / "generate_profile_kem.py", source_root / "kem.c", label]) + "\n")
        obj = BUILD / f"{label}-profile-kem.o"
        with (BUILD / f"{label}-profile-build.log").open("w") as log:
            compile_source(generated, obj, [source_root, ROOT / "compat", INCLUDE, GT], log)
            if label == "official":
                objects = [x for x in official_objects if x.name != "kem.c.o"] + [obj]
            else:
                objects = sorted(x for x in GT.glob("*.o") if x.name not in {"kem.o", "kem-normal.o"}) + [obj]
            link_shared(objects, BUILD / f"{label}-prof.so", log)
            profile_objects[label] = [x.name for x in objects]

    common = ["gcc", "-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE", "-rdynamic"]
    run([*common, ROOT / "full_harness.c", "-ldl", "-o", BUILD / "full_harness"])
    run([*common, ROOT / "profile_harness.c", "-ldl", "-o", BUILD / "profile_harness"])

    clean_logs: list[str] = []
    profile_logs: list[str] = []
    for process in range(6):
        clean_log = RAW / f"clean-{process}.csv"
        with clean_log.open("w") as log:
            run(
                ["taskset", "-c", "3", BUILD / "full_harness", BUILD / "official.so", BUILD / "gt.so", process % 2],
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        clean_logs.append(clean_log.name)
        order = ("official", "gt") if process % 2 == 0 else ("gt", "official")
        for label in order:
            profile_log = RAW / f"profile-{label}-{process}.csv"
            with profile_log.open("w") as log:
                run(
                    ["taskset", "-c", "3", BUILD / "profile_harness", label, BUILD / f"{label}.so", BUILD / f"{label}-prof.so"],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
            profile_logs.append(profile_log.name)
        print(f"completed process {process + 1}/6", flush=True)

    environment.update({
        "temperature_after": output(["vcgencmd", "measure_temp"]),
        "throttled_after": output(["vcgencmd", "get_throttled"]),
        "gt_kat_file": kat_files[0].name,
        "gt_kat_sha256": sha256(kat_files[0]),
        "binary_hashes": {name: sha256(BUILD / name) for name in ("official.so", "gt.so", "official-prof.so", "gt-prof.so")},
        "profile_link_objects": profile_objects,
        "raw_clean_logs": clean_logs,
        "raw_profile_logs": profile_logs,
    })
    (BUILD / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
    with (BUILD / "symbols.txt").open("w") as log:
        for library in ("official.so", "gt.so", "official-prof.so", "gt-prof.so"):
            log.write(f"[{library}]\n")
            log.write(output(["nm", "-D", "--defined-only", BUILD / library]) + "\n")
    print(json.dumps(environment, indent=2))


if __name__ == "__main__":
    main()
