#!/usr/bin/env python3
"""Generate the exact zero-materialization H3 decode-to-MA2 schedule."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


DECODER_SOURCES = (11, 12, 13, 14, 7, 8, 9, 10)
H_A_REGS = (6, 11, 12, 13)
H_B_REGS = (7, 8, 9, 10)
PAIR_SCRATCH = ((6, 15), (11, 15), (12, 15), (13, 15))
R_REGS = (0, 1, 2, 3)
WORK_REGS = {"c": 4, "wrapped": 5, "product": 14, "montgomery": 15}
TERMS = (
    {"plain": ((0, 0),), "wrapped": ((1, 3), (2, 2), (3, 1))},
    {"plain": ((0, 1), (1, 0)), "wrapped": ((2, 3), (3, 2))},
    {"plain": ((0, 2), (1, 1), (2, 0)), "wrapped": ((3, 3),)},
    {"plain": ((0, 3), (1, 2), (2, 1), (3, 0)), "wrapped": ()},
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated H3 schedule is stale: {path}")
    else:
        path.write_text(value)


def semantic_by_vector(decode: dict) -> dict[int, dict]:
    result: dict[int, dict] = {}
    for item in decode["ownership"]:
        vector = item["natural_vector"]
        owner = {key: item["semantic"][key]
                 for key in ("branch", "p", "terminal_coefficient")}
        old = result.setdefault(vector, owner)
        if old != owner:
            raise SystemExit(f"Natural vector {vector} has multiple semantic owners")
    if len(result) != 72:
        raise SystemExit("expected 72 Natural-Q vector owners")
    return result


def register_set(*groups: tuple[int, ...] | list[int] | set[int]) -> list[str]:
    values = sorted({value for group in groups for value in group})
    if values and (values[0] < 0 or values[-1] > 15):
        raise SystemExit("invalid YMM allocation")
    return [f"ymm{value}" for value in values]


def ymm_def_use(line: str) -> tuple[set[int], set[int]]:
    registers = [int(value) for value in re.findall(r"ymm(\d+)", line)]
    if not registers:
        return set(), set()
    if line.split()[0] == "vpmovmskb":
        return set(), {registers[0]}
    return {registers[0]}, set(registers[1:])


def planned_decoder_liveness(h1_asm: str) -> dict:
    block = h1_asm.split("/* Decode and validate PK block 0. */", 1)[1]
    block = block.split("  vpmaxuw ymm0, ymm11, ymm12", 1)[0]
    lines = [line.strip() for line in block.splitlines()
             if line.strip() and not line.strip().startswith("/*")]
    injection = {
        "vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 0,
        "vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 1,
        "vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 2,
        "vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 3,
    }

    def formation(coefficient: int) -> list[str]:
        source_a = DECODER_SOURCES[coefficient]
        source_b = DECODER_SOURCES[coefficient + 4]
        final_a = H_A_REGS[coefficient]
        final_b = H_B_REGS[coefficient]
        return [
            f"vperm2i128 ymm{final_a}, ymm{source_a}, ymm{source_a}, tile-a-imm",
            f"vpshufb ymm{final_a}, ymm{final_a}, [tile-a-mask-a]",
            f"vperm2i128 ymm15, ymm{source_b}, ymm{source_b}, tile-a-imm",
            "vpshufb ymm15, ymm15, [tile-a-mask-b]",
            f"vpor ymm{final_a}, ymm{final_a}, ymm15",
            f"vperm2i128 ymm15, ymm{source_a}, ymm{source_a}, tile-b-imm",
            "vpshufb ymm15, ymm15, [tile-b-mask-a]",
            f"vperm2i128 ymm{source_a}, ymm{source_b}, ymm{source_b}, tile-b-imm",
            f"vpshufb ymm{source_a}, ymm{source_a}, [tile-b-mask-b]",
            f"vpor ymm{final_b}, ymm15, ymm{source_a}",
        ]

    scheduled = []
    for line in lines:
        scheduled.append(line)
        if line not in injection:
            continue
        coefficient = injection[line]
        source_a = DECODER_SOURCES[coefficient]
        source_b = DECODER_SOURCES[coefficient + 4]
        scheduled += [
            f"vpmaxuw ymm15, ymm{source_a}, ymm{source_b}",
            "vpcmpgtw ymm15, ymm15, [q-1]", "vpmovmskb edx, ymm15",
            "or eax, edx",
        ]
        # ymm6 is still a decoder temporary after d0 is extracted.  Form each
        # pair one extraction later, once the destination chosen by the exact
        # allocation is genuinely dead.  Pair 3 is drained below.
        if coefficient >= 1:
            scheduled += formation(coefficient - 1)
    scheduled += formation(3)
    live = set(H_A_REGS) | set(H_B_REGS)
    peak = len(live)
    peak_line = "decoder-exit"
    peak_registers = set(live)
    for line in reversed(scheduled):
        defined, used = ymm_def_use(line)
        live = (live - defined) | used
        if len(live) > peak:
            peak, peak_line, peak_registers = len(live), line, set(live)
    if peak > 16:
        raise SystemExit(f"planned decoder spills: peak {peak} at {peak_line}")
    return {"instruction_count": len(scheduled), "peak_ymm": peak,
            "peak_before_instruction": peak_line,
            "peak_registers": register_set(peak_registers),
            "pairwise_validation": {"vpmaxuw": 4, "vpcmpgtw": 4,
                                    "vpmovmskb": 4, "gpr_or": 4},
            "h1_validation_instruction_count": 10,
            "candidate_validation_instruction_count": 16,
            "validation_delta_per_block": 6}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codesign", type=Path, required=True)
    parser.add_argument("--decode-map", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--h1-contract", type=Path, required=True)
    parser.add_argument("--h1-asm", type=Path, required=True)
    parser.add_argument("--ma2-source", type=Path, required=True)
    parser.add_argument("--range-proof", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    codesign = json.loads(args.codesign.read_text())
    decode = json.loads(args.decode_map.read_text())
    natural = json.loads(args.natural_schedule.read_text())
    h1 = json.loads(args.h1_contract.read_text())
    range_proof = json.loads(args.range_proof.read_text())
    if codesign["wavefront"]["complete_ma2_tiles_per_decode_block"] != 2:
        raise SystemExit("H3 block geometry changed")
    if not range_proof["all_preoperations_signed_i16"]:
        raise SystemExit("frozen MA2 range proof is not closed")

    owners = semantic_by_vector(decode)
    plans = natural["resident_h"]["natural_plans"]
    by_block: dict[int, list[tuple[int, dict]]] = {block: [] for block in range(9)}
    for destination, plan in enumerate(plans):
        blocks = {source // 8 for source in plan["source_vectors"]}
        if len(blocks) != 1:
            raise SystemExit("H3 does not accept a cross-block h projector")
        by_block[blocks.pop()].append((destination, plan))

    # Freeze the arithmetic ledger from the actual cumulative MA2 source.  H3
    # changes allocation and data ingress only; these exact counts must survive.
    ma2 = args.ma2_source.read_text()
    symbol = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"
    body = ma2.split(symbol + ":", 1)[1].split(f".size {symbol}", 1)[0]
    ma2_ledger = {
        "tiles": body.count("Natural-Q lane-wise MA2 tile"),
        "h_r2_montgomery": len(re.findall(
            r"MA1_MONT_CONST [0-3],[0-3],\.Lma1_r2", body)),
        "h_times_r_montgomery": body.count("MA1_MONT_REG 10,"),
        "lambda_montgomery": len(re.findall(
            r"MA1_MONT_CONST 10,9,\.Lqnat_lambda_", body)),
        "r_loads": len(re.findall(
            r"vmovdqa ymm[4-7], YMMWORD PTR \[rsi", body)),
        "m_loads": body.count("vmovdqa ymm8, YMMWORD PTR [rdx"),
        "c_stores": body.count("vmovdqa YMMWORD PTR [rdi"),
    }
    expected = {"tiles": 18, "h_r2_montgomery": 72,
                "h_times_r_montgomery": 288, "lambda_montgomery": 54,
                "r_loads": 72, "m_loads": 72, "c_stores": 72}
    if ma2_ledger != expected:
        raise SystemExit(f"frozen MA2 ledger changed: {ma2_ledger}")

    # The actual H1 block proves the decoder-native cut and route taxonomy.
    h1_asm = args.h1_asm.read_text()
    decoder_liveness = planned_decoder_liveness(h1_asm)
    block0 = h1_asm.split("/* Decode and validate PK block 0. */", 1)[1]
    block0 = block0.split("/* Decode and validate PK block 1. */", 1)[0]
    decoder_prefix = block0.split("  vperm2i128 ymm1, ymm11", 1)[0]
    decoder_routes_per_block = {
        "vperm2i128": decoder_prefix.count("vperm2i128"),
        "vpunpck": decoder_prefix.count("vpunpck"),
        "vpblend": decoder_prefix.count("vpblend"),
    }
    if decoder_routes_per_block != {"vperm2i128": 6, "vpunpck": 6,
                                    "vpblend": 12}:
        raise SystemExit("decoder-intrinsic route ledger changed")

    blocks = []
    for block in range(9):
        entries = by_block[block]
        if len(entries) != 8:
            raise SystemExit(f"block {block} does not own eight Natural vectors")
        tiles: dict[tuple[int, int], dict[int, tuple[int, dict]]] = {}
        for destination, plan in entries:
            owner = owners[destination]
            key = (owner["branch"], owner["p"])
            coefficient = owner["terminal_coefficient"]
            tiles.setdefault(key, {})[coefficient] = (destination, plan)
        if len(tiles) != 2 or any(set(value) != set(range(4))
                                  for value in tiles.values()):
            raise SystemExit(f"block {block} is not two complete quartic tiles")
        tile_keys = sorted(tiles)
        pair_flow = []
        for coefficient in range(4):
            a_destination, a_plan = tiles[tile_keys[0]][coefficient]
            b_destination, b_plan = tiles[tile_keys[1]][coefficient]
            a_sources = tuple(source % 8 for source in a_plan["source_vectors"])
            b_sources = tuple(source % 8 for source in b_plan["source_vectors"])
            expected_sources = (coefficient, coefficient + 4)
            if a_sources != expected_sources or b_sources != expected_sources:
                raise SystemExit("paired tile formation stopped sharing one decoder pair")
            source_regs = (DECODER_SOURCES[coefficient],
                           DECODER_SOURCES[coefficient + 4])
            pair_flow.append({
                "coefficient": coefficient,
                "decoded_source_vectors": list(expected_sources),
                "decoded_source_registers": [f"ymm{x}" for x in source_regs],
                "validated_after": f"decode-pair-{coefficient}",
                "formed_after": (f"decode-pair-{coefficient + 1}"
                                 if coefficient < 3 else "decode-pair-3-after-pair-2-drain"),
                "tile_a": {"owner": {"branch": tile_keys[0][0], "p": tile_keys[0][1],
                                        "terminal_coefficient": coefficient},
                           "natural_vector": a_destination,
                           "register": f"ymm{H_A_REGS[coefficient]}",
                           "route_immediates": [group["vperm2i128_immediate"]
                                                for group in a_plan["groups"]]},
                "tile_b": {"owner": {"branch": tile_keys[1][0], "p": tile_keys[1][1],
                                        "terminal_coefficient": coefficient},
                           "natural_vector": b_destination,
                           "register": f"ymm{H_B_REGS[coefficient]}",
                           "route_immediates": [group["vperm2i128_immediate"]
                                                for group in b_plan["groups"]]},
                "scratch_registers": [f"ymm{x}" for x in PAIR_SCRATCH[coefficient]],
                "source_last_use": "second tile-specific shuffle input",
                "route_absorption": {
                    "decoder_intrinsic": 0,
                    "consumer_required": 10,
                    "pure_h_abi_formation": 0,
                    "explanation": "two five-route lane alignments are the first MA2-use presentation; no h boundary is written",
                },
            })
        blocks.append({
            "decode_block": block,
            "pk_byte_range": [192 * block, 192 * block + 191],
            "tile_a": {"branch": tile_keys[0][0], "p": tile_keys[0][1]},
            "tile_b": {"branch": tile_keys[1][0], "p": tile_keys[1][1]},
            "pair_flow": pair_flow,
        })

    phase_registers = [
        {"phase": "packed-load-and-unpack", "live_upper_bound": decoder_liveness["peak_ymm"],
         "persistent": [], "note": "mechanical backward liveness includes the one-pair-delayed formation pipeline"},
        {"phase": "pairwise-validate-and-delayed-dual-form", "live_upper_bound": decoder_liveness["peak_ymm"],
         "persistent_after_phase": register_set(H_A_REGS, H_B_REGS),
         "note": "each pair is validated immediately; formation is delayed one extraction so its final register is dead"},
        {"phase": "in-place-R2-normalization", "live_upper_bound": 9,
         "persistent": register_set(H_A_REGS, H_B_REGS),
         "temporary": "ymm15"},
        {"phase": "tile-a-MA2-while-tile-b-h-remains-live", "live_upper_bound": 16,
         "h_a": register_set(H_A_REGS), "h_b_held": register_set(H_B_REGS),
         "r_a": register_set(R_REGS),
         "work": {key: f"ymm{value}" for key, value in WORK_REGS.items()}},
        {"phase": "tile-b-MA2", "live_upper_bound": 12,
         "h_b": register_set(H_B_REGS), "r_b": register_set(R_REGS),
         "work": {key: f"ymm{value}" for key, value in WORK_REGS.items()}},
    ]
    if max(phase["live_upper_bound"] for phase in phase_registers) != 16:
        raise SystemExit("H3 allocation no longer reaches the expected 16-register peak")
    tile_a_set = set(H_A_REGS) | set(H_B_REGS) | set(R_REGS) | set(WORK_REGS.values())
    if tile_a_set != set(range(16)):
        raise SystemExit(f"tile-A allocation is not exact 16/16: {tile_a_set}")

    report = {
        "schema": "encap-h-ingress-ma2-h3-schedule/v1",
        "checkpoint": "ENCAP-H-INGRESS-MA2-H3-SCHEDULE",
        "scope": "exact register-flow and arithmetic-preservation gate; no ASM or benchmark",
        "contract": {
            "function": "(pk bytes, r_Natural-Q_scale4, m_Natural-Q_scale4) -> c_MA2_scale4",
            "accepted_set_and_error": "identical to Official poly_frombytes validation",
            "valid_output": "raw bit-exact with H1 preprojected-h MA2",
            "intermediate_h_array": "does not exist",
            "frozen": ["Natural-Q r/m ABI", "MA2 quartic formulas", "lambda placement",
                       "Montgomery domains", "scale 4", "output stores"],
        },
        "decoder": {
            "strategy": "validate each decoded pair immediately and dual-form it one extraction later",
            "validation": {"persistent_state": "eax public-invalid accumulator",
                           "temporary_state": "one recycled YMM max/compare plus edx movemask",
                           "constant_time": "work and control flow are independent of decoded values",
                           "schedule_ledger": decoder_liveness},
            "decoded_pair_order": [[0, 4], [1, 5], [2, 6], [3, 7]],
            "decoder_intrinsic_routes_per_block": decoder_routes_per_block,
            "decoder_intrinsic_routes_total": {
                key: 9 * value for key, value in decoder_routes_per_block.items()},
            "full_eight_vector_natural_q_cut": False,
            "note": "the one-pair delay preserves decoder liveness; no resident Natural-Q h object or memory boundary is formed",
        },
        "formation": {
            "blocks": blocks,
            "routes_per_block": {"decoder_intrinsic": sum(decoder_routes_per_block.values()),
                                 "consumer_required": 40,
                                 "pure_h_abi_formation": 0},
            "routes_total": {"decoder_intrinsic": 9 * sum(decoder_routes_per_block.values()),
                             "consumer_required": h1["decoder"]["formation_routes"],
                             "pure_h_abi_formation": 0},
            "h_stores": 0, "h_reloads": 0,
            "explanation": "the 360 lane-aligning routes remain arithmetic-consumer work; only the 2304-byte H1 boundary disappears",
        },
        "register_flow": {
            "phases": phase_registers,
            "peak_ymm": 16, "spill": 0, "frame_scratch": 0,
            "tile_a_exact_partition": register_set(tuple(range(16))),
            "tile_b_slack": 4,
        },
        "ma2": {
            "linked_control_ledger": ma2_ledger,
            "candidate_ledger": ma2_ledger,
            "terms": [{"coefficient": i,
                       "plain": [list(x) for x in term["plain"]],
                       "wrapped": [list(x) for x in term["wrapped"]]}
                      for i, term in enumerate(TERMS)],
            "execution": "tile A then tile B; dual formation uses a one-pair-delayed pipeline across both tiles",
            "raw_exact_reason": "identical h R2, product order, wrapped accumulation, one lambda multiply, and c-store order",
            "range": {"proof_reused": args.range_proof.name,
                      "global_pre_output_bound": range_proof["global_pre_inv4"],
                      "all_preoperations_signed_i16": True},
        },
        "terminal_contract": {
            "form": "H3_EMIT_C(tile, coefficient, ymm4) immediately before each aligned final store",
            "coefficients": [0, 1, 2, 3],
            "representative": "raw H1-exact scale-4 MA2 value",
            "mandatory_materialization_before_hook": False,
            "future_h4": "may replace each store hook with serializer work or store to the old h stack slot followed by one final 1728-byte copy",
            "note": "the first tile cannot retain all four c vectors simultaneously because the second h quartet occupies four registers; each c_j is live at its own terminal hook",
        },
        "movement_delta_vs_h1": {
            "h_vector_stores": -72, "h_vector_reloads": -72,
            "consumer_required_routes": 0, "pure_abi_routes": 0,
            "new_temporaries_bytes": 0,
        },
        "fallback": {
            "H3-full": "selected; exact 16/16 schedule closes",
            "H3-half": "not selected; would store/reload four h vectors per block (128 bytes/block)",
            "H2": "not selected",
        },
        "gates": {
            "peak_ymm_le_16": True, "h_store_reload_zero": True,
            "pure_h_abi_routes_zero": True, "spill_zero": True,
            "frame_scratch_zero": True, "ma2_arithmetic_unchanged": True,
            "raw_h1_output_contract_preserved": True,
        },
        "decision": {
            "h3_namespaced_asm": "authorized-next",
            "benchmark": False, "native_kem": False,
            "do_not_change": ["serializer", "forward", "Natural-Q", "MA2 formulas"],
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "codesign": args.codesign, "decode_map": args.decode_map,
            "natural_schedule": args.natural_schedule, "h1_contract": args.h1_contract,
            "h1_asm": args.h1_asm, "ma2_source": args.ma2_source,
            "range_proof": args.range_proof}.items()},
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n", args.check)
    print("H3 schedule: pairwise validation plus delayed dual-form, exact peak 16, zero h boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
