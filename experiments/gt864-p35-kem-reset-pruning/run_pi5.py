#!/usr/bin/env python3
"""P35 correctness and balanced paired PMU gate on Raspberry Pi 5."""
import csv
import hashlib
import json
import pathlib
import re
import statistics
import subprocess

P = pathlib.Path(__file__).resolve().parent
BUILD = P / "build"
RUN = P / "pi-run"


def command(argv, cwd=None, stdout=None):
    return subprocess.run([str(x) for x in argv], cwd=cwd, check=True, text=True,
                          stdout=stdout, stderr=subprocess.STDOUT if stdout else None)


def output(argv, cwd=None):
    return subprocess.check_output([str(x) for x in argv], cwd=cwd, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


if re.search(r"(?:^|/)do-part(?: |$)", output(["ps", "-eo", "args"]), re.MULTILINE):
    raise RuntimeError("SUPERCOP do-part is active; refusing competing PMU work")
if RUN.exists():
    raise RuntimeError(f"refusing to overwrite {RUN}")
RUN.mkdir()
packages = {name: BUILD / name for name in ("baseline", "candidate")}
kats = {}
traces = {}
for name, package in packages.items():
    with (RUN / f"{name}-build.log").open("w") as log:
        command(["make", "manifest-check"], package, log)
        command(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], package, log)
    with (RUN / f"{name}-test.log").open("w") as log:
        command(["./test_kem"], package, log)
    for old in package.glob("PQCkemKAT_*.rsp"):
        old.unlink()
    with (RUN / f"{name}-kat.log").open("w") as log:
        command(["./PQCgenKAT_kem"], package, log)
    kat = next(package.glob("PQCkemKAT_*.rsp"))
    kats[name] = {"sha256": sha(kat), "cases": kat.read_text().count("count = ")}
    malformed = RUN / f"malformed-{name}"
    command(["gcc", "-O3", "-I" + str(package), P / "malformed.c", "-L" + str(package),
             "-lgt864", "-Wl,-rpath," + str(package), "-o", malformed])
    trace = RUN / f"{name}-malformed.trace"
    with trace.open("w") as log:
        command([malformed], stdout=log)
    traces[name] = {"sha256": sha(trace), "bytes": trace.stat().st_size}
assert kats["baseline"] == kats["candidate"]
assert traces["baseline"] == traces["candidate"]

test = RUN / "p35-test"
command(["gcc", "-O3", "-I" + str(packages["candidate"]), P / "test.c", P / "probe.S",
         packages["candidate"] / "randombytes.c", "-L" + str(packages["candidate"]), "-lgt864",
         "-Wl,-rpath," + str(packages["candidate"]), "-o", test])
with (RUN / "p35-test.log").open("w") as log:
    command([test], stdout=log)

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

rows = [row for path in logs for row in csv.reader(path.read_text().splitlines())
        if row and row[0] in {"full", "component"}]
summary = {}
for operation in ("inverse_to_ternary", "keygen", "encaps", "decaps"):
    summary[operation] = {}
    for label in ("baseline", "candidate"):
        values = [list(map(float, row[3:6])) for row in rows if row[1] == operation and row[2] == label]
        summary[operation][label] = {key: statistics.median(value[index] for value in values)
                                     for index, key in enumerate(("cycles", "instructions", "branches"))}
    summary[operation]["delta"] = {key: summary[operation]["candidate"][key] - summary[operation]["baseline"][key]
                                     for key in ("cycles", "instructions", "branches")}
    summary[operation]["cycle_delta_percent"] = 100 * (summary[operation]["candidate"]["cycles"] /
                                                         summary[operation]["baseline"]["cycles"] - 1)
result = {
    "status": "promote" if summary["inverse_to_ternary"]["delta"]["cycles"] < 0 and summary["decaps"]["delta"]["cycles"] < 0 else "reject",
    "correctness": {"test_kem": "pass both", "kat": kats, "malformed": traces,
                    "inverse_exact_alias_aapcs_wipe": (RUN / "p35-test.log").read_text().strip()},
    "summary": summary,
    "environment": {"uname": output(["uname", "-a"]), "gcc": output(["gcc", "--version"]).splitlines()[0],
                    "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
                    "temperature": output(["vcgencmd", "measure_temp"]), "throttled": output(["vcgencmd", "get_throttled"]),
                    "core": 3, "processes": 6, "supercop_reference_root": "/home/pi/supercop-20260831"},
    "binary_hashes": {name: sha(package / "libgt864.so") for name, package in packages.items()},
}
(P / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
