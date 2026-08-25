#!/usr/bin/env python3
"""Run native-KEM or SUPERCOP-derived primitive measurement in a campaign."""

from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-root", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--mode", choices=("native-kem", "derived-poly", "derived-itail",
                                           "derived-itail-d0", "derived-itail-d0-m2",
                                           "derived-f0-ma1", "derived-f0-ma1-ma0",
                                           "derived-f0-ma3"),
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
                     "derived-f0-ma3") and args.parameter != "1152":
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
                         "derived-f0-ma1-ma0", "derived-f0-ma3"):
            replacement_name = {
                "derived-poly": "poly_measure.c",
                "derived-itail": "itail_measure.c",
                "derived-itail-d0": "itail_d0_measure.c",
                "derived-itail-d0-m2": "itail_d0_m2_measure.c",
                "derived-f0-ma1": "f0_ma1_measure.c",
                "derived-f0-ma1-ma0": "f0_ma1_ma0_measure.c",
                "derived-f0-ma3": "f0_ma3_measure.c",
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
    else:
        required = ("f0_ma0_first_cycles", "f0_ma3_second_cycles",
                    "f0_ma3_first_cycles", "f0_ma0_second_cycles")
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
              "derived-f0-ma3": "f0_ma3_measure.c"}[args.mode])
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
