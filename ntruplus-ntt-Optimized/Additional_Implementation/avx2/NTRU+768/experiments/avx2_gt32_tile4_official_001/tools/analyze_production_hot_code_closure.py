#!/usr/bin/env python3
"""Audit the unpruned/pruned CleanGT production image closure."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


HOT_PREFIXES = ("gt32_", "gt_")
RETENTION_REASON = {
    "gt32_global_inverse_core_asm": "decap inverse core",
    "gt32_p_j1_baseinv_direct_avx2": "keypair P-J1 BaseInv",
    "gt32_p_j1_batch_inverse_tree_asm": "keypair P-J1 batch inversion",
    "gt32_q24_decode3_soa_asm": "decap three-key GT-unpack wrapper",
    "gt32_q24_decode_soa_asm": "encap/decap GT-unpack entry",
    "gt32_q24_decode_soa_body_cage": "shared production GT-unpack body",
    "gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm": "keypair SP1 GT-pack",
    "gt32_q24_encode_soa_asm": "decap centered GT-pack",
    "gt32_q24_encode_soa_encap_hr_h1_asm": "encap high-range H1 GT-pack entry",
    "gt32_q24_encode_soa_lazy10788_asm": "encap/decap lazy GT-pack body",
    "gt32_tile4_attr_forward_all_baseinv_p_l3_asm": "keypair P Forward",
    "gt32_tile4_attr_forward_all_bm_soa_asm": "encap/decap M Forward",
    "gt32_tile4_basemul_general_soa_soa_to_soa_asm": "encap and decap general BaseMul",
    "gt32_tile4_basemul_scale_soa_soa_to_m_private_asm": "decap first scale BaseMul",
    "gt32_tile4_frontend_wide_raw_asm": "shared GT Forward frontend",
    "gt32_tile4_inverse_tail_t9_isolated_private_asm": "decap inverse T9 tail",
    "gt32_tile4_soa_equal_modq_12699_asm": "decap native-domain final verification",
    "gt_basemul_native_f0_j1_e0_asm_avx2": "keypair F0 x J1 native BaseMul",
}


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def sections(elf: Path) -> dict[str, int]:
    answer: dict[str, int] = {}
    for line in command("readelf", "-S", "--wide", str(elf)).splitlines():
        match = re.search(r"\]\s+(\.text|\.rodata)\s+\S+\s+\S+\s+\S+\s+([0-9a-fA-F]+)", line)
        if match:
            answer[match.group(1)] = int(match.group(2), 16)
    return answer


def symbols(elf: Path) -> dict[str, dict[str, int | str]]:
    answer: dict[str, dict[str, int | str]] = {}
    for line in command("nm", "-S", "--size-sort", str(elf)).splitlines():
        fields = line.split()
        if len(fields) != 4:
            continue
        address, size, kind, name = fields
        if kind.lower() not in ("t", "r"):
            continue
        answer[name] = {"address": int(address, 16), "size": int(size, 16), "kind": kind}
    return answer


def normalized_disassembly(elf: Path, symbol: str) -> list[str]:
    output = command("objdump", "-d", "--no-show-raw-insn", f"--disassemble={symbol}", str(elf))
    instructions: list[str] = []
    for line in output.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+(.*)$", line)
        if not match:
            continue
        instruction = match.group(1).split("#", 1)[0].strip()
        instruction = re.sub(r"[-+]?0x[0-9a-f]+\(%rip\)", "<RIP>(%rip)", instruction)
        instruction = re.sub(r"\b[0-9a-f]+\s+<([^>]+)>", r"<\1>", instruction)
        # Local branch labels move with the function.  Keep the opcode and
        # symbolic displacement class, but not the linked virtual address.
        instruction = re.sub(r"\b[0-9a-f]+$", "<LOCAL>", instruction)
        instructions.append(instruction)
    return instructions


def sha256_lines(lines: list[str]) -> str:
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("g0", type=Path)
    parser.add_argument("gc", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    g0_sections = sections(args.g0)
    gc_sections = sections(args.gc)
    g0_symbols = symbols(args.g0)
    gc_symbols = symbols(args.gc)

    g0_gt = {name for name, item in g0_symbols.items() if item["kind"].lower() == "t" and name.startswith(HOT_PREFIXES)}
    gc_gt = {name for name, item in gc_symbols.items() if item["kind"].lower() == "t" and name.startswith(HOT_PREFIXES)}
    common = sorted(g0_gt & gc_gt)
    disassembly: dict[str, object] = {}
    all_equal = True
    for name in common:
        before = normalized_disassembly(args.g0, name)
        after = normalized_disassembly(args.gc, name)
        equal = before == after
        all_equal &= equal
        disassembly[name] = {
            "equal": equal,
            "instruction_count_g0": len(before),
            "instruction_count_gc": len(after),
            "normalized_sha256_g0": sha256_lines(before),
            "normalized_sha256_gc": sha256_lines(after),
        }

    removed_rodata = sorted(
        ({name for name, item in g0_symbols.items() if item["kind"].lower() == "r"}
         - {name for name, item in gc_symbols.items() if item["kind"].lower() == "r"})
    )
    report = {
        "schema": "gt32-production-hot-code-closure-v1",
        "images": {"g0": str(args.g0), "gc": str(args.gc)},
        "footprint": {
            "g0": g0_sections,
            "gc": gc_sections,
            "delta_gc_minus_g0": {key: gc_sections[key] - g0_sections[key] for key in (".text", ".rodata")},
            "text_reduction_percent": 100.0 * (g0_sections[".text"] - gc_sections[".text"]) / g0_sections[".text"],
            "rodata_reduction_percent": 100.0 * (g0_sections[".rodata"] - gc_sections[".rodata"]) / g0_sections[".rodata"],
        },
        "gt_text_symbols": {
            "g0_count": len(g0_gt),
            "gc_count": len(gc_gt),
            "retained": common,
            "retention_reason": {name: RETENTION_REASON.get(name, "unclassified") for name in common},
            "removed": sorted(g0_gt - gc_gt),
            "removed_named_bytes": sum(int(g0_symbols[name]["size"]) for name in g0_gt - gc_gt),
        },
        "rodata": {
            "removed_named_symbols": removed_rodata,
            "note": "Linked rodata remains mostly shared/monolithic; section-size delta is authoritative.",
        },
        "hot_instruction_equivalence": {
            "all_common_gt_symbols_equal": all_equal,
            "symbols": disassembly,
        },
        "acceptance": {
            "physical_text_closure": gc_sections[".text"] < g0_sections[".text"],
            "hot_instruction_sequence_unchanged": all_equal,
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
