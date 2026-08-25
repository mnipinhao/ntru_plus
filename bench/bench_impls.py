#!/usr/bin/env python3

from __future__ import annotations

import argparse
import difflib
import json
import platform
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ROOT_DIR.parent
BUILD_DIR = ROOT_DIR / "build"
RESULTS_DIR = ROOT_DIR / "results"
KAT_RESULTS_DIR = RESULTS_DIR / "kat"
CYCLES_RESULTS_DIR = RESULTS_DIR / "cycles"
CYCLE_HARNESS = ROOT_DIR / "cycles" / "ntruplus_cycle_bench.c"
CYCLE_COMPARATOR = ROOT_DIR / "cycles" / "compare_cycles.py"


class BenchError(RuntimeError):
    pass


@dataclass
class ImplSpec:
    label: str
    safe_label: str
    path: Path
    algname: str
    host_hint: str
    kat_compile: list[str]
    test_compile: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare arbitrary NTRU+ implementation directories with KAT and cycle benchmarks."
    )
    parser.add_argument("mode", choices=["kat", "compare"], help="Run correctness only or correctness + cycles")
    parser.add_argument("--impl-a", required=True, help="First implementation directory")
    parser.add_argument("--impl-b", required=True, help="Second implementation directory")
    parser.add_argument("--label-a", help="Friendly label for implementation A")
    parser.add_argument("--label-b", help="Friendly label for implementation B")
    parser.add_argument("--run-tag", default=timestamp_tag(), help="Result directory tag")
    parser.add_argument("--iterations", type=int, default=1000, help="Cycle benchmark iterations")
    parser.add_argument("--warmup", type=int, default=100, help="Cycle benchmark warmup iterations")
    return parser.parse_args()


def timestamp_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sanitize_label(label: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", label).strip("._-")
    if not safe:
        raise BenchError(f"Label {label!r} collapses to an empty filename-safe string")
    return safe


def default_label(path: Path) -> str:
    relative = repo_relative(path)
    return relative.replace("/", "__")


def host_machine() -> str:
    machine = platform.machine().lower()
    if machine == "arm64":
        return "aarch64"
    if machine == "amd64":
        return "x86_64"
    return machine


def read_algname(impl_dir: Path) -> str:
    params_path = impl_dir / "params.h"
    if not params_path.exists():
        raise BenchError(f"Missing params.h in {impl_dir}")

    match = re.search(r'#define\s+NTRUPLUS_ALGNAME\s+"([^"]+)"', params_path.read_text())
    if not match:
        raise BenchError(f"Unable to read NTRUPLUS_ALGNAME from {params_path}")
    return match.group(1)


def make_dry_run_compile(impl_dir: Path, target: str) -> list[str]:
    command = ["make", "-n", target]
    result = subprocess.run(command, cwd=impl_dir, text=True, capture_output=True)
    if result.returncode != 0:
        raise BenchError(
            f"make -n {target} failed in {impl_dir}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    dry_run = result.stdout + "\n" + result.stderr
    dry_run = re.sub(r"\\\s*\n\s*", " ", dry_run)
    lines = [line.strip() for line in dry_run.splitlines() if line.strip()]
    for line in reversed(lines):
        try:
            tokens = shlex.split(line)
        except ValueError:
            continue
        if is_compile_command(tokens):
            return tokens

    raise BenchError(f"Unable to extract a compile command for target {target} in {impl_dir}")


def is_compile_command(tokens: list[str]) -> bool:
    if not tokens:
        return False
    compiler = Path(tokens[0]).name
    return compiler in {"cc", "gcc", "clang"} and "-o" in tokens


def infer_host_hint(impl_dir: Path, compile_tokens: list[str]) -> str:
    normalized_parts = {part.lower() for part in impl_dir.parts}
    if "-mavx2" in compile_tokens or "avx2" in normalized_parts:
        return "x86_64"
    if "aarch64" in normalized_parts:
        return "aarch64"
    return "portable"


def validate_host_support(spec: ImplSpec) -> None:
    machine = host_machine()
    if spec.host_hint == "portable":
        return
    if spec.host_hint == "aarch64" and machine != "aarch64":
        raise BenchError(
            f"{spec.label} points to an aarch64-only implementation, but the host is {machine}"
        )
    if spec.host_hint == "x86_64" and machine != "x86_64":
        raise BenchError(
            f"{spec.label} needs an x86_64/AVX2-capable host, but the host is {machine}"
        )


def prepare_impl(path_str: str, explicit_label: str | None) -> ImplSpec:
    impl_dir = Path(path_str).expanduser()
    if not impl_dir.is_absolute():
        impl_dir = (ROOT_DIR / impl_dir).resolve()
    else:
        impl_dir = impl_dir.resolve()

    if not impl_dir.is_dir():
        raise BenchError(f"Implementation path is not a directory: {impl_dir}")
    if not (impl_dir / "Makefile").exists():
        raise BenchError(f"Missing Makefile in implementation directory: {impl_dir}")

    label = explicit_label or default_label(impl_dir)
    safe_label = sanitize_label(label)
    algname = read_algname(impl_dir)
    kat_compile = make_dry_run_compile(impl_dir, "PQCgenKAT_kem")
    test_compile = make_dry_run_compile(impl_dir, "test")
    host_hint = infer_host_hint(impl_dir, test_compile)

    spec = ImplSpec(
        label=label,
        safe_label=safe_label,
        path=impl_dir,
        algname=algname,
        host_hint=host_hint,
        kat_compile=kat_compile,
        test_compile=test_compile,
    )
    validate_host_support(spec)
    return spec


def replace_output_path(tokens: list[str], output_path: Path) -> list[str]:
    command = list(tokens)
    try:
        index = command.index("-o")
    except ValueError as exc:
        raise BenchError(f"Compile command is missing -o: {tokens}") from exc
    if index + 1 >= len(command):
        raise BenchError(f"Compile command ended immediately after -o: {tokens}")
    command[index + 1] = str(output_path)
    return command


def swap_source_token(tokens: list[str], old_suffix: str, new_token: str) -> list[str]:
    command = list(tokens)
    for index, token in enumerate(command):
        if token.replace("\\", "/").endswith(old_suffix):
            command[index] = new_token
            return command
    raise BenchError(f"Unable to find source token ending with {old_suffix!r} in {tokens}")


def build_kat_command(spec: ImplSpec, output_path: Path) -> list[str]:
    return replace_output_path(spec.kat_compile, output_path)


def build_cycle_command(spec: ImplSpec, output_path: Path) -> list[str]:
    command = replace_output_path(spec.test_compile, output_path)
    command = swap_source_token(command, "test/test.c", str(CYCLE_HARNESS))
    command.insert(1, f'-DBENCH_LABEL="{spec.label}"')
    return command


def run_command(command: list[str], cwd: Path, description: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise BenchError(
            f"{description} failed\n"
            f"cwd: {cwd}\n"
            f"command: {' '.join(shlex.quote(part) for part in command)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def ensure_dirs(run_tag: str) -> tuple[Path, Path, Path]:
    build_run_dir = BUILD_DIR / run_tag
    kat_run_dir = KAT_RESULTS_DIR / run_tag
    cycles_run_dir = CYCLES_RESULTS_DIR / run_tag
    build_run_dir.mkdir(parents=True, exist_ok=True)
    kat_run_dir.mkdir(parents=True, exist_ok=True)
    cycles_run_dir.mkdir(parents=True, exist_ok=True)
    return build_run_dir, kat_run_dir, cycles_run_dir


def locate_single_artifact(run_dir: Path, pattern: str) -> Path:
    matches = sorted(run_dir.glob(pattern))
    if len(matches) != 1:
        raise BenchError(f"Expected exactly one {pattern} in {run_dir}, found {len(matches)}")
    return matches[0]


def write_metadata(path: Path, impl_a: ImplSpec, impl_b: ImplSpec, run_tag: str, iterations: int, warmup: int) -> None:
    data = {
        "run_tag": run_tag,
        "host_machine": host_machine(),
        "impl_a": {
            "label": impl_a.label,
            "path": impl_a.path.as_posix(),
            "algname": impl_a.algname,
            "host_hint": impl_a.host_hint,
        },
        "impl_b": {
            "label": impl_b.label,
            "path": impl_b.path.as_posix(),
            "algname": impl_b.algname,
            "host_hint": impl_b.host_hint,
        },
        "iterations": iterations,
        "warmup": warmup,
    }
    path.write_text(json.dumps(data, indent=2) + "\n")


def run_kat(spec: ImplSpec, build_run_dir: Path, kat_run_dir: Path) -> tuple[Path, Path]:
    kat_binary = build_run_dir / f"kat_{spec.safe_label}"
    kat_work_dir = build_run_dir / f"kat_work_{spec.safe_label}"
    kat_work_dir.mkdir(parents=True, exist_ok=True)

    run_command(
        build_kat_command(spec, kat_binary),
        cwd=spec.path,
        description=f"building KAT generator for {spec.label}",
    )
    run_command(
        [str(kat_binary)],
        cwd=kat_work_dir,
        description=f"running KAT generator for {spec.label}",
    )

    rsp_path = locate_single_artifact(kat_work_dir, "PQCkemKAT_*.rsp")
    req_path = locate_single_artifact(kat_work_dir, "PQCkemKAT_*.req")
    final_rsp = kat_run_dir / f"{spec.safe_label}.rsp"
    final_req = kat_run_dir / f"{spec.safe_label}.req"
    final_rsp.write_bytes(rsp_path.read_bytes())
    final_req.write_bytes(req_path.read_bytes())
    return final_req, final_rsp


def compare_kat_outputs(rsp_a: Path, rsp_b: Path, diff_path: Path) -> bool:
    text_a = rsp_a.read_text().splitlines(keepends=True)
    text_b = rsp_b.read_text().splitlines(keepends=True)
    if text_a == text_b:
        return True

    diff = difflib.unified_diff(
        text_a,
        text_b,
        fromfile=rsp_a.name,
        tofile=rsp_b.name,
    )
    diff_path.write_text("".join(diff))
    return False


def run_cycles(spec: ImplSpec, build_run_dir: Path, cycles_run_dir: Path, iterations: int, warmup: int) -> Path:
    cycle_binary = build_run_dir / f"cycle_{spec.safe_label}"
    output_json = cycles_run_dir / f"raw_{spec.safe_label}.json"

    run_command(
        build_cycle_command(spec, cycle_binary),
        cwd=spec.path,
        description=f"building cycle benchmark for {spec.label}",
    )
    run_command(
        [str(cycle_binary), str(output_json), str(iterations), str(warmup)],
        cwd=spec.path,
        description=f"running cycle benchmark for {spec.label}",
    )
    return output_json


def compare_cycles(cycles_run_dir: Path, run_tag: str, json_a: Path, json_b: Path) -> None:
    run_command(
        [
            sys.executable,
            str(CYCLE_COMPARATOR),
            "--baseline",
            str(json_a),
            "--optimized",
            str(json_b),
            "--output-json",
            str(cycles_run_dir / "comparison.json"),
            "--output-md",
            str(cycles_run_dir / "summary.md"),
            "--tag",
            run_tag,
        ],
        cwd=ROOT_DIR,
        description="generating cycle comparison report",
    )


def main() -> int:
    args = parse_args()
    if args.iterations <= 0:
        raise BenchError("--iterations must be > 0")
    if args.warmup < 0:
        raise BenchError("--warmup must be >= 0")

    impl_a = prepare_impl(args.impl_a, args.label_a)
    impl_b = prepare_impl(args.impl_b, args.label_b)
    if impl_a.algname != impl_b.algname:
        raise BenchError(
            f"Algorithm mismatch: {impl_a.label} is {impl_a.algname}, "
            f"but {impl_b.label} is {impl_b.algname}"
        )
    if impl_a.safe_label == impl_b.safe_label:
        raise BenchError(
            f"Labels collide after sanitizing: {impl_a.safe_label}. "
            "Pass --label-a/--label-b to disambiguate the outputs."
        )

    build_run_dir, kat_run_dir, cycles_run_dir = ensure_dirs(args.run_tag)
    write_metadata(kat_run_dir / "metadata.json", impl_a, impl_b, args.run_tag, args.iterations, args.warmup)
    write_metadata(cycles_run_dir / "metadata.json", impl_a, impl_b, args.run_tag, args.iterations, args.warmup)

    print(f"[INFO] run tag: {args.run_tag}")
    print(f"[INFO] impl A: {impl_a.label} -> {repo_relative(impl_a.path)}")
    print(f"[INFO] impl B: {impl_b.label} -> {repo_relative(impl_b.path)}")

    _, rsp_a = run_kat(impl_a, build_run_dir, kat_run_dir)
    _, rsp_b = run_kat(impl_b, build_run_dir, kat_run_dir)

    diff_path = kat_run_dir / "diff.txt"
    if compare_kat_outputs(rsp_a, rsp_b, diff_path):
        (kat_run_dir / "status.txt").write_text("PASS\n")
        print(f"[KAT] PASS: {rsp_a.name} matches {rsp_b.name}")
    else:
        (kat_run_dir / "status.txt").write_text("FAIL\n")
        raise BenchError(f"KAT mismatch. See {diff_path}")

    if args.mode == "kat":
        print(f"[DONE] KAT artifacts: {kat_run_dir}")
        return 0

    json_a = run_cycles(impl_a, build_run_dir, cycles_run_dir, args.iterations, args.warmup)
    json_b = run_cycles(impl_b, build_run_dir, cycles_run_dir, args.iterations, args.warmup)
    compare_cycles(cycles_run_dir, args.run_tag, json_a, json_b)

    print(f"[DONE] KAT artifacts: {kat_run_dir}")
    print(f"[DONE] Cycle artifacts: {cycles_run_dir}")
    print(f"[DONE] Summary: {cycles_run_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BenchError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
