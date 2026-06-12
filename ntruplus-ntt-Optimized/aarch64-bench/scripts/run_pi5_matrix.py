#!/usr/bin/env python3
"""Run the Raspberry Pi 5 stock/GT/Slothy benchmark matrix.

The script is intentionally a thin orchestrator around the local Makefile.  It
does not change benchmark code or inputs; it only makes the case matrix
repeatable and writes logs plus CSV summaries.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import re
import shlex
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


DEFAULT_VARIANTS = ["stock", "stock_opt", "gt", "gt_opt"]
DEFAULT_MODES = [
    "ntt",
    "invntt",
    "basemul",
    "basemul_add",
    "ntt_mul_pipeline",
    "ntt_basemul_add_pipeline",
    "kem_dec",
]
INVNTT_STAGE_MODES = [
    "invntt_rows",
    "invntt_row0",
    "invntt_row1",
    "invntt_row2",
    "invntt_post",
    "invntt_post_dft3_raw",
    "invntt_post_dft3_reduce",
    "invntt_post_untwist",
    "invntt_post_finalmerge",
]
GT_ONLY_MODES = set(INVNTT_STAGE_MODES)
PERCENTILES = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99]


BENCH_NAME_RE = re.compile(r"^\s*bench_name\s*=\s*(\S+)\s*$", re.MULTILINE)
BENCH_MODE_RE = re.compile(r"^\s*bench_mode\s*=\s*(\S+)\s*$", re.MULTILINE)
CYCLES_RE = re.compile(r"^\s*(\S+)\s+cycles\s+=\s+(\d+)\s*$", re.MULTILINE)
PERCENTILES_RE = re.compile(r"^\s*(\S+)\s+percentiles:\s+(.+?)\s*$", re.MULTILINE)
SINK_RE = re.compile(r"^\s*sink\s+=\s*(\d+)\s*$", re.MULTILINE)


def parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def command_text(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


def run_command(
    cmd: list[str],
    *,
    cwd: Path,
    log,
    echo: bool,
    dry_run: bool,
) -> tuple[int, str, float]:
    rendered = command_text(cmd)
    print(f"$ {rendered}")
    log.write(f"$ {rendered}\n")
    log.flush()

    if dry_run:
        log.write("[dry-run]\n\n")
        return 0, "", 0.0

    started = time.monotonic()
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line)
        log.write(line)
        if echo:
            print(line, end="")
    rc = proc.wait()
    elapsed = time.monotonic() - started
    log.write(f"[exit={rc} elapsed={elapsed:.3f}s]\n\n")
    log.flush()
    return rc, "".join(lines), elapsed


def command_output(cmd: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return f"{command_text(cmd)}: not found\n"
    return proc.stdout


def validate_make_vars(values: list[str]) -> None:
    for value in values:
        if "=" not in value or value.startswith("="):
            raise SystemExit(f"--make-var expects KEY=VALUE, got {value!r}")


def write_environment(
    log_dir: Path,
    cwd: Path,
    *,
    dry_run: bool,
    make_vars: list[str],
) -> None:
    env_path = log_dir / "environment.txt"
    with env_path.open("w", encoding="utf-8") as out:
        timestamp = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        out.write(f"timestamp_utc={timestamp}\n")
        out.write(f"bench_dir={cwd}\n\n")
        if make_vars:
            out.write("## make_vars\n")
            for item in make_vars:
                out.write(f"{item}\n")
            out.write("\n")
        if dry_run:
            out.write("[dry-run: host commands not executed]\n")
            return
        for title, cmd in [
            ("uname", ["uname", "-a"]),
            ("lscpu", ["lscpu"]),
            ("cpufreq-info", ["cpufreq-info"]),
            ("vcgencmd_get_throttled", ["vcgencmd", "get_throttled"]),
            ("git_head", ["git", "rev-parse", "HEAD"]),
            ("git_status", ["git", "status", "--short"]),
        ]:
            out.write(f"## {title}\n")
            out.write(command_output(cmd, cwd))
            out.write("\n")


def parse_bench_output(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    match = BENCH_NAME_RE.search(output)
    if match:
        parsed["bench_name"] = match.group(1)
    match = BENCH_MODE_RE.search(output)
    if match:
        parsed["bench_mode"] = match.group(1)
    match = CYCLES_RE.search(output)
    if match:
        parsed["cycles_name"] = match.group(1)
        parsed["cycles"] = match.group(2)
    match = SINK_RE.search(output)
    if match:
        parsed["sink"] = match.group(1)
    match = PERCENTILES_RE.search(output)
    if match:
        values = match.group(2).split()
        for percentile, value in zip(PERCENTILES, values):
            parsed[f"p{percentile:02d}"] = value
    return parsed


def summarize_failure_output(output: str, *, max_chars: int = 500) -> str:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return " | ".join(lines[-5:])[-max_chars:]


def build_cmd(args: argparse.Namespace, variant: str, mode: str) -> list[str]:
    cmd = [
        "make",
        f"CYCLES={args.cycles}",
        f"VARIANT={variant}",
        f"BENCH_MODE={mode}",
        f"USE_SHAKE_ASM={args.use_shake_asm}",
        f"NTESTS={args.n_tests}",
        f"NITERATIONS={args.n_iterations}",
        f"NWARMUP={args.n_warmup}",
    ]
    cmd.extend(args.make_var)
    return cmd


def bench_cmd(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = []
    if args.sudo:
        cmd.append("sudo")
    if args.taskset:
        cmd.extend(["taskset", "-c", str(args.core)])
    cmd.append("./bench")
    return cmd


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def rows_csv_text(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return out.getvalue().rstrip("\n")


def print_summary_rows(
    title: str,
    rows: list[dict[str, str]],
    fieldnames: list[str],
) -> None:
    print()
    print(f"== {title} ==")
    print(rows_csv_text(rows, fieldnames))


def aggregate(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["variant"], row["mode"])].append(row)

    out_rows: list[dict[str, str]] = []
    for (variant, mode), group in sorted(grouped.items()):
        status_counts: dict[str, int] = defaultdict(int)
        for item in group:
            status_counts[item.get("status", "unknown")] += 1
        ok_cycles = sorted(
            int(row["cycles"])
            for row in group
            if row.get("status") == "ok" and row.get("cycles")
        )
        row: dict[str, str] = {
            "variant": variant,
            "mode": mode,
            "runs": str(len(group)),
            "ok_runs": str(len(ok_cycles)),
            "failed_runs": str(len(group) - len(ok_cycles)),
            "statuses": ";".join(
                f"{status}:{count}" for status, count in sorted(status_counts.items())
            ),
        }
        if ok_cycles:
            row["median_cycles"] = str(ok_cycles[len(ok_cycles) // 2])
            row["min_cycles"] = str(ok_cycles[0])
            row["max_cycles"] = str(ok_cycles[-1])
            row["mean_cycles"] = f"{sum(ok_cycles) / len(ok_cycles):.2f}"
        out_rows.append(row)
    return out_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--variants", default=",".join(DEFAULT_VARIANTS))
    parser.add_argument("--modes", default=",".join(DEFAULT_MODES))
    parser.add_argument("--include-invntt-stages", action="store_true")
    parser.add_argument("--cycles", default="PERF", choices=["PERF", "PMU", "MAC"])
    parser.add_argument("--use-shake-asm", type=int, choices=[0, 1], default=0)
    parser.add_argument("--n-tests", type=int, default=500)
    parser.add_argument("--n-iterations", type=int, default=300)
    parser.add_argument("--n-warmup", type=int, default=50)
    parser.add_argument("--core", type=int, default=3)
    parser.add_argument("--no-sudo", dest="sudo", action="store_false")
    parser.set_defaults(sudo=True)
    parser.add_argument("--no-taskset", dest="taskset", action="store_false")
    parser.set_defaults(taskset=True)
    parser.add_argument("--log-dir")
    parser.add_argument(
        "--make-var",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Extra Make variable to append to every build. May be repeated.",
    )
    parser.add_argument("--echo-build", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--no-print-summary",
        dest="print_summary",
        action="store_false",
        help="Do not print summary_runs.csv and summary_cases.csv contents to stdout.",
    )
    parser.set_defaults(print_summary=True)
    args = parser.parse_args()
    validate_make_vars(args.make_var)

    cwd = Path(__file__).resolve().parents[1]
    variants = parse_list(args.variants)
    modes = parse_list(args.modes)
    if args.include_invntt_stages:
        modes.extend(mode for mode in INVNTT_STAGE_MODES if mode not in modes)

    if args.log_dir:
        log_dir = Path(args.log_dir)
    else:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        log_dir = cwd / "logs" / f"pi5-matrix-{stamp}"
    log_dir.mkdir(parents=True, exist_ok=True)
    write_environment(log_dir, cwd, dry_run=args.dry_run, make_vars=args.make_var)

    rows: list[dict[str, str]] = []
    for variant in variants:
        for mode in modes:
            if mode in GT_ONLY_MODES and variant not in {"gt", "gt_opt"}:
                print(f"skip {variant}/{mode}: stage modes require gt or gt_opt")
                continue
            for run_idx in range(1, args.runs + 1):
                case_name = f"{variant}_{mode}_run{run_idx}"
                log_path = log_dir / f"{case_name}.log"
                row: dict[str, str] = {
                    "variant": variant,
                    "mode": mode,
                    "run": str(run_idx),
                    "make_vars": " ".join(args.make_var),
                    "log": str(log_path),
                }
                with log_path.open("w", encoding="utf-8") as log:
                    run_command(
                        ["make", "clean"],
                        cwd=cwd,
                        log=log,
                        echo=args.echo_build,
                        dry_run=args.dry_run,
                    )
                    rc, build_output, build_seconds = run_command(
                        build_cmd(args, variant, mode),
                        cwd=cwd,
                        log=log,
                        echo=args.echo_build,
                        dry_run=args.dry_run,
                    )
                    row["build_seconds"] = f"{build_seconds:.3f}"
                    if rc != 0:
                        row["status"] = "build_failed"
                        row["failure_output"] = summarize_failure_output(build_output)
                        rows.append(row)
                        if args.fail_fast:
                            raise SystemExit(1)
                        continue

                    rc, output, bench_seconds = run_command(
                        bench_cmd(args),
                        cwd=cwd,
                        log=log,
                        echo=True,
                        dry_run=args.dry_run,
                    )
                    row["bench_seconds"] = f"{bench_seconds:.3f}"
                    row.update(parse_bench_output(output))
                    row["status"] = "dry_run" if args.dry_run else ("ok" if rc == 0 else "bench_failed")
                    if rc != 0:
                        row["failure_output"] = summarize_failure_output(output)
                    rows.append(row)
                    if rc != 0 and args.fail_fast:
                        raise SystemExit(1)

    per_run_fields = [
        "variant",
        "mode",
        "run",
        "status",
        "failure_output",
        "bench_name",
        "bench_mode",
        "cycles",
        "p01",
        "p10",
        "p20",
        "p30",
        "p40",
        "p50",
        "p60",
        "p70",
        "p80",
        "p90",
        "p99",
        "sink",
        "make_vars",
        "build_seconds",
        "bench_seconds",
        "log",
    ]
    per_case_fields = [
        "variant",
        "mode",
        "runs",
        "ok_runs",
        "failed_runs",
        "statuses",
        "median_cycles",
        "min_cycles",
        "max_cycles",
        "mean_cycles",
    ]
    case_rows = aggregate(rows)
    summary_runs_path = log_dir / "summary_runs.csv"
    summary_cases_path = log_dir / "summary_cases.csv"
    write_rows(summary_runs_path, rows, per_run_fields)
    write_rows(summary_cases_path, case_rows, per_case_fields)
    print(f"wrote {summary_runs_path}")
    print(f"wrote {summary_cases_path}")
    if args.print_summary:
        print_summary_rows("summary_runs.csv", rows, per_run_fields)
        print_summary_rows("summary_cases.csv", case_rows, per_case_fields)
    return 0


if __name__ == "__main__":
    sys.exit(main())
