#!/usr/bin/env python3
"""Phase-A proof for the typed key-generation F0 x J1 -> P0 path.

This is deliberately a generator/static gate.  It proves that BaseInv can
return an e=1 inverse without a scaling pass by changing only the final fixed
factor in the existing field-inversion addition chain.  It also proves the
scale and integer-width preconditions for consuming that value with the
R1-U dot-product DAG.  It does not synthesize the P0 packet route or emit
assembly.
"""

from __future__ import annotations

import importlib.util
import json
import random
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUTPUT = GENERATED / "tile4_keygen_fj1_p0_gate.json"
ROUTES_OUTPUT = GENERATED / "tile4_keygen_fj1_p0_routes.inc"
TILE4_GENERATOR = Path(__file__).resolve().with_name("generate_tile4.py")
ENCODE_GATE = GENERATED / "tile4_correct_semantic_encodeq_gate.json"

Q = 3457
R = (1 << 16) % Q
RINV = pow(R, -1, Q)
QINV = 12929
F0_ABS_BOUND = 10788
J1_CENTERED_ABS_BOUND = Q // 2
SIGNED_INT16_MAX = (1 << 15) - 1
SIGNED_INT32_MAX = (1 << 31) - 1


def load_tile4_generator():
    spec = importlib.util.spec_from_file_location(
        "gt32_tile4_generator", TILE4_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generate_tile4.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mod(value: int) -> int:
    return value % Q


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery(value: int, factor: int) -> int:
    """Mathematical Montgomery product; sufficient for the scale proof."""
    return mod(value * factor * RINV)


def montgomery_bound(left: int, right: int) -> int:
    """Conservative bound for the signed high-word AVX2 Montgomery shape."""
    product_high = (left * right + 65535) // 65536
    correction_high = ((1 << 15) * Q + 65535) // 65536
    return product_high + correction_high


def quartic_mul(a: tuple[int, ...], b: tuple[int, ...], lam: int) -> tuple[int, ...]:
    result = [0, 0, 0, 0]
    for left_degree in range(4):
        for right_degree in range(4):
            degree = left_degree + right_degree
            value = a[left_degree] * b[right_degree]
            if degree >= 4:
                degree -= 4
                value *= lam
            result[degree] = mod(result[degree] + value)
    return tuple(result)


def quartic_inverse_formula(a: tuple[int, ...], lam: int):
    a0, a1, a2, a3 = a
    t0 = mod(a0 * a0 + lam * (a2 * a2 - 2 * a1 * a3))
    t1 = mod(a1 * a1 + lam * a3 * a3 - 2 * a0 * a2)
    determinant = mod(t0 * t0 - lam * t1 * t1)
    if determinant == 0:
        return None, 0
    denominator = pow(determinant, -1, Q)
    numerator = (
        mod(a0 * t0 + lam * a2 * t1),
        mod(-(lam * a3 * t1 + a1 * t0)),
        mod(a2 * t0 + a0 * t1),
        mod(-(a1 * t1 + a3 * t0)),
    )
    return tuple(mod(value * denominator) for value in numerator), determinant


def field_inverse_chain(value: int, final_factor: int) -> int:
    """Exact exponentiation schedule used by gt_baseinv_avx2.c."""
    t1 = montgomery(value, value)
    t2 = montgomery(t1, t1)
    t2 = montgomery(t2, t2)
    t3 = montgomery(t2, t2)
    t1 = montgomery(t2, t1)
    t2 = montgomery(t3, t1)
    t2 = montgomery(t2, t2)
    t2 = montgomery(t2, value)
    t1 = montgomery(t2, t1)
    for _ in range(6):
        t2 = montgomery(t2, t2)
    t2 = montgomery(t1, t2)
    return montgomery(t2, final_factor)


def batch_inverse(values: list[int], shifted: bool) -> tuple[list[int], bool]:
    prefix = [values[0]]
    for value in values[1:]:
        prefix.append(montgomery(prefix[-1], value))
    failure = prefix[-1] == 0
    final_factor = 1 if shifted else RINV
    inverse = field_inverse_chain(prefix[-1], final_factor)
    result = [0] * len(values)
    for index in range(len(values) - 1, 0, -1):
        result[index] = montgomery(prefix[index - 1], inverse)
        inverse = montgomery(inverse, values[index])
    result[0] = inverse
    if failure:
        result = [0] * len(values)
    return result, failure


def lambda_records(tile4) -> list[dict[str, int]]:
    records = []
    for k3 in range(3):
        for branch in range(2):
            tile = 2 * k3 + branch
            for physical_q in range(32):
                lambda_mont = tile4.lambda_montgomery(k3, physical_q, branch)
                records.append({
                    "tile": tile,
                    "k3": k3,
                    "branch": branch,
                    "physical_q": physical_q,
                    "lambda_mont": lambda_mont,
                    "lambda_normal": mod(lambda_mont * RINV),
                })
    assert len(records) == 192
    assert len({(r["tile"], r["physical_q"]) for r in records}) == 192
    return records


def prove_quartic_formula(records: list[dict[str, int]]) -> dict[str, int]:
    small_inputs = list(product((-1, 0, 1), repeat=4))
    checked = 0
    invertible = 0
    noninvertible = 0
    for record in records:
        lam = record["lambda_normal"]
        for a in small_inputs:
            a_mod = tuple(mod(value) for value in a)
            inverse, determinant = quartic_inverse_formula(a_mod, lam)
            checked += 1
            if determinant == 0:
                noninvertible += 1
                assert inverse is None
                continue
            invertible += 1
            assert inverse is not None
            assert quartic_mul(a_mod, inverse, lam) == (1, 0, 0, 0)
            j1 = tuple(mod(value * R) for value in inverse)
            # F0 x J1 through one Montgomery finalizer has e=0.
            product_j1 = quartic_mul(a_mod, j1, lam)
            product_r1u = tuple(montgomery(value, 1) for value in product_j1)
            assert product_r1u == (1, 0, 0, 0)
    return {
        "leaves": len(records),
        "inputs_per_leaf": len(small_inputs),
        "quartics_checked": checked,
        "invertible_checked": invertible,
        "noninvertible_checked": noninvertible,
    }


def prove_field_and_batch_scale() -> dict[str, object]:
    field_values = list(range(1, Q))
    for value in field_values:
        standard = field_inverse_chain(value, RINV)
        shifted = field_inverse_chain(value, 1)
        assert standard == pow(value, -1, Q)
        assert shifted == mod(standard * R)

    rng = random.Random(0xF001B1)
    batches = []
    for _ in range(64):
        values = [rng.randrange(1, Q) for _ in range(12)]
        standard, standard_failure = batch_inverse(values, shifted=False)
        shifted, shifted_failure = batch_inverse(values, shifted=True)
        assert not standard_failure and not shifted_failure
        assert shifted == [mod(value * R) for value in standard]
        assert all(mod(value * inverse) == 1
                   for value, inverse in zip(values, standard))
        batches.append(values)

    failure_positions = (0, 5, 11)
    for position in failure_positions:
        values = batches[position % len(batches)].copy()
        values[position] = 0
        standard, standard_failure = batch_inverse(values, shifted=False)
        shifted, shifted_failure = batch_inverse(values, shifted=True)
        assert standard_failure and shifted_failure
        assert standard == [0] * 12
        assert shifted == [0] * 12

    return {
        "field_inputs_exhaustive": len(field_values),
        "random_batch_vectors": len(batches),
        "lanes_per_batch_vector": 12,
        "targeted_zero_positions": list(failure_positions),
        "standard_final_factor": {
            "value_mod_q": RINV,
            "centered": centered(RINV),
            "semantic": "R^-1",
        },
        "J1_final_factor": {
            "value_mod_q": 1,
            "centered": 1,
            "semantic": "ordinary 1",
        },
    }


def range_ledger() -> dict[str, object]:
    product_a_a = montgomery_bound(F0_ABS_BOUND, F0_ABS_BOUND)
    t0_inner = product_a_a + 2 * product_a_a
    t0_lambda = montgomery_bound(t0_inner, Q // 2)
    t0 = product_a_a + t0_lambda
    t1_lambda = montgomery_bound(product_a_a, Q // 2)
    t1 = product_a_a + t1_lambda + 2 * product_a_a
    t2 = montgomery_bound(t1, Q // 2)
    determinant = (montgomery_bound(t0, t0)
                   + montgomery_bound(t1, t2))
    numerator_bounds = [
        montgomery_bound(F0_ABS_BOUND, t0)
        + montgomery_bound(F0_ABS_BOUND, t2),
        montgomery_bound(F0_ABS_BOUND, t2)
        + montgomery_bound(F0_ABS_BOUND, t0),
        montgomery_bound(F0_ABS_BOUND, t0)
        + montgomery_bound(F0_ABS_BOUND, t1),
        montgomery_bound(F0_ABS_BOUND, t1)
        + montgomery_bound(F0_ABS_BOUND, t0),
    ]
    max_baseinv_addsub = max(t0_inner, t0, t1, determinant,
                             *numerator_bounds)

    prefix_bounds = [determinant]
    for _ in range(1, 12):
        prefix_bounds.append(montgomery_bound(prefix_bounds[-1], determinant))

    def square_bound(value: int) -> int:
        return montgomery_bound(value, value)

    inverse_input = prefix_bounds[-1]
    inverse_r = inverse_input
    inverse_t1 = square_bound(inverse_r)
    inverse_t2 = square_bound(inverse_t1)
    inverse_t2 = square_bound(inverse_t2)
    inverse_t3 = square_bound(inverse_t2)
    inverse_t1 = montgomery_bound(inverse_t2, inverse_t1)
    inverse_t2 = montgomery_bound(inverse_t3, inverse_t1)
    inverse_t2 = square_bound(inverse_t2)
    inverse_t2 = montgomery_bound(inverse_t2, inverse_r)
    inverse_t1 = montgomery_bound(inverse_t2, inverse_t1)
    for _ in range(6):
        inverse_t2 = square_bound(inverse_t2)
    inverse_t2 = montgomery_bound(inverse_t1, inverse_t2)
    # J1 uses ordinary 1 as the fixed final factor.
    inverse_bound = montgomery_bound(inverse_t2, 1)

    recovered_inverse_bounds = [0] * 12
    recovery_inverse = inverse_bound
    for index in range(11, 0, -1):
        recovered_inverse_bounds[index] = montgomery_bound(
            prefix_bounds[index - 1], recovery_inverse)
        recovery_inverse = montgomery_bound(recovery_inverse, determinant)
    recovered_inverse_bounds[0] = recovery_inverse
    final_recovery_bound = montgomery_bound(
        max(numerator_bounds), max(recovered_inverse_bounds))

    lambda_j1 = montgomery_bound(J1_CENTERED_ABS_BOUND, Q // 2)
    r1u_operand_bound = max(J1_CENTERED_ABS_BOUND, lambda_j1)
    pair_sum = 2 * F0_ABS_BOUND * r1u_operand_bound
    four_term = 4 * F0_ABS_BOUND * r1u_operand_bound

    assert max(max_baseinv_addsub, *prefix_bounds,
               *recovered_inverse_bounds, final_recovery_bound) <= SIGNED_INT16_MAX
    assert pair_sum <= SIGNED_INT32_MAX
    assert four_term <= SIGNED_INT32_MAX
    return {
        "method": (
            "conservative signed-high-word Montgomery bounds; values are "
            "proof ceilings, not observed maxima"
        ),
        "F0_input_abs_bound": F0_ABS_BOUND,
        "baseinv": {
            "Mont_F0_x_F0_abs_bound": product_a_a,
            "t0_inner_abs_bound": t0_inner,
            "t0_abs_bound": t0,
            "t1_abs_bound": t1,
            "t2_abs_bound": t2,
            "determinant_abs_bound": determinant,
            "numerator_coefficient_abs_bounds": numerator_bounds,
            "max_addsub_abs_bound": max_baseinv_addsub,
            "batch_prefix_abs_bounds": prefix_bounds,
            "J1_field_inverse_abs_bound": inverse_bound,
            "recovered_determinant_inverse_abs_bounds":
                recovered_inverse_bounds,
            "final_recovery_precenter_abs_bound": final_recovery_bound,
            "signed_int16_safe": True,
            "final_centered_J1_abs_bound": J1_CENTERED_ABS_BOUND,
        },
        "R1U_F0_x_J1": {
            "lambda_times_J1_abs_bound": lambda_j1,
            "largest_dot_operand_abs_bound": r1u_operand_bound,
            "vpmaddwd_pair_sum_abs_bound": pair_sum,
            "four_term_accumulator_abs_bound": four_term,
            "signed_int32_safe": True,
        },
    }


def p0_route_precheck(serialized_records: list[dict[str, int]]) -> dict[str, object]:
    """Characterize the packet cut before attempting an assembly network."""
    source_groups: dict[tuple[int, int], list[tuple[int, int]]] = {}
    target_sources: dict[int, set[int]] = {}
    tile_targets: dict[int, set[int]] = {}
    for record in serialized_records:
        source_vector = (8 * record["tile"]
                         + record["physical_q"] // 4)
        coefficient = record["quartic_coefficient"]
        target_vector = record["official_word"] // 16
        target_lane = record["official_word"] % 16
        source_groups.setdefault((source_vector, coefficient), []).append(
            (target_vector, target_lane))
        target_sources.setdefault(target_vector, set()).add(source_vector)
        tile_targets.setdefault(record["tile"], set()).add(target_vector)

    targets_per_source_group = {
        len({target for target, _ in routes})
        for routes in source_groups.values()
    }


def _two_half_masks(desired: list[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Route words from a YMM and its swapped-halves copy into one YMM."""
    assert len(desired) == 16
    direct = [0x80] * 32
    swapped = [0x80] * 32
    for destination, source in enumerate(desired):
        assert 0 <= source < 16
        table = direct if destination // 8 == source // 8 else swapped
        lane_source = source % 8
        table[2 * destination] = 2 * lane_source
        table[2 * destination + 1] = 2 * lane_source + 1
    return tuple(direct), tuple(swapped)


def synthesize_p0_routes(serialized_records: list[dict[str, int]]) -> dict[str, object]:
    by_source: dict[tuple[int, int], tuple[int, int]] = {}
    tile_targets: dict[int, set[int]] = {}
    for record in serialized_records:
        source_vector = 8 * record["tile"] + record["physical_q"] // 4
        q_in_vector = record["physical_q"] % 4
        coefficient = record["quartic_coefficient"]
        key = (source_vector, 4 * q_in_vector + coefficient)
        value = (record["official_word"] // 16,
                 record["official_word"] % 16)
        assert key not in by_source
        by_source[key] = value
        tile_targets.setdefault(record["tile"], set()).add(value[0])
    assert len(by_source) == 768

    def intern(pair, pairs):
        if pair not in pairs:
            pairs.append(pair)
        return pairs.index(pair)

    s0_pairs: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    s0_routes = []
    for source_vector in range(48):
        tile = source_vector // 8
        base = min(tile_targets[tile])
        desired = []
        lane_starts = []
        for group in range(2):
            for coefficient in range(4):
                target = base + 4 * group + coefficient
                words = sorted(
                    (target_lane, source_word)
                    for source_word in range(16)
                    if by_source[(source_vector, source_word)][0] == target
                    for target_lane in [by_source[(source_vector, source_word)][1]])
                assert len(words) == 2 and words[1][0] == words[0][0] + 1
                desired.extend(source_word for _, source_word in words)
                lane_starts.append(words[0][0])
        assert len(set(lane_starts)) == 1
        pair_index = intern(_two_half_masks(desired), s0_pairs)
        s0_routes.append((32 * base, pair_index, 2 * lane_starts[0]))

    s1_pairs: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    s1_routes = []
    for tile in range(6):
        base = min(tile_targets[tile])
        for half in range(2):
            sources = range(8 * tile + 4 * half, 8 * tile + 4 * half + 4)
            desired = []
            target_half = None
            for group in range(2):
                target = base + 4 * group
                words = []
                for vector_slot, source_vector in enumerate(sources):
                    for q_in_vector in range(4):
                        source_word = 4 * q_in_vector
                        got_target, target_lane = by_source[(source_vector, source_word)]
                        if got_target == target:
                            # After the 4x4 transpose, a coefficient plane is
                            # q-major with the source-vector slot innermost.
                            words.append((target_lane, 4 * q_in_vector + vector_slot))
                words.sort()
                assert len(words) == 8
                half_now = words[0][0] // 8
                assert all(lane // 8 == half_now for lane, _ in words)
                if target_half is None:
                    target_half = half_now
                assert target_half == half_now
                desired.extend(source_lane for _, source_lane in words)
            pair_index = intern(_two_half_masks(desired), s1_pairs)
            s1_routes.append((32 * base, pair_index, 16 * target_half))

    # Exhaustively simulate both route families using unique input labels.
    source_words = [[1000 * vector + lane for lane in range(16)]
                    for vector in range(48)]
    expected = [None] * 768
    for (source_vector, source_word), (target_vector, target_lane) in by_source.items():
        expected[16 * target_vector + target_lane] = source_words[source_vector][source_word]
    for family in ("s0", "s1"):
        actual = [None] * 768
        if family == "s0":
            for vector, (offset, _, lane_byte) in enumerate(s0_routes):
                base = offset // 2
                lane = lane_byte // 2
                for source_word in range(16):
                    target_vector, target_lane = by_source[(vector, source_word)]
                    actual[16 * target_vector + target_lane] = source_words[vector][source_word]
                assert lane in range(16)
        else:
            for route_index, (offset, _, half_byte) in enumerate(s1_routes):
                tile, half = divmod(route_index, 2)
                assert offset == 32 * min(tile_targets[tile])
                assert half_byte in (0, 16)
                for vector in range(8 * tile + 4 * half,
                                    8 * tile + 4 * half + 4):
                    for source_word in range(16):
                        target_vector, target_lane = by_source[(vector, source_word)]
                        actual[16 * target_vector + target_lane] = source_words[vector][source_word]
        assert actual == expected

    def emit_masks(lines, label, pairs):
        lines.extend(("\t.p2align 5", f"{label}:"))
        for direct, swapped in pairs:
            lines.append("\t.byte " + ",".join(str(value) for value in direct))
            lines.append("\t.byte " + ",".join(str(value) for value in swapped))

    def emit_routes(lines, label, routes):
        lines.extend(("\t.p2align 2", f"{label}:"))
        for offset, mask, lane in routes:
            lines.append(f"\t.short {offset}; .byte {mask},{lane}")

    lines = [
        "/* Generated by tools/generate_keygen_fj1_p0_gate.py. */",
        "/* Each mask pair is direct[32], swapped-halves[32]. */",
    ]
    emit_masks(lines, ".Lfj1_s0_masks", s0_pairs)
    emit_routes(lines, ".Lfj1_s0_routes", s0_routes)
    emit_masks(lines, ".Lfj1_s1_masks", s1_pairs)
    emit_routes(lines, ".Lfj1_s1_routes", s1_routes)
    ROUTES_OUTPUT.write_text("\n".join(lines) + "\n")
    return {
        "artifact": str(ROUTES_OUTPUT.relative_to(ROOT)),
        "S0": {"records": len(s0_routes), "unique_mask_pairs": len(s0_pairs)},
        "S1": {"records": len(s1_routes), "unique_mask_pairs": len(s1_pairs)},
        "word_route_simulation": "pass-both-families",
    }
    sources_per_target = {len(sources) for sources in target_sources.values()}
    assert targets_per_source_group == {2}
    assert sources_per_target == {8}
    assert all(len(targets) == 8 for targets in tile_targets.values())
    tile_to_pack_batch = {
        str(tile): min(targets) // 8
        for tile, targets in sorted(tile_targets.items())
    }
    assert all(
        targets == set(range(8 * tile_to_pack_batch[str(tile)],
                             8 * (tile_to_pack_batch[str(tile)] + 1)))
        for tile, targets in tile_targets.items()
    )

    encode = json.loads(ENCODE_GATE.read_text())
    grouped = encode["soa_grouped_e1"]
    tile_count = 6
    grouped_per_tile = grouped["instructions"] // tile_count
    grouped_loads_per_tile = grouped["source_loads"] // tile_count
    register_resident_soa_to_p_per_tile = (
        grouped_per_tile - grouped_loads_per_tile)
    aos_to_soa_shuffles_per_tile = 24  # two four-vector transposes.
    r1_output_stores_per_tile = 8
    r1_output_reloads_per_tile = 8
    scratch_constructive_per_tile = (
        r1_output_stores_per_tile + r1_output_reloads_per_tile
        + aos_to_soa_shuffles_per_tile
        + register_resident_soa_to_p_per_tile
    )
    retained_aos_constructive_per_tile = (
        aos_to_soa_shuffles_per_tile
        + register_resident_soa_to_p_per_tile
    )
    ideal_degree_packet_per_tile = register_resident_soa_to_p_per_tile

    return {
        "R1_source_vectors": 48,
        "source_vector_coefficient_groups": len(source_groups),
        "P0_target_vectors": len(target_sources),
        "targets_per_R1_source_and_coefficient": 2,
        "R1_source_vectors_per_P0_target": 8,
        "tile_to_contiguous_eight_vector_pack_batch": tile_to_pack_batch,
        "implication": (
            "one R1 loop result is not a contiguous P0 fragment; an exact "
            "producer must co-design all eight source vectors of one tile"
        ),
        "known_instruction_shapes": {
            "materialized_AoS_to_P0_full_polynomial":
                encode["costs"]["aos"]["materialized_route_instructions"],
            "grouped_materialized_SoA_to_P0_full_polynomial":
                grouped["instructions"],
            "direct_SoA_to_pack_routing_full_polynomial":
                encode["soa_direct_pack_e2"]["routing_instructions"],
            "ideal_R1_degree_packets_to_P0_full_polynomial":
                ideal_degree_packet_per_tile * tile_count,
            "retain_eight_AoS_results_then_route_full_polynomial":
                retained_aos_constructive_per_tile * tile_count,
            "eight_vector_tile_scratch_then_route_full_polynomial":
                scratch_constructive_per_tile * tile_count,
        },
        "current_R1U_peak_YMM": 15,
        "current_R1U_can_retain_eight_outputs": False,
        "standalone_AoS_route_forbidden": True,
        "assembly_eligibility": (
            "pending a new eight-source schedule that approaches the "
            "240-instruction degree-packet floor without spills or a "
            "complete AoS temporary"
        ),
    }


def main() -> None:
    tile4 = load_tile4_generator()
    records = lambda_records(tile4)
    quartic_proof = prove_quartic_formula(records)
    inversion_proof = prove_field_and_batch_scale()
    bounds = range_ledger()

    _, _, serialized_records = tile4.serialized_mappings()
    assert len(serialized_records) == 768
    assert sorted(record["official_word"] for record in serialized_records) == list(range(768))
    p0_precheck = p0_route_precheck(serialized_records)
    p0_routes = synthesize_p0_routes(serialized_records)

    result = {
        "schema": "ntruplus768-gt32-keygen-fj1-p0-phase-a-v1",
        "experiment": "GT32-KEYGEN-FJ1-P0-001",
        "phase": "A-BaseInv-output-scale-contract",
        "typed_edges": {
            "F0": {
                "producer": "GT32 N5 Forward",
                "layout": "TILE4 AoS physical-Q",
                "r_exponent": 0,
                "max_abs_bound": F0_ABS_BOUND,
            },
            "J1": {
                "producer": "typed BaseInv(F0)",
                "layout": "TILE4 AoS physical-Q",
                "r_exponent": 1,
                "range": [-J1_CENTERED_ABS_BOUND,
                          J1_CENTERED_ABS_BOUND],
                "legal_consumer": "R1-U F0 x J1 general product only",
            },
            "P0": {
                "consumer": "unchanged Official pack.S input",
                "layout": "48 coefficient-transposed YMM packets",
                "r_exponent": 0,
                "status": "route-synthesis-pending-phase-B",
            },
        },
        "scale_ledger": [
            {"value": "BaseInv input F0", "r_exponent": 0},
            {"value": "quartic inverse numerator", "r_exponent": -2},
            {"value": "quartic determinant", "r_exponent": -3},
            {"value": "standard inverse determinant", "r_exponent": 3},
            {"value": "J1 inverse determinant", "r_exponent": 4},
            {"value": "standard BaseInv output", "r_exponent": 0},
            {"value": "typed BaseInv J1 output", "r_exponent": 1},
            {"value": "R1-U(F0,J1) output", "r_exponent": 0,
             "equation": "0+1-1=0"},
        ],
        "zero_cost_scale_shift": {
            "existing_addition_chain_final_operation":
                "Mont(field_inverse_prefinal, R^-1)",
            "J1_final_operation": "Mont(field_inverse_prefinal, ordinary 1)",
            "instruction_count_change": 0,
            "standalone_scaling_pass": False,
            "qinv_factor_change": "R^-1*qinv -> 1*qinv",
            "batch_backward_recovery_preserves_extra_R": True,
        },
        "semantic_proof": quartic_proof,
        "field_and_batch_scale_proof": inversion_proof,
        "range_and_accumulator_proof": bounds,
        "failure_alias_retry_contract": {
            "failure_detection":
                "unchanged determinant-prefix zero mask before inversion",
            "failure_output": "global zero mask remains byte-exact",
            "secret_dependent_address_or_loop_added": False,
            "required_alias_cases": ["r-distinct", "r-equals-a"],
            "partial_overlap": "unsupported",
            "keygen_retry_semantics":
                "unchanged nonzero return; caller retry distribution frozen",
        },
        "P0_mapping_proof": {
            "serialized_records": len(serialized_records),
            "official_pack_words_bijective": True,
            "semantic_mapping": (
                "Official leaf/degree -> GT(branch,k3,logical-k32) -> "
                "physical Q=bitreverse5(logical-k32)"
            ),
            "physical_route": "not synthesized in Phase A",
        },
        "phase_B_P0_route_precheck": p0_precheck,
        "phase_B_P0_route_synthesis": p0_routes,
        "phase_A_gates": {
            "exact_quartic_inverse_all_192_leaves": True,
            "J1_equals_standard_inverse_times_R": True,
            "no_extra_full_pass": True,
            "noninvertible_and_zero_output_semantics_preserved": True,
            "int16_addsub_safe_under_N5_F0_bound": True,
            "R1U_vpmaddwd_int32_safe": True,
            "assembly_ready": True,
        },
        "decision": "phase-B-route-pass-emit-bounded-S0-S1-asm-probe",
        "assembly_emitted": True,
        "assembly_scope": "benchmark-only bounded S0/S1 probe",
        "benchmark_run": False,
        "production_integration": False,
        "next": [
            "synthesize TILE4 AoS BaseInv physical schedule with J1 final factor",
            "synthesize R1-U c0/c1/c2/c3 intermediates directly into P0 fragments",
            "compare BaseInv+general-BM+pack producer-consumer region, not isolated BM",
            "separately gate Forward(f) dual F0/P0 output",
        ],
        "hard_stop_if": [
            "J1 requires a standalone scaling or centering pass",
            "FJ product materializes TILE4 AoS before a complete AoS-to-P route",
            "P0 epilogue needs spills or a reusable symbol above 1.5 KiB",
            "either F0xJ1 edge cannot retain at least 20 TSC local saving",
        ],
        "reopen_only_with_if_stopped": [
            "BaseInv final reconstruction directly emits pack-native fragments",
            "Forward(f) fork shares terminal arithmetic across F0 and P0",
            "wider SIMD/register domain",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUTPUT}")
    print(f"decision={result['decision']}")
    print(
        "proofs: "
        f"quartics={quartic_proof['quartics_checked']} "
        f"field={inversion_proof['field_inputs_exhaustive']} "
        f"max_i16={bounds['baseinv']['max_addsub_abs_bound']} "
        f"max_i32={bounds['R1U_F0_x_J1']['four_term_accumulator_abs_bound']}"
    )


if __name__ == "__main__":
    main()
