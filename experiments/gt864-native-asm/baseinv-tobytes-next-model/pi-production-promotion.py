"""Validate and benchmark the promoted production tree on Raspberry Pi 5.

Run from the uploaded promotion bundle.  The selected comparison source is the
unmodified SUPERCOP 20260831 ntruplus864/aarch64 directory.
"""
import csv
import hashlib
import json
import pathlib
import re
import shutil
import statistics
import subprocess

P = pathlib.Path(__file__).resolve().parent
PROD = P / "production"
OUT = P / "promotion-results"
SUPERCOP = pathlib.Path("/home/pi/supercop-20260831")
OFFICIAL_SRC = SUPERCOP / "crypto_kem/ntruplus864/aarch64"
COMPAT = P / "supercop-compat"
OUT.mkdir(exist_ok=True)

processes = subprocess.check_output(["ps", "-eo", "args"], text=True)
if re.search(r"(?:^|/)do-part(?: |$)", processes, re.M):
    raise RuntimeError("SUPERCOP benchmark is active; refusing a competing PMU run")


def run(command, *, cwd=None, log=None):
    stream = None if log is None else log.open("a")
    try:
        subprocess.run(command, cwd=cwd, check=True, stdout=stream,
                       stderr=subprocess.STDOUT if stream else None)
    finally:
        if stream:
            stream.close()


build_log = OUT / "build-production.log"
build_log.write_text("")
run(["make", "manifest-check"], cwd=PROD, log=build_log)
run(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"],
    cwd=PROD, log=build_log)
run(["./test_kem"], cwd=PROD, log=OUT / "test-production.log")
run(["./PQCgenKAT_kem"], cwd=PROD, log=OUT / "kat-production.log")

# Exercise the linked BaseInv objects: success/failure, every zero leaf, exact
# in-place aliasing, output canaries, AAPCS preservation and wrapper scratch wipe.
prod_objects = [str(p) for p in PROD.glob("*.o") if p.name != "kem-normal.o"]
run([
    "gcc", "-O2", "-I" + str(PROD),
    str(P / "integration/test_baseinv.c"),
    str(P / "integration/probe_baseinv.S"),
    *prod_objects, "-o", str(OUT / "check-baseinv"),
])
run([str(OUT / "check-baseinv")], log=OUT / "baseinv-production.log")

# Record the complete valid/tampered/malformed KEM transcript.  KAT equality is
# the compatibility oracle; this transcript additionally covers rejection paths.
run([
    "gcc", "-O2", "-I" + str(PROD), str(P / "kem-malformed-transcript.c"),
    *[str(p) for p in PROD.glob("*.o")], "-o", str(OUT / "malformed-transcript"),
])
with (OUT / "malformed.trace").open("w") as trace:
    subprocess.run([str(OUT / "malformed-transcript")], check=True, stdout=trace)

# Build the selected Official source without modifying the SUPERCOP tree.
official_copy = OUT / "official-source"
shutil.copytree(OFFICIAL_SRC, official_copy, dirs_exist_ok=True)
flags = [
    "gcc", "-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE",
    "-fPIC", "-ffunction-sections", "-fdata-sections", "-I" + str(official_copy),
    "-I" + str(COMPAT), "-I" + str(SUPERCOP / "bench/pinhao/include/aarch64"),
    "-I" + str(PROD),
]
official_objects = []
official_log = OUT / "build-official.log"
official_log.write_text("")
for source in sorted(official_copy.iterdir()):
    if source.suffix not in (".c", ".s"):
        continue
    obj = OUT / (source.name + ".o")
    run(flags + ["-x", "assembler-with-cpp" if source.suffix == ".s" else "c",
                 "-c", str(source), "-o", str(obj)], log=official_log)
    official_objects.append(obj)
optblocker = OUT / "optblocker.o"
run(flags + ["-c", str(COMPAT / "optblocker.c"), "-o", str(optblocker)],
    log=official_log)
official_objects.append(optblocker)
run(["gcc", "-shared", "-Wl,-Bsymbolic", "-Wl,--gc-sections",
     *map(str, official_objects), "-o", str(OUT / "official.so")], log=official_log)
shutil.copy2(PROD / "libgt864.so", OUT / "gt-production.so")

run(["gcc", "-O3", "-rdynamic", str(P / "pi-kem-only.c"), "-ldl",
     "-o", str(OUT / "kem-only")])
rows = []
for repetition in range(6):
    csv_file = OUT / f"paired-{repetition}.csv"
    with csv_file.open("w") as output:
        subprocess.run([
            "taskset", "-c", "3", str(OUT / "kem-only"),
            str(OUT / "official.so"), str(OUT / "gt-production.so"),
            str(repetition % 2),
        ], check=True, stdout=output, stderr=subprocess.STDOUT)
    for row in csv.reader(csv_file.read_text().splitlines()):
        if row and row[0] in ("keygen", "encaps", "decaps"):
            rows.append((row[0], row[1], *map(float, row[2:])))

summary = {}
for operation in ("keygen", "encaps", "decaps"):
    summary[operation] = {}
    for implementation in ("official", "gt-candidate"):
        values = [row[2:] for row in rows if row[:2] == (operation, implementation)]
        summary[operation][implementation] = {
            key: statistics.median(value[index] for value in values)
            for index, key in enumerate(("cycles", "instructions", "branches"))
        }
    summary[operation]["cycle_delta_percent"] = 100 * (
        summary[operation]["gt-candidate"]["cycles"]
        / summary[operation]["official"]["cycles"] - 1
    )

kat = PROD / "PQCkemKAT_2624.rsp"
trace = OUT / "malformed.trace"
result = {
    "production_source": str(PROD),
    "official_source": str(OFFICIAL_SRC),
    "official_upstream_latest_verified": False,
    "correctness": {
        "test_kem": "pass",
        "kat_cases": kat.read_text().count("count = "),
        "kat_sha256": hashlib.sha256(kat.read_bytes()).hexdigest(),
        "baseinv_linked_component": "pass",
        "malformed_trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest(),
        "malformed_trace_bytes": trace.stat().st_size,
    },
    "summary": summary,
    "environment": {
        "uname": subprocess.check_output(["uname", "-a"], text=True).strip(),
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "governor": pathlib.Path(
            "/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor"
        ).read_text().strip(),
        "temperature": subprocess.check_output(
            ["vcgencmd", "measure_temp"], text=True
        ).strip(),
    },
    "hashes": {
        name: hashlib.sha256((OUT / name).read_bytes()).hexdigest()
        for name in ("official.so", "gt-production.so")
    },
}
(P / "production-promotion-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
