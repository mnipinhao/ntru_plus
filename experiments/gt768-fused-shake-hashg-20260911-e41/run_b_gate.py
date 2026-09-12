#!/usr/bin/env python3
"""Run from the staged experiment directory on Pi5; outputs stay in .build."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("root", type=Path)
ap.add_argument("--name", default="b-gate-v1")
ap.add_argument("--gate", choices=("B", "C", "D"), default="B")
args = ap.parse_args()
root = args.root.resolve()
build = root / ".build" / args.name
build.mkdir(parents=True, exist_ok=False)
sources = {"A": root / "baseline", "B": root / "candidate"}
if args.gate == "C":
    sources["C"] = root / "candidate-c"
if args.gate == "D":
    sources = {"A": root / "baseline", "C": root / "candidate-c", "D": root / "candidate-d"}
target_label = args.gate
pair_count = 62 if args.gate == "B" else 66
orders = list(itertools.permutations(sources))
harness = root / "harness"
flags = ["-march=armv8-a", "-mtune=cortex-a76", "-O3", "-fomit-frame-pointer",
         "-ffunction-sections", "-fdata-sections", "-std=c99"]
kem = ["kem.c", "symmetric.c", "fips202.c", "keygen.c", "keygen_lambda.c",
       "basemul_lambda.c", "ntt.S", "base.S", "pack.S", "cbd.S",
       "crepmod3.S", "kem_api.S", "add.S", "keccakf1600.S"]
commands = []

def run(cmd, logfile=None, cwd=None):
    cmd = list(map(str, cmd))
    commands.append({"command": cmd, "cwd": str(cwd or root)})
    p = subprocess.run(cmd, cwd=cwd or root, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if logfile:
        (build / logfile).write_text(p.stdout)
    if p.returncode:
        raise RuntimeError(str(cmd) + "\n" + p.stdout[-6000:])
    return p.stdout

def env():
    return {"throttling": run(["vcgencmd", "get_throttled"]).strip(),
            "temperature": run(["vcgencmd", "measure_temp"]).strip(),
            "frequency": run(["vcgencmd", "measure_clock", "arm"]).strip()}

def stats(v):
    v = sorted(v)
    return {"count": len(v), "min": min(v), "p10": v[len(v)//10],
            "p50": statistics.median(v), "p90": v[len(v)*9//10], "max": max(v)}

environment = {"before": env(), "jobs": run(["ps", "-eo", "pid,pcpu,args", "--sort=-pcpu"])}
print("Building and checking selected packages: " + ", ".join(sources), flush=True)
for label, src in sources.items():
    run(["make", "-j3", "check", "CC=gcc", "CFLAGS=" + " ".join(flags),
         "BUILD_DIR=" + str(build / ("package-" + label))],
        "check-" + label + ".log", src)

src = sources[target_label]
includes = ["-I" + str(src), "-I" + str(harness)]
testobj = build / "fips-test.o"
run(["gcc", *flags, *includes, "-DGT_SECURE_CLEAR_AUDIT_HOOK",
     "-Dntruplus_keccak_f1600_x1_aarch64=counted_permute", "-c",
     src / "fips202.c", "-o", testobj])
d_test = (["-DTEST_FUSED", root / "experiment/test_fused_frame.c",
           root / "experiment/capture_fused_frame.S"] if args.gate == "D" else [])
run(["gcc", *flags, *includes, "-DGT_SECURE_CLEAR_AUDIT_HOOK", *d_test,
     root / ("experiment/test_prefix.c" if args.gate == "B" else "experiment/test_fixed.c"), testobj, src / "symmetric.c",
     src / "keccakf1600.S", "-o", build / "test-prefix"])
test_result = run([build / "test-prefix"], "prefix-test.log").strip()
print(test_result, flush=True)

bins = {}
for label, src in sources.items():
    inc = ["-I" + str(src), "-I" + str(harness)]
    for mode in ("hash_g", "encap", "decap"):
        binary = build / (label + "-" + mode)
        inputs = ([harness / "bench_hash.c", src / "symmetric.c",
                   src / "fips202.c", src / "keccakf1600.S"] if mode == "hash_g"
                  else [harness / "bench_kem.c", harness / "deterministic_randombytes.c",
                        *[src / f for f in kem]])
        run(["gcc", *flags, *inc, "-DNTESTS=1", "-DNITERATIONS=2000",
             '-DBENCH_MODE_STR="' + mode + '"', *inputs, harness / "perf_counter.c",
             "-Wl,--gc-sections", "-o", binary], label + "-" + mode + "-build.log")
        bins[label, mode] = binary
        run(["objdump", "-d", binary], label + "-" + mode + ".dis")

environment["before_timing"] = env()
samples = {}
result = {}
for mode in ("hash_g", "encap", "decap"):
    print("Paired measurement: " + mode, flush=True)
    samples[mode] = {label: [] for label in sources}
    sinks = set()
    for pair in range(pair_count):
        for label in orders[pair % len(orders)]:
            text = run(["taskset", "-c", "3", bins[label, mode]],
                       f"{mode}-{pair:02d}-{label}.txt")
            fields = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)
            samples[mode][label].append(int(fields["samples"]))
            sinks.add(fields["sink"])
    assert len(sinks) == 1, (mode, sinks)
    a, b = samples[mode]["A"], samples[mode][target_label]
    delta = [x-y for x,y in zip(a,b)]
    result[mode] = {**{label: stats(v) for label, v in samples[mode].items()},
                    "paired_saved_cycles_vs_A": stats(delta),
                    "sink": next(iter(sinks)),
                    "percent_saved_from_medians": 100*(statistics.median(a)-statistics.median(b))/statistics.median(a)}
    if args.gate != "B":
        previous_label = "B" if args.gate == "C" else "C"
        previous = samples[mode][previous_label]
        result[mode]["paired_saved_cycles_vs_" + previous_label] = stats([x-y for x,y in zip(previous,b)])
        result[mode]["percent_saved_vs_" + previous_label] = 100*(statistics.median(previous)-statistics.median(b))/statistics.median(previous)
    print(json.dumps({mode: result[mode]}), flush=True)

# Long component runs reduce process-start overhead in external perf counts.
pmu = {}
for label, src in sources.items():
    binary = build / (label + "-hash-g-pmu")
    run(["gcc", *flags, "-I" + str(src), "-I" + str(harness),
         "-DNTESTS=1", "-DNITERATIONS=200000", "-DNWARMUP=0",
         '-DBENCH_MODE_STR="hash_g"', harness / "bench_hash.c",
         src / "symmetric.c", src / "fips202.c", src / "keccakf1600.S",
         harness / "perf_counter.c", "-Wl,--gc-sections", "-o", binary])
    bins[label, "pmu"] = binary
for repeat in range(4 if args.gate == "B" else 6):
    for label in orders[repeat % len(orders)]:
        raw = run(["perf", "stat", "-x,", "-e",
                   "instructions:u,ld_spec:u,st_spec:u,stall_backend:u",
                   "taskset", "-c", "3", bins[label, "pmu"]],
                  f"pmu-{repeat}-{label}.txt")
        values = {}
        for line in raw.splitlines():
            fields = line.split(",")
            if len(fields) > 4 and fields[0].strip().isdigit():
                values[fields[2]] = int(fields[0]) / 200000
        assert len(values) == 4, raw
        pmu.setdefault(label, []).append(values)
environment["after"] = env()
sizes = {label: run(["size", bins[label, "hash_g"], bins[label, "encap"]]).strip()
         for label in sources}
identities = {
    label: {f: hashlib.sha256((src/f).read_bytes()).hexdigest()
            for f in ("symmetric.c", "fips202.c", "fips202.h", "keccakf1600.S")}
    for label, src in sources.items()
}
summary = {"experiment_id": "gt768-fused-shake-hashg-20260911-e41",
           "gate": args.gate, "baseline_revision": "a64e7035cb13410554af1c67870d4132a30037b4",
           "B_revision": "5300d169fa04b2459bf1093c435e9e22843cfee4",
           "C_revision": "1493b298e790990038d15c146288280db943d79e",
           "host": run(["uname", "-a"]).strip(),
           "compiler": run(["gcc", "--version"]).splitlines()[0], "flags": flags,
           "core": 3, "pairs": pair_count, "operations_per_sample": 2000, "warmups": 100,
           "order": orders,
           "test": test_result, "results": result, "pmu_per_operation": pmu,
           "sizes": sizes, "source_sha256": identities, "environment": environment}
(build / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
(build / "samples.json").write_text(json.dumps(samples, indent=2) + "\n")
(build / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
print("Complete: " + str(build / "summary.json"), flush=True)
