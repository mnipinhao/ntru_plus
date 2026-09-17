#!/usr/bin/env python3
"""Build the exact D3 VPMADDWD/MR32 feasibility ledger.

This is deliberately a gate, not an assembly generator.  It proves the
packed operand routes and the signed-dword Montgomery reduction, then prices
the complete tile against the selected 18-route P + official cubic BaseMul.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import random
import subprocess
import tempfile
from collections import Counter

Q = 3457
QINV = 12929
R = 1 << 16
I16_MIN = -(1 << 15)
I16_MAX = (1 << 15) - 1
I32_MIN = -(1 << 31)
I32_MAX = (1 << 31) - 1

PAIR_SPECS = {
    "s0": {"a": (1, 2), "b": (2, 1)},
    "s1": {"a": (0, 1), "b": (1, 0)},
    "s2": {"a": (0, 2), "b": (2, 0)},
}


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_halves() -> list[list[tuple[int, int]]]:
    words = [(q, j) for q in range(16) for j in range(3)]
    return [words[i : i + 8] for i in range(0, 48, 8)]


def shuf_mask(source: list[tuple[int, int]], desired: list[tuple[int, int]]) -> list[int]:
    index = {owner: i for i, owner in enumerate(source)}
    mask: list[int] = []
    for owner in desired:
        if owner in index:
            k = index[owner]
            mask.extend((2 * k, 2 * k + 1))
        else:
            mask.extend((0x80, 0x80))
    assert len(mask) == 16
    return mask


def simulate_mask(source: list[tuple[int, int]], desired: list[tuple[int, int]]) -> list[tuple[int, int] | None]:
    present = set(source)
    return [owner if owner in present else None for owner in desired]


def build_pair_routes() -> dict:
    halves = source_halves()
    # Original V0=(S0,S1) and V2=(S4,S5) are free.  C12 and C34 are the
    # only new half carriers and are shared by all three pair sums.
    bands = {
        "q00_07": ((0, 1), (1, 2), range(0, 8)),
        "q08_15": ((3, 4), (4, 5), range(8, 16)),
    }
    all_operands: dict[str, dict] = {}
    for operand in ("a", "b"):
        targets = []
        for sum_name, spec in PAIR_SPECS.items():
            js = spec[operand]
            for band_name, (pair0, pair1, qs) in bands.items():
                desired = [(q, j) for q in qs for j in js]
                assert len(desired) == 16
                low_desired, high_desired = desired[:8], desired[8:]
                carriers = []
                merged: list[tuple[int, int] | None] = [None] * 16
                for low_half, high_half in (pair0, pair1):
                    low = halves[low_half]
                    high = halves[high_half]
                    low_sim = simulate_mask(low, low_desired)
                    high_sim = simulate_mask(high, high_desired)
                    contribution = low_sim + high_sim
                    for i, owner in enumerate(contribution):
                        if owner is not None:
                            assert merged[i] is None
                            merged[i] = owner
                    carriers.append(
                        {
                            "halves": [low_half, high_half],
                            "low_vpshufb_mask": shuf_mask(low, low_desired),
                            "high_vpshufb_mask": shuf_mask(high, high_desired),
                        }
                    )
                assert merged == desired
                targets.append(
                    {
                        "sum": sum_name,
                        "band": band_name,
                        "coefficient_pair": list(js),
                        "desired_owners": [list(x) for x in desired],
                        "carriers": carriers,
                        "instructions": {"vpshufb": 2, "vpor": 1},
                    }
                )
        all_operands[operand] = {
            "new_shared_half_carriers": [[1, 2], [3, 4]],
            "carrier_instructions": 2,
            "targets": targets,
            "target_instructions": 18,
            "total_routes": 20,
        }
    return {
        "model": "vperm2i128 half carriers + lane-local vpshufb + disjoint vpor",
        "joint_reuse": "C12 and C34 are reused across s0, s1, and s2",
        "lower_bound": {
            "reason": "each of six target vectors per operand draws each 128-bit output lane from two distinct source halves, requiring at least two lane-local selections and one merge; the two non-native half pairings require at least two shared carriers",
            "per_operand": 2 + 6 * 3,
            "both_operands": 2 * (2 + 6 * 3),
        },
        "constructive_schedule": all_operands,
        "total_routes": 40,
    }


def product_interval(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    values = [x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1]]
    return min(values), max(values)


def add_interval(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return x[0] + y[0], x[1] + y[1]


def mr32_bounds() -> dict:
    canonical = (0, Q - 1)
    signed = (I16_MIN, I16_MAX)
    product = product_interval(canonical, signed)
    pair_sum = add_interval(product, product)
    t = (I16_MIN, I16_MAX)
    tq = product_interval(t, (Q, Q))
    numerator = (pair_sum[0] - tq[1], pair_sum[1] - tq[0])
    postshift = (numerator[0] // R, numerator[1] // R)
    return {
        "caller_contract": {
            "one_operand": list(canonical),
            "other_operand": list(signed),
            "covered": ["encapsulation poly_basemul", "decapsulation poly_basemul_scale", "decapsulation verification poly_basemul"],
            "not_covered": ["key-generation poly_basemul: both operands are transform/baseinv results"],
        },
        "vpmaddwd_pair_sum": list(pair_sum),
        "signed_i32_safe": I32_MIN <= pair_sum[0] <= pair_sum[1] <= I32_MAX,
        "signed_t": list(t),
        "t_times_q": list(tq),
        "subtraction_numerator": list(numerator),
        "subtraction_signed_i32_safe": I32_MIN <= numerator[0] <= numerator[1] <= I32_MAX,
        "postshift_conservative": list(postshift),
        "packssdw_non_saturating": I16_MIN <= postshift[0] <= postshift[1] <= I16_MAX,
        "q_times_qinv_mod_2_16": (Q * QINV) & 0xFFFF,
        "divisibility_identity": "S - int16(low16(S) * qinv) * q is divisible by 2^16",
        "montgomery_exponent": "one R^-1, identical to the existing 16-bit Montgomery product",
    }


def parse_baseline(path: pathlib.Path) -> dict:
    lines = path.read_text().splitlines()
    begin = lines.index("#positive zeta")
    end = next(i for i in range(begin, len(lines)) if lines[i].strip() == "add $96, %rdi")
    opcodes = []
    for raw in lines[begin:end]:
        line = raw.strip()
        if line and not line.startswith("#") and not line.startswith("."):
            opcodes.append(line.split()[0])
    counts = Counter(opcodes)
    expected = {"vpmullw": 14, "vpmulhw": 22, "vpsubw": 11, "vpaddw": 6, "vmovdqa": 12}
    assert all(counts[k] == v for k, v in expected.items())
    return {
        "selected_positive_zeta_tile_instructions": len(opcodes),
        "opcode_counts": dict(sorted(counts.items())),
        "ordinary_variable_montgomery_products": 9,
        "fixed_zeta_montgomery_products": 2,
        "qinv_premultiplies": 3,
        "arithmetic_instructions": 53,
        "memory_instructions": 12,
    }


def run_scalar_proof() -> dict:
    assert (Q * QINV) % R == 1
    rng = random.Random(0xD3864)
    checked = 0
    extrema = [0, Q - 1]
    signed_extrema = [I16_MIN, I16_MAX, -1, 0, 1]
    cases = []
    for a0 in extrema:
        for a1 in extrema:
            for b0 in signed_extrema:
                for b1 in signed_extrema:
                    cases.append((a0, a1, b0, b1))
    for _ in range(200_000):
        cases.append((rng.randrange(Q), rng.randrange(Q), rng.randrange(I16_MIN, I16_MAX + 1), rng.randrange(I16_MIN, I16_MAX + 1)))
    min_out, max_out = I32_MAX, I32_MIN
    for a0, a1, b0, b1 in cases:
        s = a0 * b0 + a1 * b1
        t = ((s & 0xFFFF) * QINV) & 0xFFFF
        if t >= 0x8000:
            t -= 0x10000
        numerator = s - t * Q
        assert numerator % R == 0
        out = numerator // R
        assert I16_MIN <= out <= I16_MAX
        assert (out * R - s) % Q == 0
        min_out, max_out = min(min_out, out), max(max_out, out)
        checked += 1
    return {"deterministic_cases": checked, "observed_postshift": [min_out, max_out], "seed": "0xD3864"}


def build_ledger(baseline: dict, pair_routes: dict) -> dict:
    # Candidate arithmetic: 3 packed diagonal Montgomery products (15 insns
    # including the same three qinv premultiplies), three 12-insn pair sums,
    # two 4-insn zeta products, and three final adds.
    candidate_arithmetic = 15 + 36 + 8 + 3
    candidate_output_routes = 18  # exact P network applied to packed diagonals
    baseline_total = 18 + baseline["selected_positive_zeta_tile_instructions"]
    # Use the same 12 input/constant/final-store memory instructions as the
    # official body.  This is optimistic for the candidate (q-even may need an
    # extra constant operand), so failure under this accounting is decisive.
    candidate_total_optimistic = pair_routes["total_routes"] + candidate_output_routes + candidate_arithmetic + baseline["memory_instructions"]
    return {
        "unit": "one Q16 x I3 tile; loop-control instructions excluded",
        "baseline": {
            "full_packed_to_plane_routes": 18,
            "pair_operand_formation": 0,
            "ordinary_variable_montgomery_products": 9,
            "vpmaddwd_data_products": 0,
            "mr32_instructions": 0,
            "repack_instructions": 0,
            "fixed_zeta_products": 2,
            "output_routing": 0,
            "spill_or_intermediate_materialization": 0,
            "peak_ymm": 16,
            "basemul_body_instructions": baseline["selected_positive_zeta_tile_instructions"],
            "total_instructions": baseline_total,
        },
        "candidate": {
            "full_packed_to_plane_routes": 0,
            "pair_operand_formation": 40,
            "ordinary_variable_montgomery_products": 3,
            "vpmaddwd_data_products": 6,
            "mr32_instructions": 24,
            "repack_instructions": 6,
            "fixed_zeta_products": 2,
            "output_routing": candidate_output_routes,
            "spill_or_intermediate_materialization": 0,
            "peak_ymm": 15,
            "peak_ymm_proof": "six packed inputs + four shared carriers + two completed pair sums + one low-half dword sum + two routed operands; MR32 constants are memory operands and its temporary reuses one routed-operand register",
            "arithmetic_instructions": candidate_arithmetic,
            "memory_instructions_optimistic": baseline["memory_instructions"],
            "total_instructions_optimistic": candidate_total_optimistic,
        },
        "delta_candidate_minus_baseline": candidate_total_optimistic - baseline_total,
        "static_risk_signal": {
            "arithmetic_delta_before_routing": candidate_arithmetic - baseline["arithmetic_instructions"],
            "pair_routing_minus_removed_P": pair_routes["total_routes"] - 18,
            "delta_before_required_output_routing": (candidate_arithmetic - baseline["arithmetic_instructions"]) + (pair_routes["total_routes"] - 18),
            "note": "candidate has more static instructions before its exact 18-route diagonal/output formation is charged; this is not a cycle proof because the instruction mix, port pressure, dependency depth, and overlap differ",
        },
        "inverse_handoff": "final c0/c1/c2 coefficient planes exactly match the existing inverse-entry physical ABI; no post-output adapter is needed, but extracting the three packed diagonal products costs the exact 18-route P network",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--basemul-source", type=pathlib.Path, required=True)
    parser.add_argument("--p3-map", type=pathlib.Path, required=True)
    parser.add_argument("--avx2-test", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    p3 = json.loads(args.p3_map.read_text())
    assert p3["parameter_report"]["actual_selected_boundary"]["forward_native_to_plane_routes_per_tile"] == 18
    pair_routes = build_pair_routes()
    baseline = parse_baseline(args.basemul_source)
    bounds = mr32_bounds()
    scalar = run_scalar_proof()
    ledger = build_ledger(baseline, pair_routes)
    decision = {
        "mr32_gate": "pass",
        "pair_routing_gate": "pass_exact_40_routes",
        "complete_tile_gate": "inconclusive_requires_machine_pricing",
        "asm_authorized": True,
        "asm_scope": "namespaced single-tile microkernel only",
        "benchmark_authorized": "same_elf_paired_tile_after_correctness_and_linked_audit",
        "full_integration_authorized": False,
        "reason": "the optimistic candidate is +49 static instructions/tile, but static instruction count cannot decide cycles across different multiply, shuffle, dword-reduction, and dependency structures",
    }
    report = {
        "schema": "ntruplus-d3-vpmaddwd-reduction-gate-v1",
        "checkpoint": "D3-VPMADDWD-REDUCTION-GATE",
        "parameter": 864,
        "constants": {"q": Q, "qinv": QINV, "R": R},
        "mr32": {"sequence": ["2 x vpmaddwd(data)", "2 x vpmullw(qinv)", "2 x vpmaddwd([q,0])", "2 x vpsubd", "2 x vpsrad(16)", "vpackssdw", "vpermq(0xd8)"], "instructions_per_pair_sum": 12, "bounds": bounds, "scalar_oracle": scalar},
        "joint_pair_routing": pair_routes,
        "official_tile": baseline,
        "complete_tile_ledger": ledger,
        "decision": decision,
        "scope": {"reduction_candidates": ["exact R=2^16 Montgomery"], "barrett_searched": False, "keygen_covered": False},
        "source_sha256": {"basemul.s": sha256(args.basemul_source), "p3_map": sha256(args.p3_map)},
    }
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        assert args.output.read_text() == encoded, f"stale generated file: {args.output}"
        if args.avx2_test:
            with tempfile.TemporaryDirectory(prefix="ntruplus864-d3-") as directory:
                binary = pathlib.Path(directory) / "test_d3_mr32"
                subprocess.run(["cc", "-O2", "-Wall", "-Wextra", "-Werror", "-mavx2", str(args.avx2_test), "-o", str(binary)], check=True)
                subprocess.run([str(binary)], check=True)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
    print(json.dumps({"decision": decision, "delta": ledger["delta_candidate_minus_baseline"], "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
