#!/usr/bin/env python3
"""Lower M2D packed24 ownership into a linked-H3 executable schedule."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import re
from pathlib import Path


YMM_REGISTERS = {f"ymm{index}" for index in range(16)}
GPR = re.compile(
    r"\b(?:r(?:ax|bx|cx|dx|si|di|bp|sp)|"
    r"e(?:ax|bx|cx|dx|si|di|bp|sp)|r(?:8|9|10|11|12|13|14|15)(?:d|w|b)?)\b")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated H4-M2E artifact is stale: {path}")
    else:
        path.write_text(rendered)


def load_disassembler(path: Path):
    spec = importlib.util.spec_from_file_location("h3_liveness", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load H3 liveness helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.disassemble


def canonical_gpr(register: str) -> str:
    legacy = {
        "eax": "rax", "ebx": "rbx", "ecx": "rcx", "edx": "rdx",
        "esi": "rsi", "edi": "rdi", "ebp": "rbp", "esp": "rsp",
    }
    if register in legacy:
        return legacy[register]
    if re.fullmatch(r"r(?:8|9|10|11|12|13|14|15)[dwb]", register):
        return register[:-1]
    return register


def optimized_pair_lowering(record: dict) -> dict:
    before = record["pair32_before_sort"]
    desired = record["pair32_half_runs"]
    before_halves = [before[:4], before[4:]]
    if before_halves == desired:
        sort_class = "none"
    elif before_halves == desired[::-1]:
        sort_class = "chunk-swap-absorbed-by-store-address"
    else:
        sort_class = "hard-intra-chunk-vpermd"
    routes = ([] if record["vpermq_output_to_input_qword"] == [0, 1, 2, 3]
              else ["vpermq pair-localize"])
    routes.append("vpshufb orient-low-high")
    if sort_class == "hard-intra-chunk-vpermd":
        routes.append("vpermd pair32-sort")
    physical_halves = (desired if sort_class !=
                       "chunk-swap-absorbed-by-store-address" else desired[::-1])
    return {
        "sort_class": sort_class,
        "routes": routes,
        "route_count": len(routes),
        "pair32_physical_halves": physical_halves,
        "post_madd": "vpmaddwd [1,4096]",
        "pack24": "vpshufb four-dword-to-twelve-byte per 128-bit half",
    }


def choose_chunk_order(vectors: list[int], records: dict[int, dict],
                       block: int) -> tuple[list[int], tuple[int, ...]]:
    base_pair = 64 * block
    choices = []
    for vector in vectors:
        choices.append([(run[0] - base_pair) // 4
                        for run in records[vector]["pair32_half_runs"]])
    best = None
    for orientation in itertools.product(range(2), repeat=8):
        order = []
        for index, chunks in enumerate(choices):
            first = orientation[index]
            order.extend([chunks[first], chunks[1 - first]])
        position = {chunk: index for index, chunk in enumerate(order)}
        safe = sum(chunk == 15 or position[chunk] < position[chunk + 1]
                   for chunk in range(16))
        candidate = (safe, tuple(-value for value in order), tuple(order),
                     orientation)
        if best is None or candidate > best:
            best = candidate
    assert best is not None
    return list(best[2]), best[3]


def replay_block(block: int, emission: list[dict]) -> dict:
    state = [None] * 196
    events = []
    for sequence, chunk in enumerate(emission):
        offset = 12 * chunk["block_chunk"]
        for byte in range(12):
            state[offset + byte] = ("valid", block, chunk["block_chunk"], byte)
        if chunk["store_strategy"] == "overlap16":
            for byte in range(12, 16):
                state[offset + byte] = ("junk", sequence, byte - 12)
        events.append({
            "sequence": sequence,
            "block_chunk": chunk["block_chunk"],
            "scratch_byte_offset": 192 * block + offset,
            "strategy": chunk["store_strategy"],
        })
    expected = [("valid", block, chunk, byte)
                for chunk in range(16) for byte in range(12)]
    if state[:192] != expected:
        raise SystemExit(f"block {block} overlapping-store replay failed")
    return {
        "proof": "all 192 logical bytes exact after terminal emission",
        "events": events,
        "ignored_padding_bytes": list(range(192, 196)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m2d", type=Path, required=True)
    parser.add_argument("--h3-liveness", type=Path, required=True)
    parser.add_argument("--h3-object", type=Path, required=True)
    parser.add_argument("--liveness-tool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    m2d = json.loads(args.m2d.read_text())
    liveness = json.loads(args.h3_liveness.read_text())
    if m2d["schema"] != "encap-h4-m2d-physical-wire/v1":
        raise SystemExit("M2D schema changed")
    if liveness["terminal_store_count"] != 72:
        raise SystemExit("linked H3 no longer exposes 72 terminal hooks")

    disassemble = load_disassembler(args.liveness_tool)
    instructions = disassemble(args.h3_object)
    stores = [index for index, insn in enumerate(instructions)
              if insn["output_vector"] is not None]
    if len(stores) != 72:
        raise SystemExit("linked H3 terminal-store recovery changed")

    raw_records = {item["vector"]: item for item in m2d["vector_ownership"]}
    lowering = {vector: optimized_pair_lowering(record)
                for vector, record in raw_records.items()}
    sort_counts = {}
    for record in lowering.values():
        key = record["sort_class"]
        sort_counts[key] = sort_counts.get(key, 0) + 1
    if sort_counts != {
            "chunk-swap-absorbed-by-store-address": 8,
            "hard-intra-chunk-vpermd": 56,
            "none": 8}:
        raise SystemExit(f"unexpected vpermd classification: {sort_counts}")

    per_hook = []
    blocks = []
    overlap_stores = exact_chunks = repaired_overlap_bytes = 0
    exact_high_half_extractions = 0
    for block in range(9):
        hooks = liveness["terminal_stores"][8 * block:8 * block + 8]
        vectors = [hook["output_vector"] for hook in hooks]
        expected_vectors = m2d["blocks_128_coeff_192_bytes"][block]["terminal_vectors"]
        if sorted(vectors) != expected_vectors:
            raise SystemExit(f"block {block} terminal-vector membership changed")
        chunk_order, orientation = choose_chunk_order(vectors, raw_records, block)
        position = {chunk: index for index, chunk in enumerate(chunk_order)}
        emission = []
        for local, hook in enumerate(hooks):
            vector = hook["output_vector"]
            runs = raw_records[vector]["pair32_half_runs"]
            selected = [orientation[local], 1 - orientation[local]]
            temp = 1
            for within_hook, half in enumerate(selected):
                block_chunk = (runs[half][0] - 64 * block) // 4
                physical_half = lowering[vector]["pair32_physical_halves"].index(
                    runs[half])
                safe = block_chunk == 15 or position[block_chunk] < position[block_chunk + 1]
                strategy = "overlap16" if safe else "exact8plus4"
                emission.append({
                    "terminal_index": hook["terminal_index"],
                    "vector": vector,
                    "within_hook": within_hook,
                    "pair32_half": half,
                    "physical_pair32_half": physical_half,
                    "wire_pairs": runs[half],
                    "block_chunk": block_chunk,
                    "scratch_byte_offset": 3 * runs[half][0],
                    "store_strategy": strategy,
                    "store_instructions": 1 if safe else 2,
                    "store_bytes": 16 if safe else 12,
                    "overrun_bytes": 4 if safe else 0,
                })
                if safe:
                    overlap_stores += 1
                    if block_chunk != 15:
                        repaired_overlap_bytes += 4
                else:
                    exact_chunks += 1
                    if physical_half == 1:
                        exact_high_half_extractions += 1
            if hook["terminal_index"] + 1 < 72:
                interval = instructions[
                    stores[hook["terminal_index"]] + 1:
                    stores[hook["terminal_index"] + 1] + 1]
            else:
                interval = []
            untouched = sorted(
                YMM_REGISTERS - set().union(*(
                    set(insn["defs"]) | set(insn["uses"])
                    for insn in interval)) if interval else YMM_REGISTERS,
                key=lambda register: int(register[3:]))
            per_hook.append({
                "terminal_index": hook["terminal_index"],
                "block": block,
                "output_vector": vector,
                "output_register": hook["output_register"],
                "live_before": hook["live_before_store"],
                "live_before_count": hook["live_count_before_store"],
                "temporaries_needed": temp,
                "peak_with_terminal_lowering": hook["live_count_before_store"] + temp,
                "live_after": hook["live_after_store"],
                "chunk_emission_order": [entry["block_chunk"]
                                          for entry in emission[-2:]],
                "untouched_ymm_until_next_hook": untouched,
            })
        replay = replay_block(block, emission)
        blocks.append({
            "block": block,
            "wire_coefficients": [128 * block, 128 * block + 127],
            "terminal_vectors_in_linked_order": vectors,
            "chunk_emission_order": chunk_order,
            "chunks": emission,
            "overlap16_chunks": sum(x["store_strategy"] == "overlap16"
                                    for x in emission),
            "exact8plus4_chunks": sum(x["store_strategy"] == "exact8plus4"
                                      for x in emission),
            "scratch_store_instructions": sum(x["store_instructions"]
                                              for x in emission),
            "scratch_store_bytes": sum(x["store_bytes"] for x in emission),
            "overlap_proof": replay,
            "final_copy": {
                "loads": 6, "permutations": 0, "ct_stores": 6,
                "bytes": 192,
            },
        })

    if overlap_stores + exact_chunks != 144:
        raise SystemExit("M2E did not schedule all 144 packed12 chunks")
    ignored_padding = 9 * 4
    overlap_bytes = 4 * overlap_stores
    if repaired_overlap_bytes + ignored_padding != overlap_bytes:
        raise SystemExit("overlap byte accounting does not close")

    pair_routes = sum(record["route_count"] for record in lowering.values())
    ledgers = {
        "A-exact-wire-8plus4": {
            "terminal_normalization": 432,
            "pair_orientation_routes": pair_routes,
            "pair_madd": 72,
            "pair32_to_packed24_routes": 72,
            "exact_high_half_extract_routes": 72,
            "scratch_store_instructions": 288,
            "scratch_to_wire_loads": 54,
            "final_permutations": 0,
            "ct_stores": 54,
        },
        "B-terminal-native-16plus8": {
            "lower_bound_only": True,
            "reason": "same two stores as C-terminal-native plus nonzero concatenate work",
            "lower_bound_total": 1192,
        },
        "C-terminal-native-overlap": {
            "terminal_normalization": 432,
            "pair_orientation_routes": pair_routes,
            "pair_madd": 72,
            "pair32_to_packed24_routes": 72,
            "exact_high_half_extract_routes": 0,
            "scratch_store_instructions": 144,
            "scratch_to_wire_loads": 144,
            "final_permutations": 0,
            "ct_stores": 144,
        },
        "C-mixed-direct-wire-overlap-selected": {
            "terminal_normalization": 432,
            "pair_orientation_routes": pair_routes,
            "pair_madd": 72,
            "pair32_to_packed24_routes": 72,
            "exact_high_half_extract_routes": exact_high_half_extractions,
            "scratch_store_instructions": overlap_stores + 2 * exact_chunks,
            "scratch_to_wire_loads": 54,
            "final_permutations": 0,
            "ct_stores": 54,
        },
        "D-two-vector-48byte-aggregate": {
            "optimistic_lower_bound_only": True,
            "terminal_store_lower_bound": 108,
            "concatenation_routes_ignored": True,
            "final_terminal_native_copy_lower_bound": 288,
            "lower_bound_total": 1156,
            "reason": "even a zero-concatenation lower bound loses to selected direct-wire schedule",
        },
    }
    for record in ledgers.values():
        if "terminal_normalization" in record:
            record["total_instructions"] = sum(record.values())
    selected = ledgers["C-mixed-direct-wire-overlap-selected"]
    if selected["total_instructions"] != 1115:
        raise SystemExit(f"selected instruction total changed: {selected}")

    used_gprs = sorted({canonical_gpr(match.group(0))
                        for insn in instructions
                        for match in GPR.finditer(insn["operands"])})
    document = {
        "schema": "encap-h4-m2e-packed24-schedule/v1",
        "checkpoint": "H4-M2E-LINKED-H3-PACKED24-SCHEDULE",
        "source_sha256": {
            "m2d": sha256(args.m2d),
            "h3_liveness": sha256(args.h3_liveness),
            "h3_object": sha256(args.h3_object),
            "liveness_tool": sha256(args.liveness_tool),
        },
        "frozen_contract": {
            "wire_coefficient": "Official physical coefficient k",
            "pair32": "c[2i] + (c[2i+1] << 12)",
            "scratch_layout": "exact 1728-byte wire order in existing 2304-byte allocation",
            "final_copy": "nine independent 192-byte blocks, six YMM loads and stores each",
            "algebra_ownership_and_scale_reopened": False,
        },
        "vpermd_reclassification": {
            "classes": sort_counts,
            "hard_vpermd_count": 56,
            "vpermd_removed_by_store_address": 8,
            "unique_hard_vpermd_indices": 2,
        },
        "mask_and_constant_ledger": {
            "unique_pair_vpshufb_masks": sorted({
                tuple(item["vpshufb_output_to_post_vpermq_byte"])
                for item in raw_records.values()}),
            "nonidentity_vpermq_output_to_input_qword": [[0, 2, 1, 3]],
            "hard_vpermd_output_to_input_dword": sorted({
                tuple(item["pair32_vpermd_output_to_input_dword"])
                for vector, item in raw_records.items()
                if lowering[vector]["sort_class"] == "hard-intra-chunk-vpermd"}),
            "packed24_vpshufb_mask": 2 * [
                0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14,
                128, 128, 128, 128],
            "pair_weight_words": 8 * [1, 4096],
        },
        "store_ledger": {
            "logical_packed12_chunks": 144,
            "overlap16_chunks": overlap_stores,
            "exact8plus4_chunks": exact_chunks,
            "scratch_store_instructions": overlap_stores + 2 * exact_chunks,
            "exact_high_half_extract_routes": exact_high_half_extractions,
            "scratch_store_bytes": 16 * overlap_stores + 12 * exact_chunks,
            "logical_scratch_bytes": 1728,
            "overlapping_store_bytes": overlap_bytes,
            "intentional_overwritten_bytes": repaired_overlap_bytes,
            "ignored_block_padding_bytes": ignored_padding,
            "scratch_to_wire_loads": 54,
            "final_permutations": 0,
            "ct_stores": 54,
        },
        "instruction_ledgers": ledgers,
        "register_and_liveness": {
            "linked_h3_peak_ymm": liveness["peak_live_ymm"],
            "terminal_lowering_peak_ymm": max(
                item["peak_with_terminal_lowering"] for item in per_hook),
            "whole_symbol_peak_ymm": max(
                liveness["peak_live_ymm"],
                max(item["peak_with_terminal_lowering"] for item in per_hook)),
            "temporaries_per_hook": 1,
            "linked_h3_unique_gprs": used_gprs,
            "linked_h3_unique_gpr_count": len(used_gprs),
            "predicted_h4_unique_gpr_count": len(used_gprs) + 1,
            "predicted_h4_peak_live_gpr": len(used_gprs) + 1,
            "incremental_frame_bytes": 0,
            "spill_bytes": 0,
            "per_hook": per_hook,
        },
        "blocks_128_coeff_192_bytes": blocks,
        "pair32_oracle": [
            {
                "wire_pair": pair,
                "expected_expression": f"c[{2 * pair}] + (c[{2 * pair + 1}] << 12)",
                "source": "independent physical coefficient array, not generated ownership",
            }
            for pair in range(576)
        ],
        "decision": {
            "selected": "C-mixed-direct-wire-overlap",
            "selected_total_instructions": selected["total_instructions"],
            "credit_vs_exact_A": (selected["total_instructions"] -
                                  ledgers["A-exact-wire-8plus4"]["total_instructions"]),
            "credit_vs_S1_S2": selected["total_instructions"] - 1452,
            "one_8vector_192byte_schedule_executable": True,
            "asm_authorized": True,
            "asm_scope": "one corrected namespaced H4-M3B replacing only terminal stores and H1 fallback",
            "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
    }
    write(args.output, document, args.check)
    print("H4-M2E: selected mixed direct-wire overlap schedule, total=1115")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
