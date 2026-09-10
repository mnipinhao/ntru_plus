#!/usr/bin/env python3
"""Build, audit, validate, and paired-PMU benchmark P4 on Raspberry Pi 5."""

import csv
import hashlib
import json
import pathlib
import re
import statistics
import subprocess


P = pathlib.Path(__file__).resolve().parent
BUILD = P / "build"
RESULTS = P / "pi-results"
RESULTS.mkdir(exist_ok=True)


def run(command, *, cwd=None, log=None):
    stream = None if log is None else log.open("a")
    try:
        subprocess.run(command, cwd=cwd, check=True, stdout=stream,
                       stderr=subprocess.STDOUT if stream else None)
    finally:
        if stream:
            stream.close()


processes = subprocess.check_output(["ps", "-eo", "args"], text=True)
if re.search(r"(?:^|/)do-part(?: |$)", processes, re.M):
    raise RuntimeError("SUPERCOP benchmark is active; refusing a competing PMU run")

for name in ("p3a", "p4"):
    package = BUILD / name
    build_log = RESULTS / f"build-{name}.log"
    build_log.write_text("")
    run(["make", "manifest-check"], cwd=package, log=build_log)
    run(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], cwd=package, log=build_log)
    run(["./test_kem"], cwd=package, log=RESULTS / f"test-{name}.log")
    run(["./PQCgenKAT_kem"], cwd=package, log=RESULTS / f"kat-{name}.log")

kat_hashes = {
    name: hashlib.sha256((BUILD / name / "PQCkemKAT_2624.rsp").read_bytes()).hexdigest()
    for name in ("p3a", "p4")
}
assert len(set(kat_hashes.values())) == 1

run(["gcc", "-O3", "-rdynamic", str(P / "kem-rejection.c"), "-ldl", "-o", str(RESULTS / "kem-rejection")])
rejection = subprocess.check_output([
    "taskset", "-c", "3", str(RESULTS / "kem-rejection"),
    str(BUILD / "p3a/libgt864.so"), str(BUILD / "p4/libgt864.so"),
], text=True).strip()
(RESULTS / "kem-rejection.txt").write_text(rejection + "\n")

candidate_disassembly = subprocess.check_output([
    "objdump", "-d", str(BUILD / "p4/cluster_transpose_frombytes.o")
], text=True)
baseline_api_disassembly = subprocess.check_output([
    "objdump", "-d", str(BUILD / "p3a/byte_api.o")
], text=True)
candidate_api_disassembly = subprocess.check_output([
    "objdump", "-d", str(BUILD / "p4/byte_api.o")
], text=True)
(RESULTS / "candidate-cluster.objdump").write_text(candidate_disassembly)
(RESULTS / "baseline-byte-api.objdump").write_text(baseline_api_disassembly)
(RESULTS / "candidate-byte-api.objdump").write_text(candidate_api_disassembly)
core_match = re.search(
    r"<transpose_top_checked>:\n(?P<body>.*?)(?=\n[0-9a-f]+ <[^>]+>:\n)",
    candidate_disassembly,
    re.S,
)
assert core_match
core = core_match.group("body")
assert not re.search(r"\b(?:str|stur|stp|ldr|ldur|ldp)\s+q\d+.*\[sp", core)
assert "umaxv" in core
assert "gt864_fr0_cluster_transpose_frombytes_checked_raw" in candidate_disassembly
assert len(candidate_api_disassembly.splitlines()) < len(baseline_api_disassembly.splitlines())
object_audit = {
    "candidate_transpose_vector_stack_accesses": 0,
    "candidate_transpose_has_umaxv": True,
    "checked_byte_api_disassembly_lines": {
        "p3a": len(baseline_api_disassembly.splitlines()),
        "p4": len(candidate_api_disassembly.splitlines()),
    },
    "candidate_cluster_object_bytes": (BUILD / "p4/cluster_transpose_frombytes.o").stat().st_size,
    "baseline_cluster_object_bytes": (BUILD / "p3a/cluster_transpose_frombytes.o").stat().st_size,
}
(P / "object-audit.json").write_text(json.dumps(object_audit, indent=2) + "\n")

run(["gcc", "-O3", "-rdynamic", str(P / "pi-bench.c"), "-ldl", "-o", str(RESULTS / "pi-bench")])
rows = []
correctness = []
for repetition in range(6):
    output = subprocess.check_output([
        "taskset", "-c", "3", str(RESULTS / "pi-bench"),
        str(BUILD / "p3a/libgt864.so"), str(BUILD / "p4/libgt864.so"),
        str(repetition % 2),
    ], text=True)
    (RESULTS / f"paired-{repetition}.csv").write_text(output)
    for row in csv.reader(output.splitlines()):
        if row and row[0] == "correctness=pass valid_kem=24 checked_frombytes_exact=24":
            correctness.append(row[0])
        if row and row[0] in ("full", "component"):
            rows.append((row[0], row[1], row[2], *map(float, row[3:])))

summary = {}
for boundary, operation in (
    ("component", "frombytes_checked"),
    ("full", "keygen"), ("full", "encaps"), ("full", "decaps"),
):
    summary[operation] = {}
    for implementation in ("p3a", "p4"):
        values = [row[3:] for row in rows if row[:3] == (boundary, operation, implementation)]
        summary[operation][implementation] = {
            metric: statistics.median(value[index] for value in values)
            for index, metric in enumerate(("cycles", "instructions", "branches"))
        }
    summary[operation]["delta"] = {
        metric: summary[operation]["p4"][metric] - summary[operation]["p3a"][metric]
        for metric in ("cycles", "instructions", "branches")
    }
    summary[operation]["cycle_delta_percent"] = 100 * (
        summary[operation]["p4"]["cycles"] / summary[operation]["p3a"]["cycles"] - 1
    )

result = {
    "baseline": "current GT production P3-A",
    "candidate": "P4 fused FromBytes legality accumulation",
    "correctness_repetitions": len(correctness),
    "rejection": rejection,
    "kat_sha256": kat_hashes,
    "object_audit": object_audit,
    "summary": summary,
    "environment": {
        "uname": subprocess.check_output(["uname", "-a"], text=True).strip(),
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
        "temperature": subprocess.check_output(["vcgencmd", "measure_temp"], text=True).strip(),
        "supercop_reference_root": "/home/pi/supercop-20260831",
    },
    "hashes": {
        name: hashlib.sha256((BUILD / name / "libgt864.so").read_bytes()).hexdigest()
        for name in ("p3a", "p4")
    },
}
(P / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
