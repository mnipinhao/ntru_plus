#!/usr/bin/env python3
"""Generate GT32-FWD-LANDING-BASEINV-001.

This is a bounded co-design gate for three linked hypotheses:

* progressively migrate the final NTT32 layers into a coefficient-plane ABI;
* treat range checkpoints as search variables rather than fixed stages; and
* keep keygen in a SoA BaseInv/BaseMul island instead of TILE4/J1/R1-U.

The script deliberately reuses the already exhaustively checked P terminal
and does not search another universal polynomial ABI.  It adds an exact
whole-YMM checkpoint search for the direct BaseInv multiplication bound.
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "generated"
Q = 3457
BASEINV_PRODUCT_LIMIT = 10643


def load_tile4_generator():
    path = ROOT / "tools" / "generate_tile4.py"
    spec = importlib.util.spec_from_file_location("tile4_generator", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = load_tile4_generator()


@functools.cache
def montgomery_bound(bound: int, factor: int) -> int:
    return G.product_bound(bound, [factor])


@functools.cache
def center10_bound(bound: int) -> int:
    """Exact signed VPMULHRSW(value,10), then value-q*t image bound."""
    def reduce(value: int) -> int:
        quotient = (value * 10 + (1 << 14)) >> 15
        return value - Q * quotient

    return max(abs(reduce(value)) for value in range(-bound, bound + 1))


@functools.cache
def frontend_value_set(branch: int, n: int) -> tuple[int, ...]:
    """Exact wide-raw frontend value set before the length-3 DFT.

    Each value depends on two independent small coefficients.  Unlike the
    older 1728 core-entry model, this follows FRONTEND_WIDE_ITER_BODY's raw
    -722 top split and its subsequent Montgomery twist exactly.
    """
    factor = G.centered(pow(G.BRANCH_SCALE[branch], -n, Q) * G.R)
    values = set()
    for low in range(-3, 5):
        for high in range(-3, 5):
            split = -722 * high
            value = (low + split if branch == 0
                     else low + high - split)
            values.add(G.montgomery_fixed(value, factor))
    return tuple(sorted(values))


def exact_frontend_bounds() -> list[list[int]]:
    """Return exact abs bounds indexed by TILE4 tile then physical Q."""
    result = []
    for k3 in range(3):
        for branch in range(2):
            row = []
            for q_value in range(32):
                streams = [frontend_value_set(
                    branch, (64 * n3 + 33 * q_value) % 96)
                    for n3 in range(3)]
                maximum = 0
                for x0, x1, x2 in itertools.product(*streams):
                    omega = G.montgomery_fixed(x1 - x2, -886)
                    outputs = (x0 + x1 + x2,
                               x0 - x2 + omega,
                               x0 - x1 - omega)
                    maximum = max(maximum, abs(outputs[k3]))
                row.append(maximum)
            result.append(row)
    return result


def propagate(initial: list[int],
              checkpoints: dict[int, tuple[int, ...]]) -> tuple[list[int], list[dict]]:
    bounds = initial[:]
    stages = []
    for stage in range(1, 6):
        distance = 32 >> stage
        output = bounds[:]
        for base in range(0, 32, 2 * distance):
            factor = G.mont_root(G.forward_power(stage, base))
            for offset in range(distance):
                low = bounds[base + offset]
                high = bounds[base + offset + distance]
                product = high if stage == 1 else montgomery_bound(high, factor)
                output[base + offset] = low + product
                output[base + offset + distance] = low + product
        before = output[:]
        for vector in checkpoints.get(stage, ()):
            for q_value in range(4 * vector, 4 * vector + 4):
                output[q_value] = center10_bound(output[q_value])
        stages.append({
            "stage": stage,
            "before_checkpoint": before,
            "checkpoint_vectors": list(checkpoints.get(stage, ())),
            "after_checkpoint": output[:],
            "maximum_after_checkpoint": max(output),
        })
        bounds = output
    return bounds, stages


def checkpoint_search() -> dict:
    frontend_bounds = exact_frontend_bounds()
    baseline_records = [propagate(row, {}) for row in frontend_bounds]
    baseline_max = max(max(record[0]) for record in baseline_records)
    nodes = [(stage, vector) for stage in range(1, 5) for vector in range(8)]
    one_checkpoint = []
    two_checkpoint = []
    for count in (1, 2):
        for selected in itertools.combinations(nodes, count):
            checkpoints: dict[int, list[int]] = {}
            for stage, vector in selected:
                checkpoints.setdefault(stage, []).append(vector)
            normalized = {stage: tuple(vectors) for stage, vectors
                          in checkpoints.items()}
            propagated = [propagate(row, normalized)
                          for row in frontend_bounds]
            terminal_max = max(max(record[0]) for record in propagated)
            record = {
                "nodes": [{"stage": stage, "vector": vector}
                          for stage, vector in selected],
                "terminal_max_abs_bound": terminal_max,
                "terminal_bounds_by_tile_and_Q": [record[0]
                                                    for record in propagated],
                "stage_maxima_by_tile": [
                    [entry["maximum_after_checkpoint"] for entry in record[1]]
                    for record in propagated],
                "baseinv_product_safe": terminal_max <= BASEINV_PRODUCT_LIMIT,
            }
            (one_checkpoint if count == 1 else two_checkpoint).append(record)

    safe_pairs = [record for record in two_checkpoint
                  if record["baseinv_product_safe"]]
    assert not any(record["baseinv_product_safe"] for record in one_checkpoint)
    assert safe_pairs
    safe_pairs.sort(key=lambda record: (
        record["terminal_max_abs_bound"],
        [(node["stage"], node["vector"]) for node in record["nodes"]],
    ))
    selected = safe_pairs[0]
    assert selected["nodes"] == [
        {"stage": 1, "vector": 0},
        {"stage": 1, "vector": 4},
    ]

    return {
        "baseinv_direct_product_limit": BASEINV_PRODUCT_LIMIT,
        "frontend_proof": {
            "input_contract": [-3, 4],
            "model": "exact enumeration of raw top split, twist, and DFT3",
            "bounds_by_tile_and_Q": frontend_bounds,
            "maximum_abs_bound": max(max(row) for row in frontend_bounds),
        },
        "baseline_terminal_bounds_by_tile_and_Q": [record[0]
                                                    for record in baseline_records],
        "baseline_terminal_max_abs_bound": baseline_max,
        "baseline_stages_by_tile": [record[1] for record in baseline_records],
        "one_checkpoint_candidates": len(one_checkpoint),
        "one_checkpoint_safe_candidates": 0,
        "two_checkpoint_candidates": len(two_checkpoint),
        "two_checkpoint_safe_candidates": len(safe_pairs),
        "selected": selected,
        "dynamic_center_instructions_per_tile": 6,
        "tiles_per_forward": 6,
        "dynamic_center_instructions_per_forward": 36,
        "extra_montgomery_chains": 0,
        "signed_int16_safe": max(
            maximum for row in selected["stage_maxima_by_tile"]
            for maximum in row) < 32768,
    }


def mapping_proof(permutation_gate: dict) -> dict:
    standard_q = permutation_gate["permutation"][
        "standard_private_plane_q_order"]
    p_q = permutation_gate["permutation"][
        "logical_q_at_physical_plane_lane"]
    assert sorted(standard_q) == list(range(16))
    assert sorted(p_q) == list(range(16))

    records = []
    tile_words = set()
    standard_words = set()
    p_words = set()
    gtn_words = set()
    for k3 in range(3):
        for branch in range(2):
            tile = 2 * k3 + branch
            for q_value in range(32):
                half = q_value // 16
                group = 2 * tile + half
                local_q = q_value & 15
                for degree in range(4):
                    tile_word = (128 * tile + 16 * (q_value // 4)
                                 + 4 * (q_value % 4) + degree)
                    standard_lane = standard_q.index(local_q)
                    p_lane = p_q.index(local_q)
                    standard_word = 64 * group + 16 * degree + standard_lane
                    p_word = 64 * group + 16 * degree + p_lane
                    gtn_batch = 4 * k3 + q_value // 8
                    gtn_lane = 8 * branch + q_value % 8
                    gtn_word = 64 * gtn_batch + 16 * degree + gtn_lane
                    records.append({
                        "k3": k3,
                        "branch": branch,
                        "Q": q_value,
                        "degree": degree,
                        "tile4_word": tile_word,
                        "standard_private_SoA_word": standard_word,
                        "P_private_SoA_word": p_word,
                        "GTN_L3_word": gtn_word,
                    })
                    tile_words.add(tile_word)
                    standard_words.add(standard_word)
                    p_words.add(p_word)
                    gtn_words.add(gtn_word)
    assert all(len(words) == 768 for words in
               (tile_words, standard_words, p_words, gtn_words))
    return {
        "records": records,
        "all_four_layouts_are_bijections": True,
        "same_logical_leaf_and_degree": True,
        "standard_private_q_order": standard_q,
        "P_private_q_order": p_q,
        "GTN_L3_formula": {
            "batch": "4*k3 + Q/8",
            "lane": "8*branch + Q%8",
            "word": "64*batch + 16*degree + lane",
        },
        "P_to_BaseInv_absorption": {
            "data_permutation_required": False,
            "reason": (
                "quartic adjugate/determinant arithmetic is lane-wise and "
                "batch inversion is order-independent; reorder lambda/mu "
                "metadata and stores instead"
            ),
        },
    }


def emit_p_baseinv_tables(path: Path, p_q: list[int]) -> None:
    lines = [
        "/* Generated P-lane lambda tables for the reusable SoA BaseInv. */",
        "const int16_t gt_native_lambda[12][16]",
        "\t__attribute__((aligned(32))) = {",
    ]
    tables = []
    for k3 in range(3):
        for branch in range(2):
            for half in range(2):
                tables.append([G.lambda_montgomery(
                    k3, 16 * half + logical_q, branch)
                    for logical_q in p_q])
    for row in tables:
        lines.append("\t{" + ", ".join(str(value) for value in row) + "},")
    lines.extend([
        "};", "",
        "const int16_t gt_native_lambda_qinv[12][16]",
        "\t__attribute__((aligned(32))) = {",
    ])
    for row in tables:
        lines.append("\t{" + ", ".join(
            str(G.factor_qinv(value)) for value in row) + "},")
    lines.extend(["};", ""])
    path.write_text("\n".join(lines))


def emit_p_mapping_header(path: Path, mapping: dict) -> None:
    by_key = {(record["k3"], record["branch"], record["Q"],
               record["degree"]): record["P_private_SoA_word"]
              for record in mapping["records"]}
    serialized = json.loads(
        (GENERATED / "tile4_serialized_mapping.json").read_text())["records"]
    p_words = [by_key[(record["k3"], record["branch"],
                       record["physical_q"],
                       record["quartic_coefficient"])]
               for record in serialized]
    official_words = [record["official_word"] for record in serialized]
    assert sorted(p_words) == list(range(768))
    assert sorted(official_words) == list(range(768))
    lines = [
        "#ifndef NTRUPLUS_GT32_P_BASEINV_MAPPING_H",
        "#define NTRUPLUS_GT32_P_BASEINV_MAPPING_H",
        "#include <stdint.h>",
    ]
    for name, values in (("gt32_p_word_from_serialized", p_words),
                         ("gt32_official_word_from_serialized",
                          official_words)):
        lines.append(f"static const uint16_t {name}[768] = {{")
        for offset in range(0, 768, 16):
            lines.append("\t" + ", ".join(
                str(value) for value in values[offset:offset + 16]) + ",")
        lines.extend(["};", ""])
    lines.extend(["#endif", ""])
    path.write_text("\n".join(lines))


def serialized_p_words(mapping: dict) -> list[int]:
    by_key = {(record["k3"], record["branch"], record["Q"],
               record["degree"]): record["P_private_SoA_word"]
              for record in mapping["records"]}
    serialized = json.loads(
        (GENERATED / "tile4_serialized_mapping.json").read_text())["records"]
    words = [by_key[(record["k3"], record["branch"],
                     record["physical_q"],
                     record["quartic_coefficient"])]
             for record in serialized]
    assert sorted(words) == list(range(768))
    return words


def emit_p_q24_pack(asm_path: Path, json_path: Path, mapping: dict) -> None:
    """Emit direct progressive-P SoA to Q24 packet routing.

    A plane-block transpose leaves quartic lane L in register 4+(L mod 4)
    and qword floor(L/4).  Every serialized Q24 packet draws one 128-bit
    half from each of exactly two such registers.  One vperm2i128 therefore
    creates the packet carrier; the existing vpermq/reducer/packer finishes
    it without a global P-to-standard repair.
    """
    words = serialized_p_words(mapping)
    packets = []
    for packet in range(48):
        packet_words = words[16 * packet:16 * packet + 16]
        blocks = {word // 64 for word in packet_words}
        assert len(blocks) == 1
        block = blocks.pop()
        quartics = []
        for quartic in range(4):
            degree_words = packet_words[4 * quartic:4 * quartic + 4]
            lanes = {word % 16 for word in degree_words}
            assert len(lanes) == 1
            lane = lanes.pop()
            assert [word // 16 % 4 for word in degree_words] == [0, 1, 2, 3]
            quartics.append((4 + lane % 4, lane // 4))
        reg_a, half_a = quartics[0][0], quartics[0][1] // 2
        reg_b, half_b = quartics[2][0], quartics[2][1] // 2
        assert all(reg == reg_a and qword // 2 == half_a
                   for reg, qword in quartics[:2])
        assert all(reg == reg_b and qword // 2 == half_b
                   for reg, qword in quartics[2:])
        assert reg_a != reg_b
        assembled = [(reg_a, 2 * half_a), (reg_a, 2 * half_a + 1),
                     (reg_b, 2 * half_b), (reg_b, 2 * half_b + 1)]
        sources = [assembled.index(item) for item in quartics]
        permq = sum(source << (2 * output)
                    for output, source in enumerate(sources))
        perm2 = half_a | ((2 + half_b) << 4)
        packets.append({
            "packet": packet,
            "P_block": block,
            "quartic_sources": quartics,
            "vperm2i128_imm": perm2,
            "vpermq_imm": permq,
        })

    lines = ["/* Generated progressive-P SoA Q24 pack route. */", "",
             ".macro Q24_ENCODE_P_SOA_BODY"]
    for group in range(12):
        group_packets = packets[4 * group:4 * group + 4]
        blocks = {packet["P_block"] for packet in group_packets}
        assert len(blocks) == 1
        block = blocks.pop()
        lines.extend([
            f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
            f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
            f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
            f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        ])
        for packet in group_packets:
            reg_a = packet["quartic_sources"][0][0]
            reg_b = packet["quartic_sources"][2][0]
            lines.extend([
                f"\tvperm2i128 ${packet['vperm2i128_imm']}, "
                f"%ymm{reg_b}, %ymm{reg_a}, %ymm0",
                "\tQ24_ENCODE_REG_PACKET %ymm0,%xmm0,"
                f"{packet['vpermq_imm']},{24 * packet['packet']},"
                f"{int(packet['packet'] == 47)}",
            ])
    lines.extend([".endm", ""])

    # D2: keep each post-transpose YMM intact.  Each 128-bit half already
    # contains exactly the two quartics needed by one wire-packet half.
    # Reorder qwords independently inside each lane, reduce/pack the source
    # YMM, then scatter its two 12-byte products to their packet addresses.
    half_masks: dict[tuple[bool, bool], str] = {}
    d2_groups = []
    lines.append(".macro Q24_ENCODE_P_SOA_HALF_SCATTER_BODY")
    for group in range(12):
        group_packets = packets[4 * group:4 * group + 4]
        block = group_packets[0]["P_block"]
        assert all(packet["P_block"] == block for packet in group_packets)
        source_to_destination = {}
        for packet in group_packets:
            for packet_half in range(2):
                pair = packet["quartic_sources"][2 * packet_half:
                                                     2 * packet_half + 2]
                reg = pair[0][0]
                source_half = pair[0][1] // 2
                assert all(item[0] == reg and item[1] // 2 == source_half
                           for item in pair)
                natural = [(reg, 2 * source_half),
                           (reg, 2 * source_half + 1)]
                assert pair in (natural, natural[::-1])
                key = (reg, source_half)
                assert key not in source_to_destination
                source_to_destination[key] = {
                    "packet": packet["packet"],
                    "packet_half": packet_half,
                    "swap_qwords": pair == natural[::-1],
                }
        assert len(source_to_destination) == 8
        lines.extend([
            f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
            f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
            f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
            f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
            "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        ])
        for reg in range(4, 8):
            swaps = tuple(source_to_destination[(reg, half)]["swap_qwords"]
                          for half in range(2))
            label = half_masks.setdefault(
                swaps, f".Lq24_p_half_mask_{int(swaps[0])}{int(swaps[1])}")
            lines.append(f"\tvpshufb {label}(%rip), %ymm{reg}, %ymm{reg}")
        lines.extend([
            "\tQ24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7",
        ])
        packet_stores = []
        for packet in group_packets:
            sources = []
            for packet_half in range(2):
                matches = [
                    (reg, half) for (reg, half), destination
                    in source_to_destination.items()
                    if destination["packet"] == packet["packet"]
                    and destination["packet_half"] == packet_half
                ]
                assert len(matches) == 1
                sources.append(matches[0])
            (low_reg, low_half), (high_reg, high_half) = sources
            lines.append(
                "\tQ24_STORE_SCATTER_PACKET "
                f"%ymm{low_reg},%xmm{low_reg},{low_half},"
                f"%ymm{high_reg},%xmm{high_reg},{high_half},"
                f"{24 * packet['packet']},{int(packet['packet'] == 47)}"
            )
            packet_stores.append({
                "packet": packet["packet"],
                "low_source": [low_reg, low_half],
                "high_source": [high_reg, high_half],
            })
        d2_groups.append({
            "group": group,
            "P_block": block,
            "source_halves": {
                f"ymm{reg}.{'high' if half else 'low'}": destination
                for (reg, half), destination
                in sorted(source_to_destination.items())
            },
            "packet_stores": packet_stores,
        })
    lines.extend([".endm", ""])

    # TF1 removes 00 identity masks and absorbs 11 symmetric qword swaps by
    # reversing the operands of the final qword-unpack transpose layer.
    tf1_mask_counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    tf1_residual_masks = 0
    tf1_groups = []
    lines.append(".macro Q24_ENCODE_P_SOA_HALF_SCATTER_TF1_BODY")
    for d2_group in d2_groups:
        block = d2_group["P_block"]
        destinations = d2_group["source_halves"]
        orientations = []
        residuals = []
        for reg in range(4, 8):
            swaps = tuple(destinations[
                f"ymm{reg}.{'high' if half else 'low'}"]["swap_qwords"]
                for half in range(2))
            key = f"{int(swaps[0])}{int(swaps[1])}"
            tf1_mask_counts[key] += 1
            orientations.append(int(swaps == (True, True)))
            residuals.append(swaps if swaps in ((False, True),
                                                 (True, False)) else None)
        lines.extend([
            f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
            f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
            f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
            f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
            "\tQ24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7," +
            ",".join(map(str, orientations)),
        ])
        for reg, swaps in zip(range(4, 8), residuals):
            if swaps is not None:
                lines.append(
                    f"\tvpshufb {half_masks[swaps]}(%rip), "
                    f"%ymm{reg}, %ymm{reg}")
                tf1_residual_masks += 1
        lines.append("\tQ24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7")
        for store in d2_group["packet_stores"]:
            low_reg, low_half = store["low_source"]
            high_reg, high_half = store["high_source"]
            packet = store["packet"]
            lines.append(
                "\tQ24_STORE_SCATTER_PACKET "
                f"%ymm{low_reg},%xmm{low_reg},{low_half},"
                f"%ymm{high_reg},%xmm{high_reg},{high_half},"
                f"{24 * packet},{int(packet == 47)}"
            )
        tf1_groups.append({
            "block": block,
            "orientations": orientations,
            "residuals": residuals,
            "packet_stores": d2_group["packet_stores"],
        })
    lines.extend([".endm", ""])
    assert tf1_mask_counts == {"00": 19, "01": 4, "10": 9, "11": 16}
    assert tf1_residual_masks == 13

    # SP1 keeps the exact TF1 operations but preloads the next source block
    # into ymm8..ymm11 between the current quotient estimate and correction.
    lines.append(".macro Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY")
    for index, tf1_group in enumerate(tf1_groups):
        block = tf1_group["block"]
        if index == 0:
            lines.extend([
                f"\tvmovdqu {128 * block + 0}(%rsi), %ymm0",
                f"\tvmovdqu {128 * block + 32}(%rsi), %ymm1",
                f"\tvmovdqu {128 * block + 64}(%rsi), %ymm2",
                f"\tvmovdqu {128 * block + 96}(%rsi), %ymm3",
                "\tQ24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,"
                "ymm4,ymm5,ymm6,ymm7," +
                ",".join(map(str, tf1_group["orientations"])),
            ])
        else:
            lines.append(
                "\tQ24_TRANSPOSE_TF1 ymm8,ymm9,ymm10,ymm11,"
                "ymm4,ymm5,ymm6,ymm7," +
                ",".join(map(str, tf1_group["orientations"])))
        for reg, swaps in zip(range(4, 8), tf1_group["residuals"]):
            if swaps is not None:
                lines.append(
                    f"\tvpshufb {half_masks[swaps]}(%rip), "
                    f"%ymm{reg}, %ymm{reg}")
        if index + 1 < len(tf1_groups):
            next_block = tf1_groups[index + 1]["block"]
            lines.append(
                "\tQ24_HALF_REDUCE_PACK4_SP1 %ymm4,%ymm5,%ymm6,%ymm7,"
                f"{128 * next_block + 0},{128 * next_block + 32},"
                f"{128 * next_block + 64},{128 * next_block + 96}")
        else:
            lines.append("\tQ24_HALF_REDUCE_PACK4 %ymm4,%ymm5,%ymm6,%ymm7")
        for store in tf1_group["packet_stores"]:
            low_reg, low_half = store["low_source"]
            high_reg, high_half = store["high_source"]
            packet = store["packet"]
            lines.append(
                "\tQ24_STORE_SCATTER_PACKET "
                f"%ymm{low_reg},%xmm{low_reg},{low_half},"
                f"%ymm{high_reg},%xmm{high_reg},{high_half},"
                f"{24 * packet},{int(packet == 47)}"
            )
    lines.extend([".endm", ""])

    for swaps, label in sorted(half_masks.items()):
        mask = []
        for swap in swaps:
            mask.extend(range(8, 16) if swap else range(0, 8))
            mask.extend(range(0, 8) if swap else range(8, 16))
        lines.extend([".p2align 5", f"{label}:",
                      "\t.byte " + ",".join(map(str, mask))])
    asm_path.write_text("\n".join(lines))
    json_path.write_text(json.dumps({
        "schema": "ntruplus768-gt32-progressive-p-q24-pack-v1",
        "experiment": "GT32-KEYGEN-P-Q24-001",
        "input": "progressive-P coefficient-plane SoA, e=0, abs<=10788",
        "output": "Official canonical 1152-byte serialization",
        "global_P_to_standard_pass": False,
        "extra_cross_lane_shuffles": 48,
        "extra_shuffles_per_packet": 1,
        "spill_required": False,
        "packets": packets,
        "D1_wire_paired_terminal": {
            "zero_merge_candidate_exists": False,
            "evidence": "all 24 exact S4/S5 terminal candidates need four merges per block",
        },
        "D2_half_native_scatter": {
            "cross_half_merges": 0,
            "lane_local_qword_shuffles_per_block": 4,
            "packet_first_route_shuffles_removed_per_block": 4,
            "reducer_and_pack_arithmetic_unchanged": True,
            "source_first_giant_DAG": False,
            "groups": d2_groups,
            "assembly_eligible": True,
        },
        "TF1_transpose_tail_orientation": {
            "control_half_masks": tf1_mask_counts,
            "control_half_mask_instructions": 48,
            "identity_masks_removed": tf1_mask_counts["00"],
            "symmetric_masks_absorbed": tf1_mask_counts["11"],
            "residual_asymmetric_masks": tf1_residual_masks,
            "extra_instructions": 0,
            "expected_instruction_delta": -35,
            "assembly_eligible": True,
        },
        "SP1_next_block_preload": {
            "base": "TF1_transpose_tail_orientation",
            "preload_registers": ["ymm8", "ymm9", "ymm10", "ymm11"],
            "preload_point": "after-current-vpmulhrsw-before-vpmullw-correction",
            "instruction_delta": 0,
            "load_delta": 0,
            "store_delta": 0,
            "arithmetic_changed": False,
            "routing_changed": False,
            "spill_required": False,
            "assembly_eligible": True,
        },
        "decision": "D1-static-stop-D2-bounded-assembly-eligible",
    }, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=GENERATED /
                        "tile4_forward_landing_baseinv_gate.json")
    args = parser.parse_args()

    permutation_gate = json.loads((GENERATED /
        "tile4_permutation_native_gate.json").read_text())
    terminal_gate = json.loads((GENERATED /
        "tile4_terminal_layout_family_gate.json").read_text())
    checkpoint = checkpoint_search()
    mapping = mapping_proof(permutation_gate)
    emit_p_baseinv_tables(GENERATED / "tile4_baseinv_p_tables.inc",
                          mapping["P_private_q_order"])
    emit_p_mapping_header(GENERATED / "tile4_baseinv_p_mapping.h", mapping)
    emit_p_q24_pack(GENERATED / "tile4_q24_p_encode.inc",
                    GENERATED / "tile4_q24_p_encode_gate.json", mapping)

    standard_terminal = terminal_gate["current_full_soa_control"][
        "one_forward_terminal_shuffles"]
    p_terminal = terminal_gate["selected_exact_candidate"][
        "static_shuffles_per_16_quartic_block"]["one_forward_terminal"]
    blocks = 12
    p_saving = (standard_terminal - p_terminal) * blocks
    assert p_saving == 48

    result = {
        "schema": "ntruplus768-gt32-forward-landing-baseinv-001-v1",
        "experiment": "GT32-FWD-LANDING-BASEINV-001",
        "hypothesis_A_progressive_layout": {
            "status": "pass-existing-P-terminal-is-consumer-absorbable",
            "mathematical_form": "P_(i+1) * B_i * inverse(P_i)",
            "selected_cut": "stage4-packed-P -> stage5-P -> coefficient planes",
            "standard_private_terminal_shuffles_per_16_quartics":
                standard_terminal,
            "selected_P_terminal_shuffles_per_16_quartics": p_terminal,
            "removed_shuffles_per_forward": p_saving,
            "measured_prior_single_forward_saving_tsc": 3.402,
            "incremental_effect": "real-but-small",
            "why_no_earlier_degree_migration": (
                "S1-S3 butterflies permute Q while the coefficient-plane "
                "transpose permutes degree; these orthogonal index bits "
                "commute but do not share an AVX2 shuffle.  The first exact "
                "overlap is the already generated S4 reconstruct elision."
            ),
        },
        "hypothesis_B_proof_driven_reduction": {
            "status": "pass-two-vector-checkpoint-schedule-found",
            **checkpoint,
            "selected_schedule": (
                "after S1, center whole vectors 0 and 4 in every TILE4 tile"
            ),
            "effect": (
                "tightens the proven wide-raw N5 P/SoA output below the "
                "10643 direct BaseInv product limit"
            ),
        },
        "hypothesis_C_hybrid_keygen": {
            "status": "assembly-eligible-bounded-forward-probe",
            "pipeline": [
                "N5 frontend",
                "S1-S3 plus two proof-selected whole-vector centers",
                "P-domain progressive S4/S5 coefficient-plane landing",
                "Official-style SoA BaseInv with P-reordered metadata",
                "SoA scale-aware BaseMul",
                "Q24 GT-pack",
            ],
            "avoids": [
                "TILE4 AoS BaseInv transposes",
                "J1 AoS representation",
                "R1-U horizontal-dot consumer",
                "full 48-vector BaseInv center-on-load pass",
            ],
            "static_instruction_accounting_per_forward_BaseInv_edge": {
                "P_terminal_shuffle_saving": p_saving,
                "new_forward_checkpoint_cost":
                    checkpoint["dynamic_center_instructions_per_forward"],
                "removed_BaseInv_center_on_load_instructions": 144,
                "net_instruction_saving": p_saving -
                    checkpoint["dynamic_center_instructions_per_forward"] + 144,
            },
            "K3B_334_cycle_reopen_floor_applies": False,
            "reason": (
                "this is a different SoA BaseInv/SoA BM architecture and "
                "does not retain either measured K3-B loser"
            ),
            "next_gate": (
                "benchmark P forward with/without the selected checkpoints; "
                "then clone the proven SoA BaseInv schedule with reordered "
                "metadata only if the forward cost is bounded"
            ),
        },
        "mapping_proof": mapping,
        "assembly_candidate": {
            "symbol": "gt32_tile4_attr_forward_all_baseinv_p_l3_asm",
            "input": "N5 TILE4 frontend scratch, e=0",
            "output": ("P coefficient-plane SoA, e=0, abs<="
                       f"{checkpoint['selected']['terminal_max_abs_bound']}"),
            "spill_required": False,
            "new_masks": 0,
            "new_montgomery_chains": 0,
            "new_instructions_per_tile": 6,
            "production_selected": False,
        },
        "baseinv_table_artifact": "generated/tile4_baseinv_p_tables.inc",
        "mapping_header_artifact": "generated/tile4_baseinv_p_mapping.h",
        "P_q24_artifacts": [
            "generated/tile4_q24_p_encode.inc",
            "generated/tile4_q24_p_encode_gate.json",
        ],
        "continuation_gate": {
            "correctness": [
                "word congruent to existing P forward",
                "all generated bounds <=10643",
                "1000 random small-input trials",
            ],
            "performance_region": "full Forward candidate vs existing P Forward",
            "maximum_allowed_regression_tsc": 20,
            "reason": (
                "the downstream direct-BaseInv normalization removal is 144 "
                "instructions; a small Forward regression can be amortized"
            ),
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
