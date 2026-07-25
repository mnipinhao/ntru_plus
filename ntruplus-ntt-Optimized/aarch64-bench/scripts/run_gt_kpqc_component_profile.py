#!/usr/bin/env python3
"""Run comparable GT-production and KPQC-final kernel/KEM profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_VARIANTS = ("gt_production_default", "kpqc_final")
COMPONENT_MODES = ("kernel_components", "kem_components")
FULL_MODES = ("kem_keygen", "kem_enc", "kem_dec")
COUNTERS = {"cycles": "PERF", "instructions": "INSTRUCTIONS"}
PERCENTILES = (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99)
PROFILE_SYMBOLS = (
    "gt_experiment_poly_ntt_to_cq",
    "gt_experiment_keygen_baseinv_cq_to_cq_scaled_r",
    "gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r",
    "gt_keygen_blockmajor_to_bpq",
    "gt_keygen_baseinv_bpq_to_cq_scaled_r",
    "gt_keygen_baseinv_bpq_prepare",
    "gt_keygen_baseinv_hier_k8",
    "gt_keygen_baseinv_cq_finish",
    "gt_keygen_basemul_bpq_cq_to_cq_scaled_r",
    "gt_keygen_tobytes_cq",
    "gt_keygen_tobytes_bpq_p1",
    "poly_ntt",
    "gt_ntt32_batch8_to_blockmajor",
    "poly_invntt",
    "poly_invntt_from_rminus1",
    "poly_basemul",
    "poly_basemul_rminus1",
    "poly_basemul_add",
    "poly_basemul_add32",
    "poly_basemul_scaled_r_input",
    "poly_basemul_add_encap_direct32_q31_tobytes_contract",
    "gt_decap_verify_to_bytes",
    "gt_decap_verify_pointwise",
    "poly_baseinv",
    "poly_baseinv_1",
    "poly_baseinv_gt_batch",
    "poly_baseinv_gt_batch_scaled_r",
    "poly_baseinv_scaled_r",
    "baseinv_batch_finish24_n1_asm",
    "gt_fqinv15_asm",
    "poly_ntt_mul3",
    "poly_ntt_mul3_add1",
    "poly_tobytes",
    "poly_frombytes",
    "poly_tobytes_gt_canonical",
    "poly_frombytes_gt_canonical",
    "poly_tobytes_gt_canonical_p1",
    "poly_frombytes_gt_canonical_u1",
)


def run(command: list[str], cwd: Path) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def collect_git_environment(root: Path) -> dict[str, Any]:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if head.returncode != 0:
        return {
            "git_head": "unavailable (rsync mirror)",
            "git_dirty": None,
        }

    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "git_head": head.stdout.strip(),
        "git_dirty": bool(status.stdout.strip()),
    }


def parse_distribution(segment: str, counter: str) -> dict[str, Any]:
    median_match = re.search(rf"\s{re.escape(counter)} = (\d+)$", segment, re.M)
    percentile_match = re.search(r"percentiles:\s+([0-9 ]+)$", segment, re.M)
    if median_match is None or percentile_match is None:
        raise ValueError(f"unable to parse {counter} distribution")
    values = [int(value) for value in percentile_match.group(1).split()]
    if len(values) != len(PERCENTILES):
        raise ValueError(f"expected {len(PERCENTILES)} percentiles, got {len(values)}")
    percentiles = dict(zip((str(value) for value in PERCENTILES), values))
    return {
        "median": int(median_match.group(1)),
        "percentiles": percentiles,
        "p10": percentiles["10"],
        "p50": percentiles["50"],
        "p90": percentiles["90"],
    }


def parse_components(output: str, counter: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for segment in output.split("component_group = ")[1:]:
        group = segment.splitlines()[0].strip()
        kind_match = re.search(r"^component_kind = (\S+)$", segment, re.M)
        count_match = re.search(r"^component_count = (\d+)$", segment, re.M)
        name_match = re.search(r"^bench_name = (\S+)$", segment, re.M)
        if kind_match is None or count_match is None or name_match is None:
            raise ValueError(f"incomplete component metadata for group {group}")
        name = name_match.group(1)
        result[name] = {
            "group": group,
            "kind": kind_match.group(1),
            "count": int(count_match.group(1)),
            **parse_distribution(segment, counter),
        }
    if not result:
        raise ValueError("no component rows found")
    return result


def parse_full(output: str, counter: str) -> dict[str, Any]:
    return parse_distribution(output, counter)


def binary_metadata(binary: Path, root: Path) -> dict[str, Any]:
    size_fields = run(["size", str(binary)], root).splitlines()[-1].split()
    symbols: dict[str, dict[str, int]] = {}
    raw_symbols: list[tuple[int, int | None, str, str]] = []
    for line in run(["nm", "-n", "-S", "--defined-only", str(binary)], root).splitlines():
        fields = line.split()
        if len(fields) == 4:
            address_text, size_text, symbol_type, symbol_name = fields
            explicit_size: int | None = int(size_text, 16)
        elif len(fields) == 3:
            address_text, symbol_type, symbol_name = fields
            explicit_size = None
        else:
            continue
        if symbol_type.lower() != "t":
            continue
        raw_symbols.append((int(address_text, 16), explicit_size,
                            symbol_type, symbol_name))

    distinct_addresses = sorted({entry[0] for entry in raw_symbols})
    next_address = {
        address: distinct_addresses[index + 1]
        for index, address in enumerate(distinct_addresses[:-1])
    }
    for address, explicit_size, _symbol_type, symbol_name in raw_symbols:
        name = symbol_name.lstrip("_")
        if name not in PROFILE_SYMBOLS or name in symbols:
            continue
        symbol_size = explicit_size
        if not symbol_size:
            symbol_size = next_address.get(address, address) - address
        symbols[name] = {
            "address": address,
            "size": symbol_size,
            "address_mod32": address % 32,
            "address_mod64": address % 64,
        }
    return {
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "text": int(size_fields[0]),
        "data": int(size_fields[1]),
        "bss": int(size_fields[2]),
        "total": int(size_fields[3]),
        "symbols": symbols,
    }


def percent_delta(value: int, baseline: int) -> float:
    return 100.0 * (value - baseline) / baseline


def fmt_int(value: int | None) -> str:
    return "n/a" if value is None else str(value)


def render_full_table(report: dict[str, Any]) -> list[str]:
    rows = report["full"]
    lines = [
        "## Full KEM",
        "",
        "| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for mode in FULL_MODES:
        kpqc_cycles = rows["cycles"][mode]["kpqc_final"]["p50"]
        gt_cycles = rows["cycles"][mode]["gt_production_default"]["p50"]
        kpqc_instr = rows.get("instructions", {}).get(mode, {}).get("kpqc_final", {}).get("p50")
        gt_instr = rows.get("instructions", {}).get(mode, {}).get("gt_production_default", {}).get("p50")
        lines.append(
            f"| {mode} | {rows['cycles'][mode]['kpqc_final']['p10']}/{kpqc_cycles}/"
            f"{rows['cycles'][mode]['kpqc_final']['p90']} | "
            f"{rows['cycles'][mode]['gt_production_default']['p10']}/{gt_cycles}/"
            f"{rows['cycles'][mode]['gt_production_default']['p90']} | "
            f"{percent_delta(gt_cycles, kpqc_cycles):+.2f}% | "
            f"{fmt_int(kpqc_instr)} | {fmt_int(gt_instr)} |"
        )
    return lines


def render_candidate_full_table(report: dict[str, Any]) -> list[str]:
    cycle_rows = report["full"]["cycles"]
    instruction_rows = report["full"].get("instructions", {})
    variants = [
        variant for variant in report["binaries"]
        if variant not in {"gt_production_default", "kpqc_final"}
    ]
    if not variants:
        return []

    lines = [
        "## Optional Candidate Variants",
        "",
        "These variants were linked and measured in the same profile run but "
        "remain separate from the production default.",
        "",
        "| Operation | Candidate | Candidate cycles | Delta vs GT production | "
        "Delta vs KPQC | Candidate instr |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for mode in FULL_MODES:
        kpqc = cycle_rows[mode]["kpqc_final"]
        production = cycle_rows[mode]["gt_production_default"]
        for variant in variants:
            candidate = cycle_rows[mode][variant]
            candidate_i = instruction_rows.get(mode, {}).get(variant, {}).get("p50")
            lines.append(
                f"| {mode} | {variant} | {candidate['p50']} | "
                f"{candidate['p50'] - production['p50']:+d} "
                f"({percent_delta(candidate['p50'], production['p50']):+.2f}%) | "
                f"{candidate['p50'] - kpqc['p50']:+d} "
                f"({percent_delta(candidate['p50'], kpqc['p50']):+.2f}%) | "
                f"{fmt_int(candidate_i)} |"
            )
    return lines


def render_primitive_table(report: dict[str, Any]) -> list[str]:
    rows = report["components"]
    cycle_rows = rows["cycles"]["kernel_components"]
    instruction_rows = rows.get("instructions", {}).get("kernel_components", {})
    names = list(cycle_rows["kpqc_final"])
    lines = [
        "## Generic/Public Primitive Diagnostics",
        "",
        "These rows compare isolated public/generic kernels. They are API and algorithm "
        "diagnostics, not a list of the specialized kernels selected by the production KEM. "
        "In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and "
        "`baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.",
        "Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, "
        "not byte-identical intermediate arrays.",
        "The primitive transform/pipeline rows rotate over `NITERATIONS` input/output "
        "polynomials; they intentionally expose the larger working-set behavior.",
        "`*_internal_layout` serialization rows are diagnostics. For GT they omit the "
        "canonical wire permutation; their delta to `*_canonical` isolates boundary cost.",
        "",
        "| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in names:
        kpqc = cycle_rows["kpqc_final"][name]
        gt = cycle_rows["gt_production_default"][name]
        kpqc_i = instruction_rows.get("kpqc_final", {}).get(name, {}).get("p50")
        gt_i = instruction_rows.get("gt_production_default", {}).get(name, {}).get("p50")
        kpqc_cpi = "n/a" if not kpqc_i else f"{kpqc['p50'] / kpqc_i:.3f}"
        gt_cpi = "n/a" if not gt_i else f"{gt['p50'] / gt_i:.3f}"
        lines.append(
            f"| {kpqc['group']} | {name} | {kpqc['p50']} | {gt['p50']} | "
            f"{percent_delta(gt['p50'], kpqc['p50']):+.2f}% | "
            f"{fmt_int(kpqc_i)} | {fmt_int(gt_i)} | {kpqc_cpi} | {gt_cpi} |"
        )
    return lines


def render_kem_components(report: dict[str, Any]) -> list[str]:
    rows = report["components"]
    cycle_rows = rows["cycles"]["kem_components"]
    instruction_rows = rows.get("instructions", {}).get("kem_components", {})
    names = list(cycle_rows["kpqc_final"])
    lines = [
        "## Actual Production KEM-Path Components",
        "",
        "These rows follow the same production macros as the full-KEM binaries. The GT "
        "configuration in this report selects the production Good-Thomas forward NTT, the keygen-only "
        "BPQ/CQ backend with hierarchical K=8/fqinv15 inversion, direct-Q31 encapsulation, "
        "the rminus1 basemul/InvNTT decapsulation pair, and the canonical pointwise verify backend. "
        "Default-off experiments such as the compact serialization candidate are not "
        "included until promoted.",
        "`path` rows are non-overlapping call-graph components. `combined` rows are "
        "boundary diagnostics and are excluded from weighted subtotals.",
        "These rows use fixed, deterministic buffers reconstructed from a valid KEM "
        "key/ciphertext and satisfy each GT representation/range contract.",
        "GT keygen explicitly forms 3F+1/3G, calls the shared production poly_ntt, "
        "then converts the generic GT block-major result to BPQ. It converts the "
        "operand being inverted to CQ during baseinv prepare, performs "
        "hierarchical K=8 batch inversion with `gt_fqinv15_asm`, and keeps the result "
        "in scaled-R CQ layout for the mixed BPQ x CQ basemul. Its baseinv and basemul "
        "rows must therefore be interpreted together, not as independent generic-API "
        "drop-in kernels.",
        "The isolated `inverse_ntt_generic` primitive calls the public generic "
        "`poly_invntt`. The production decapsulation row "
        "`dec_first_invntt_actual` instead calls the paired "
        "`poly_invntt_from_rminus1` backend when the GT production flag is active.",
        "The decapsulation verify path is compared as one logical "
        "`dec_verify_product_to_bytes_actual` row: GT calls the production fused "
        "canonical backend, while KPQC performs canonical `hinv` unpack, normal "
        "basemul, and canonical pack. Both sides therefore start from serialized "
        "`hinv` bytes and end at serialized product bytes. "
        "The separate generic basemul and pack rows are diagnostics and are not "
        "included in the path subtotal.",
    ]
    for group in ("KEYGEN", "ENCAP", "DECAP"):
        lines.extend(
            [
                "",
                f"### {group.title()}",
                "",
                "| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        kpqc_subtotal = 0
        gt_subtotal = 0
        for name in names:
            kpqc = cycle_rows["kpqc_final"][name]
            if kpqc["group"] != group:
                continue
            gt = cycle_rows["gt_production_default"][name]
            count = kpqc["count"]
            weighted_delta = (gt["p50"] - kpqc["p50"]) * count
            if name in {"keygen_baseinv_actual", "keygen_basemul_actual"}:
                weighted_delta_text = "paired only"
            else:
                weighted_delta_text = f"{weighted_delta:+d}"
            kpqc_i = instruction_rows.get("kpqc_final", {}).get(name, {}).get("p50")
            gt_i = instruction_rows.get("gt_production_default", {}).get(name, {}).get("p50")
            lines.append(
                f"| {kpqc['kind']} | {name} | {count} | {kpqc['p50']} | {gt['p50']} | "
                f"{percent_delta(gt['p50'], kpqc['p50']):+.2f}% | "
                f"{weighted_delta_text} | "
                f"{fmt_int(kpqc_i)} | {fmt_int(gt_i)} |"
            )
            if kpqc["kind"] == "path":
                kpqc_subtotal += kpqc["p50"] * count
                gt_subtotal += gt["p50"] * count
        lines.append(
            f"| **path subtotal** | | | **{kpqc_subtotal}** | **{gt_subtotal}** | "
            f"**{percent_delta(gt_subtotal, kpqc_subtotal):+.2f}%** | "
            f"**{gt_subtotal - kpqc_subtotal:+d}** | | |"
        )
    return lines


def render_candidate_components(report: dict[str, Any]) -> list[str]:
    component_rows = report["components"]
    candidates = [
        variant for variant in report["binaries"]
        if variant not in {"gt_production_default", "kpqc_final"}
    ]
    if not candidates:
        return []

    lines = [
        "## Optional Candidate Component Deltas",
        "",
        "These tables use the same fixtures and measured boundaries as the two "
        "baseline component tables. Candidate rows are actual candidate-macro "
        "paths, not generic substitutes.",
    ]
    for mode, title in (
        ("kernel_components", "Generic/Public Primitive Diagnostics"),
        ("kem_components", "Actual KEM-Path Components"),
    ):
        cycle_rows = component_rows["cycles"][mode]
        instruction_rows = component_rows.get("instructions", {}).get(mode, {})
        names = list(cycle_rows["kpqc_final"])
        for candidate in candidates:
            lines.extend(
                [
                    "",
                    f"### {title}: `{candidate}`",
                    "",
                    "| Group | Kind | Component | Count | KPQC cycles | GT production cycles | Candidate cycles | Candidate vs GT | Candidate vs KPQC | KPQC instr | GT instr | Candidate instr |",
                    "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
                ]
            )
            for name in names:
                kpqc = cycle_rows["kpqc_final"][name]
                production = cycle_rows["gt_production_default"][name]
                selected = cycle_rows[candidate][name]
                kpqc_i = instruction_rows.get("kpqc_final", {}).get(name, {}).get("p50")
                production_i = instruction_rows.get("gt_production_default", {}).get(name, {}).get("p50")
                selected_i = instruction_rows.get(candidate, {}).get(name, {}).get("p50")
                lines.append(
                    f"| {selected['group']} | {selected['kind']} | {name} | "
                    f"{selected['count']} | {kpqc['p50']} | {production['p50']} | "
                    f"{selected['p50']} | "
                    f"{selected['p50'] - production['p50']:+d} "
                    f"({percent_delta(selected['p50'], production['p50']):+.2f}%) | "
                    f"{selected['p50'] - kpqc['p50']:+d} "
                    f"({percent_delta(selected['p50'], kpqc['p50']):+.2f}%) | "
                    f"{fmt_int(kpqc_i)} | {fmt_int(production_i)} | "
                    f"{fmt_int(selected_i)} |"
                )
    return lines


def render_opportunity_table(report: dict[str, Any]) -> list[str]:
    cycle_rows = report["components"]["cycles"]["kem_components"]
    candidates = []
    paired_keygen_names = {
        "keygen_baseinv_actual",
        "keygen_basemul_actual",
    }
    for name, kpqc in cycle_rows["kpqc_final"].items():
        if kpqc["kind"] != "path":
            continue
        if "hash" in name or "shake" in name:
            continue
        if name in paired_keygen_names:
            continue
        gt = cycle_rows["gt_production_default"][name]
        weighted_delta = (gt["p50"] - kpqc["p50"]) * kpqc["count"]
        candidates.append((weighted_delta, name, kpqc, gt))

    pair_name = "keygen_baseinv_plus_basemul_contract"
    if pair_name in cycle_rows["kpqc_final"]:
        kpqc = cycle_rows["kpqc_final"][pair_name]
        gt = cycle_rows["gt_production_default"][pair_name]
        weighted_delta = (gt["p50"] - kpqc["p50"]) * kpqc["count"]
        candidates.append((weighted_delta, pair_name, kpqc, gt))
    candidates.sort(reverse=True, key=lambda item: item[0])

    lines = [
        "## Measured Optimization Budget",
        "",
        "Positive rows are places where GT currently spends more cycles than KPQC. "
        "The weighted delta is the first-order full-KEM budget if that row were only "
        "brought to KPQC parity; it is not a guaranteed end-to-end saving.",
        "The GT scaled baseinv and its matching keygen basemul are represented by "
        "their combined contract row; their individual factor-shifted rows are not "
        "counted as separate optimization budgets.",
        "Hash/SHAKE rows remain visible in the component tables but are excluded here.",
        "",
        "| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |",
        "|---|---|---:|---:|---:|---:|",
    ]
    emitted = False
    for weighted_delta, name, kpqc, gt in candidates:
        if weighted_delta <= 0:
            continue
        emitted = True
        lines.append(
            f"| {kpqc['group']} | {name} | {kpqc['count']} | {kpqc['p50']} | "
            f"{gt['p50']} | +{weighted_delta} |"
        )
    if not emitted:
        lines.append("| - | no GT-slower path rows | - | - | - | 0 |")
    return lines


def render_metadata(report: dict[str, Any]) -> list[str]:
    lines = [
        "## Binary Metadata",
        "",
        "Metadata is recorded from each mode's cycle-counter binary.",
        "",
        "| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |",
        "|---|---|---|---:|---|---:|---:|",
    ]
    for variant, modes in report["binaries"].items():
        for mode, metadata in modes.items():
            first = True
            for name, symbol in metadata["symbols"].items():
                lines.append(
                    f"| {variant if first else ''} | {mode if first else ''} | "
                    f"{metadata['sha256'][:12] if first else ''} | "
                    f"{metadata['text'] if first else ''} | {name} | "
                    f"{symbol['size']} | "
                    f"{symbol['address_mod32']}/{symbol['address_mod64']} |"
                )
                first = False
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    settings = report["settings"]
    environment = report["environment"]
    if "instructions" in report["full"]:
        counter_note = (
            "Cycles and retired instructions are collected in separate counter "
            "builds/runs. Derived CPI is therefore diagnostic rather than a "
            "same-group atomic PMU sample."
        )
    else:
        counter_note = (
            "This run collected cycles only; instruction and CPI columns are "
            "reported as n/a."
        )
    lines = [
        "# GT Production vs KPQC Final Detailed Profile",
        "",
        "Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.",
        f"Each row is p50 of {settings['ntests']} samples x "
        f"{settings['niterations']} calls; warmup={settings['nwarmup']}.",
        "All variants use uniform section GC."
        if settings["uniform_gc"]
        else "Variants use their current Makefile section-GC policy.",
        "All binaries run deterministic KEM setup and correctness checks before PMU; "
        "the component mode also runs a reconstructed-ciphertext decapsulation postflight. "
        "Full KEM totals are decisive; component subtotals omit copies/call overhead and "
        "are used for hotspot attribution only.",
        counter_note,
        "",
        "## Measurement Environment",
        "",
        f"- Git HEAD: `{environment['git_head']}`"
        + (
            " (not a Git worktree)"
            if environment["git_dirty"] is None
            else f" ({'dirty' if environment['git_dirty'] else 'clean'} worktree)"
        ),
        f"- Compiler: `{environment['compiler']}`",
        f"- Host: `{environment['uname']}`",
        "",
        *render_full_table(report),
        "",
        *render_candidate_full_table(report),
        "",
        *render_primitive_table(report),
        "",
        *render_kem_components(report),
        "",
        *render_candidate_components(report),
        "",
        *render_opportunity_table(report),
        "",
        *render_metadata(report),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--core", type=int, default=3)
    parser.add_argument("--ntests", type=int, default=31)
    parser.add_argument("--niterations", type=int, default=2000)
    parser.add_argument("--nwarmup", type=int, default=100)
    parser.add_argument("--cycles-only", action="store_true")
    parser.add_argument("--keep-binaries", action="store_true")
    parser.add_argument("--uniform-gc", action="store_true")
    parser.add_argument("--variants", nargs="+", default=list(DEFAULT_VARIANTS))
    args = parser.parse_args()
    variants = tuple(args.variants)
    if "gt_production_default" not in variants or "kpqc_final" not in variants:
        parser.error("--variants must include gt_production_default and kpqc_final")

    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    environment = {
        **collect_git_environment(root),
        "compiler": run(["cc", "--version"], root).splitlines()[0],
        "uname": run(["uname", "-a"], root).strip(),
    }
    bin_dir = output / "bin"
    raw_dir = output / "raw"
    bin_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    counters = {"cycles": COUNTERS["cycles"]} if args.cycles_only else COUNTERS
    components: dict[str, dict[str, dict[str, Any]]] = {}
    full: dict[str, dict[str, dict[str, Any]]] = {}
    binaries: dict[str, dict[str, Any]] = {}
    build_log: list[str] = []

    for counter_index, (counter, make_counter) in enumerate(counters.items()):
        components[counter] = {}
        full[counter] = {}
        for mode_index, mode in enumerate((*COMPONENT_MODES, *FULL_MODES)):
            built: dict[str, Path] = {}
            for variant in variants:
                binary = bin_dir / f"{variant}_{mode}_{counter}"
                command = [
                    "make", "-f", "Makefile.production", "-B", str(binary),
                    f"TARGET={binary}",
                    f"VARIANT={variant}", f"BENCH_MODE={mode}",
                    f"CYCLES={make_counter}", f"NTESTS={args.ntests}",
                    f"NITERATIONS={args.niterations}", f"NWARMUP={args.nwarmup}",
                ]
                if args.uniform_gc:
                    command.append(
                        "EXTRA_CFLAGS=-ffunction-sections -fdata-sections "
                        "-Wl,--gc-sections"
                    )
                build_log.append(f"$ {' '.join(command)}\n")
                build_log.append(run(command, root))
                built[variant] = binary
                if counter == "cycles":
                    binaries.setdefault(variant, {})[mode] = binary_metadata(
                        binary, root
                    )

            order = variants if (counter_index + mode_index) % 2 == 0 else tuple(reversed(variants))
            for variant in order:
                raw = run(["taskset", "-c", str(args.core), str(built[variant])], root)
                (raw_dir / f"{variant}_{mode}_{counter}.out").write_text(raw)
                if mode in COMPONENT_MODES:
                    components[counter].setdefault(mode, {})[variant] = parse_components(raw, counter)
                else:
                    full[counter].setdefault(mode, {})[variant] = parse_full(raw, counter)

    report = {
        "environment": environment,
        "settings": {
            "host": "Pi5 Cortex-A76",
            "core": args.core,
            "ntests": args.ntests,
            "niterations": args.niterations,
            "nwarmup": args.nwarmup,
            "hash_path": "NO_CE",
            "uniform_gc": args.uniform_gc,
            "deterministic_inputs": True,
            "primitive_measurement": "rotating-buffer repeated call",
            "kem_path_component_measurement": "fixed contract-valid buffer repeated call",
        },
        "components": components,
        "full": full,
        "binaries": binaries,
    }
    (output / "build.log").write_text("".join(build_log))
    (output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (output / "summary.md").write_text(render_markdown(report))
    if not args.keep_binaries:
        shutil.rmtree(bin_dir)
    print(output / "summary.json")
    print(output / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
