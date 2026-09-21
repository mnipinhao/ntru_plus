#!/usr/bin/env python3
"""Encap-first architecture gate for the NTRU+768 Forward redesign.

This gate deliberately does not emit assembly.  It combines the qualified
machine evidence for the three authorized design families and adds the one
new domain-specific proof needed by this campaign: whether N32-first can omit
its row-0 repair when the input is an actual Encap r/m polynomial in [-1,1].
"""

from __future__ import annotations

import functools
import json

import generate_n32_bm_inv_joint_range_gate as joint_range
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_forward_redesign_gate.json"
INT16_MAX = 32767
ENCAP_INPUT = (-1, 1)

Interval = tuple[int, int]


def add(a: Interval, b: Interval) -> Interval:
    return a[0] + b[0], a[1] + b[1]


def sub(a: Interval, b: Interval) -> Interval:
    return a[0] - b[1], a[1] - b[0]


def peak(a: Interval) -> int:
    return max(abs(a[0]), abs(a[1]))


@functools.lru_cache(maxsize=None)
def mont_interval(low: int, high: int, factor: int) -> Interval:
    values = [gt.montgomery_fixed(value, factor)
              for value in range(low, high + 1)]
    return min(values), max(values)


def top_interval(branch: int) -> Interval:
    values = []
    for low in range(ENCAP_INPUT[0], ENCAP_INPUT[1] + 1):
        for high in range(ENCAP_INPUT[0], ENCAP_INPUT[1] + 1):
            product = -722 * high
            values.append(low + product if branch == 0
                          else low + high - product)
    return min(values), max(values)


def n32_rows(branch: int) -> tuple[list[list[list[Interval]]], list[int]]:
    """Exact interval execution of the emitted conjugated NTT32 schedule."""
    scale = gt.BRANCH_SCALE[branch]
    residual = [[
        pow(scale, -((64 * row + 33 * q) % 96), gt.Q)
        for q in range(32)
    ] for row in range(3)]
    initial = top_interval(branch)
    rows = [[[initial for _degree in range(4)] for _q in range(32)]
            for _row in range(3)]
    for stage in range(1, 6):
        distance = 32 >> stage
        next_residual = [row[:] for row in residual]
        next_rows = [[lane[:] for lane in row] for row in rows]
        for row in range(3):
            for group in range(0, 32, 2 * distance):
                zeta = pow(gt.OMEGA32,
                           gt.forward_power(stage, group), gt.Q)
                for lane in range(distance):
                    low_q = group + lane
                    high_q = low_q + distance
                    normal = (zeta * residual[row][high_q]
                              * pow(residual[row][low_q], -1, gt.Q)) % gt.Q
                    factor = gt.centered(normal * gt.R)
                    for degree in range(4):
                        low = rows[row][low_q][degree]
                        high = rows[row][high_q][degree]
                        product = mont_interval(*high, factor)
                        next_rows[row][low_q][degree] = add(low, product)
                        next_rows[row][high_q][degree] = sub(low, product)
                    next_residual[row][high_q] = residual[row][low_q]
        rows = next_rows
        residual = next_residual
    factors = []
    for row in residual:
        assert len(set(row)) == 1
        factors.append(gt.centered(row[0] * gt.R))
    assert factors[0] == gt.centered(gt.R)
    return rows, factors


def n32_encap_range_gate() -> dict[str, object]:
    outputs: list[list[int]] = []
    branches = []
    all_forward_safe = True
    for branch in range(2):
        rows, factors = n32_rows(branch)
        maxima = [0, 0, 0]
        worst = 0
        for q in range(32):
            for degree in range(4):
                row0 = rows[0][q][degree]
                row1 = mont_interval(*rows[1][q][degree], factors[1])
                row2 = mont_interval(*rows[2][q][degree], factors[2])
                difference = sub(row1, row2)
                omega = mont_interval(*difference, -886)
                y0 = add(add(row0, row1), row2)
                y1 = add(sub(row0, row2), omega)
                y2 = sub(sub(row0, row1), omega)
                intermediates = (row0, row1, row2, difference, omega,
                                 y0, y1, y2)
                worst = max(worst, *(peak(value) for value in intermediates))
                for output, value in enumerate((y0, y1, y2)):
                    maxima[output] = max(maxima[output], peak(value))
        all_forward_safe &= worst <= INT16_MAX
        outputs.append(maxima)
        branches.append({
            "branch": branch,
            "raw_top_interval": list(top_interval(branch)),
            "row_residual_montgomery_factors": factors,
            "DFT3_output_abs_bounds": maxima,
            "DFT3_worst_intermediate_abs_bound": worst,
        })

    intervals, basemul = joint_range.derive_r1u_intervals(outputs)
    inverse = joint_range.prove_inverse(intervals)
    inverse_stages = [record["max_output_abs_bound"]
                      for record in inverse["global_stage_output_abs_bounds"]]
    closes = (all_forward_safe
              and basemul["maximum_output_abs_bound"] <= INT16_MAX
              and inverse["all_frontiers_signed_int16_safe"])
    return {
        "input_domain": "actual Encap r/m coefficients [-1,1]",
        "method": (
            "exact enumeration of every fixed-factor signed Montgomery product "
            "over propagated intervals, followed by the qualified R1-U/inverse proof"
        ),
        "branches": branches,
        "Forward_signed_int16_safe": all_forward_safe,
        "R1U_max_abs_bound": basemul["maximum_output_abs_bound"],
        "inverse_IDFT3_internal_abs_bound": inverse[
            "global_IDFT3_internal_addsub_abs_bound"],
        "inverse_stage_abs_bounds": inverse_stages,
        "inverse_all_frontiers_signed_int16_safe": inverse[
            "all_frontiers_signed_int16_safe"],
        "zero_row0_repair_contract_closes": closes,
        "failure": None if closes else (
            "small input shrinks the raw top split, but the raw representative "
            "still violates the frozen R1-U/inverse signed-i16 contract"
        ),
    }


def family_a() -> dict[str, object]:
    dependency = json.loads((gt.GENERATED /
        "tile4_frontend_dependency_schedule_gate.json").read_text())
    wave = json.loads((gt.GENERATED /
        "tile4_wavefront_schedule_gate.json").read_text())
    # One frontend iteration emits one vector into each of six terminal tiles.
    # A tile becomes executable only after all eight iterations.  With the
    # current frontend macro already at peak 16, retaining even one completed
    # vector across the next iteration requires a new allocation/schedule.
    return {
        "name": "A-GT3-first-joint-frontend-NTT32",
        "qualified_control": "materialized frontend -> six terminal tiles",
        "dependency_geometry": {
            "frontend_iterations": 8,
            "terminal_tiles": 6,
            "vectors_emitted_per_iteration": 6,
            "vectors_required_before_one_terminal_tile_can_start": 8,
            "materialized_boundary_vector_stores": 48,
            "materialized_boundary_vector_reloads": 48,
        },
        "tested_schedules": {
            "dependency_only_F14": dependency["local_results"][
                "F14_eight_launch_two_placements"],
            "next_packet_preload_W2": wave["candidates"]["F14_W2"],
        },
        "current_macro_peak_YMM": 16,
        "one_or_two_tile_persistence": (
            "not allocatable by merely retaining current outputs; it requires a "
            "different frontend circuit or a deliberate spill/reload schedule"
        ),
        "decision": "no-new-ASM",
        "reason": (
            "The only executable current-DAG wavefronts hide latency but remove no "
            "store/reload or dependency layer.  W2 is explicitly excluded and no "
            "new allocation mechanism closes the 16-register frontier."
        ),
    }


def family_c() -> dict[str, object]:
    landing = json.loads((gt.GENERATED /
        "tile4_forward_official_landing_gate.json").read_text())
    encap = json.loads((gt.GENERATED /
        "tile4_encap_representation_architecture_gate.json").read_text())
    return {
        "name": "C-Official-like-hybrid-consumer-landing",
        "GT_to_Official_landing": landing["static_cost"],
        "GT_to_Official_decision": landing["gate"],
        "M_to_distinct_final_P_best": encap["best_distinct_P"],
        "decision": "no-new-ASM",
        "reason": (
            "The exact Official landing mixes five or six source-half routes per "
            "target and adds 576 routing instructions over the private terminal. "
            "The bounded Encap final-layout search also finds no distinct P that "
            "beats retaining M.  A new hybrid needs a direct consumer DAG, not a bridge."
        ),
    }


def main() -> None:
    b = n32_encap_range_gate()
    result = {
        "schema": "ntruplus768-forward-redesign-gate-v1",
        "experiment": "NTRUPLUS768-FORWARD-REDESIGN-001",
        "frozen": {
            "Official": "SUPERCOP-20260831 crypto_kem/ntruplus768/avx2",
            "current_GT": "avx2-gt32-clean",
            "external_wire_and_API": True,
            "terminal_quartic_factors": True,
            "output_Montgomery_exponent": 0,
        },
        "consumer_contracts": {
            "r": "coeff -> arithmetic M state plus exact hash-input bytes",
            "m": "coeff -> transformed M addend -> h*r+m -> exact ciphertext bytes",
            "h": "validated Q24 PK bytes -> M leaves with matching lambda identity",
        },
        "families": {
            "A": family_a(),
            "B": {
                "name": "B-N32-first-interleaved-GT",
                "new_mechanism": "specialize representative proof to Encap [-1,1]",
                "range_gate": b,
                "decision": "no-new-ASM" if not b[
                    "zero_row0_repair_contract_closes"] else "ASM-eligible",
                "reason": b["failure"],
            },
            "C": family_c(),
        },
        "prototype_budget": 2,
        "prototypes_emitted": 0,
        "decision": "stop-after-gates-no-qualified-new-mechanism",
        "why_zero_prototypes_is_correct": (
            "The plan permits fewer than two prototypes.  A removes no complete "
            "boundary with the allocatable schedule, B fails the actual Encap "
            "consumer range contract, and C pays a larger exact bridge than it removes."
        ),
        "retained_research_baseline": (
            "current GT remains the Forward/Encap research baseline; existing F14 "
            "is a benchmark-only dependency schedule, not a new decomposition"
        ),
    }
    # Preserve the original evidence, but retract the unsupported inference.
    # Actual Encap has no R1-U/inverse edge, and a failed interval proof is not
    # a reachable counterexample. Neither a fixed 16-register allocation nor
    # bridge instruction counts reject the full A/C design families.
    result['historical_decision'] = result['decision']
    result['historical_rationale'] = result.pop('why_zero_prototypes_is_correct')
    result['decision'] = 'A-reopened-in-range-wavefront-002;B-C-deferred-not-rejected'
    result['schema'] = 'ntruplus768-forward-redesign-gate-v2-corrected-scope'
    for key, scope in {
        'A': 'fixed prior allocation only; partial D16/D8 readiness was not tested',
        'B': 'R1-U/inverse proof is not the actual Encap consumer; no overflow witness',
        'C': 'specific bridge counts only; no cycle proof or direct-hybrid machine test',
    }.items():
        family = result['families'][key]
        family['historical_decision'] = family['decision']
        family['historical_reason'] = family['reason']
        family['decision'] = 'superseded-by-wavefront-002' if key == 'A' else 'deferred'
        family['reason'] = scope
    result['superseding_artifacts'] = [
        'tile4_encap_range_closure.json', 'tile4_encap_wavefront_search.json']
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
