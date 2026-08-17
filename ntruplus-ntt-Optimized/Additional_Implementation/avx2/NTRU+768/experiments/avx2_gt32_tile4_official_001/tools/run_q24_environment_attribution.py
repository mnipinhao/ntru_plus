#!/usr/bin/env python3
"""Attribute Q24 launch variance to PIE/ASLR and absolute code addresses."""

import argparse
import json
import platform
import statistics
import subprocess
from pathlib import Path

from run_q24_decap import aggregate, median_mad, run


def read_text(path: str) -> str | None:
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def cpu_ticks(cpu: int) -> tuple[int, int] | None:
    prefix = f"cpu{cpu} "
    try:
        for line in Path("/proc/stat").read_text().splitlines():
            if line.startswith(prefix):
                fields = [int(value) for value in line.split()[1:]]
                total = sum(fields)
                idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
                return total, total - idle
    except OSError:
        return None
    return None


def runtime_snapshot() -> dict:
    return {
        "sibling_cpu2_ticks": cpu_ticks(2),
        "cpu1_scaling_cur_khz": read_text(
            "/sys/devices/system/cpu/cpu1/cpufreq/scaling_cur_freq"),
    }


def runtime_delta(before: dict, after: dict) -> dict:
    before_ticks = before["sibling_cpu2_ticks"]
    after_ticks = after["sibling_cpu2_ticks"]
    result = {
        "cpu1_scaling_cur_khz_before": before["cpu1_scaling_cur_khz"],
        "cpu1_scaling_cur_khz_after": after["cpu1_scaling_cur_khz"],
    }
    if before_ticks is not None and after_ticks is not None:
        total = after_ticks[0] - before_ticks[0]
        active = after_ticks[1] - before_ticks[1]
        result.update({
            "sibling_cpu2_total_ticks": total,
            "sibling_cpu2_active_ticks": active,
            "sibling_cpu2_active_fraction": active / total if total else 0.0,
        })
    return result


def elf_type(binary: Path) -> str:
    output = subprocess.run(["readelf", "-h", str(binary)], check=True,
                            text=True, capture_output=True).stdout
    for line in output.splitlines():
        if "Type:" in line:
            return line.split("Type:", 1)[1].strip()
    raise RuntimeError(f"ELF type missing from {binary}")


def correlation_table(launches: list[dict[str, object]], symbol: str) -> dict:
    result = {}
    for bits in range(1, 7):
        mask = (1 << bits) - 1
        groups: dict[int, list[dict[str, object]]] = {}
        for launch in launches:
            address = launch["virtual_addresses"][symbol]
            key = (address >> 12) & mask
            groups.setdefault(key, []).append(launch)
        entries = {}
        for key, members in sorted(groups.items()):
            deltas = [member["q24_minus_control_tsc"]["median"]
                      for member in members]
            entries[str(key)] = {
                "launches": len(members),
                "median_delta_tsc": statistics.median(deltas),
                "good_launches": sum(member["good_launch"]
                                     for member in members),
            }
        result[f"page_number_mod_{1 << bits}"] = entries
    return result


def summarize_launches(launches: list[dict[str, object]]) -> dict:
    summary = aggregate(launches)
    launch_deltas = [launch["q24_minus_control_tsc"]["median"]
                     for launch in launches]
    launch_median, launch_mad = median_mad(launch_deltas)
    addresses = [launch["virtual_addresses"] for launch in launches]
    summary.update({
        "launch_median_delta_tsc": launch_median,
        "launch_delta_mad_tsc": launch_mad,
        "good_launches": sum(launch["good_launch"] for launch in launches),
        "launches": len(launches),
        "unique_text_load_biases": len({entry["text_load_bias"]
                                         for entry in addresses}),
        "unique_q24_body_addresses": len({entry["q24_body"]
                                            for entry in addresses}),
        "address_low_bits": [{
            "text_load_bias": entry["text_load_bias"],
            "q24_body": entry["q24_body"],
            "q24_mod_8k": entry["q24_body"] % 8192,
            "q24_mod_16k": entry["q24_body"] % 16384,
            "q24_mod_32k": entry["q24_body"] % 32768,
            "q24_mod_64k": entry["q24_body"] % 65536,
        } for entry in addresses],
        "q24_body_page_correlation": correlation_table(launches, "q24_body"),
        "q24_decode3_page_correlation": correlation_table(
            launches, "q24_decode3"),
    })
    return summary


def run_mode(name: str, binaries: dict[str, Path], prefix: list[str],
             iterations: int, launches: int) -> dict:
    placements = {}
    try:
        for placement, binary in binaries.items():
            records = []
            for launch_id in range(launches):
                before = runtime_snapshot()
                record = run(binary, iterations, prefix)
                after = runtime_snapshot()
                record["launch_id"] = launch_id + 1
                record["runtime"] = runtime_delta(before, after)
                record["good_launch"] = (
                    record["q24_wins_vs_control"] >= 18
                    and record["q24_minus_control_tsc"]["median"] < 0)
                records.append(record)
            placements[placement] = {
                "launches": records,
                "summary": summarize_launches(records),
            }
    except (subprocess.CalledProcessError, RuntimeError) as error:
        return {"status": "unavailable", "error": str(error)}
    return {
        "status": "measured",
        "command_prefix": prefix,
        "placements": placements,
    }


def combine_batches(batches: list[dict]) -> dict:
    result = {}
    for mode_name in batches[0]:
        if any(batch[mode_name]["status"] != "measured"
               for batch in batches):
            result[mode_name] = {
                "status": "unavailable-in-one-or-more-batches"}
            continue
        placements = {}
        for placement in ("normal", "reversed"):
            records = [launch for batch in batches
                       for launch in batch[mode_name]["placements"][
                           placement]["launches"]]
            placements[placement] = {
                "summary": summarize_launches(records),
                "good_launches_by_batch": [
                    batch[mode_name]["placements"][placement]["summary"][
                        "good_launches"] for batch in batches],
            }
        result[mode_name] = {"status": "measured", "placements": placements}
    return result


def system_context() -> dict:
    paths = {
        "randomize_va_space": "/proc/sys/kernel/randomize_va_space",
        "perf_event_paranoid": "/proc/sys/kernel/perf_event_paranoid",
        "cpu1_thread_siblings":
            "/sys/devices/system/cpu/cpu1/topology/thread_siblings_list",
        "cpu1_governor":
            "/sys/devices/system/cpu/cpu1/cpufreq/scaling_governor",
        "cpu1_scaling_min_khz":
            "/sys/devices/system/cpu/cpu1/cpufreq/scaling_min_freq",
        "cpu1_scaling_max_khz":
            "/sys/devices/system/cpu/cpu1/cpufreq/scaling_max_freq",
        "cpu1_cpuinfo_max_khz":
            "/sys/devices/system/cpu/cpu1/cpufreq/cpuinfo_max_freq",
        "cpu_core_pmu_type": "/sys/bus/event_source/devices/cpu_core/type",
    }
    return {
        "machine": platform.machine(),
        "kernel": platform.release(),
        **{name: read_text(path) for name, path in paths.items()},
        "aperf_mperf": {
            "availability": "not-supported-per-thread",
            "reason": "perf reports msr/aperf and msr/mperf require system-wide mode",
            "frequency_proxy": "region-scoped core-cycles/ref-cycles",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--nonpie-binary", type=Path, required=True)
    parser.add_argument("--nonpie-reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--batches", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    machine = platform.machine()
    pie = {"normal": args.binary, "reversed": args.reversed_binary}
    nonpie = {"normal": args.nonpie_binary,
              "reversed": args.nonpie_reversed_binary}
    batches = []
    for _ in range(args.batches):
        batches.append({
            "pie_aslr_on": run_mode(
                "pie_aslr_on", pie, [], args.iterations, args.launches),
            "pie_aslr_disabled": run_mode(
                "pie_aslr_disabled", pie, ["setarch", machine, "-R"],
                args.iterations, args.launches),
            "nonpie_fixed_address": run_mode(
                "nonpie_fixed_address", nonpie, [], args.iterations,
                args.launches),
        })
    combined = combine_batches(batches)
    all_correct = all(mode["status"] == "measured"
                      for batch in batches for mode in batch.values())
    fixed_stable = all(
        placement["summary"]["unique_q24_body_addresses"] == 1
        for batch in batches
        for mode_name in ("pie_aslr_disabled", "nonpie_fixed_address")
        for placement in batch[mode_name].get("placements", {}).values())
    fixed_reliably_good = all(
        good >= 6
        for mode_name in ("pie_aslr_disabled", "nonpie_fixed_address")
        for placement in combined[mode_name]["placements"].values()
        for good in placement["good_launches_by_batch"])
    result = {
        "schema": "ntruplus768-gt32-q24-launch-environment-v1",
        "experiment": "GT32-Q24-LAUNCH-ENVIRONMENT-001",
        "benchmark": {
            "iterations": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "independent_batches": args.batches,
            "total_launches_per_mode_placement": args.launches * args.batches,
            "cpu": 1,
            "order": "paired ABC/CBA",
            "unit": "TSC ticks per decapsulation",
            "serious_100k": False,
        },
        "system": system_context(),
        "binaries": {
            "pie_normal": {"path": str(args.binary),
                           "elf_type": elf_type(args.binary)},
            "pie_reversed": {"path": str(args.reversed_binary),
                             "elf_type": elf_type(args.reversed_binary)},
            "nonpie_normal": {"path": str(args.nonpie_binary),
                              "elf_type": elf_type(args.nonpie_binary)},
            "nonpie_reversed": {"path": str(args.nonpie_reversed_binary),
                                "elf_type": elf_type(
                                    args.nonpie_reversed_binary)},
        },
        "batches": batches,
        "combined": combined,
        "correctness": {
            "valid_byte_exact_every_launch": all_correct,
            "cpu_affinity_every_launch": 1,
            "fixed_address_controls_have_one_q24_va": fixed_stable,
            "fixed_address_is_sufficient_for_reliable_good_launches":
                fixed_reliably_good,
        },
        "decision": ("fixed-address-sufficient" if fixed_reliably_good else
                     "absolute-va-participates-but-is-not-sufficient"),
        "q24_assembly_modified": False,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for mode_name, mode in combined.items():
        print(mode_name)
        if mode["status"] != "measured":
            print(f"  unavailable: {mode['error']}")
            continue
        for placement, data in mode["placements"].items():
            summary = data["summary"]
            print(f"  {placement}: launch median delta="
                  f"{summary['launch_median_delta_tsc']:.3f} TSC, "
                  f"good={summary['good_launches']}/"
                  f"{args.launches * args.batches}, batches="
                  f"{data['good_launches_by_batch']}, "
                  f"unique-VA={summary['unique_q24_body_addresses']}")


if __name__ == "__main__":
    main()
