"""Pi5 correctness and paired PMU for P2-A, P2-B, and combined P2-AB."""
import csv
import hashlib
import json
import pathlib
import statistics
import subprocess

P = pathlib.Path(__file__).resolve().parent
B = P / "build"
OUT = P / "pi-results"
OUT.mkdir(exist_ok=True)
variants = ["p1", "p2a", "p2b", "p2ab"]
env = {
    "uname": subprocess.check_output(["uname", "-a"], text=True).strip(),
    "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
    "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
}
for name in variants:
    path = B / name
    with (OUT / f"build-{name}.log").open("w") as log:
        subprocess.run(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], cwd=path, check=True, stdout=log, stderr=subprocess.STDOUT)
    for exe in ["test_kem", "PQCgenKAT_kem"]:
        with (OUT / f"{exe}-{name}.log").open("w") as log:
            subprocess.run([f"./{exe}"], cwd=path, check=True, stdout=log, stderr=subprocess.STDOUT)
    (OUT / f"{name}.so").write_bytes((path / "libgt864.so").read_bytes())

kats = {(B / name / "PQCkemKAT_2624.rsp").read_bytes() for name in variants}
assert len(kats) == 1
harness = P / "pi-bench.c"
subprocess.run(["gcc", "-O3", "-rdynamic", str(harness), "-ldl", "-o", str(OUT / "pi-bench")], check=True)
rows = []
for candidate in variants[1:]:
    for reverse in [0, 1]:
        for repeat in range(3):
            command = ["taskset", "-c", "3", str(OUT / "pi-bench"), str(OUT / "p1.so"), str(OUT / f"{candidate}.so"), str(reverse)]
            text = subprocess.check_output(command, text=True)
            (OUT / f"{candidate}-{reverse}-{repeat}.csv").write_text(text)
            for row in csv.reader(text.splitlines()):
                if row and row[0] in ("full", "component"):
                    rows.append((candidate, row[1], row[2], *map(float, row[3:6])))

summary = {}
for candidate in variants[1:]:
    for op in sorted({x[1] for x in rows if x[0] == candidate}):
        entry = summary.setdefault(candidate, {}).setdefault(op, {})
        for side in ["baseline", "candidate"]:
            vals = [x[3:] for x in rows if x[:3] == (candidate, op, side)]
            entry[side] = {key: statistics.median(v[i] for v in vals) for i, key in enumerate(["cycles", "instructions", "branches"])}
        entry["delta"] = {key: entry["candidate"][key] - entry["baseline"][key] for key in ["cycles", "instructions", "branches"]}
        entry["cycle_delta_percent"] = 100 * (entry["candidate"]["cycles"] / entry["baseline"]["cycles"] - 1)
result = {
    "environment": env, "benchmarks": summary,
    "kat_sha256": hashlib.sha256(next(iter(kats))).hexdigest(),
    "binaries": {name: hashlib.sha256((OUT / f"{name}.so").read_bytes()).hexdigest() for name in variants},
}
(P / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
