#!/usr/bin/env python3
"""Pi 5 correctness, paired PMU, and selected-Official P10 profiler gate."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
SUPPORT = BUILD / "support"
RUN = HERE / os.environ.get("P10_RUN", "run")
SC = pathlib.Path("/home/pi/supercop-20260831")
OFFICIAL = SC / "crypto_kem/ntruplus864/aarch64"
INCLUDE = SC / "bench/pinhao/include/aarch64"


def command(argv, *, cwd=None, stdout=None):
    return subprocess.run([str(x) for x in argv], cwd=cwd, check=True, text=True,
                          stdout=stdout, stderr=subprocess.STDOUT if stdout else None)


def output(argv, *, cwd=None):
    return subprocess.check_output([str(x) for x in argv], cwd=cwd, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def median_rows(paths, prefix):
    rows = []
    for path in paths:
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] == prefix:
                rows.append(row)
    return rows


def compile_source(source, obj, includes, log):
    language = "assembler-with-cpp" if source.suffix in {".s", ".S"} else "c"
    flags = ["gcc", "-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE",
             "-fPIC", "-ffunction-sections", "-fdata-sections"]
    flags += ["-I" + str(x) for x in includes]
    command([*flags, "-x", language, "-c", source, "-o", obj], stdout=log)


def main():
    processes = output(["ps", "-eo", "args"])
    if re.search(r"(?:^|/)do-part(?: |$)", processes, re.MULTILINE):
        raise RuntimeError("SUPERCOP do-part is active; refusing competing PMU work")
    if RUN.exists():
        raise RuntimeError(f"refusing to overwrite {RUN}")
    RUN.mkdir()

    packages = {name: BUILD / name for name in ("p9", "p10")}
    kats = {}
    malformed = {}
    for name, package in packages.items():
        with (RUN / f"{name}-build.log").open("w") as log:
            command(["make", "manifest-check"], cwd=package, stdout=log)
            command(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], cwd=package, stdout=log)
        with (RUN / f"{name}-test.log").open("w") as log:
            command(["./test_kem"], cwd=package, stdout=log)
        for old in package.glob("PQCkemKAT_*.rsp"):
            old.unlink()
        with (RUN / f"{name}-kat.log").open("w") as log:
            command(["./PQCgenKAT_kem"], cwd=package, stdout=log)
        kat = next(package.glob("PQCkemKAT_*.rsp"))
        kats[name] = {"sha256": sha(kat), "cases": kat.read_text().count("count = ")}

        objects = sorted(x for x in package.glob("*.o") if x.name != "kem-normal.o")
        check_source = SUPPORT / ("test_baseinv_p10.c" if name == "p10" else "test_baseinv.c")
        check = RUN / f"check-baseinv-{name}"
        command(["gcc", "-O2", "-I" + str(package), check_source,
                 SUPPORT / "probe_baseinv.S", *objects, "-o", check])
        with (RUN / f"{name}-baseinv-check.log").open("w") as log:
            command([check], stdout=log)

        transcript = RUN / f"{name}-malformed.trace"
        binary = RUN / f"{name}-malformed"
        command(["gcc", "-O2", "-I" + str(package), SUPPORT / "kem-malformed-transcript.c",
                 *sorted(package.glob("*.o")), "-o", binary])
        with transcript.open("w") as log:
            command([binary], stdout=log)
        malformed[name] = {"sha256": sha(transcript), "bytes": transcript.stat().st_size}
    assert kats["p9"] == kats["p10"]
    assert malformed["p9"] == malformed["p10"]

    # Same-boundary P9/P10 component and full-KEM paired PMU.
    pair_bench = RUN / "pair-bench"
    command(["gcc", "-O3", "-rdynamic", SUPPORT / "pi-bench.c", "-ldl", "-o", pair_bench])
    pair_logs = []
    for repetition in range(6):
        log_path = RUN / f"pair-{repetition}.csv"
        with log_path.open("w") as log:
            command(["taskset", "-c", "3", pair_bench,
                     packages["p9"] / "libgt864.so", packages["p10"] / "libgt864.so",
                     repetition & 1], stdout=log)
        pair_logs.append(log_path)

    pair_summary = {}
    for prefix in ("full", "component"):
        rows = median_rows(pair_logs, prefix)
        for operation in sorted({row[1] for row in rows}):
            pair_summary[operation] = {}
            for label, public in (("baseline", "p9"), ("candidate", "p10")):
                values = [list(map(float, row[3:6])) for row in rows if row[1] == operation and row[2] == label]
                pair_summary[operation][public] = {
                    key: statistics.median(x[i] for x in values)
                    for i, key in enumerate(("cycles", "instructions", "branches"))
                }
            pair_summary[operation]["cycle_delta"] = (
                pair_summary[operation]["p10"]["cycles"] - pair_summary[operation]["p9"]["cycles"]
            )

    # Build the exact selected SUPERCOP source and call-site profilers.
    official_copy = RUN / "official-source"
    shutil.copytree(OFFICIAL, official_copy)
    official_objects = []
    with (RUN / "official-build.log").open("w") as log:
        for source in sorted(official_copy.iterdir()):
            if source.suffix not in {".c", ".s", ".S"}:
                continue
            obj = RUN / (source.name + ".official.o")
            compile_source(source, obj, [official_copy, SUPPORT / "compat", INCLUDE], log)
            official_objects.append(obj)
        blocker = RUN / "optblocker.o"
        compile_source(SUPPORT / "compat/optblocker.c", blocker,
                       [official_copy, SUPPORT / "compat", INCLUDE], log)
        official_objects.append(blocker)
        command(["gcc", "-shared", "-Wl,-Bsymbolic", "-Wl,--gc-sections",
                 *official_objects, "-o", RUN / "official.so"], stdout=log)

    profile_objects = {}
    for label, source_root in (("official", official_copy), ("p10", packages["p10"])):
        generated = RUN / f"{label}-profile-kem.c"
        mode = "official" if label == "official" else "gt"
        generated.write_text(output([sys.executable, SUPPORT / "generate_profile_kem.py", source_root / "kem.c", mode]) + "\n")
        obj = RUN / f"{label}-profile-kem.o"
        with (RUN / f"{label}-profile-build.log").open("w") as log:
            compile_source(generated, obj, [source_root, SUPPORT / "compat", INCLUDE, packages["p10"]], log)
            if label == "official":
                objects = [x for x in official_objects if x.name != "kem.c.official.o"] + [obj]
            else:
                objects = sorted(x for x in source_root.glob("*.o") if x.name not in {"kem.o", "kem-normal.o"}) + [obj]
            command(["gcc", "-shared", "-Wl,-Bsymbolic", "-Wl,--gc-sections", *objects,
                     "-o", RUN / f"{label}-prof.so"], stdout=log)
            profile_objects[label] = [x.name for x in objects]

    command(["gcc", "-O3", "-rdynamic", SUPPORT / "full_harness.c", "-ldl", "-o", RUN / "full-harness"])
    command(["gcc", "-O3", "-rdynamic", SUPPORT / "profile_harness.c", "-ldl", "-o", RUN / "profile-harness"])
    clean_logs = []
    profile_logs = []
    for repetition in range(6):
        clean = RUN / f"official-p10-clean-{repetition}.csv"
        with clean.open("w") as log:
            command(["taskset", "-c", "3", RUN / "full-harness", RUN / "official.so",
                     packages["p10"] / "libgt864.so", repetition & 1], stdout=log)
        clean_logs.append(clean)
        order = ("official", "p10") if repetition % 2 == 0 else ("p10", "official")
        for label in order:
            plain = RUN / "official.so" if label == "official" else packages["p10"] / "libgt864.so"
            profile = RUN / f"{label}-profile-{repetition}.csv"
            with profile.open("w") as log:
                command(["taskset", "-c", "3", RUN / "profile-harness", label, plain,
                         RUN / f"{label}-prof.so"], stdout=log)
            profile_logs.append(profile)
        print(f"completed target repetition {repetition + 1}/6", flush=True)

    clean_rows = median_rows(clean_logs, "clean")
    official_summary = {}
    for operation in ("keygen", "encaps", "decaps"):
        official_summary[operation] = {}
        for raw_label, public in (("official", "official"), ("gt", "p10")):
            values = [list(map(float, row[3:6])) for row in clean_rows if row[1] == operation and row[2] == raw_label]
            official_summary[operation][public] = {
                key: statistics.median(x[i] for x in values)
                for i, key in enumerate(("cycles", "instructions", "branches"))
            }
        official_summary[operation]["cycle_delta"] = (
            official_summary[operation]["p10"]["cycles"] - official_summary[operation]["official"]["cycles"]
        )

    profile_rows = median_rows(profile_logs, "profile")
    profiles = {}
    for operation in ("keygen", "encaps", "decaps"):
        profiles[operation] = {}
        groups = sorted({row[3] for row in profile_rows if row[1] == operation})
        for label in ("official", "p10"):
            profiles[operation][label] = {}
            for group in groups:
                values = [float(row[5]) for row in profile_rows
                          if row[1] == operation and row[2] == label and row[3] == group]
                if values:
                    profiles[operation][label][group] = statistics.median(values)

    p10_baseinv_two_calls = profiles["keygen"]["p10"]["BaseInv"]
    official_baseinv_two_calls = profiles["keygen"]["official"]["BaseInv"]
    result = {
        "status": "pass" if p10_baseinv_two_calls < official_baseinv_two_calls else "investigate",
        "completion_gate": {
            "metric": "call-site profiler net cycles for two BaseInv calls per Keygen",
            "official": official_baseinv_two_calls,
            "p10": p10_baseinv_two_calls,
            "delta": p10_baseinv_two_calls - official_baseinv_two_calls,
            "passed": p10_baseinv_two_calls < official_baseinv_two_calls,
        },
        "correctness": {
            "test_kem": "pass both",
            "kat": kats,
            "malformed": malformed,
            "baseinv_808_success_failure_alias_aapcs_scratch": "pass both",
        },
        "p9_vs_p10": pair_summary,
        "official_vs_p10": official_summary,
        "call_site_profiles_cycles": profiles,
        "official": {
            "source": str(OFFICIAL),
            "upstream_latest_verified": False,
            "tree_key_hashes": {name: sha(OFFICIAL / name) for name in ("kem.c", "symmetric.c", "api.h")},
        },
        "environment": {
            "uname": output(["uname", "-a"]),
            "gcc": output(["gcc", "--version"]).splitlines()[0],
            "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
            "temperature": output(["vcgencmd", "measure_temp"]),
            "throttled": output(["vcgencmd", "get_throttled"]),
            "core": 3,
            "processes": 6,
        },
        "binary_hashes": {
            "p9": sha(packages["p9"] / "libgt864.so"),
            "p10": sha(packages["p10"] / "libgt864.so"),
            "official": sha(RUN / "official.so"),
        },
        "profile_link_objects": profile_objects,
    }
    (HERE / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
