#!/usr/bin/env python3
"""P13 correctness, malformed-input, and paired-PMU gate on Raspberry Pi 5."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import pathlib
import re
import statistics
import subprocess

P = pathlib.Path(__file__).resolve().parent
BUILD = P / "build"
RUN = P / os.environ.get("P13_RUN", "pi-run")
CANDIDATE_NAME = os.environ.get("P13_CANDIDATE", "candidate")
RESULT_NAME = os.environ.get("P13_RESULT", "pi-results.json")


def command(argv, *, cwd=None, stdout=None):
    return subprocess.run([str(x) for x in argv], cwd=cwd, check=True, text=True,
                          stdout=stdout, stderr=subprocess.STDOUT if stdout else None)


def output(argv, *, cwd=None):
    return subprocess.check_output([str(x) for x in argv], cwd=cwd, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    processes = output(["ps", "-eo", "args"])
    if re.search(r"(?:^|/)do-part(?: |$)", processes, re.MULTILINE):
        raise RuntimeError("SUPERCOP do-part is active; refusing competing PMU work")
    if RUN.exists():
        raise RuntimeError(f"refusing to overwrite {RUN}")
    RUN.mkdir()
    packages = {"baseline": BUILD / "baseline", "candidate": BUILD / CANDIDATE_NAME}
    kats = {}
    traces = {}
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
        malformed = RUN / f"malformed-{name}"
        # malformed.c supplies its own deterministic randombytes implementation.
        command(["gcc", "-O3", "-I" + str(package), P / "malformed.c",
                 "-L" + str(package), "-lgt864", "-Wl,-rpath," + str(package), "-o", malformed])
        trace = RUN / f"{name}-malformed.trace"
        with trace.open("w") as log:
            command([malformed], stdout=log)
        traces[name] = {"sha256": sha(trace), "bytes": trace.stat().st_size}
    if kats["baseline"] != kats["candidate"]:
        raise RuntimeError("KAT mismatch")
    if traces["baseline"] != traces["candidate"]:
        raise RuntimeError("malformed-ciphertext transcript mismatch")

    p11_test = RUN / "p13-test"
    command(["gcc", "-O3", "-I" + str(packages["candidate"]), P / "test.c", P / "probe.S",
             packages["candidate"] / "randombytes.c", "-L" + str(packages["candidate"]), "-lgt864",
             "-Wl,-rpath," + str(packages["candidate"]), "-o", p11_test])
    with (RUN / "p11-test.log").open("w") as log:
        command([p11_test], stdout=log)

    bench = RUN / "pi-bench"
    command(["gcc", "-O3", "-rdynamic", P / "pi-bench.c", "-ldl", "-o", bench])
    logs = []
    for repetition in range(6):
        path = RUN / f"paired-{repetition}.csv"
        with path.open("w") as log:
            command(["taskset", "-c", "3", bench, packages["baseline"] / "libgt864.so",
                     packages["candidate"] / "libgt864.so", repetition & 1], stdout=log)
        logs.append(path)
        print(f"completed paired process {repetition + 1}/6", flush=True)

    rows = []
    for path in logs:
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] in {"full", "component"}:
                rows.append(row)
    summary = {}
    for operation in ("inverse_to_ternary", "keygen", "encaps", "decaps"):
        summary[operation] = {}
        for label in ("baseline", "candidate"):
            values = [list(map(float, row[3:6])) for row in rows if row[1] == operation and row[2] == label]
            summary[operation][label] = {
                key: statistics.median(value[index] for value in values)
                for index, key in enumerate(("cycles", "instructions", "branches"))
            }
        summary[operation]["delta"] = {
            key: summary[operation]["candidate"][key] - summary[operation]["baseline"][key]
            for key in ("cycles", "instructions", "branches")
        }
        summary[operation]["cycle_delta_percent"] = 100 * (
            summary[operation]["candidate"]["cycles"] / summary[operation]["baseline"]["cycles"] - 1
        )
    component = summary["inverse_to_ternary"]
    decaps = summary["decaps"]
    result = {
        "status": "promote" if component["delta"]["cycles"] < 0 and decaps["delta"]["cycles"] < 0 else "reject",
        "completion_gate": {
            "component_cycles_improve": component["delta"]["cycles"] < 0,
            "full_decaps_cycles_improve": decaps["delta"]["cycles"] < 0,
            "no_keygen_encaps_instruction_change": all(
                abs(summary[name]["delta"]["instructions"]) < 1 for name in ("keygen", "encaps")
            ),
        },
        "correctness": {
            "test_kem": "pass both",
            "kat": kats,
            "malformed": traces,
            "inverse_4096_exact_alias_aapcs_wipe": "pass candidate",
            "in_benchmark_valid_tampered_inverse_alias": "pass all six processes",
        },
        "summary": summary,
        "environment": {
            "uname": output(["uname", "-a"]),
            "gcc": output(["gcc", "--version"]).splitlines()[0],
            "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
            "temperature": output(["vcgencmd", "measure_temp"]),
            "throttled": output(["vcgencmd", "get_throttled"]),
            "core": 3,
            "processes": 6,
            "supercop_reference_root": "/home/pi/supercop-20260831",
        },
        "binary_hashes": {name: sha(package / "libgt864.so") for name, package in packages.items()},
    }
    (P / RESULT_NAME).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
