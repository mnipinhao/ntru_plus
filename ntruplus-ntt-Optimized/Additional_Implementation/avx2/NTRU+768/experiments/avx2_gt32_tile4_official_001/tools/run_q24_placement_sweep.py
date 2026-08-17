#!/usr/bin/env python3
"""Run the fixed-size Q24 private-SoA body placement sweep."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_q24_decap import aggregate, run  # noqa: E402


OFFSETS = (0, 32, 64, 96, 128, 160, 192, 224)
BODY_SYMBOL = "gt32_q24_decode_soa_body_cage"
FIXED_SYMBOLS = (
    "crypto_kem_dec_gt32_soa_domain_candidate",
    "crypto_kem_dec_gt32_q24_decode_candidate",
    "gt32_q24_decode3_soa_asm",
    "gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm",
    "gt32_tile4_inverse_all_pair_asm",
    "gt32_tile4_inverse_tail_t9_isolated_private_asm",
)


def symbols(binary: Path) -> dict[str, dict[str, int]]:
    process = subprocess.run(
        ["nm", "-nS", "--defined-only", str(binary)],
        check=True, text=True, capture_output=True)
    result = {}
    for line in process.stdout.splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        address, size, _, name = fields
        if name == BODY_SYMBOL or name in FIXED_SYMBOLS:
            result[name] = {
                "address": int(address, 16),
                "size": int(size, 16),
            }
    missing = (set(FIXED_SYMBOLS) | {BODY_SYMBOL}) - result.keys()
    if missing:
        raise RuntimeError(f"{binary}: missing symbols {sorted(missing)}")
    return result


def loaded_sections(binary: Path) -> dict[str, dict[str, int]]:
    process = subprocess.run(
        ["size", "-A", str(binary)], check=True, text=True,
        capture_output=True)
    result = {}
    for line in process.stdout.splitlines():
        fields = line.split()
        if len(fields) != 3 or fields[0] not in (
                ".text", ".rodata", ".data", ".bss"):
            continue
        result[fields[0]] = {
            "size": int(fields[1]),
            "address": int(fields[2]),
        }
    if set(result) != {".text", ".rodata", ".data", ".bss"}:
        raise RuntimeError(f"{binary}: missing loaded section in size output")
    return result


def verify_cages(build_dir: Path) -> dict[str, object]:
    placements = {}
    for placement, prefix in (
            ("normal", "bench_q24_cage_"),
            ("reversed", "bench_q24_cage_reversed_")):
        variants = {}
        fixed_reference = None
        loaded_reference = None
        body_base = None
        for offset in OFFSETS:
            binary = build_dir / f"{prefix}{offset}"
            current = symbols(binary)
            current_fixed = {name: current[name] for name in FIXED_SYMBOLS}
            if fixed_reference is None:
                fixed_reference = current_fixed
                loaded_reference = loaded_sections(binary)
                body_base = current[BODY_SYMBOL]["address"]
            if current_fixed != fixed_reference:
                raise RuntimeError(
                    f"{placement} offset {offset}: non-Q24 symbol moved")
            current_loaded = loaded_sections(binary)
            if current_loaded != loaded_reference:
                raise RuntimeError(
                    f"{placement} offset {offset}: loaded section changed")
            body = current[BODY_SYMBOL]
            if body["address"] != body_base + offset:
                raise RuntimeError(
                    f"{placement} offset {offset}: body did not move exactly")
            if body["address"] % 4096 != offset:
                raise RuntimeError(
                    f"{placement} offset {offset}: wrong page offset")
            variants[str(offset)] = {
                "binary": str(binary),
                "ELF_file_size": binary.stat().st_size,
                "loaded_sections": current_loaded,
                "body": body,
                "fixed_symbols": current_fixed,
            }
        placements[placement] = {
            "body_base": body_base,
            "loaded_sections": loaded_reference,
            "variants": variants,
        }
    return {
        "cage_size": 4096,
        "body_size": placements["normal"]["variants"]["0"]["body"]["size"],
        "body_moves_exactly_by_requested_offset": True,
        "fixed_symbols_and_loaded_sections_unchanged": True,
        "ELF_debug_section_size_is_not_an_invariant": True,
        "placements": placements,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-dir", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cage_audit = verify_cages(args.build_dir)
    collected = {
        str(offset): {"normal": [], "reversed": []}
        for offset in OFFSETS
    }
    for launch in range(args.launches):
        offset_order = OFFSETS if launch % 2 == 0 else tuple(reversed(OFFSETS))
        placement_order = (("normal", "bench_q24_cage_"),
                           ("reversed", "bench_q24_cage_reversed_"))
        if launch % 2 != 0:
            placement_order = tuple(reversed(placement_order))
        for offset in offset_order:
            for placement, prefix in placement_order:
                binary = args.build_dir / f"{prefix}{offset}"
                collected[str(offset)][placement].append(
                    run(binary, args.iterations))

    variants = {}
    stable_offsets = []
    for offset in OFFSETS:
        offset_result = {"placements": {}}
        stable = True
        for placement in ("normal", "reversed"):
            launches = collected[str(offset)][placement]
            summary = aggregate(launches)
            launch_medians = [
                launch["q24_minus_control_tsc"]["median"]
                for launch in launches
            ]
            launch_wins = [launch["q24_wins_vs_control"]
                           for launch in launches]
            placement_stable = all(
                delta < 0 and wins >= 18
                for delta, wins in zip(launch_medians, launch_wins))
            stable = stable and placement_stable
            offset_result["placements"][placement] = {
                "launches": launches,
                "aggregate": summary,
                "launch_median_delta_tsc": launch_medians,
                "launch_wins_vs_control": launch_wins,
                "stable": placement_stable,
            }
        offset_result["stable_both_placements"] = stable
        if stable:
            stable_offsets.append(offset)
        variants[str(offset)] = offset_result

    result = {
        "schema": "ntruplus768-gt32-q24-fixed-cage-placement-v1",
        "experiment": "GT32-Q24-FIXED-CAGE-PLACEMENT-001",
        "benchmark": {
            "iterations": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "cpu": 1,
            "sample_order": "paired-ABC-CBA",
            "variant_order": "forward-reverse-alternating",
            "unit": "TSC ticks per decapsulation",
        },
        "correctness": "byte-exact-valid-decap-marker-required-every-launch",
        "cage_audit": cage_audit,
        "continuation_gate": {
            "minimum_wins_every_launch": 18,
            "normal_and_reversed_required": True,
            "stable_offsets": stable_offsets,
            "passed": bool(stable_offsets),
        },
        "variants": variants,
        "decision": ("stable-placement-found" if stable_offsets else
                     "no-stable-placement-compact-code-shape-next"),
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    print("offset  normal median/wins       reversed median/wins     stable")
    for offset in OFFSETS:
        variant = variants[str(offset)]
        columns = []
        for placement in ("normal", "reversed"):
            data = variant["placements"][placement]
            delta = data["aggregate"]["q24_minus_control_tsc"]["median"]
            wins = "/".join(str(value)
                            for value in data["launch_wins_vs_control"])
            columns.append(f"{delta:8.3f} [{wins}]")
        print(f"{offset:>6}  {columns[0]:<27} {columns[1]:<27} "
              f"{variant['stable_both_placements']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
