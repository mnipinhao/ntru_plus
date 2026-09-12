#!/usr/bin/env python3
"""P9 target audit, same-boundary PMU and conditional full-KEM campaign."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
SYNC = BUILD / "sync"
RAW = BUILD / "pi5"
HOST = "pi@100.99.191.9"
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p9-20260912"


def output(arguments: list[object], cwd: Path | None = None) -> str:
    return subprocess.check_output(
        [str(value) for value in arguments], cwd=cwd, text=True,
        stderr=subprocess.STDOUT,
    )


def ssh(command: str) -> str:
    return output([
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
        HOST, command,
    ])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stage() -> None:
    subprocess.run([sys.executable, HERE / "prepare.py"], check=True)
    if SYNC.exists():
        shutil.rmtree(SYNC)
    shutil.copytree(BUILD / "packages", SYNC / "packages")
    component = (ROOT / (
        "experiments/gt864-native-asm/p6-zero-scratch-tobytes/"
        "p6e-pi-timing/bench.c"
    )).read_text()
    component = component.replace(
        'must_symbol(hc, small ? "gt864_p6d3_small_asm" : "gt864_p6d3_full_asm")',
        'must_symbol(hc, small ? "gt864_fr0_tobytes_small" : "gt864_fr0_tobytes_full")',
    )
    (SYNC / "component.c").write_text(component)
    kem = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    kem = kem.replace('v?"gt":"official"', 'v?"candidate":"baseline"')
    (SYNC / "kem.c").write_text(kem)
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 SYNC / "malformed.c")
    manifest = {
        str(path.relative_to(SYNC)): sha256(path)
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    (BUILD / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )


def function_body(disassembly: str, needle: str) -> str:
    labels = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:\n", disassembly))
    matches = [index for index, label in enumerate(labels)
               if needle in label.group(2)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one {needle} symbol, got {matches}")
    index = matches[0]
    start = labels[index].end()
    end = labels[index + 1].start() if index + 1 < len(labels) else len(disassembly)
    return disassembly[start:end]


def instruction_count(body: str) -> int:
    return len(re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+\S+", body))


def target_audit() -> dict[str, object]:
    audit: dict[str, object] = {}
    for mode in ("full", "small"):
        disassembly = ssh(
            f"cd {REMOTE}/packages/{mode} && "
            f"objdump -d gt864_p9_tobytes_{mode}.o && "
            f"objdump -d p9_tobytes_public_{mode}.o"
        )
        (RAW / f"object-{mode}.log").write_text(disassembly)
        top = function_body(disassembly, f"p9_input_once_top_{mode}")
        inner = function_body(disassembly, f"gt864_p9_input_once_{mode}_inner")
        public = function_body(disassembly, f"gt864_p9_tobytes_{mode}_asm")
        top_instructions = instruction_count(top)
        dynamic = 2 * top_instructions + instruction_count(inner) + instruction_count(public)
        q_stack = re.findall(
            r"(?mi)^.*\b(?:ldr|str|ldp|stp)\s+q[^\n]*\[sp[^\n]*$", top
        )
        if q_stack:
            raise RuntimeError(f"{mode} coefficient-vector spill: {q_stack[:3]}")
        if dynamic > 4061 - 829:
            raise RuntimeError(f"{mode} static gate failed: {dynamic}")
        mnemonics = re.findall(
            r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+(\S+)", top
        )
        audit[mode] = {
            "top_instructions": top_instructions,
            "inner_instructions": instruction_count(inner),
            "public_instructions": instruction_count(public),
            "dynamic_path_instructions": dynamic,
            "delta_vs_p6_d3_4061": dynamic - 4061,
            "load_mnemonics_per_top": sum(x.startswith(("ldr", "ldp")) for x in mnemonics),
            "sqrdmulh_per_top": mnemonics.count("sqrdmulh"),
            "mls_per_top": mnemonics.count("mls"),
            "tbl_per_top": sum(x.startswith("tbl") for x in mnemonics),
            "coefficient_q_spill": False,
        }
    if audit["small"]["sqrdmulh_per_top"] != 0:
        raise RuntimeError("small path unexpectedly retained Barrett SQRDMULH")
    (BUILD / "target-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    return audit


def parse_component(paths: list[Path]) -> dict[str, dict[str, float]]:
    rows: dict[str, list[list[float]]] = {}
    for path in paths:
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] == "sample":
                rows.setdefault(row[2], []).append([float(x) for x in row[4:9]])
    metrics = ["cycles", "instructions", "branches", "mem_access_rd", "mem_access_wr"]
    return {
        variant: {
            metric: statistics.median(sample[index] for sample in samples)
            for index, metric in enumerate(metrics)
        }
        for variant, samples in rows.items()
    }


def parse_kem(paths: list[Path]) -> dict[str, dict[str, dict[str, float]]]:
    rows: dict[tuple[str, str], list[list[float]]] = {}
    for path in paths:
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] == "clean":
                rows.setdefault((row[1], row[2]), []).append(
                    [float(x) for x in row[3:6]]
                )
    result: dict[str, dict[str, dict[str, float]]] = {}
    for (operation, variant), samples in rows.items():
        result.setdefault(operation, {})[variant] = {
            metric: statistics.median(sample[index] for sample in samples)
            for index, metric in enumerate(("cycles", "instructions", "branches"))
        }
    return result


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
    if "Cortex" not in ssh("lscpu | grep 'Model name'") or "throttled=0x0" not in environment:
        raise RuntimeError(environment)
    (RAW / "environment-before.txt").write_text(environment)

    commands = []
    for name in ("baseline", "full", "small", "both"):
        commands.append(
            f"make -C packages/{name} clean >/dev/null 2>&1 || true; "
            f"make -C packages/{name} -B -j4 libgt864.so test_kem PQCgenKAT_kem; "
            f"packages/{name}/test_kem; "
            f"cd packages/{name}; ./PQCgenKAT_kem >/dev/null; cd ../.."
        )
    commands += [
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic component.c -ldl -o component",
        "gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic kem.c -ldl -o kem",
    ]
    build_log = ssh(f"cd {REMOTE} && " + " && ".join(commands))
    if build_log.count("PASS: 64 KEM") != 4:
        raise RuntimeError("not all target KEM tests passed")
    (RAW / "build.log").write_text(build_log)
    audit = target_audit()
    print("P9 target static gate passed", json.dumps(audit), flush=True)

    components: dict[str, object] = {}
    winning: list[str] = []
    for mode in ("full", "small"):
        paths = []
        for reverse in (0, 1):
            path = RAW / f"component-{mode}-{reverse}.csv"
            text = ssh(
                f"cd {REMOTE} && taskset -c 3 ./component "
                f"packages/baseline/libgt864.so packages/{mode}/libgt864.so "
                f"{mode} {reverse}"
            )
            path.write_text(text)
            if "correctness=pass" not in text:
                raise RuntimeError(f"{mode} target correctness failed")
            paths.append(path)
        summary = parse_component(paths)
        delta = {
            metric: summary["candidate"][metric] - summary["baseline"][metric]
            for metric in summary["baseline"]
        }
        components[mode] = {"measurements": summary, "delta": delta}
        if delta["cycles"] < 0:
            winning.append(mode)
        print(f"P9 {mode} component delta {delta}", flush=True)

    if not winning:
        raise RuntimeError("P9 has no winning public ToBytes mode")
    kem_variants = winning + (["both"] if len(winning) == 2 else [])
    kem_results: dict[str, object] = {}
    for candidate in kem_variants:
        paths = []
        for process in range(6):
            path = RAW / f"kem-{candidate}-{process}.csv"
            text = ssh(
                f"cd {REMOTE} && taskset -c 3 ./kem "
                f"packages/baseline/libgt864.so packages/{candidate}/libgt864.so "
                f"{process % 2}"
            )
            path.write_text(text)
            if "correctness=pass exact=100 tampered=100" not in text:
                raise RuntimeError(f"{candidate} KEM compatibility failed")
            paths.append(path)
        summary = parse_kem(paths)
        for operation in summary:
            summary[operation]["delta"] = {
                metric: (summary[operation]["candidate"][metric] -
                         summary[operation]["baseline"][metric])
                for metric in summary[operation]["baseline"]
            }
        kem_results[candidate] = summary
        print(f"P9 {candidate} full-KEM complete", flush=True)

    # Exact KAT and malformed transcript are required only for the combined
    # candidate when both modes win; otherwise they cover the sole winner.
    promoted = "both" if "both" in kem_variants else winning[0]
    transcript = ssh(
        f"cd {REMOTE} && "
        f"gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic "
        f"-Ipackages/{promoted} malformed.c -Lpackages/{promoted} -lgt864 "
        f"-Wl,-rpath,{REMOTE}/packages/{promoted} -o malformed-{promoted} && "
        f"./malformed-{promoted} | sha256sum && "
        f"cd packages/{promoted} && sha256sum PQCkemKAT_2624.rsp"
    )
    hashes = [line.split()[0] for line in transcript.strip().splitlines()]
    if hashes != [
        "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67",
        "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c",
    ]:
        raise RuntimeError(f"P9 transcript/KAT mismatch: {hashes}")
    environment_after = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
    if "throttled=0x0" not in environment_after:
        raise RuntimeError(environment_after)
    (RAW / "environment-after.txt").write_text(environment_after)

    result = {
        "experiment": "P9",
        "host": HOST,
        "remote": REMOTE,
        "baseline_revision": "766cc844",
        "static_audit": audit,
        "components": components,
        "winning_modes": winning,
        "kem": kem_results,
        "promotion_candidate": promoted,
        "transcript_and_kat": transcript.strip().splitlines(),
        "environment_before": environment.strip().splitlines(),
        "environment_after": environment_after.strip().splitlines(),
        "source_manifest_sha256": sha256(BUILD / "source-manifest.json"),
    }
    (HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
