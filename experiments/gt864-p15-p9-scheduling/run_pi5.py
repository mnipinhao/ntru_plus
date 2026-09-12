#!/usr/bin/env python3
"""Build, audit, and benchmark P15 against the frozen production P9 boundary."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import statistics
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
SYNC = BUILD / "sync"
RAW = BUILD / "pi5"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p15-20260912"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")


def output(args: list[object], cwd: Path | None = None) -> str:
    return subprocess.check_output([str(x) for x in args], cwd=cwd, text=True,
                                   stderr=subprocess.STDOUT)


def ssh(command: str) -> str:
    return output(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                   HOST, command])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract(destination: Path) -> None:
    data = subprocess.check_output(["git", "archive", "HEAD", str(PRODUCTION)], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        for member in archive.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())


def stage() -> None:
    if SYNC.exists():
        shutil.rmtree(SYNC)
    for name in ("baseline", "candidate"):
        extract(SYNC / "packages" / name)
    candidate = SYNC / "packages" / "candidate"
    for mode in ("full", "small"):
        shutil.copy2(BUILD / f"p15-{mode}.opt.S", candidate / f"p15-{mode}.S")
    makefile = candidate / "Makefile"
    text = makefile.read_text()
    for mode in ("full", "small"):
        old = (
            f"gt864_p9_tobytes_{mode}.o: gt864_p9_tobytes_{mode}.c p9_tobytes.h\n"
            "\t$(CC) $(CFLAGS) -I. -c $< -o $@"
        )
        new = (
            f"gt864_p9_tobytes_{mode}.o: p15-{mode}.S p9_tobytes.h\n"
            "\t$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@"
        )
        if text.count(old) != 1:
            raise RuntimeError(f"Makefile rule drift: {mode}")
        text = text.replace(old, new)
    makefile.write_text(text)
    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c"
    )).read_text().replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")',
    )
    (SYNC / "component.c").write_text(component)
    manifest = {str(p.relative_to(SYNC)): sha256(p)
                for p in sorted(SYNC.rglob("*")) if p.is_file()}
    (BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def function_body(disassembly: str, needle: str) -> str:
    labels = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:\n", disassembly))
    matches = [i for i, label in enumerate(labels) if needle in label.group(2)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {needle} symbol, got {matches}")
    index = matches[0]
    return disassembly[labels[index].end():
                       labels[index + 1].start() if index + 1 < len(labels) else len(disassembly)]


def section_body(disassembly: str, name: str) -> str:
    marker = f"Disassembly of section {name}:\n"
    if disassembly.count(marker) != 1:
        raise RuntimeError(f"expected one {name} section")
    body = disassembly.split(marker, 1)[1]
    return body.split("\nDisassembly of section ", 1)[0]


def count_instructions(body: str) -> int:
    return len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", body))


def target_audit() -> dict[str, object]:
    result: dict[str, object] = {}
    for mode in ("full", "small"):
        entries = {}
        for variant in ("baseline", "candidate"):
            dis = ssh(f"cd {REMOTE}/packages/{variant} && objdump -d gt864_p9_tobytes_{mode}.o")
            (RAW / f"object-{variant}-{mode}.log").write_text(dis)
            # Slothy window labels are deliberately retained in the candidate
            # object and therefore appear as local symbols in objdump.  Audit
            # the whole function section instead of stopping at the first
            # window label.
            body = section_body(dis, f".text.p9_input_once_top_{mode}")
            entries[variant] = {
                "top_instructions": count_instructions(body),
                "q_stack_accesses": len(re.findall(
                    r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", body)),
            }
        if entries["baseline"] != entries["candidate"]:
            raise RuntimeError(f"target audit changed {mode}: {entries}")
        result[mode] = entries
    return result


def summarize(paths: list[Path]) -> dict[str, dict[str, float]]:
    samples: dict[str, list[list[float]]] = {}
    for path in paths:
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] == "sample":
                samples.setdefault(row[2], []).append([float(x) for x in row[4:9]])
    metrics = ("cycles", "instructions", "branches", "mem_access_rd", "mem_access_wr")
    return {name: {metric: statistics.median(x[i] for x in values)
                   for i, metric in enumerate(metrics)}
            for name, values in samples.items()}


def main() -> None:
    stage()
    RAW.mkdir(parents=True, exist_ok=True)
    ssh(f"mkdir -p {REMOTE}")
    print(output(["rsync", "-av", str(SYNC) + "/", HOST + ":" + REMOTE + "/"]),
          flush=True)
    environment = ssh(
        "uname -a; gcc --version | head -1; "
        "cat /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor; "
        "vcgencmd measure_temp; vcgencmd get_throttled; "
        "ps -eo args | grep '[d]o-part' || true"
    )
    if "throttled=0x0" not in environment or ssh("lscpu | grep 'Model name'").count("Cortex-A76") != 1:
        raise RuntimeError(environment)
    (RAW / "environment-before.txt").write_text(environment)
    commands = []
    for variant in ("baseline", "candidate"):
        commands += [
            f"make -C packages/{variant} clean >/dev/null 2>&1 || true",
            f"make -C packages/{variant} -B -j4 libgt864.so test_kem PQCgenKAT_kem",
            f"packages/{variant}/test_kem",
            f"cd packages/{variant}; ./PQCgenKAT_kem >/dev/null; cd ../..",
        ]
    commands.append("gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic component.c -ldl -o component")
    build = ssh(f"cd {REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2:
        raise RuntimeError("target KEM validation failed")
    (RAW / "build.log").write_text(build)
    kat_lines = ssh(
        f"cd {REMOTE} && sha256sum "
        "packages/baseline/PQCkemKAT_2624.rsp "
        "packages/candidate/PQCkemKAT_2624.rsp"
    ).strip().splitlines()
    kat_hashes = [line.split()[0] for line in kat_lines]
    if len(kat_hashes) != 2 or len(set(kat_hashes)) != 1:
        raise RuntimeError(f"KAT mismatch: {kat_lines}")
    audit = target_audit()
    modes: dict[str, object] = {}
    for mode in ("full", "small"):
        paths = []
        for reverse in (0, 1):
            path = RAW / f"component-{mode}-{reverse}.csv"
            measured = ssh(
                f"cd {REMOTE} && taskset -c 3 ./component "
                f"packages/baseline/libgt864.so packages/candidate/libgt864.so {mode} {reverse}"
            )
            path.write_text(measured)
            if "correctness=pass cases=513 canaries=pass" not in measured:
                raise RuntimeError(f"{mode} correctness failed")
            paths.append(path)
        values = summarize(paths)
        delta = {metric: values["candidate"][metric] - values["baseline"][metric]
                 for metric in values["baseline"]}
        modes[mode] = {"measurements": values, "delta": delta,
                       "wins_cycles": delta["cycles"] < 0}
        print(mode, delta, flush=True)
    after = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
    if "throttled=0x0" not in after:
        raise RuntimeError(after)
    result = {
        "experiment": "P15",
        "baseline_revision": output(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "host": HOST,
        "remote": REMOTE,
        "target_audit": audit,
        "kat_sha256": kat_hashes[0],
        "modes": modes,
        "promotion_gate_passed": all(x["wins_cycles"] for x in modes.values()),
        "environment_before": environment.strip().splitlines(),
        "environment_after": after.strip().splitlines(),
        "source_manifest_sha256": sha256(BUILD / "source-manifest.json"),
    }
    (HERE / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
