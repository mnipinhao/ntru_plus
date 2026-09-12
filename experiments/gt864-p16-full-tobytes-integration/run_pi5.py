#!/usr/bin/env python3
"""Run P16 full-only P15 schedule integration and production gates on Pi 5."""

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
REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p16-20260912"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")
P15_FULL = ROOT / "experiments/gt864-p15-p9-scheduling/build/p15-full.opt.S"
P15_FULL_SHA256 = "2a59fbf9567124f28c009de0c1989e33600be64e795c4a47e634ba4d0a46deb2"
EXPECTED_KAT = "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c"
EXPECTED_MALFORMED = "2404a992d9e625c1287f0fb5b95134fbadf8632830af5fb1532e3f7a3bfdeb67"


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
    if sha256(P15_FULL) != P15_FULL_SHA256:
        raise RuntimeError("P15 full artifact identity changed")
    if SYNC.exists():
        shutil.rmtree(SYNC)
    for name in ("baseline", "candidate"):
        extract(SYNC / "packages" / name)
    candidate = SYNC / "packages" / "candidate"
    shutil.copy2(P15_FULL, candidate / "p16-full.S")
    makefile = candidate / "Makefile"
    text = makefile.read_text()
    old = (
        "gt864_p9_tobytes_full.o: gt864_p9_tobytes_full.c p9_tobytes.h\n"
        "\t$(CC) $(CFLAGS) -I. -c $< -o $@"
    )
    new = (
        "gt864_p9_tobytes_full.o: p16-full.S p9_tobytes.h\n"
        "\t$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@"
    )
    if text.count(old) != 1:
        raise RuntimeError("full ToBytes Makefile rule drift")
    makefile.write_text(text.replace(old, new))
    harness = (ROOT / "experiments/gt864-official-profile-p8/full_harness.c").read_text()
    harness = harness.replace('v?"gt":"official"', 'v?"candidate":"baseline"')
    (SYNC / "kem.c").write_text(harness)
    shutil.copy2(ROOT / "experiments/gt864-native-asm/kem-malformed-transcript.c",
                 SYNC / "malformed.c")
    manifest = {str(p.relative_to(SYNC)): sha256(p)
                for p in sorted(SYNC.rglob("*")) if p.is_file()}
    (BUILD / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def section(disassembly: str, name: str) -> str:
    marker = f"Disassembly of section {name}:\n"
    if disassembly.count(marker) != 1:
        raise RuntimeError(f"expected one section {name}")
    return disassembly.split(marker, 1)[1].split("\nDisassembly of section ", 1)[0]


def instructions(body: str) -> list[str]:
    return re.findall(r"(?m)^\s*[0-9a-f]+:\s+[0-9a-f]+\s+(.*)$", body)


def object_audit() -> dict[str, object]:
    result: dict[str, object] = {}
    for mode in ("full", "small"):
        variants = {}
        for variant in ("baseline", "candidate"):
            dis = ssh(f"cd {REMOTE}/packages/{variant} && objdump -d gt864_p9_tobytes_{mode}.o")
            (RAW / f"object-{variant}-{mode}.log").write_text(dis)
            body = section(dis, f".text.p9_input_once_top_{mode}")
            ins = instructions(body)
            variants[variant] = {
                "top_instructions": len(ins),
                "q_stack_accesses": sum(
                    bool(re.search(r"\b(?:ldr|str|ldp|stp)\s+q.*\[sp", x)) for x in ins
                ),
            }
        if variants["baseline"] != variants["candidate"]:
            raise RuntimeError(f"object contract changed for {mode}: {variants}")
        result[mode] = variants
    # Small was not rebuilt from a different source: require complete object identity.
    hashes = ssh(
        f"cd {REMOTE} && sha256sum packages/baseline/gt864_p9_tobytes_small.o "
        "packages/candidate/gt864_p9_tobytes_small.o"
    ).strip().splitlines()
    small_hashes = [line.split()[0] for line in hashes]
    if len(set(small_hashes)) != 1:
        raise RuntimeError(f"small object changed: {hashes}")
    result["small_object_sha256"] = small_hashes[0]
    return result


def parse_kem(paths: list[Path]) -> dict[str, object]:
    values: dict[tuple[str, str], list[list[float]]] = {}
    deltas: dict[str, list[list[float]]] = {}
    for path in paths:
        rows = [row for row in csv.reader(path.read_text().splitlines())
                if row and row[0] == "clean"]
        by_operation: dict[str, list[list[str]]] = {}
        for row in rows:
            by_operation.setdefault(row[1], []).append(row)
            values.setdefault((row[1], row[2]), []).append([float(x) for x in row[3:6]])
        for operation, operation_rows in by_operation.items():
            if len(operation_rows) % 2:
                raise RuntimeError(f"unpaired samples in {path}: {operation}")
            for index in range(0, len(operation_rows), 2):
                pair = {row[2]: [float(x) for x in row[3:6]]
                        for row in operation_rows[index:index + 2]}
                if set(pair) != {"baseline", "candidate"}:
                    raise RuntimeError(f"bad pair in {path}: {pair}")
                deltas.setdefault(operation, []).append(
                    [pair["candidate"][i] - pair["baseline"][i] for i in range(3)]
                )
    metrics = ("cycles", "instructions", "branches")
    result: dict[str, object] = {}
    for operation in ("keygen", "encaps", "decaps"):
        result[operation] = {
            variant: {metric: statistics.median(sample[i] for sample in values[(operation, variant)])
                      for i, metric in enumerate(metrics)}
            for variant in ("baseline", "candidate")
        }
        result[operation]["paired_delta"] = {
            metric: statistics.median(sample[i] for sample in deltas[operation])
            for i, metric in enumerate(metrics)
        }
        result[operation]["observations"] = len(deltas[operation])
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
    commands.append("gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE -rdynamic kem.c -ldl -o kem")
    build = ssh(f"cd {REMOTE} && " + " && ".join(commands))
    if build.count("PASS: 64 KEM") != 2:
        raise RuntimeError("production KEM tests failed")
    (RAW / "build.log").write_text(build)
    audit = object_audit()
    kat_lines = ssh(
        f"cd {REMOTE} && sha256sum packages/baseline/PQCkemKAT_2624.rsp "
        "packages/candidate/PQCkemKAT_2624.rsp"
    ).strip().splitlines()
    kat_hashes = [line.split()[0] for line in kat_lines]
    if kat_hashes != [EXPECTED_KAT, EXPECTED_KAT]:
        raise RuntimeError(f"KAT mismatch: {kat_lines}")
    malformed_hashes = []
    for variant in ("baseline", "candidate"):
        command = (
            f"cd {REMOTE} && gcc -O3 -std=c11 -march=armv8-a+simd -D_DEFAULT_SOURCE "
            f"-Ipackages/{variant} malformed.c -Lpackages/{variant} -lgt864 "
            f"-Wl,-rpath,{REMOTE}/packages/{variant} -o malformed-{variant} && "
            f"./malformed-{variant} | sha256sum"
        )
        malformed_hashes.append(ssh(command).split()[0])
    if malformed_hashes != [EXPECTED_MALFORMED, EXPECTED_MALFORMED]:
        raise RuntimeError(f"malformed transcript mismatch: {malformed_hashes}")
    paths = []
    for process in range(6):
        path = RAW / f"kem-{process}.csv"
        measured = ssh(
            f"cd {REMOTE} && taskset -c 3 ./kem packages/baseline/libgt864.so "
            f"packages/candidate/libgt864.so {process % 2}"
        )
        path.write_text(measured)
        if "correctness=pass exact=100 tampered=100" not in measured:
            raise RuntimeError(f"full KEM compatibility failed in process {process}")
        paths.append(path)
    kem = parse_kem(paths)
    promotion = all(kem[op]["paired_delta"]["cycles"] < 0
                    for op in ("keygen", "encaps", "decaps"))
    after = ssh("vcgencmd measure_temp; vcgencmd get_throttled")
    if "throttled=0x0" not in after:
        raise RuntimeError(after)
    result = {
        "experiment": "P16",
        "baseline_revision": output(["git", "rev-parse", "HEAD"], ROOT).strip(),
        "candidate_p15_full_sha256": P15_FULL_SHA256,
        "host": HOST,
        "remote": REMOTE,
        "target_audit": audit,
        "kat_sha256": kat_hashes[0],
        "malformed_transcript_sha256": malformed_hashes[0],
        "kem": kem,
        "promotion_gate_passed": promotion,
        "environment_before": environment.strip().splitlines(),
        "environment_after": after.strip().splitlines(),
        "source_manifest_sha256": sha256(BUILD / "source-manifest.json"),
    }
    (HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
