#!/usr/bin/env python3
"""Consumer-aware range gate for the checkpoint-free NTT32 from gate 128."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
I16_MAX = 32767
CURRENT_FORWARD_BOUND = 18424
SELECTED_FRONTEND_BOUND = 5275
DECODED_H_BOUND = Q - 1
RSQ = 867


def ceil_div(value: int, divisor: int) -> int:
    return (value + divisor - 1) // divisor


def mont_bound(a_bound: int, factor_bound: int) -> int:
    return ceil_div(a_bound * factor_bound, 1 << 16) + ceil_div(Q, 2)


def label_shorts(source: str, label: str) -> list[int]:
    tail = source.split(f"{label}:", 1)[1]
    lines: list[str] = []
    for line in tail.splitlines():
        stripped = line.strip()
        if stripped.startswith(".section") or (
                stripped.startswith(".L") and stripped.endswith(":")):
            break
        lines.append(line)
    values: list[int] = []
    for line in lines:
        if ".short" in line:
            values.extend(int(value) for value in
                          re.findall(r"-?\d+", line.split(".short", 1)[1]))
    return values


def quartic_bounds(r_bound: int, m_bound: int, lambda_bound: int) -> dict:
    product = mont_bound(DECODED_H_BOUND, r_bound)
    raw = [
        mont_bound(3 * product, lambda_bound) + product,
        mont_bound(2 * product, lambda_bound) + 2 * product,
        mont_bound(product, lambda_bound) + 3 * product,
        4 * product,
    ]
    final = [mont_bound(value, RSQ) for value in raw]
    summed = [value + m_bound for value in final]
    return {
        "runtime_product": product,
        "raw_degree": raw,
        "final_degree": final,
        "product_plus_m": summed,
        "signed_i16_safe": max(raw + final + summed) <= I16_MAX,
    }


def quartic_mul(a: list[int], b: list[int], lam: int) -> list[int]:
    return [
        (a[0] * b[0] + lam * (a[1] * b[3] + a[2] * b[2] + a[3] * b[1])) % Q,
        (a[1] * b[0] + a[0] * b[1] + lam * (a[3] * b[2] + a[2] * b[3])) % Q,
        (a[2] * b[0] + a[1] * b[1] + a[0] * b[2] + lam * a[3] * b[3]) % Q,
        (a[3] * b[0] + a[2] * b[1] + a[1] * b[2] + a[0] * b[3]) % Q,
    ]


def bitreverse(value: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (value & 1)
        value >>= 1
    return result


def stage_pairs(stage: int) -> list[tuple[int, int]]:
    distance = 32 >> stage
    pairs = []
    for group in range(0, 32, 2 * distance):
        for offset in range(distance):
            pairs.append((group + offset, group + offset + distance))
    return sorted(pairs)


def mont_factor(power: int) -> int:
    omega32 = pow(675, 3, Q)
    value = pow(omega32, power, Q) * R % Q
    return value - Q if value > Q // 2 else value


def propagate_selected_frontend(candidate: dict) -> dict:
    bounds = [SELECTED_FRONTEND_BOUND] * 32
    first_failure = None
    stage_maxima = []
    for stage in range(1, 6):
        output = bounds[:]
        pairs = stage_pairs(stage)
        for packet in range(4):
            packet_pairs = pairs[4 * packet:4 * packet + 4]
            mode = candidate["modes_by_stage"][stage - 1][packet]
            powers = candidate["factor_powers_by_stage"][stage - 1][packet]
            packet_mont = any(powers)
            for lane, (low, high) in enumerate(packet_pairs):
                low_bound, high_bound = bounds[low], bounds[high]
                factor = abs(mont_factor(powers[lane]))
                if mode == "CT":
                    product = (mont_bound(high_bound, factor)
                               if packet_mont else high_bound)
                    pre_add = low_bound + product
                    values = [pre_add, pre_add]
                else:
                    pre_add = low_bound + high_bound
                    product = (mont_bound(pre_add, factor)
                               if packet_mont else pre_add)
                    values = [pre_add, product]
                if first_failure is None and max(pre_add, *values) > I16_MAX:
                    first_failure = {
                        "stage": stage, "packet": packet, "lane": lane,
                        "pair": [low, high], "mode": mode,
                        "input_bounds": [low_bound, high_bound],
                        "pre_add_bound": pre_add,
                        "output_bounds": values,
                    }
                output[low], output[high] = values
        bounds = output
        stage_maxima.append(max(bounds))
    return {
        "input_abs_bound": SELECTED_FRONTEND_BOUND,
        "stage_maxima_without_machine_wrap": stage_maxima,
        "signed_i16_proven": first_failure is None,
        "first_proof_failure": first_failure,
        "note": "conservative interval failure is not an executable counterexample",
    }


def consumer_oracle(lambda_values: list[int], cases: int = 4096) -> dict:
    rng = random.Random(0x130)
    checked_words = 0
    for _ in range(cases):
        a = [rng.randrange(Q) for _ in range(4)]
        r_control = [rng.randrange(Q) for _ in range(4)]
        # Gate 128 proves the mixed network has the same terminal residues.
        # Exercise arbitrary signed representatives of those residues here.
        r_candidate = [value + rng.choice((-2, -1, 0, 1, 2)) * Q
                       for value in r_control]
        m_control = [rng.randrange(Q) for _ in range(4)]
        m_candidate = [value + rng.choice((-3, -2, -1, 0, 1, 2, 3)) * Q
                       for value in m_control]
        lam = lambda_values[rng.randrange(len(lambda_values))] % Q
        control = quartic_mul(a, r_control, lam)
        candidate = quartic_mul(a, r_candidate, lam)
        for degree in range(4):
            assert candidate[degree] == control[degree]
            assert (candidate[degree] + m_candidate[degree]) % Q == (
                control[degree] + m_control[degree]) % Q
            checked_words += 1
    return {
        "cases": cases,
        "degree_words_checked": checked_words,
        "R1_general_B3_mod_q_exact": True,
        "R2_B3_plus_m_mod_q_exact": True,
    }


def build(root: Path) -> dict:
    search128 = json.loads((root / "experiments/gt32_mixed_ctgs_range_128/generated/search.json").read_text())
    proof032 = json.loads((root / "experiments/gt32_encap_b3_addm_032/generated/proof.json").read_text())
    candidate = search128["nearest_range_candidates"][0]
    assert candidate["mode_bits"] == "00000000100000000000"
    assert candidate["range"]["all_i16_safe"]
    assert candidate["range"]["montgomery_packets"] == 14
    assert proof032["range"]["forward_stage_bounds"]["S5_M_terminal"] == CURRENT_FORWARD_BOUND

    lambda_values = label_shorts((root / "basemul.s").read_text(),
                                 ".Ltile4_bm_lambda")
    assert len(lambda_values) == 12 * 16
    candidate_q = candidate["range"]["final_bounds"]
    assert len(candidate_q) == 32

    profiles = {}
    profile_inputs = {
        "R0_production": (CURRENT_FORWARD_BOUND, CURRENT_FORWARD_BOUND),
        "R1_r_checkpoint_free": (candidate_q, CURRENT_FORWARD_BOUND),
        "R2_r_and_m_checkpoint_free": (candidate_q, candidate_q),
    }
    for name, (r_bounds, m_bounds) in profile_inputs.items():
        records = []
        maxima = {"runtime_product": 0, "raw_degree": 0,
                  "final_degree": 0, "product_plus_m": 0}
        all_safe = True
        for physical_q, lam in enumerate(lambda_values):
            logical_q = physical_q % 32
            rb = r_bounds if isinstance(r_bounds, int) else r_bounds[logical_q]
            mb = m_bounds if isinstance(m_bounds, int) else m_bounds[logical_q]
            bounds = quartic_bounds(rb, mb, abs(lam))
            all_safe &= bounds["signed_i16_safe"]
            maxima["runtime_product"] = max(maxima["runtime_product"], bounds["runtime_product"])
            maxima["raw_degree"] = max(maxima["raw_degree"], *bounds["raw_degree"])
            maxima["final_degree"] = max(maxima["final_degree"], *bounds["final_degree"])
            maxima["product_plus_m"] = max(maxima["product_plus_m"], *bounds["product_plus_m"])
            records.append({"physical_q": physical_q, "logical_q": logical_q,
                            "lambda": lam, "r_bound": rb, "m_bound": mb,
                            **bounds})
        profiles[name] = {
            "maxima": maxima,
            "all_signed_i16_safe": all_safe,
            "Q24_full_signed_i16_contract_satisfied": all_safe,
            "per_physical_q": records,
        }

    selected_frontend_gate = propagate_selected_frontend(candidate)
    passed = (all(profile["all_signed_i16_safe"] for profile in profiles.values())
              and selected_frontend_gate["signed_i16_proven"])
    return {
        "schema": "ntruplus768-gt32-consumer-aware-forward-reduction-v1",
        "experiment": "GT32-CONSUMER-AWARE-FORWARD-REDUCTION-130",
        "production_modified": False,
        "candidate_from_128": {
            "mode_bits": candidate["mode_bits"],
            "modes_by_stage": candidate["modes_by_stage"],
            "factor_powers_by_stage": candidate["factor_powers_by_stage"],
            "terminal_max_abs_bound": candidate["range"]["final_max_abs_bound"],
            "terminal_bounds_by_logical_q": candidate_q,
            "all_intermediates_signed_i16_safe": candidate["range"]["all_i16_safe"],
            "montgomery_packets_per_tile": candidate["range"]["montgomery_packets"],
            "oracle_mod_q_exact": candidate["oracle_mod_q_exact"],
        },
        "corrected_consumer_contract": {
            "historical_128_B3_bound": 10788,
            "status": "stale scalar ceiling, not the selected executable contract",
            "selected_forward_conservative_bound": CURRENT_FORWARD_BOUND,
            "selected_B3_plus_m_conservative_bound": proof032["range"]["maximum"],
            "Q24_reducer": "proven for every signed int16 input by 032R",
        },
        "conditional_128_input_consumer_profiles": profiles,
        "selected_frontend_input_gate": selected_frontend_gate,
        "consumer_oracle": consumer_oracle(lambda_values),
        "static_delta": {
            "removed_S2_identity_Montgomery_packets_per_tile": 2,
            "tiles_per_Forward": 6,
            "removed_vector_Montgomery_chains_per_Forward": 12,
            "removed_vector_instructions_per_chain": 4,
            "estimated_removed_vector_instructions_per_Forward": 48,
            "hidden_terminal_center_or_reduction": 0,
            "B3_or_Q24_operation_added": 0,
        },
        "generator_gate_pass": passed,
        "decision": ("continue-zero-spill-asm" if passed else
                     "pause-fast-asm-selected-frontend-range-proof-fails"),
        "claim_limit": "range/correctness gate only; cycles require executable adjudication",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build(args.root.resolve())
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if args.output.read_text() != rendered:
            raise SystemExit("generated consumer-aware proof is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(json.dumps({
        "experiment": result["experiment"],
        "candidate_terminal_bound": result["candidate_from_128"]["terminal_max_abs_bound"],
        "R1_max": result["conditional_128_input_consumer_profiles"]["R1_r_checkpoint_free"]["maxima"],
        "R2_max": result["conditional_128_input_consumer_profiles"]["R2_r_and_m_checkpoint_free"]["maxima"],
        "selected_frontend_input_gate": result["selected_frontend_input_gate"],
        "generator_gate_pass": result["generator_gate_pass"],
        "decision": result["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
