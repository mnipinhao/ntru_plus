#!/usr/bin/env python3
"""Run native-KEM or SUPERCOP-derived primitive measurement in a campaign."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import stat
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from supercop_workflow import LOCK_PATH, REPO_ROOT, read_lock, sha256_file


def read_text(path: Path) -> str | None:
    return path.read_text(encoding="utf-8").strip() if path.is_file() else None


def frequency_state(cpu: int, cpu_model: str) -> dict[str, object]:
    cpufreq = Path(f"/sys/devices/system/cpu/cpu{cpu}/cpufreq")
    topology = Path(f"/sys/devices/system/cpu/cpu{cpu}/topology")
    state: dict[str, object] = {
        "scaling_governor": read_text(cpufreq / "scaling_governor"),
        "scaling_min_freq": read_text(cpufreq / "scaling_min_freq"),
        "scaling_max_freq": read_text(cpufreq / "scaling_max_freq"),
        "base_frequency": read_text(cpufreq / "base_frequency"),
        "cpuinfo_max_freq": read_text(cpufreq / "cpuinfo_max_freq"),
        "thread_siblings_list": read_text(topology / "thread_siblings_list"),
        "core_type": read_text(topology / "core_type"),
        "intel_no_turbo": read_text(Path("/sys/devices/system/cpu/intel_pstate/no_turbo")),
        "amd_boost": read_text(cpufreq / "boost") or
                     read_text(Path("/sys/devices/system/cpu/cpufreq/boost")),
    }
    available_maxima = []
    for candidate in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/cpuinfo_max_freq"):
        value = read_text(candidate)
        if value and value.isdigit():
            available_maxima.append(int(value))
    selected_max = state["cpuinfo_max_freq"]
    if selected_max and str(selected_max).isdigit() and available_maxima:
        state["inferred_core_class"] = (
            "performance" if int(str(selected_max)) == max(available_maxima) else "efficiency")
        state["system_max_cpuinfo_freq"] = str(max(available_maxima))
    else:
        state["inferred_core_class"] = "unknown"
        state["system_max_cpuinfo_freq"] = None

    failures = []
    if state["scaling_governor"] != "performance":
        failures.append("scaling governor is not performance")
    if "Intel" in cpu_model and state["intel_no_turbo"] != "1":
        failures.append("Intel turbo is not disabled")
    if "AMD" in cpu_model and state["amd_boost"] != "0":
        failures.append("AMD boost is not disabled")
    if state["inferred_core_class"] != "performance":
        failures.append("selected CPU is not identified as a physical P-core")
    state["formal_policy_passed"] = not failures
    state["formal_policy_failures"] = failures
    return state


def decode_observations(text: str, operation: str) -> list[int]:
    values: list[int] = []
    for line in text.splitlines():
        words = line.split()
        if not words or words[0] != operation or len(words) < 3:
            continue
        center = int(words[2] if words[1] == "-" else words[1])
        encoded = "".join(words[3:] if words[1] == "-" else words[2:])
        # printentry emits the StQ2 center as a separate word followed by one
        # concatenated +/- delta word. With mbytes=-1, words are op, '-', center,
        # deltas; tolerate the no-placeholder shape for replay portability.
        for match in re.finditer(r"([+-])(\d+)", encoded):
            delta = int(match.group(2))
            values.append(center + delta if match.group(1) == "+" else center - delta)
    return values


def stabilized_quartiles(values: list[int]) -> list[float]:
    if not values:
        raise ValueError("cannot compute stabilized quartiles of no observations")
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return [sum(expanded[(1 + 2 * index) * count:(3 + 2 * index) * count]) /
            (2 * count) for index in range(3)]


def measure_identity(text: str) -> dict[str, str]:
    identity = {}
    for line in text.splitlines():
        words = line.split()
        if words and words[0] in ("implementation", "cpuid", "cpucycles_persecond",
                                  "cpucycles_implementation", "compiler"):
            identity[words[0]] = " ".join(words[1:])
    return identity


def elf_layout(path: Path, symbols: tuple[str, ...]) -> dict[str, object]:
    """Record placement and sizes from the exact replay ELF."""
    nm = subprocess.run(["nm", "-n", "-S", "--defined-only", str(path)], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    wanted = set(symbols)
    entries = []
    for line in nm.stdout.splitlines():
        words = line.split()
        if len(words) == 4:
            entries.append((int(words[0], 16), int(words[1], 16), words[2], words[3]))
        elif len(words) == 3:
            entries.append((int(words[0], 16), None, words[1], words[2]))
    symbol_layout = {}
    for index, (address, size_value, symbol_type, name) in enumerate(entries):
        if name not in wanted:
            continue
        size_source = "elf-symbol-size"
        if size_value is None:
            next_global = next((other_address for other_address, _, other_type, _
                                in entries[index + 1:]
                                if other_address > address and other_type.isupper()), None)
            size_value = next_global - address if next_global is not None else None
            size_source = "inferred-to-next-global-symbol"
        symbol_layout[name] = {
            "address": address, "address_mod32": address % 32,
            "address_mod64": address % 64, "size": size_value,
            "size_source": size_source,
        }
    size = subprocess.run(["size", "-A", str(path)], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    sections = {}
    for line in size.stdout.splitlines():
        words = line.split()
        if len(words) >= 2 and words[0] in (".text", ".rodata") and words[1].isdigit():
            sections[words[0]] = int(words[1])
    return {"symbols": symbol_layout, "sections": sections}


def direct_transfer_targets(path: Path, symbol_name: str) -> list[str]:
    """Return direct call/tail-jump targets in one linked ELF symbol."""
    record = elf_layout(path, (symbol_name,))["symbols"][symbol_name]
    begin = int(record["address"])
    end = begin + int(record["size"])
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(path)], text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
    targets = []
    for line in disassembly.splitlines():
        match = re.match(
            r"\s*([0-9a-f]+):.*\b(?:call|jmp)\s+[^<]*<([^>]+)>", line)
        if match and begin <= int(match.group(1), 16) < end:
            target = match.group(2).split("@", 1)[0]
            if not target.startswith(symbol_name + "+"):
                targets.append(target)
    return targets


def perf_diagnostics(path: Path, cpu: int, result_dir: Path) -> dict[str, object]:
    """Collect non-headline retired-op attribution with reset-only subtraction."""
    modes = ("baseline1x", "legacy1x", "p1h1x",
             "baseline2x", "legacy2x", "p1h2x")
    events = ("instructions:u", "mem_inst_retired.all_loads:u",
              "mem_inst_retired.all_stores:u")
    repetitions = 3
    raw_dir = result_dir / "perf-diagnostics"
    raw_dir.mkdir()
    totals: dict[str, dict[str, list[int]]] = {
        mode: {event: [] for event in events} for mode in modes}
    for mode in modes:
        for run_number in range(1, repetitions + 1):
            environment = os.environ.copy()
            environment["NTRUPLUS_F0_PROD1_PERF"] = mode
            command = ["taskset", "-c", str(cpu), "perf", "stat", "-x", ";",
                       "-e", ",".join(events), str(path.resolve())]
            completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, env=environment, check=False)
            stem = raw_dir / f"{mode}-run-{run_number:02d}"
            stem.with_suffix(".out").write_text(completed.stdout, encoding="utf-8")
            stem.with_suffix(".err").write_text(completed.stderr, encoding="utf-8")
            if completed.returncode:
                raise SystemExit(f"perf diagnostic {mode} run {run_number} failed")
            found = {}
            for line in completed.stderr.splitlines():
                fields = line.split(";")
                if len(fields) < 3:
                    continue
                reported_event = fields[2].strip()
                event = next((candidate for candidate in events
                              if candidate.split(":", 1)[0] in reported_event), None)
                if event and fields[0].strip().isdigit():
                    # Hybrid Intel PMUs emit an uncounted cpu_atom row and a
                    # counted cpu_core row for the same requested event.
                    found[event] = found.get(event, 0) + int(fields[0].strip())
            missing = [event for event in events if event not in found]
            if missing:
                raise SystemExit(f"perf diagnostic lacks {', '.join(missing)}; see {stem}.err")
            for event, value in found.items():
                totals[mode][event].append(value)
    medians = {
        mode: {event: statistics.median(values) for event, values in by_event.items()}
        for mode, by_event in totals.items()
    }
    adjusted = {}
    for width in ("1x", "2x"):
        baseline = medians[f"baseline{width}"]
        for variant in ("legacy", "p1h"):
            label = f"{variant}{width}"
            adjusted[label] = {
                event: (medians[label][event] - baseline[event]) / 4096
                for event in events
            }
    return {
        "role": "diagnostic-attribution-not-cycle-headline",
        "fresh_processes_per_mode": repetitions,
        "operations_per_process": 4096,
        "events": list(events),
        "median_raw_process_counts": medians,
        "baseline_adjusted_counts_per_operation": adjusted,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--mode", choices=("native-kem", "derived-poly", "derived-itail",
                                           "derived-itail-d0", "derived-itail-d0-m2",
                                           "derived-f0-ma1", "derived-f0-ma1-ma0",
                                           "derived-f0-ma3", "derived-f0-ma2-chunk",
                                           "derived-f0-ma2", "derived-f0-prod1",
                                           "derived-f0-prod2",
                                           "derived-f0-prod2-consumer",
                                           "derived-gt9x16-prod3-price",
                                           "derived-gt9x16-prod3-consumer",
                                           "derived-gt9x16-prod3-hash-fanout",
                                           "derived-gt9x16-prod3-hash-h1-price",
                                           "derived-gt9x16-prod3-qorder-price",
                                           "derived-gt9x16-prod3-t0-beta-price",
                                           "derived-gt9x16-prod3-encap-attribution-v2",
                                           "derived-gt9x16-prod3-encap-tail-attribution-v1",
                                           "derived-encap-h-ingress-ma2-h3-price"),
                        required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--compiler-wrapper", type=Path,
                        help="force one common SUPERCOP okc recipe (campaign only)")
    parser.add_argument("--fresh-launches", type=int, default=3,
                        help="fresh measure-ELF processes used for pooled StQ1/2/3")
    parser.add_argument("--require-frequency-control", action="store_true",
                        help="require performance governor and disabled turbo/boost")
    args = parser.parse_args()
    if args.mode in ("derived-itail", "derived-itail-d0", "derived-itail-d0-m2",
                     "derived-f0-ma1", "derived-f0-ma1-ma0",
                     "derived-f0-ma3", "derived-f0-ma2-chunk",
                     "derived-f0-ma2", "derived-f0-prod1",
                     "derived-f0-prod2", "derived-f0-prod2-consumer",
                     "derived-gt9x16-prod3-price",
                     "derived-gt9x16-prod3-consumer",
                     "derived-gt9x16-prod3-hash-fanout",
                     "derived-gt9x16-prod3-hash-h1-price",
                     "derived-gt9x16-prod3-qorder-price",
                     "derived-gt9x16-prod3-t0-beta-price",
                     "derived-gt9x16-prod3-encap-attribution-v2",
                     "derived-gt9x16-prod3-encap-tail-attribution-v1",
                     "derived-encap-h-ingress-ma2-h3-price") and args.parameter != "1152":
        raise SystemExit("the selected derived measure is defined only for NTRU+1152")

    root = args.campaign_root.resolve()
    marker = root / ".ntruplus-campaign.json"
    if not marker.is_file():
        raise SystemExit("benchmarking is allowed only in a prepared disposable campaign")
    marker_record = json.loads(marker.read_text(encoding="utf-8"))
    if marker_record.get("kind") != "disposable-supercop-campaign":
        raise SystemExit("campaign marker has the wrong kind")
    pinned = read_lock()
    if marker_record.get("supercop_version") != pinned["version"]:
        raise SystemExit("campaign version does not match bench/supercop.lock")
    if not (root / "do-part").is_file():
        raise SystemExit(f"missing SUPERCOP do-part in {root}")
    primitive = f"ntruplus{args.parameter}"
    primitive_dir = root / "crypto_kem" / primitive
    selected = primitive_dir / args.implementation
    if not selected.is_dir():
        raise SystemExit(f"missing implementation: {selected}")
    if args.result_dir.exists():
        raise SystemExit(f"refusing to overwrite result directory: {args.result_dir}")
    if args.fresh_launches < 1:
        raise SystemExit("--fresh-launches must be positive")

    cpu_model = "unknown"
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lower().startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    frequency = frequency_state(args.cpu, cpu_model)
    if args.require_frequency_control and not frequency["formal_policy_passed"]:
        raise SystemExit("formal SUPERCOP frequency preflight failed: " +
                         "; ".join(frequency["formal_policy_failures"]))
    args.result_dir.mkdir(parents=True)

    implementations = sorted(path for path in primitive_dir.iterdir() if path.is_dir())
    original_modes = {path: stat.S_IMODE(path.stat().st_mode) for path in implementations}
    measure_path = root / "crypto_kem" / "measure.c"
    original_measure = measure_path.read_bytes()
    original_measure_mode = stat.S_IMODE(measure_path.stat().st_mode)
    adapter_backups: dict[Path, bytes | None] = {}
    compiler_backup: tuple[Path, bytes, int] | None = None
    started = time.time()
    try:
        for path in implementations:
            path.chmod(original_modes[path] | stat.S_ISVTX)
        selected.chmod(original_modes[selected] & ~stat.S_ISVTX)
        if args.mode in ("derived-poly", "derived-itail", "derived-itail-d0",
                         "derived-itail-d0-m2", "derived-f0-ma1",
                         "derived-f0-ma1-ma0", "derived-f0-ma3",
                         "derived-f0-ma2-chunk", "derived-f0-ma2",
                         "derived-f0-prod1", "derived-f0-prod2",
                         "derived-f0-prod2-consumer",
                         "derived-gt9x16-prod3-price",
                         "derived-gt9x16-prod3-consumer",
                         "derived-gt9x16-prod3-hash-fanout",
                         "derived-gt9x16-prod3-hash-h1-price",
                         "derived-gt9x16-prod3-qorder-price",
                         "derived-gt9x16-prod3-t0-beta-price",
                         "derived-gt9x16-prod3-encap-attribution-v2",
                         "derived-gt9x16-prod3-encap-tail-attribution-v1",
                         "derived-encap-h-ingress-ma2-h3-price"):
            replacement_name = {
                "derived-poly": "poly_measure.c",
                "derived-itail": "itail_measure.c",
                "derived-itail-d0": "itail_d0_measure.c",
                "derived-itail-d0-m2": "itail_d0_m2_measure.c",
                "derived-f0-ma1": "f0_ma1_measure.c",
                "derived-f0-ma1-ma0": "f0_ma1_ma0_measure.c",
                "derived-f0-ma3": "f0_ma3_measure.c",
                "derived-f0-ma2-chunk": "f0_ma2_chunk_measure.c",
                "derived-f0-ma2": "f0_ma2_measure.c",
                "derived-f0-prod1": "f0_prod1_measure.c",
                "derived-f0-prod2": "f0_prod2_measure.c",
                "derived-f0-prod2-consumer": "f0_prod2_consumer_measure.c",
                "derived-gt9x16-prod3-price": "gt9x16_prod3_aos_price_measure.c",
                "derived-gt9x16-prod3-consumer":
                    "gt9x16_prod3_aos_consumer_measure.c",
                "derived-gt9x16-prod3-hash-fanout":
                    "gt9x16_prod3_hash_fanout_measure.c",
                "derived-gt9x16-prod3-hash-h1-price":
                    "gt9x16_prod3_hash_h1_price_measure.c",
                "derived-gt9x16-prod3-qorder-price":
                    "gt9x16_prod3_qorder_price_measure.c",
                "derived-gt9x16-prod3-t0-beta-price":
                    "gt9x16_prod3_t0_beta_price_measure.c",
                "derived-gt9x16-prod3-encap-attribution-v2":
                    "gt9x16_prod3_encap_attribution_v2_measure.c",
                "derived-gt9x16-prod3-encap-tail-attribution-v1":
                    "gt9x16_prod3_encap_tail_attribution_v1_measure.c",
                "derived-encap-h-ingress-ma2-h3-price":
                    "encap_h_ingress_ma2_h3_price_measure.c",
            }[args.mode]
            replacement = REPO_ROOT / "bench" / "supercop" / replacement_name
            shutil.copyfile(replacement, measure_path)
            if args.mode == "derived-poly":
                for name in ("ntruplus_bench.c", "ntruplus_bench.h"):
                    destination = selected / name
                    adapter_backups[destination] = destination.read_bytes() if destination.exists() else None
                    shutil.copy2(REPO_ROOT / "bench" / "supercop" / name, destination)
        if args.compiler_wrapper:
            wrappers = list((root / "bench").glob("*/bin/okc-amd64"))
            if len(wrappers) != 1:
                raise SystemExit(f"expected one campaign okc-amd64, found {len(wrappers)}")
            wrapper = wrappers[0]
            compiler_backup = (wrapper, wrapper.read_bytes(), stat.S_IMODE(wrapper.stat().st_mode))
            shutil.copy2(args.compiler_wrapper, wrapper)
            wrapper.chmod(wrapper.stat().st_mode | 0o111)
        with (args.result_dir / "run.out").open("wb") as output:
            completed = subprocess.run(
                ["taskset", "-c", str(args.cpu), "./do-part", "crypto_kem", primitive],
                cwd=root,
                stdout=output,
                stderr=subprocess.STDOUT,
                check=False,
            )
    finally:
        measure_path.write_bytes(original_measure)
        measure_path.chmod(original_measure_mode)
        for path, content in adapter_backups.items():
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)
        if compiler_backup:
            path, content, mode = compiler_backup
            path.write_bytes(content)
            path.chmod(mode)
        for path, mode in original_modes.items():
            path.chmod(mode)

    data_files = [
        path for path in (root / "bench").glob("*/data")
        if path.stat().st_mtime >= started - 1
    ]
    if len(data_files) != 1:
        raise SystemExit(f"expected one updated bench/*/data, found {len(data_files)}")
    shutil.copy2(data_files[0], args.result_dir / "data")
    run_text = (args.result_dir / "run.out").read_text(encoding="utf-8", errors="replace")
    data_text = (args.result_dir / "data").read_text(encoding="utf-8", errors="replace")
    if completed.returncode:
        raise SystemExit(f"SUPERCOP do-part exited {completed.returncode}; see run.out")
    if "tryfails" in run_text.lower() or "measurefails" in run_text.lower():
        raise SystemExit("SUPERCOP reported tryfails or measurefails")
    if args.mode == "native-kem":
        required = ("keypair_cycles", "enc_cycles", "dec_cycles")
    elif args.mode == "derived-poly":
        required = ("forward_small_cycles", "forward_general_cycles", "basemul_cycles",
                    "inverse_cycles", "baseinv_cycles", "poly_mul_small_cycles",
                    "poly_mul_general_cycles")
    elif args.mode == "derived-itail":
        required = ("inverse_ntt9_b0_first_cycles", "inverse_ntt9_b1_second_cycles",
                    "inverse_ntt9_b1_first_cycles", "inverse_ntt9_b0_second_cycles")
    elif args.mode == "derived-itail-d0":
        required = ("inverse_tail_d0_m0_first_cycles", "inverse_tail_d0_m1_second_cycles",
                    "inverse_tail_d0_m1_first_cycles", "inverse_tail_d0_m0_second_cycles")
    elif args.mode == "derived-itail-d0-m2":
        required = tuple(
            f"inverse_tail_d0_{variant}_{position}_cycles"
            for variant, position in (
                ("m0", "first"), ("m1", "second"), ("m2", "third"),
                ("m2", "first"), ("m0", "second"), ("m1", "third"),
                ("m1", "first"), ("m2", "second"), ("m0", "third")))
    elif args.mode == "derived-f0-ma1":
        required = ("f0_ma1_c0_first_cycles", "f0_ma1_c1_second_cycles",
                    "f0_ma1_c1_first_cycles", "f0_ma1_c0_second_cycles")
    elif args.mode == "derived-f0-ma1-ma0":
        required = tuple(
            f"{variant}_{position}_cycles"
            for variant, position in (
                ("f0_ma1_c0", "first"), ("f0_ma1_c1", "second"),
                ("f0_ma0", "third"), ("f0_ma0", "first"),
                ("f0_ma1_c0", "second"), ("f0_ma1_c1", "third"),
                ("f0_ma1_c1", "first"), ("f0_ma0", "second"),
                ("f0_ma1_c0", "third")))
    elif args.mode == "derived-f0-ma3":
        required = ("f0_ma0_first_cycles", "f0_ma3_second_cycles",
                    "f0_ma3_first_cycles", "f0_ma0_second_cycles")
    elif args.mode == "derived-f0-ma2-chunk":
        required = ("f0_ma0_first_cycles", "f0_ma2_repeat_second_cycles",
                    "f0_ma2_repeat_first_cycles", "f0_ma0_second_cycles")
    elif args.mode == "derived-f0-prod1":
        required = tuple(
            f"f0_prod1_{width}_{variant}_{position}_cycles"
            for width in ("1x", "2x")
            for variant, position in (("legacy", "first"), ("p1h", "second"),
                                      ("p1h", "first"), ("legacy", "second")))
    elif args.mode == "derived-f0-prod2":
        required = tuple(
            f"f0_prod2_{width}_{variant}_{position}_cycles"
            for width in ("1x", "2x")
            for variant, position in (("control", "first"),
                                      ("candidate", "second"),
                                      ("candidate", "first"),
                                      ("control", "second")))
    elif args.mode == "derived-f0-prod2-consumer":
        required = (
            "f0_prod2_consumer_control_first_cycles",
            "f0_prod2_consumer_candidate_second_cycles",
            "f0_prod2_consumer_candidate_first_cycles",
            "f0_prod2_consumer_control_second_cycles",
        )
    elif args.mode == "derived-gt9x16-prod3-price":
        required = tuple(
            f"gt9x16_prod3_price_{width}_{variant}_{position}_cycles"
            for width in ("1x", "2x")
            for variant, position in (("control", "first"),
                                      ("candidate", "second"),
                                      ("candidate", "first"),
                                      ("control", "second")))
    elif args.mode == "derived-gt9x16-prod3-consumer":
        required = (
            "gt9x16_prod3_consumer_control_first_cycles",
            "gt9x16_prod3_consumer_candidate_second_cycles",
            "gt9x16_prod3_consumer_candidate_first_cycles",
            "gt9x16_prod3_consumer_control_second_cycles",
        )
    elif args.mode == "derived-gt9x16-prod3-hash-fanout":
        required = tuple(
            f"gt9x16_prod3_hash_fanout_{variant}_pos{position}_cycles"
            for variant in ("o0", "o1", "c0", "c1")
            for position in range(1, 5))
    elif args.mode == "derived-gt9x16-prod3-hash-h1-price":
        required = tuple(
            f"gt9x16_prod3_hash_h1_price_{variant}_pos{position}_cycles"
            for variant in ("h0", "h1") for position in range(1, 5))
    elif args.mode == "derived-gt9x16-prod3-qorder-price":
        required = (
            "gt9x16_prod3_qorder_price_current_first_cycles",
            "gt9x16_prod3_qorder_price_natural_second_cycles",
            "gt9x16_prod3_qorder_price_natural_first_cycles",
            "gt9x16_prod3_qorder_price_current_second_cycles",
        )
    elif args.mode == "derived-gt9x16-prod3-t0-beta-price":
        required = tuple(
            f"gt9x16_prod3_t0_beta_price_{width}_{variant}_{position}_cycles"
            for width in ("1x", "2x", "caller")
            for variant, position in (("control", "first"),
                                      ("candidate", "second"),
                                      ("candidate", "first"),
                                      ("control", "second")))
    elif args.mode == "derived-gt9x16-prod3-encap-attribution-v2":
        required = tuple(
            f"gt9x16_prod3_encap_attribution_v2_{boundary}_{variant}_{position}_cycles"
            for boundary in ("producer_r", "producer_m", "dual_r", "tail")
            for variant, position in (("official", "first"),
                                      ("gt", "second"),
                                      ("gt", "first"),
                                      ("official", "second")))
    elif args.mode == "derived-gt9x16-prod3-encap-tail-attribution-v1":
        required = tuple(
            f"gt9x16_prod3_encap_tail_attribution_v1_{boundary}_{variant}_{position}_cycles"
            for boundary in ("t0", "t1", "t2")
            for variant, position in (("official", "first"),
                                      ("gt", "second"),
                                      ("gt", "first"),
                                      ("official", "second")))
    elif args.mode == "derived-encap-h-ingress-ma2-h3-price":
        required = tuple(
            f"encap_h_ingress_ma2_h3_price_{control}_{variant}_{position}_cycles"
            for control in ("current", "h1")
            for variant, position in (("control", "first"),
                                      ("h3", "second"),
                                      ("h3", "first"),
                                      ("control", "second")))
    else:
        required = ("f0_ma0_first_cycles", "f0_ma2_second_cycles",
                    "f0_ma2_first_cycles", "f0_ma0_second_cycles")
    missing = [name for name in required if f" {name} " not in data_text]
    if missing:
        raise SystemExit(f"benchmark data lacks {', '.join(missing)}")

    measure_elf = data_files[0].parent / "work" / "compile" / "measure"
    if not measure_elf.is_file():
        raise SystemExit(f"missing SUPERCOP-built measure ELF: {measure_elf}")
    saved_elf = args.result_dir / "measure"
    shutil.copy2(measure_elf, saved_elf)
    launch_dir = args.result_dir / "fresh-launches"
    launch_dir.mkdir()
    pooled = {name: [] for name in required}
    identities = []
    launch_observations = []
    for launch_number in range(1, args.fresh_launches + 1):
        replay = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(saved_elf.resolve())],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        output_path = launch_dir / f"launch-{launch_number:02d}.out"
        output_path.write_text(replay.stdout, encoding="utf-8")
        if replay.returncode:
            raise SystemExit(f"fresh SUPERCOP measure launch {launch_number} failed")
        identities.append(measure_identity(replay.stdout))
        current_launch = {}
        for name in required:
            observed = decode_observations(replay.stdout, name)
            if len(observed) != 96:
                raise SystemExit(
                    f"fresh launch {launch_number} has {len(observed)} {name} observations; expected 96")
            pooled[name].extend(observed)
            current_launch[name] = observed
        launch_observations.append(current_launch)
    if any(identity != identities[0] for identity in identities[1:]):
        raise SystemExit("SUPERCOP measure identity changed between fresh launches")
    required_identity = ("implementation", "cpuid", "cpucycles_persecond",
                         "cpucycles_implementation", "compiler")
    missing_identity = [name for name in required_identity if name not in identities[0]]
    if missing_identity:
        raise SystemExit("SUPERCOP measure identity lacks " + ", ".join(missing_identity))
    expected_identity = f"crypto_kem/{primitive}/{args.implementation}"
    if expected_identity not in identities[0]["implementation"]:
        raise SystemExit(
            f"SUPERCOP measured {identities[0]['implementation']}, expected {expected_identity}")
    summary = {
        "estimator": "SUPERCOP-20260627-stabilized-quartiles",
        "fresh_process_launches": args.fresh_launches,
        "observations_per_operation_per_launch": 96,
        "measure_loops": 3,
        "timings_per_loop": 32,
        "measure_identity": identities[0],
        "operations": {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in pooled.items()
        },
    }
    if args.mode == "derived-itail":
        combined = {
            "inverse_ntt9_b0_cycles": (
                pooled["inverse_ntt9_b0_first_cycles"] +
                pooled["inverse_ntt9_b0_second_cycles"]),
            "inverse_ntt9_b1_cycles": (
                pooled["inverse_ntt9_b1_first_cycles"] +
                pooled["inverse_ntt9_b1_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            b0_values = (observed["inverse_ntt9_b0_first_cycles"] +
                         observed["inverse_ntt9_b0_second_cycles"])
            b1_values = (observed["inverse_ntt9_b1_first_cycles"] +
                         observed["inverse_ntt9_b1_second_cycles"])
            b0_stq2 = stabilized_quartiles(b0_values)[1]
            b1_stq2 = stabilized_quartiles(b1_values)[1]
            paired_launches.append({
                "launch": launch_number,
                "inverse_ntt9_b0_stq2": b0_stq2,
                "inverse_ntt9_b1_stq2": b1_stq2,
                "b1_minus_b0_cycles": b1_stq2 - b0_stq2,
            })
        deltas = [entry["b1_minus_b0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "b1_faster_launches": sum(delta < 0 for delta in deltas),
            "b1_slower_launches": sum(delta > 0 for delta in deltas),
            "tied_launches": sum(delta == 0 for delta in deltas),
            "median_b1_minus_b0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-itail-d0":
        combined = {
            "inverse_tail_d0_m0_cycles": (
                pooled["inverse_tail_d0_m0_first_cycles"] +
                pooled["inverse_tail_d0_m0_second_cycles"]),
            "inverse_tail_d0_m1_cycles": (
                pooled["inverse_tail_d0_m1_first_cycles"] +
                pooled["inverse_tail_d0_m1_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            m0_values = (observed["inverse_tail_d0_m0_first_cycles"] +
                         observed["inverse_tail_d0_m0_second_cycles"])
            m1_values = (observed["inverse_tail_d0_m1_first_cycles"] +
                         observed["inverse_tail_d0_m1_second_cycles"])
            m0_stq2 = stabilized_quartiles(m0_values)[1]
            m1_stq2 = stabilized_quartiles(m1_values)[1]
            paired_launches.append({
                "launch": launch_number,
                "inverse_tail_d0_m0_stq2": m0_stq2,
                "inverse_tail_d0_m1_stq2": m1_stq2,
                "m1_minus_m0_cycles": m1_stq2 - m0_stq2,
            })
        deltas = [entry["m1_minus_m0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "m1_faster_launches": sum(delta < 0 for delta in deltas),
            "m1_slower_launches": sum(delta > 0 for delta in deltas),
            "tied_launches": sum(delta == 0 for delta in deltas),
            "median_m1_minus_m0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-itail-d0-m2":
        combined = {
            f"inverse_tail_d0_{variant}_cycles": sum(
                (pooled[f"inverse_tail_d0_{variant}_{position}_cycles"]
                 for position in ("first", "second", "third")), [])
            for variant in ("m0", "m1", "m2")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            stq2 = {
                variant: stabilized_quartiles(sum(
                    (observed[f"inverse_tail_d0_{variant}_{position}_cycles"]
                     for position in ("first", "second", "third")), []))[1]
                for variant in ("m0", "m1", "m2")
            }
            paired_launches.append({
                "launch": launch_number,
                **{f"inverse_tail_d0_{variant}_stq2": value
                   for variant, value in stq2.items()},
                "m1_minus_m0_cycles": stq2["m1"] - stq2["m0"],
                "m2_minus_m0_cycles": stq2["m2"] - stq2["m0"],
                "m2_minus_m1_cycles": stq2["m2"] - stq2["m1"],
            })
        m2_m0 = [entry["m2_minus_m0_cycles"] for entry in paired_launches]
        m2_m1 = [entry["m2_minus_m1_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "m2_faster_than_m0_launches": sum(delta < 0 for delta in m2_m0),
            "m2_slower_than_m0_launches": sum(delta > 0 for delta in m2_m0),
            "m2_tied_with_m0_launches": sum(delta == 0 for delta in m2_m0),
            "median_m2_minus_m0_cycles": statistics.median(m2_m0),
            "m2_faster_than_m1_launches": sum(delta < 0 for delta in m2_m1),
            "m2_slower_than_m1_launches": sum(delta > 0 for delta in m2_m1),
            "m2_tied_with_m1_launches": sum(delta == 0 for delta in m2_m1),
            "median_m2_minus_m1_cycles": statistics.median(m2_m1),
        }
    if args.mode == "derived-f0-ma1":
        combined = {
            "f0_ma1_c0_cycles": (pooled["f0_ma1_c0_first_cycles"] +
                                  pooled["f0_ma1_c0_second_cycles"]),
            "f0_ma1_c1_cycles": (pooled["f0_ma1_c1_first_cycles"] +
                                  pooled["f0_ma1_c1_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            c0 = stabilized_quartiles(
                observed["f0_ma1_c0_first_cycles"] +
                observed["f0_ma1_c0_second_cycles"])[1]
            c1 = stabilized_quartiles(
                observed["f0_ma1_c1_first_cycles"] +
                observed["f0_ma1_c1_second_cycles"])[1]
            paired_launches.append({
                "launch": launch_number,
                "f0_ma1_c0_stq2": c0,
                "f0_ma1_c1_stq2": c1,
                "c1_minus_c0_cycles": c1 - c0,
            })
        deltas = [entry["c1_minus_c0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "c1_faster_launches": sum(delta < 0 for delta in deltas),
            "c1_slower_launches": sum(delta > 0 for delta in deltas),
            "tied_launches": sum(delta == 0 for delta in deltas),
            "median_c1_minus_c0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-f0-ma1-ma0":
        combined = {
            f"{variant}_cycles": sum(
                (pooled[f"{variant}_{position}_cycles"]
                 for position in ("first", "second", "third")), [])
            for variant in ("f0_ma1_c0", "f0_ma1_c1", "f0_ma0")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            stq2 = {
                variant: stabilized_quartiles(sum(
                    (observed[f"{variant}_{position}_cycles"]
                     for position in ("first", "second", "third")), []))[1]
                for variant in ("f0_ma1_c0", "f0_ma1_c1", "f0_ma0")
            }
            paired_launches.append({
                "launch": launch_number,
                **{f"{variant}_stq2": value for variant, value in stq2.items()},
                "c1_minus_ma0_cycles": stq2["f0_ma1_c1"] - stq2["f0_ma0"],
                "c1_minus_c0_cycles": stq2["f0_ma1_c1"] - stq2["f0_ma1_c0"],
            })
        c1_ma0 = [entry["c1_minus_ma0_cycles"] for entry in paired_launches]
        c1_c0 = [entry["c1_minus_c0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "c1_faster_than_ma0_launches": sum(delta < 0 for delta in c1_ma0),
            "c1_slower_than_ma0_launches": sum(delta > 0 for delta in c1_ma0),
            "median_c1_minus_ma0_cycles": statistics.median(c1_ma0),
            "c1_faster_than_c0_launches": sum(delta < 0 for delta in c1_c0),
            "median_c1_minus_c0_cycles": statistics.median(c1_c0),
        }
    if args.mode == "derived-f0-ma3":
        combined = {
            "f0_ma0_cycles": (pooled["f0_ma0_first_cycles"] +
                              pooled["f0_ma0_second_cycles"]),
            "f0_ma3_cycles": (pooled["f0_ma3_first_cycles"] +
                              pooled["f0_ma3_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            ma0 = stabilized_quartiles(
                observed["f0_ma0_first_cycles"] +
                observed["f0_ma0_second_cycles"])[1]
            ma3 = stabilized_quartiles(
                observed["f0_ma3_first_cycles"] +
                observed["f0_ma3_second_cycles"])[1]
            paired_launches.append({
                "launch": launch_number,
                "f0_ma0_stq2": ma0,
                "f0_ma3_stq2": ma3,
                "ma3_minus_ma0_cycles": ma3 - ma0,
            })
        deltas = [entry["ma3_minus_ma0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "ma3_faster_than_ma0_launches": sum(x < 0 for x in deltas),
            "ma3_slower_than_ma0_launches": sum(x > 0 for x in deltas),
            "ma3_tied_with_ma0_launches": sum(x == 0 for x in deltas),
            "median_ma3_minus_ma0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-f0-ma2-chunk":
        combined = {
            "f0_ma0_cycles": (pooled["f0_ma0_first_cycles"] +
                              pooled["f0_ma0_second_cycles"]),
            "f0_ma2_repeat_cycles": (pooled["f0_ma2_repeat_first_cycles"] +
                                     pooled["f0_ma2_repeat_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            ma0 = stabilized_quartiles(
                observed["f0_ma0_first_cycles"] +
                observed["f0_ma0_second_cycles"])[1]
            ma2 = stabilized_quartiles(
                observed["f0_ma2_repeat_first_cycles"] +
                observed["f0_ma2_repeat_second_cycles"])[1]
            paired_launches.append({
                "launch": launch_number,
                "f0_ma0_stq2": ma0,
                "f0_ma2_repeat_stq2": ma2,
                "ma2_repeat_minus_ma0_cycles": ma2 - ma0,
                "ma2_repeat_over_ma0_ratio": ma2 / ma0,
            })
        deltas = [entry["ma2_repeat_minus_ma0_cycles"]
                  for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "ma2_repeat_faster_than_ma0_launches": sum(x < 0 for x in deltas),
            "ma2_repeat_slower_than_ma0_launches": sum(x > 0 for x in deltas),
            "ma2_repeat_tied_with_ma0_launches": sum(x == 0 for x in deltas),
            "median_ma2_repeat_minus_ma0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-f0-ma2":
        combined = {
            "f0_ma0_cycles": pooled["f0_ma0_first_cycles"] + pooled["f0_ma0_second_cycles"],
            "f0_ma2_cycles": pooled["f0_ma2_first_cycles"] + pooled["f0_ma2_second_cycles"],
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values), "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            ma0 = stabilized_quartiles(observed["f0_ma0_first_cycles"] +
                                       observed["f0_ma0_second_cycles"])[1]
            ma2 = stabilized_quartiles(observed["f0_ma2_first_cycles"] +
                                       observed["f0_ma2_second_cycles"])[1]
            paired_launches.append({"launch": launch_number,
                                    "f0_ma0_stq2": ma0, "f0_ma2_stq2": ma2,
                                    "ma2_minus_ma0_cycles": ma2 - ma0,
                                    "ma2_over_ma0_ratio": ma2 / ma0})
        deltas = [entry["ma2_minus_ma0_cycles"] for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "ma2_faster_than_ma0_launches": sum(x < 0 for x in deltas),
            "ma2_slower_than_ma0_launches": sum(x > 0 for x in deltas),
            "ma2_tied_with_ma0_launches": sum(x == 0 for x in deltas),
            "median_ma2_minus_ma0_cycles": statistics.median(deltas),
        }
    if args.mode == "derived-f0-prod1":
        combined = {
            f"f0_prod1_{width}_{variant}_cycles": (
                pooled[f"f0_prod1_{width}_{variant}_first_cycles"] +
                pooled[f"f0_prod1_{width}_{variant}_second_cycles"])
            for width in ("1x", "2x") for variant in ("legacy", "p1h")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            entry: dict[str, object] = {"launch": launch_number}
            for width in ("1x", "2x"):
                legacy = stabilized_quartiles(
                    observed[f"f0_prod1_{width}_legacy_first_cycles"] +
                    observed[f"f0_prod1_{width}_legacy_second_cycles"])[1]
                p1h = stabilized_quartiles(
                    observed[f"f0_prod1_{width}_p1h_first_cycles"] +
                    observed[f"f0_prod1_{width}_p1h_second_cycles"])[1]
                entry.update({
                    f"{width}_legacy_stq2": legacy,
                    f"{width}_p1h_stq2": p1h,
                    f"{width}_p1h_minus_legacy_cycles": p1h - legacy,
                    f"{width}_p1h_over_legacy_ratio": p1h / legacy,
                })
            paired_launches.append(entry)
        one_deltas = [float(entry["1x_p1h_minus_legacy_cycles"])
                      for entry in paired_launches]
        two_deltas = [float(entry["2x_p1h_minus_legacy_cycles"])
                      for entry in paired_launches]
        two_credit = -statistics.median(two_deltas)
        if two_credit < 300:
            screen = "poor-or-insufficient-for-current-ma2-gap"
        elif two_credit < 800:
            screen = "likely-insufficient-for-current-ma2-gap"
        elif two_credit < 1300:
            screen = "caller-attribution-worthy"
        else:
            screen = "strong-caller-integration-signal"
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "p1h_1x_faster_launches": sum(x < 0 for x in one_deltas),
            "p1h_1x_slower_launches": sum(x > 0 for x in one_deltas),
            "median_1x_p1h_minus_legacy_cycles": statistics.median(one_deltas),
            "p1h_2x_faster_launches": sum(x < 0 for x in two_deltas),
            "p1h_2x_slower_launches": sum(x > 0 for x in two_deltas),
            "median_2x_p1h_minus_legacy_cycles": statistics.median(two_deltas),
        }
        summary["producer_credit_screen"] = {
            "two_forward_credit_cycles": two_credit,
            "comparison_gap_cycles_approximate": 1312,
            "classification": screen,
            "note": "screening signal only; not a KEM promotion result",
        }

        relevant_symbols = (
            "poly_ntt", "ntruplus1152_exp001_official_to_f0",
            "ntruplus1152_exp001_f0_forward_for_ma2_p1h",
            "ntruplus1152_exp001_f0_prod1_p1h_pair",
            "ntruplus1152_exp001_f0_prod1_legacy_1x",
            "ntruplus1152_exp001_f0_prod1_p1h_1x",
            "ntruplus1152_exp001_f0_prod1_legacy_2x",
            "ntruplus1152_exp001_f0_prod1_p1h_2x",
        )
        summary["elf_layout"] = elf_layout(saved_elf, relevant_symbols)
        summary["static_call_attribution_per_forward"] = {
            "legacy": {"poly_ntt": 1, "official_to_f0": 1, "total": 2},
            "p1h": {"top_split": 1, "p1h_pair_helper": 4, "total": 5},
        }
        summary["perf_diagnostics"] = perf_diagnostics(
            saved_elf, args.cpu, args.result_dir)
        audit_paths = list(REPO_ROOT.glob(
            "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
            "experiments/*/generated/f0-prod1-p1h-audit.json"))
        if len(audit_paths) != 1:
            raise SystemExit(f"expected one P1-H audit, found {len(audit_paths)}")
        summary["p1h_static_instruction_attribution"] = json.loads(
            audit_paths[0].read_text(encoding="utf-8"))[
                "dynamic_instruction_attribution_per_forward"]
        shutil.copy2(audit_paths[0], args.result_dir / "f0-prod1-p1h-audit.json")
    if args.mode == "derived-f0-prod2":
        combined = {
            f"f0_prod2_{width}_{variant}_cycles": (
                pooled[f"f0_prod2_{width}_{variant}_first_cycles"] +
                pooled[f"f0_prod2_{width}_{variant}_second_cycles"])
            for width in ("1x", "2x") for variant in ("control", "candidate")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            entry: dict[str, object] = {"launch": launch_number}
            for width in ("1x", "2x"):
                control = stabilized_quartiles(
                    observed[f"f0_prod2_{width}_control_first_cycles"] +
                    observed[f"f0_prod2_{width}_control_second_cycles"])[1]
                candidate = stabilized_quartiles(
                    observed[f"f0_prod2_{width}_candidate_first_cycles"] +
                    observed[f"f0_prod2_{width}_candidate_second_cycles"])[1]
                entry.update({
                    f"{width}_control_stq2": control,
                    f"{width}_candidate_stq2": candidate,
                    f"{width}_candidate_minus_control_cycles": candidate - control,
                    f"{width}_candidate_over_control_ratio": candidate / control,
                })
            paired_launches.append(entry)
        one_deltas = [float(entry["1x_candidate_minus_control_cycles"])
                      for entry in paired_launches]
        two_deltas = [float(entry["2x_candidate_minus_control_cycles"])
                      for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "candidate_1x_faster_launches": sum(x < 0 for x in one_deltas),
            "candidate_1x_slower_launches": sum(x > 0 for x in one_deltas),
            "candidate_1x_tied_launches": sum(x == 0 for x in one_deltas),
            "median_1x_candidate_minus_control_cycles": statistics.median(one_deltas),
            "candidate_2x_faster_launches": sum(x < 0 for x in two_deltas),
            "candidate_2x_slower_launches": sum(x > 0 for x in two_deltas),
            "candidate_2x_tied_launches": sum(x == 0 for x in two_deltas),
            "median_2x_candidate_minus_control_cycles": statistics.median(two_deltas),
        }
        summary["decision"] = {
            "headline": "2x exact-MA2-boundary",
            "consumer_native_materialization_validated": (
                all(delta < 0 for delta in two_deltas)),
            "kem_promotion_result": False,
            "ma2_arithmetic_executed": False,
        }
        relevant_symbols = (
            "ntruplus1152_exp001_f0_forward_for_ma2_p1h",
            "ntruplus1152_exp001_f0_forward_for_ma2_p2b",
            "ntruplus1152_exp001_f0_generic_to_ma2_planes",
            "ntruplus1152_exp001_f0_prod2_control_1x",
            "ntruplus1152_exp001_f0_prod2_candidate_1x",
            "ntruplus1152_exp001_f0_prod2_control_2x",
            "ntruplus1152_exp001_f0_prod2_candidate_2x",
        )
        summary["elf_layout"] = elf_layout(saved_elf, relevant_symbols)
        audit_paths = list(REPO_ROOT.glob(
            "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
            "experiments/*/generated/f0-prod2-boundary-audit.json"))
        if len(audit_paths) != 1:
            raise SystemExit(f"expected one PROD2 boundary audit, found {len(audit_paths)}")
        summary["linked_movement_audit"] = json.loads(
            audit_paths[0].read_text(encoding="utf-8"))
        shutil.copy2(audit_paths[0], args.result_dir / "f0-prod2-boundary-audit.json")
    if args.mode == "derived-f0-prod2-consumer":
        combined = {
            "f0_prod2_consumer_control_cycles": (
                pooled["f0_prod2_consumer_control_first_cycles"] +
                pooled["f0_prod2_consumer_control_second_cycles"]),
            "f0_prod2_consumer_candidate_cycles": (
                pooled["f0_prod2_consumer_candidate_first_cycles"] +
                pooled["f0_prod2_consumer_candidate_second_cycles"]),
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            control = stabilized_quartiles(
                observed["f0_prod2_consumer_control_first_cycles"] +
                observed["f0_prod2_consumer_control_second_cycles"])[1]
            candidate = stabilized_quartiles(
                observed["f0_prod2_consumer_candidate_first_cycles"] +
                observed["f0_prod2_consumer_candidate_second_cycles"])[1]
            paired_launches.append({
                "launch": launch_number,
                "control_stq2": control,
                "candidate_stq2": candidate,
                "candidate_minus_control_cycles": candidate - control,
                "candidate_over_control_ratio": candidate / control,
            })
        deltas = [float(entry["candidate_minus_control_cycles"])
                  for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "candidate_faster_launches": sum(x < 0 for x in deltas),
            "candidate_slower_launches": sum(x > 0 for x in deltas),
            "candidate_tied_launches": sum(x == 0 for x in deltas),
            "median_candidate_minus_control_cycles": statistics.median(deltas),
        }
        control_symbol = "ntruplus1152_exp001_f0_prod2_consumer_control"
        candidate_symbol = "ntruplus1152_exp001_f0_prod2_consumer_candidate"
        native_ma2 = "ntruplus1152_exp001_f0_ma2_native_full"
        control_calls = direct_transfer_targets(saved_elf, control_symbol)
        candidate_calls = direct_transfer_targets(saved_elf, candidate_symbol)
        expected_control = [
            "ntruplus1152_exp001_f0_forward_for_ma2_p1h",
            "ntruplus1152_exp001_f0_forward_for_ma2_p1h",
            "ntruplus1152_exp001_f0_generic_to_ma2_planes",
            "ntruplus1152_exp001_f0_generic_to_ma2_planes",
            native_ma2,
        ]
        expected_candidate = [
            "ntruplus1152_exp001_f0_forward_for_ma2_p2b",
            "ntruplus1152_exp001_f0_forward_for_ma2_p2b",
            native_ma2,
        ]
        if control_calls != expected_control or candidate_calls != expected_candidate:
            raise SystemExit(
                f"consumer-island call graph changed: {control_calls} / {candidate_calls}")
        summary["linked_consumer_island_audit"] = {
            "control_direct_transfers": control_calls,
            "candidate_direct_transfers": candidate_calls,
            "shared_ma2_symbol": native_ma2,
            "shared_ma2_tail_transfers_per_island": 1,
            "resident_h_projection": "same native MA2 symbol and input pointer",
            "ma2_schedule_inv4_serializer": "same linked symbol",
            "generic_ma2_symbol_calls": 0,
            "only_r_m_producer_boundary_differs": True,
        }
        summary["decision"] = {
            "headline": "two-producer-plus-unchanged-ma2-consumer-island",
            "native_kem_result": False,
            "candidate_direction_stable": all(delta < 0 for delta in deltas),
        }
        summary["elf_layout"] = elf_layout(saved_elf, (
            control_symbol, candidate_symbol,
            "ntruplus1152_exp001_f0_forward_for_ma2_p1h",
            "ntruplus1152_exp001_f0_forward_for_ma2_p2b",
            "ntruplus1152_exp001_f0_generic_to_ma2_planes", native_ma2,
        ))
    if args.mode == "derived-gt9x16-prod3-price":
        prefix = "gt9x16_prod3_price"
        combined = {
            f"{prefix}_{width}_{variant}_cycles": (
                pooled[f"{prefix}_{width}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{width}_{variant}_second_cycles"])
            for width in ("1x", "2x")
            for variant in ("control", "candidate")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            entry: dict[str, object] = {"launch": launch_number}
            for width in ("1x", "2x"):
                control = stabilized_quartiles(
                    observed[f"{prefix}_{width}_control_first_cycles"] +
                    observed[f"{prefix}_{width}_control_second_cycles"])[1]
                candidate = stabilized_quartiles(
                    observed[f"{prefix}_{width}_candidate_first_cycles"] +
                    observed[f"{prefix}_{width}_candidate_second_cycles"])[1]
                entry.update({
                    f"{width}_control_stq2": control,
                    f"{width}_candidate_stq2": candidate,
                    f"{width}_candidate_minus_control_cycles": candidate - control,
                    f"{width}_candidate_over_control_ratio": candidate / control,
                })
            paired_launches.append(entry)
        one_deltas = [float(entry["1x_candidate_minus_control_cycles"])
                      for entry in paired_launches]
        two_deltas = [float(entry["2x_candidate_minus_control_cycles"])
                      for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "candidate_1x_faster_launches": sum(x < 0 for x in one_deltas),
            "candidate_1x_slower_launches": sum(x > 0 for x in one_deltas),
            "candidate_1x_tied_launches": sum(x == 0 for x in one_deltas),
            "median_1x_candidate_minus_control_cycles": statistics.median(one_deltas),
            "candidate_2x_faster_launches": sum(x < 0 for x in two_deltas),
            "candidate_2x_slower_launches": sum(x > 0 for x in two_deltas),
            "candidate_2x_tied_launches": sum(x == 0 for x in two_deltas),
            "median_2x_candidate_minus_control_cycles": statistics.median(two_deltas),
        }
        summary["decision"] = {
            "headline": "2x-post-top-split-to-exact-MA2-boundary",
            "ma2_arithmetic_executed": False,
            "native_kem_result": False,
        }
        price_symbol = "ntruplus1152_exp001_gt9x16_prod3_aos_full_price"
        forbidden_symbols = (
            "ntruplus1152_exp001_gt9x16_prod3_aos_branch0",
            "ntruplus1152_exp001_gt9x16_prod3_aos_full",
        )
        relevant_symbols = (
            "ntruplus1152_exp001_f0_prod2_ma2_p2b_pair",
            "ntruplus1152_exp001_gt9x16_prod3_price_control_1x",
            "ntruplus1152_exp001_gt9x16_prod3_price_candidate_1x",
            "ntruplus1152_exp001_gt9x16_prod3_price_control_2x",
            "ntruplus1152_exp001_gt9x16_prod3_price_candidate_2x",
            price_symbol,
            *forbidden_symbols,
        )
        layout = elf_layout(saved_elf, relevant_symbols)
        retained_forbidden = [name for name in forbidden_symbols
                              if name in layout["symbols"]]
        if retained_forbidden:
            raise SystemExit(
                "PRICE ELF retained duplicate PROD3 symbols: " +
                ", ".join(retained_forbidden))
        price_layout = layout["symbols"].get(price_symbol)
        if price_layout is None or price_layout["size"] != 16569:
            raise SystemExit(
                f"unexpected candidate-only PROD3 size: {price_layout}")
        summary["elf_layout"] = layout
        summary["linked_retention_gate"] = {
            "candidate_only_symbol": price_symbol,
            "candidate_only_text_bytes": price_layout["size"],
            "forbidden_duplicate_symbols": list(forbidden_symbols),
            "forbidden_duplicate_symbols_retained": retained_forbidden,
            "passed": True,
        }
        audit_paths = list(REPO_ROOT.glob(
            "ntruplus-ntt-Optimized/Additional_Implementation/avx2/NTRU+1152/"
            "experiments/*/generated/gt9x16-prod3-aos-full-audit.json"))
        if len(audit_paths) != 1:
            raise SystemExit(f"expected one PROD3 full audit, found {len(audit_paths)}")
        summary["linked_movement_audit"] = json.loads(
            audit_paths[0].read_text(encoding="utf-8"))
        shutil.copy2(audit_paths[0], args.result_dir / audit_paths[0].name)
    if args.mode == "derived-gt9x16-prod3-consumer":
        prefix = "gt9x16_prod3_consumer"
        combined = {
            f"{prefix}_{variant}_cycles": (
                pooled[f"{prefix}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{variant}_second_cycles"])
            for variant in ("control", "candidate")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            control = stabilized_quartiles(
                observed[f"{prefix}_control_first_cycles"] +
                observed[f"{prefix}_control_second_cycles"])[1]
            candidate = stabilized_quartiles(
                observed[f"{prefix}_candidate_first_cycles"] +
                observed[f"{prefix}_candidate_second_cycles"])[1]
            paired_launches.append({
                "launch": launch_number,
                "control_stq2": control,
                "candidate_stq2": candidate,
                "candidate_minus_control_cycles": candidate - control,
                "candidate_over_control_ratio": candidate / control,
            })
        deltas = [float(entry["candidate_minus_control_cycles"])
                  for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "candidate_faster_launches": sum(x < 0 for x in deltas),
            "candidate_slower_launches": sum(x > 0 for x in deltas),
            "candidate_tied_launches": sum(x == 0 for x in deltas),
            "median_candidate_minus_control_cycles": statistics.median(deltas),
        }
        control_symbol = "ntruplus1152_exp001_gt9x16_prod3_consumer_control"
        candidate_symbol = "ntruplus1152_exp001_gt9x16_prod3_consumer_candidate"
        top_split = "ntruplus1152_exp001_top_split_small"
        p2b = "ntruplus1152_exp001_f0_prod2_ma2_p2b_pair"
        price_symbol = "ntruplus1152_exp001_gt9x16_prod3_aos_full_price"
        native_ma2 = "ntruplus1152_exp001_f0_ma2_native_full"
        control_calls = direct_transfer_targets(saved_elf, control_symbol)
        candidate_calls = direct_transfer_targets(saved_elf, candidate_symbol)
        expected_control = [top_split, p2b, p2b, p2b, p2b,
                            top_split, p2b, p2b, p2b, p2b, native_ma2]
        expected_candidate = [top_split, price_symbol, top_split,
                              price_symbol, native_ma2]
        if control_calls != expected_control or candidate_calls != expected_candidate:
            raise SystemExit(
                f"PROD3 consumer call graph changed: {control_calls} / {candidate_calls}")
        forbidden_symbols = (
            "ntruplus1152_exp001_gt9x16_prod3_aos_branch0",
            "ntruplus1152_exp001_gt9x16_prod3_aos_full",
        )
        layout = elf_layout(saved_elf, (
            control_symbol, candidate_symbol, top_split, p2b,
            price_symbol, native_ma2, *forbidden_symbols))
        retained_forbidden = [name for name in forbidden_symbols
                              if name in layout["symbols"]]
        if retained_forbidden:
            raise SystemExit(
                "consumer ELF retained duplicate PROD3 symbols: " +
                ", ".join(retained_forbidden))
        price_layout = layout["symbols"].get(price_symbol)
        if price_layout is None or price_layout["size"] != 16569:
            raise SystemExit(f"unexpected consumer PROD3 size: {price_layout}")
        summary["linked_consumer_island_audit"] = {
            "control_direct_transfers": control_calls,
            "candidate_direct_transfers": candidate_calls,
            "shared_top_split_symbol": top_split,
            "shared_ma2_symbol": native_ma2,
            "resident_h_pointer": "same measure allocation and value",
            "ma2_inv4_serializer": "same linked native MA2 symbol",
            "only_two_gt_producers_differ": True,
            "forbidden_duplicate_symbols_retained": retained_forbidden,
        }
        summary["elf_layout"] = layout
        summary["decision"] = {
            "headline": "two-producer-plus-unchanged-ma2-consumer-island",
            "native_kem_result": False,
            "candidate_direction_stable": all(delta < 0 for delta in deltas),
        }
    if args.mode == "derived-gt9x16-prod3-hash-fanout":
        prefix = "gt9x16_prod3_hash_fanout"
        variants = ("o0", "o1", "c0", "c1")
        combined = {
            variant: sum(
                (pooled[f"{prefix}_{variant}_pos{position}_cycles"]
                 for position in range(1, 5)), [])
            for variant in variants
        }
        summary["balanced_combined_operations"] = {
            f"{prefix}_{variant}_cycles": {
                "observations": len(values),
                "stq1": stabilized_quartiles(values)[0],
                "stq2": stabilized_quartiles(values)[1],
                "stq3": stabilized_quartiles(values)[2],
            }
            for variant, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            stq2 = {
                variant: stabilized_quartiles(sum(
                    (observed[f"{prefix}_{variant}_pos{position}_cycles"]
                     for position in range(1, 5)), []))[1]
                for variant in variants
            }
            official_fanout = stq2["o1"] - stq2["o0"]
            candidate_fanout = stq2["c1"] - stq2["c0"]
            paired_launches.append({
                "launch": launch_number,
                **{f"{variant}_stq2": value for variant, value in stq2.items()},
                "official_hash_fanout_cycles": official_fanout,
                "candidate_hash_fanout_cycles": candidate_fanout,
                "excess_hash_fanout_tax_cycles":
                    candidate_fanout - official_fanout,
                "producer_candidate_minus_official_cycles":
                    stq2["c0"] - stq2["o0"],
                "complete_dual_output_candidate_minus_official_cycles":
                    stq2["c1"] - stq2["o1"],
            })
        excess = [float(entry["excess_hash_fanout_tax_cycles"])
                  for entry in paired_launches]
        producer = [float(entry["producer_candidate_minus_official_cycles"])
                    for entry in paired_launches]
        complete = [float(entry[
            "complete_dual_output_candidate_minus_official_cycles"])
                    for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "median_excess_hash_fanout_tax_cycles": statistics.median(excess),
            "positive_excess_tax_launches": sum(value > 0 for value in excess),
            "negative_excess_tax_launches": sum(value < 0 for value in excess),
            "median_producer_candidate_minus_official_cycles":
                statistics.median(producer),
            "candidate_producer_faster_launches":
                sum(value < 0 for value in producer),
            "candidate_producer_slower_launches":
                sum(value > 0 for value in producer),
            "median_complete_dual_output_candidate_minus_official_cycles":
                statistics.median(complete),
            "candidate_complete_dual_output_faster_launches":
                sum(value < 0 for value in complete),
            "candidate_complete_dual_output_slower_launches":
                sum(value > 0 for value in complete),
        }
        symbols = {
            variant: f"ntruplus1152_exp001_hash_fanout_{variant}"
            for variant in variants
        }
        top_split = "ntruplus1152_exp001_top_split_small"
        price_symbol = "ntruplus1152_exp001_gt9x16_prod3_aos_full_price"
        hash_bridge = "ntruplus1152_exp001_prod3_hash_bytes"
        expected = {
            "o0": ["poly_ntt"],
            "o1": ["poly_ntt", "poly_tobytes"],
            "c0": [top_split, price_symbol],
            "c1": [top_split, price_symbol, hash_bridge],
        }
        transfers = {
            variant: direct_transfer_targets(saved_elf, symbol)
            for variant, symbol in symbols.items()
        }
        if transfers != expected:
            raise SystemExit(
                f"PROD3 hash-fanout call graph changed: {transfers}")
        layout = elf_layout(saved_elf, (
            *symbols.values(), top_split, price_symbol, hash_bridge,
            "ntruplus1152_exp001_f0_ma2_planes_to_generic",
            "ntruplus1152_exp001_f0_ma0_to_official",
            "poly_ntt", "poly_tobytes"))
        price_layout = layout["symbols"].get(price_symbol)
        if price_layout is None or price_layout["size"] != 16569:
            raise SystemExit(f"unexpected hash-fanout PROD3 size: {price_layout}")
        summary["linked_hash_fanout_audit"] = {
            "direct_transfers": transfers,
            "latin_square_positions_per_variant": [1, 2, 3, 4],
            "same_coefficient_input_residency": True,
            "o0_output": "Official transformed state",
            "o1_output": "Official transformed state plus exact 1728 bytes",
            "c0_output": "PROD3 exact MA2-native planes",
            "c1_output": "same MA2-native planes plus exact 1728 bytes",
            "prod3_arithmetic_frozen": True,
        }
        summary["elf_layout"] = layout
        summary["decision"] = {
            "headline": "excess-hash-fanout-tax-(c1-c0)-(o1-o0)",
            "native_kem_result": False,
            "direct_hash_serializer_implemented": False,
        }
    if args.mode == "derived-gt9x16-prod3-hash-h1-price":
        prefix = "gt9x16_prod3_hash_h1_price"
        variants = ("h0", "h1")
        combined = {
            variant: sum(
                (pooled[f"{prefix}_{variant}_pos{position}_cycles"]
                 for position in range(1, 5)), [])
            for variant in variants
        }
        summary["balanced_combined_operations"] = {
            f"{prefix}_{variant}_cycles": {
                "observations": len(values),
                "stq1": stabilized_quartiles(values)[0],
                "stq2": stabilized_quartiles(values)[1],
                "stq3": stabilized_quartiles(values)[2],
            }
            for variant, values in combined.items()
        }
        paired_launches = []
        for launch_number, observed in enumerate(launch_observations, start=1):
            stq2 = {
                variant: stabilized_quartiles(sum(
                    (observed[f"{prefix}_{variant}_pos{position}_cycles"]
                     for position in range(1, 5)), []))[1]
                for variant in variants
            }
            paired_launches.append({
                "launch": launch_number,
                "h0_stq2": stq2["h0"],
                "h1_stq2": stq2["h1"],
                "h1_minus_h0_cycles": stq2["h1"] - stq2["h0"],
            })
        deltas = [float(entry["h1_minus_h0_cycles"])
                  for entry in paired_launches]
        summary["balanced_paired_launches"] = {
            "launches": paired_launches,
            "median_h1_minus_h0_cycles": statistics.median(deltas),
            "h1_faster_launches": sum(value < 0 for value in deltas),
            "h1_slower_launches": sum(value > 0 for value in deltas),
        }
        wrappers = {
            "h0": "ntruplus1152_exp001_prod3_hash_h1_price_h0",
            "h1": "ntruplus1152_exp001_prod3_hash_h1_price_h1",
        }
        bridge = "ntruplus1152_exp001_prod3_hash_bytes"
        direct = "ntruplus1152_exp001_prod3_ma2_hash_h1"
        transfers = {
            variant: direct_transfer_targets(saved_elf, symbol)
            for variant, symbol in wrappers.items()
        }
        expected = {"h0": [bridge], "h1": [direct]}
        if transfers != expected:
            raise SystemExit(f"PROD3 H1 price call graph changed: {transfers}")
        layout = elf_layout(saved_elf, (
            *wrappers.values(), bridge, direct,
            "ntruplus1152_exp001_f0_ma2_planes_to_generic",
            "ntruplus1152_exp001_f0_ma0_to_official", "poly_tobytes"))
        summary["linked_hash_h1_price_audit"] = {
            "direct_transfers": transfers,
            "input_boundary": "same materialized scale-4 MA2 planes",
            "output_boundary": "same exact 1728-byte hash input",
            "h0_path": "planes-to-generic; generic-to-Official; inv4; poly_tobytes",
            "h1_path": "direct H1 serializer",
            "producer_executed": False,
            "ma2_arithmetic_executed": False,
            "native_kem_result": False,
        }
        summary["elf_layout"] = layout
        summary["decision"] = {
            "headline": "direct-H1-minus-current-H0-recovery",
            "native_kem_result": False,
            "candidate_direction_stable": all(delta < 0 for delta in deltas),
        }
    if args.mode == "derived-gt9x16-prod3-qorder-price":
        prefix = "gt9x16_prod3_qorder_price"
        combined = {
            variant: (pooled[f"{prefix}_{variant}_first_cycles"] +
                      pooled[f"{prefix}_{variant}_second_cycles"])
            for variant in ("current", "natural")
        }
        summary["balanced_combined_operations"] = {
            f"{prefix}_{variant}_cycles": {
                "observations": len(values),
                "stq1": stabilized_quartiles(values)[0],
                "stq2": stabilized_quartiles(values)[1],
                "stq3": stabilized_quartiles(values)[2],
            } for variant, values in combined.items()
        }
        launches = []
        for number, observed in enumerate(launch_observations, start=1):
            current = stabilized_quartiles(
                observed[f"{prefix}_current_first_cycles"] +
                observed[f"{prefix}_current_second_cycles"])[1]
            natural = stabilized_quartiles(
                observed[f"{prefix}_natural_first_cycles"] +
                observed[f"{prefix}_natural_second_cycles"])[1]
            launches.append({"launch": number, "current_stq2": current,
                             "natural_stq2": natural,
                             "natural_minus_current_cycles": natural-current})
        deltas = [float(row["natural_minus_current_cycles"]) for row in launches]
        summary["balanced_paired_launches"] = {
            "launches": launches,
            "natural_faster_launches": sum(x < 0 for x in deltas),
            "natural_slower_launches": sum(x > 0 for x in deltas),
            "median_natural_minus_current_cycles": statistics.median(deltas),
        }
        wrappers = {"current": "ntruplus1152_exp001_qorder_price_current",
                    "natural": "ntruplus1152_exp001_qorder_price_natural"}
        symbols = {
            "top": "ntruplus1152_exp001_top_split_small",
            "current_producer": "ntruplus1152_exp001_gt9x16_prod3_aos_full_price",
            "natural_producer": "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
            "current_ma2": "ntruplus1152_exp001_f0_ma2_planes_current_q",
            "natural_ma2": "ntruplus1152_exp001_f0_ma2_planes_natural_q",
            "current_h1": "ntruplus1152_exp001_prod3_ma2_hash_h1",
            "natural_h1": "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
        }
        transfers = {key: direct_transfer_targets(saved_elf, value)
                     for key, value in wrappers.items()}
        expected = {
            "current": [symbols["top"], symbols["current_producer"],
                        symbols["top"], symbols["current_producer"],
                        symbols["current_ma2"], symbols["current_h1"],
                        symbols["current_h1"]],
            "natural": [symbols["top"], symbols["natural_producer"],
                        symbols["top"], symbols["natural_producer"],
                        symbols["natural_ma2"], symbols["natural_h1"],
                        symbols["natural_h1"]],
        }
        if transfers != expected:
            raise SystemExit(f"Q-order PRICE call graph changed: {transfers}")
        summary["linked_qorder_price_audit"] = {
            "direct_transfers": transfers,
            "two_producers": True, "resident_h_multiplicity": 1,
            "MA2_arithmetic_identical": True,
            "hash_and_ciphertext_H1_multiplicity": 2,
            "same_input_residency": True, "same_output_bytes": True,
            "static_delta": {"routing": -192, "data_loads": 16,
                             "total_instructions": -176},
        }
        summary["elf_layout"] = elf_layout(
            saved_elf, (*wrappers.values(), *symbols.values()))
        summary["decision"] = {
            "headline": "complete-caller-shaped-current-Q-vs-natural-Q",
            "native_kem_result": False,
            "freeze_qorder_after_four-setting-arbitration": True,
        }
    if args.mode == "derived-gt9x16-prod3-t0-beta-price":
        prefix = "gt9x16_prod3_t0_beta_price"
        combined = {
            f"{prefix}_{width}_{variant}_cycles": (
                pooled[f"{prefix}_{width}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{width}_{variant}_second_cycles"])
            for width in ("1x", "2x", "caller")
            for variant in ("control", "candidate")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        launches = []
        for number, observed in enumerate(launch_observations, 1):
            entry: dict[str, object] = {"launch": number}
            for width in ("1x", "2x", "caller"):
                control = stabilized_quartiles(
                    observed[f"{prefix}_{width}_control_first_cycles"] +
                    observed[f"{prefix}_{width}_control_second_cycles"])[1]
                candidate = stabilized_quartiles(
                    observed[f"{prefix}_{width}_candidate_first_cycles"] +
                    observed[f"{prefix}_{width}_candidate_second_cycles"])[1]
                entry.update({f"{width}_control_stq2": control,
                              f"{width}_candidate_stq2": candidate,
                              f"{width}_candidate_minus_control_cycles":
                                  candidate - control})
            launches.append(entry)
        summary["balanced_paired_launches"] = {"launches": launches}
        symbols = {
            "control_1x": "ntruplus1152_exp001_t0_beta_price_control_1x",
            "candidate_1x": "ntruplus1152_exp001_t0_beta_price_candidate_1x",
            "control_2x": "ntruplus1152_exp001_t0_beta_price_control_2x",
            "candidate_2x": "ntruplus1152_exp001_t0_beta_price_candidate_2x",
            "control_caller": "ntruplus1152_exp001_t0_beta_price_control_caller",
            "candidate_caller": "ntruplus1152_exp001_t0_beta_price_candidate_caller",
            "control_forward":
                "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
            "candidate_forward":
                "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta",
            "top": "ntruplus1152_exp001_top_split_small",
            "ma2": "ntruplus1152_exp001_f0_ma2_planes_natural_q",
            "h1": "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
        }
        expected = {
            "control_1x": [symbols["top"], symbols["control_forward"]],
            "candidate_1x": [symbols["top"], symbols["candidate_forward"]],
            "control_2x": [symbols["control_1x"], symbols["control_1x"]],
            "candidate_2x": [symbols["candidate_1x"], symbols["candidate_1x"]],
            "control_caller": [symbols["control_2x"], symbols["ma2"],
                               symbols["h1"], symbols["h1"]],
            "candidate_caller": [symbols["candidate_2x"], symbols["ma2"],
                                 symbols["h1"], symbols["h1"]],
        }
        transfers = {key: direct_transfer_targets(saved_elf, symbols[key])
                     for key in expected}
        if transfers != expected:
            raise SystemExit(f"T0-beta PRICE call graph changed: {transfers}")
        summary["linked_t0_beta_price_audit"] = {
            "direct_transfers": transfers,
            "producer_semantic_abi":
                "Natural-Q scale-4; raw representative may differ",
            "producer_preflight": "canonical equality and signed-i16 range",
            "caller_preflight": "ciphertext and hash bytes exact",
            "shared_resident_h_ma2_h1": True,
            "schedule_taxonomy": {"constant_operands": [666, 650],
                                  "estimated_rodata_delta_bytes": 448},
            "natural_q_linked_taxonomy": {
                "constant_operands": [594, 578],
                "actual_rodata_delta_bytes": 416},
            "taxonomy_note":
                "absolute baselines differ by schedule taxonomy and linker retained set; principal deltas agree",
            "native_kem_result": False,
        }
        summary["elf_layout"] = elf_layout(saved_elf, tuple(symbols.values()))
        summary["decision"] = {
            "headline": "2x-producer-and-frozen-caller-island",
            "native_kem_result": False,
        }
    if args.mode == "derived-gt9x16-prod3-encap-attribution-v2":
        prefix = "gt9x16_prod3_encap_attribution_v2"
        boundaries = ("producer_r", "producer_m", "dual_r", "tail")
        combined = {
            f"{prefix}_{boundary}_{variant}_cycles": (
                pooled[f"{prefix}_{boundary}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{boundary}_{variant}_second_cycles"])
            for boundary in boundaries for variant in ("official", "gt")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        launches = []
        for number, observed in enumerate(launch_observations, 1):
            entry: dict[str, object] = {"launch": number}
            deltas = {}
            for boundary in boundaries:
                official = stabilized_quartiles(
                    observed[f"{prefix}_{boundary}_official_first_cycles"] +
                    observed[f"{prefix}_{boundary}_official_second_cycles"])[1]
                gt = stabilized_quartiles(
                    observed[f"{prefix}_{boundary}_gt_first_cycles"] +
                    observed[f"{prefix}_{boundary}_gt_second_cycles"])[1]
                deltas[boundary] = gt - official
                entry.update({f"{boundary}_official_stq2": official,
                              f"{boundary}_gt_stq2": gt,
                              f"{boundary}_gt_minus_official_cycles": gt - official})
            entry["hash_fanout_excess_cycles"] = (
                deltas["dual_r"] - deltas["producer_r"])
            entry["rough_modeled_debt_cycles"] = (
                deltas["producer_r"] + deltas["producer_m"] +
                entry["hash_fanout_excess_cycles"] + deltas["tail"])
            launches.append(entry)
        summary["balanced_paired_launches"] = {"launches": launches}
        symbols = {
            "official_producer": "ntruplus1152_exp001_attr_v2_official_producer",
            "gt_producer": "ntruplus1152_exp001_attr_v2_gt_producer",
            "official_dual": "ntruplus1152_exp001_attr_v2_official_dual",
            "gt_dual": "ntruplus1152_exp001_attr_v2_gt_dual",
            "official_tail": "ntruplus1152_exp001_attr_v2_official_tail",
            "gt_tail": "ntruplus1152_exp001_attr_v2_gt_tail",
            "official_forward": "poly_ntt",
            "gt_top": "ntruplus1152_exp001_top_split_small",
            "gt_forward":
                "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta",
            "official_basemul": "poly_basemul",
            "official_add": "poly_add",
            "official_tobytes": "poly_tobytes",
            "gt_ma2": "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4",
            "gt_h1": "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
        }
        expected = {
            "official_producer": [symbols["official_forward"]],
            "gt_producer": [symbols["gt_top"], symbols["gt_forward"]],
            "official_dual": [symbols["official_producer"],
                              symbols["official_tobytes"]],
            "gt_dual": [symbols["gt_producer"], symbols["gt_h1"]],
            "official_tail": [symbols["official_basemul"],
                              symbols["official_add"],
                              symbols["official_tobytes"]],
            "gt_tail": [symbols["gt_ma2"], symbols["gt_h1"]],
        }
        transfers = {key: direct_transfer_targets(saved_elf, symbols[key])
                     for key in expected}
        if transfers != expected:
            raise SystemExit(f"Attribution V2 call graph changed: {transfers}")
        summary["linked_encap_attribution_v2_audit"] = {
            "direct_transfers": transfers,
            "producer_boundary": "coefficient input to native transformed state",
            "dual_boundary": "coefficient input to native state plus exact 1728 bytes",
            "tail_boundary": "resident transformed r/m/h to exact ciphertext polynomial bytes",
            "preflight": "Official poly_tobytes equals GT Direct H1; tail bytes exact",
            "candidate": "persistent-AoS + Natural-Q + T0-beta + scale4 MA2 + Direct H1",
            "native_kem_result": False,
        }
        summary["elf_layout"] = elf_layout(saved_elf, tuple(symbols.values()))
        summary["decision"] = {
            "headline": "ENCAP-CALLER-ATTRIBUTION-V2",
            "next_if_residual_large":
                "r-dual-output-to-hash-g-to-sotp-to-m-producer-chain",
            "new_asm": False,
            "native_kem_result": False,
        }
    if args.mode == "derived-gt9x16-prod3-encap-tail-attribution-v1":
        prefix = "gt9x16_prod3_encap_tail_attribution_v1"
        boundaries = ("t0", "t1", "t2")
        combined = {
            f"{prefix}_{boundary}_{variant}_cycles": (
                pooled[f"{prefix}_{boundary}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{boundary}_{variant}_second_cycles"])
            for boundary in boundaries for variant in ("official", "gt")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        summary["tail_attribution_contract"] = {
            "t0": "resident h projection",
            "t1": "resident h projection plus MA2 arithmetic",
            "t2": "resident h projection plus MA2 arithmetic plus ciphertext serialization",
            "starting_residency": "reset coefficients and independently prepare identical semantic r/m/h states before every balanced entry",
            "gt_scale_contract": "scale-4 MA2 followed by exactly one Direct H1 inv4",
            "preflight": "resident-h raw map exact; T1 semantic bytes exact; GT T2 equals cumulative production path equals Official bytes",
            "new_asm": False,
            "native_kem_result": False,
        }
    if args.mode == "derived-encap-h-ingress-ma2-h3-price":
        prefix = "encap_h_ingress_ma2_h3_price"
        combined = {
            f"{prefix}_{control}_{variant}_cycles": (
                pooled[f"{prefix}_{control}_{variant}_first_cycles"] +
                pooled[f"{prefix}_{control}_{variant}_second_cycles"])
            for control in ("current", "h1") for variant in ("control", "h3")
        }
        summary["balanced_combined_operations"] = {
            name: {"observations": len(values),
                   "stq1": stabilized_quartiles(values)[0],
                   "stq2": stabilized_quartiles(values)[1],
                   "stq3": stabilized_quartiles(values)[2]}
            for name, values in combined.items()
        }
        summary["h3_price_contract"] = {
            "input": "valid 1728-byte public key plus resident Natural-Q scale-4 r/m",
            "output": "raw-exact Natural-Q scale-4 MA2 state",
            "current": "Official poly_frombytes plus cumulative Natural-Q h projection/MA2",
            "h1": "Natural-Q H1 decoder plus materialized h plus preprojected MA2",
            "h3": "streaming PK decode/validate directly into unchanged MA2",
            "serializer": "excluded",
            "native_kem_result": False,
        }
    (args.result_dir / "stq-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lock = read_lock()
    metadata = {
        **lock,
        "benchmark_class": ("supercop-native-kem" if args.mode == "native-kem"
                            else "supercop-derived-poly" if args.mode == "derived-poly"
                            else "supercop-derived-itail-d0" if args.mode == "derived-itail-d0"
                            else "supercop-derived-itail-d0-m2" if args.mode == "derived-itail-d0-m2"
                            else "supercop-derived-poly-f0-ma1" if args.mode == "derived-f0-ma1"
                            else "supercop-derived-poly-f0-ma1-ma0" if args.mode == "derived-f0-ma1-ma0"
                            else "supercop-derived-poly-f0-ma3" if args.mode == "derived-f0-ma3"
                            else "supercop-derived-poly-f0-ma2-chunk-diagnostic" if args.mode == "derived-f0-ma2-chunk"
                            else "supercop-derived-poly-f0-ma2" if args.mode == "derived-f0-ma2"
                            else "supercop-derived-poly-f0-prod1" if args.mode == "derived-f0-prod1"
                            else "supercop-derived-poly-f0-prod2-boundary" if args.mode == "derived-f0-prod2"
                            else "supercop-derived-poly-f0-prod2-consumer" if args.mode == "derived-f0-prod2-consumer"
                            else "supercop-derived-gt9x16-prod3-price" if args.mode == "derived-gt9x16-prod3-price"
                            else "supercop-derived-gt9x16-prod3-consumer" if args.mode == "derived-gt9x16-prod3-consumer"
                            else "supercop-derived-gt9x16-prod3-hash-fanout" if args.mode == "derived-gt9x16-prod3-hash-fanout"
                            else "supercop-derived-gt9x16-prod3-hash-h1-price" if args.mode == "derived-gt9x16-prod3-hash-h1-price"
                            else "supercop-derived-gt9x16-prod3-qorder-price" if args.mode == "derived-gt9x16-prod3-qorder-price"
                            else "supercop-derived-gt9x16-prod3-t0-beta-price" if args.mode == "derived-gt9x16-prod3-t0-beta-price"
                            else "supercop-derived-gt9x16-prod3-encap-attribution-v2" if args.mode == "derived-gt9x16-prod3-encap-attribution-v2"
                            else "supercop-derived-gt9x16-prod3-encap-tail-attribution-v1" if args.mode == "derived-gt9x16-prod3-encap-tail-attribution-v1"
                            else "supercop-derived-encap-h-ingress-ma2-h3-price" if args.mode == "derived-encap-h-ingress-ma2-h3-price"
                            else "supercop-derived-itail"),
        "bench_cpu": args.cpu,
        "campaign": str(root),
        "candidate_source_manifest_sha256": (
            sha256_file(selected / "SOURCE-MANIFEST.json")
            if (selected / "SOURCE-MANIFEST.json").is_file() else None),
        "candidate_sha256s_sha256": (
            sha256_file(selected / "SHA256SUMS")
            if (selected / "SHA256SUMS").is_file() else None),
        "compiler_policy": "fixed-common" if args.compiler_wrapper else "native-supercop-selection",
        "compiler_wrapper": str(args.compiler_wrapper.resolve()) if args.compiler_wrapper else None,
        "compiler_wrapper_sha256": sha256_file(args.compiler_wrapper) if args.compiler_wrapper else None,
        "cpu_model": cpu_model,
        "do_part_exit_code": completed.returncode,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "implementation": args.implementation,
        "kernel": platform.release(),
        "machine": platform.machine(),
        "frequency_control": frequency,
        "frequency_policy": "required" if args.require_frequency_control else "record-only",
        "fresh_process_launches": args.fresh_launches,
        "measure_elf_sha256": sha256_file(saved_elf),
        "stq_summary_sha256": sha256_file(args.result_dir / "stq-summary.json"),
        "measure_source_sha256": sha256_file(
            root / "crypto_kem" / "measure.c" if args.mode == "native-kem"
            else REPO_ROOT / "bench" / "supercop" /
            ({"derived-poly": "poly_measure.c",
              "derived-itail": "itail_measure.c",
              "derived-itail-d0": "itail_d0_measure.c",
              "derived-itail-d0-m2": "itail_d0_m2_measure.c",
              "derived-f0-ma1": "f0_ma1_measure.c",
              "derived-f0-ma1-ma0": "f0_ma1_ma0_measure.c",
              "derived-f0-ma3": "f0_ma3_measure.c",
              "derived-f0-ma2-chunk": "f0_ma2_chunk_measure.c",
              "derived-f0-ma2": "f0_ma2_measure.c",
              "derived-f0-prod1": "f0_prod1_measure.c",
              "derived-f0-prod2": "f0_prod2_measure.c",
              "derived-f0-prod2-consumer": "f0_prod2_consumer_measure.c",
              "derived-gt9x16-prod3-price":
                  "gt9x16_prod3_aos_price_measure.c",
              "derived-gt9x16-prod3-consumer":
                  "gt9x16_prod3_aos_consumer_measure.c",
              "derived-gt9x16-prod3-hash-fanout":
                  "gt9x16_prod3_hash_fanout_measure.c",
              "derived-gt9x16-prod3-hash-h1-price":
                  "gt9x16_prod3_hash_h1_price_measure.c",
              "derived-gt9x16-prod3-qorder-price":
                  "gt9x16_prod3_qorder_price_measure.c",
              "derived-gt9x16-prod3-t0-beta-price":
                  "gt9x16_prod3_t0_beta_price_measure.c",
              "derived-gt9x16-prod3-encap-attribution-v2":
                  "gt9x16_prod3_encap_attribution_v2_measure.c",
              "derived-gt9x16-prod3-encap-tail-attribution-v1":
                  "gt9x16_prod3_encap_tail_attribution_v1_measure.c",
              "derived-encap-h-ingress-ma2-h3-price":
                  "encap_h_ingress_ma2_h3_price_measure.c"}[args.mode])
        ),
        "parameter": args.parameter,
        "result_data_source": str(data_files[0]),
    }
    (args.result_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(LOCK_PATH, args.result_dir / "supercop.lock")
    print(f"completed {metadata['benchmark_class']}: {args.result_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
