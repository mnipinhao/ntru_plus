#!/usr/bin/env python3
"""Prove which production inverse-final reduction chains can be shortened."""

from __future__ import annotations

import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONSTANTS = (
    ROOT
    / "asm/gt/invntt/poly_invntt_branchfold_constants_rminus1.inc"
)
RESULT_JSON = HERE / "result.json"
RESULT_MD = HERE / "result.md"

Q = 3457
CENTER = (Q - 1) // 2
BARRETT_MULTIPLIER = 19412
DFT3_TWIDDLE = -723
DFT3_PRECOMPUTE = -6853


def s16(value: int) -> int:
    return ((value + 0x8000) & 0xFFFF) - 0x8000


def sat16(value: int) -> int:
    return max(-0x8000, min(0x7FFF, value))


def sqdmulh(a: int, b: int) -> int:
    return sat16((a * b) >> 15)


def sqrdmulh(a: int, b: int) -> int:
    if a == -0x8000 and b == -0x8000:
        return 0x7FFF
    return sat16((a * b + (1 << 14)) >> 15)


def srshr(a: int, shift: int) -> int:
    return s16((a + (1 << (shift - 1))) >> shift)


def fqmul(value: int, normal: int, precompute: int) -> int:
    quotient = sqrdmulh(value, precompute)
    return s16(s16(value * normal) - s16(quotient * Q))


def barrett_quotient(value: int) -> int:
    return srshr(sqdmulh(value, BARRETT_MULTIPLIER), 11)


def barrett_reduce(value: int) -> int:
    return s16(value - barrett_quotient(value) * Q)


def mark_interval(diff: list[int], lo: int, hi: int, offset: int) -> None:
    diff[lo + offset] += 1
    diff[hi + offset + 1] -= 1


def reachable_post_dft3() -> dict[str, list[int]]:
    # Stage45 row-end Barrett reductions produce centered field elements.
    lo_limit = -3 * CENTER
    hi_limit = 3 * CENTER
    size = hi_limit - lo_limit + 1
    offset = -lo_limit
    v8_diff = [0] * (size + 1)
    v9_diff = [0] * (size + 1)

    for delta in range(-2 * CENTER, 2 * CENTER + 1):
        b_lo = max(-CENTER, -CENTER - delta)
        b_hi = min(CENTER, CENTER - delta)
        product = fqmul(delta, DFT3_TWIDDLE, DFT3_PRECOMPUTE)

        v8_lo = -CENTER - b_hi + product
        v8_hi = CENTER - b_lo + product
        v9_lo = -CENTER - b_hi - delta - product
        v9_hi = CENTER - b_lo - delta - product
        mark_interval(v8_diff, v8_lo, v8_hi, offset)
        mark_interval(v9_diff, v9_lo, v9_hi, offset)

    def materialize(diff: list[int]) -> list[int]:
        live = 0
        values = []
        for index in range(size):
            live += diff[index]
            if live:
                values.append(index - offset)
        return values

    return {
        "dft3_out0_v7": list(range(lo_limit, hi_limit + 1)),
        "dft3_out1_v8": materialize(v8_diff),
        "dft3_out2_v9": materialize(v9_diff),
    }


def parse_branchfold_constants() -> list[dict[str, object]]:
    rows: list[list[int]] = []
    for raw in CONSTANTS.read_text(encoding="ascii").splitlines():
        code = raw.split("//", 1)[0].strip()
        if not code.startswith(".hword"):
            continue
        values = [int(value) for value in re.findall(r"-?\d+", code)]
        if len(values) != 8:
            raise ValueError(f"expected eight constants: {raw}")
        rows.append(values)
    if len(rows) % 4:
        raise ValueError(f"constant row count is not divisible by four: {len(rows)}")

    entries = []
    for site in range(len(rows) // 4):
        normal_lo, pre_lo, normal_hi, pre_hi = rows[4 * site : 4 * site + 4]
        entries.append(
            {
                "site": site,
                "low": {
                    "normal": [normal_lo[0], normal_lo[4]],
                    "precompute": [pre_lo[0], pre_lo[4]],
                },
                "high": {
                    "normal": [normal_hi[0], normal_hi[4]],
                    "precompute": [pre_hi[0], pre_hi[4]],
                },
            }
        )
    return entries


def fq_image(
    inputs: list[int], normal: int, precompute: int
) -> dict[int, int]:
    image: dict[int, int] = {}
    for value in inputs:
        image.setdefault(fqmul(value, normal, precompute), value)
    return image


def sumset(left: dict[int, int], right: dict[int, int]) -> tuple[int, int, int]:
    left_values = sorted(left)
    right_values = sorted(right)
    right_min = right_values[0]
    right_bits = 0
    for value in right_values:
        right_bits |= 1 << (value - right_min)

    sum_min = left_values[0] + right_min
    bits = 0
    for value in left_values:
        bits |= right_bits << (value - left_values[0])
    return sum_min, bits, bits.bit_count()


def iter_sumset(sum_min: int, bits: int):
    while bits:
        lowest = bits & -bits
        bit = lowest.bit_length() - 1
        yield sum_min + bit
        bits ^= lowest


def find_pair(
    target: int, left: dict[int, int], right: dict[int, int]
) -> dict[str, int]:
    for left_output, left_input in left.items():
        right_output = target - left_output
        if right_output in right:
            return {
                "raw": target,
                "left_input": left_input,
                "right_input": right[right_output],
                "left_fqmul": left_output,
                "right_fqmul": right_output,
            }
    raise ValueError(f"sumset witness missing for {target}")


def analyze_chain(
    site: int,
    output_name: str,
    dft3_name: str,
    inputs: list[int],
    constants: dict[str, list[int]],
) -> dict[str, object]:
    left = fq_image(inputs, constants["normal"][0], constants["precompute"][0])
    right = fq_image(inputs, constants["normal"][1], constants["precompute"][1])
    sum_min, bits, cardinality = sumset(left, right)
    reachable = list(iter_sumset(sum_min, bits))

    delete_bad = next(
        (value for value in reachable if barrett_reduce(value) != value), None
    )
    direct_candidates = list(range(-0x8000, 0x8000))
    direct_failures = {}
    for value in reachable:
        wanted = barrett_quotient(value)
        direct_candidates = [
            multiplier
            for multiplier in direct_candidates
            if sqrdmulh(value, multiplier) == wanted
        ]
        if not direct_candidates:
            break
    for multiplier in (9, 10):
        bad = next(
            (
                value
                for value in reachable
                if sqrdmulh(value, multiplier) != barrett_quotient(value)
            ),
            None,
        )
        if bad is not None:
            direct_failures[str(multiplier)] = {
                **find_pair(bad, left, right),
                "wanted_quotient": barrett_quotient(bad),
                "direct_quotient": sqrdmulh(bad, multiplier),
            }

    result: dict[str, object] = {
        "site": site,
        "dft3_output": dft3_name,
        "branchfold_output": output_name,
        "constants": constants,
        "reachable_raw_min": reachable[0],
        "reachable_raw_max": reachable[-1],
        "reachable_raw_count": cardinality,
        "delete_final_barrett_safe": delete_bad is None,
        "direct_sqrdmulh_multipliers": direct_candidates,
    }
    if delete_bad is not None:
        result["delete_counterexample"] = {
            **find_pair(delete_bad, left, right),
            "reduced": barrett_reduce(delete_bad),
        }
    if not direct_candidates:
        result["direct_quotient_counterexamples"] = direct_failures
    return result


def main() -> None:
    post_sets = reachable_post_dft3()
    entries = parse_branchfold_constants()
    if len(entries) != 96:
        raise ValueError(f"expected 96 branchfold sites, got {len(entries)}")

    dft3_names = list(post_sets)
    chains = []
    for entry in entries:
        dft3_name = dft3_names[int(entry["site"]) % 3]
        for output_name in ("low", "high"):
            chains.append(
                analyze_chain(
                    int(entry["site"]),
                    output_name,
                    dft3_name,
                    post_sets[dft3_name],
                    entry[output_name],
                )
            )

    delete_safe = [chain for chain in chains if chain["delete_final_barrett_safe"]]
    direct_safe = [
        chain for chain in chains if chain["direct_sqrdmulh_multipliers"]
    ]
    result = {
        "model": {
            "q": Q,
            "stage45_centered_input": [-CENTER, CENTER],
            "dft3_reachable": {
                name: {
                    "min": values[0],
                    "max": values[-1],
                    "count": len(values),
                }
                for name, values in post_sets.items()
            },
            "branchfold_sites": len(entries),
            "final_barrett_chains": len(chains),
        },
        "instruction_accounting": {
            "post_dft3_v0": 32 * 3,
            "branchfold_fqmul_v0": 96 * 2 * 3,
            "final_barrett_v0": 96 * 2 * 3,
            "total_final_region_v0": 32 * 3 + 96 * 2 * 6,
            "delete_all_barrett_upper_bound": 96 * 2 * 3,
            "two_instruction_barrett_upper_bound": 96 * 2,
        },
        "summary": {
            "delete_final_barrett_safe_chains": len(delete_safe),
            "direct_two_instruction_barrett_safe_chains": len(direct_safe),
            "candidate_emitted": False,
            "decision": (
                "emit_candidate"
                if delete_safe or direct_safe
                else "stop_no_proof_backed_instruction_deletion"
            ),
        },
        "chains": chains,
    }
    RESULT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")

    first_delete = next(
        chain.get("delete_counterexample")
        for chain in chains
        if chain.get("delete_counterexample")
    )
    first_direct = next(
        chain.get("direct_quotient_counterexamples")
        for chain in chains
        if chain.get("direct_quotient_counterexamples")
    )
    markdown = f"""# Inverse final V0 arithmetic result

## Scope

This model covers the active rminus1 inverse final path:

```text
Stage45 centered row outputs
-> inverse DFT3
-> branchfold Montgomery products
-> final Barrett reductions
-> signed time-domain stores
```

It models the exact signed 16-bit behavior of `sqrdmulh`, `sqdmulh`, `srshr`,
`mul`, and `mls`. The three inverse-DFT3 output sets are constructed from every
triple in `[-{CENTER}, {CENTER}]^3`; the model then checks all 192 low/high
branchfold reduction chains and all production rminus1 constants. The
two-instruction quotient search covers all 65,536 signed 16-bit
`sqrdmulh` multipliers.

## Static cost

| Category | Dynamic V0 instructions per inverse |
|---|---:|
| inverse DFT3 multiply | {result["instruction_accounting"]["post_dft3_v0"]} |
| branchfold Montgomery multiply | {result["instruction_accounting"]["branchfold_fqmul_v0"]} |
| final Barrett reduction | {result["instruction_accounting"]["final_barrett_v0"]} |
| total final region | {result["instruction_accounting"]["total_final_region_v0"]} |

Deleting every final Barrett would save at most
{result["instruction_accounting"]["delete_all_barrett_upper_bound"]} vector
instructions. Replacing each three-instruction quotient/reduction with one
`sqrdmulh` quotient plus `mls` would save at most
{result["instruction_accounting"]["two_instruction_barrett_upper_bound"]}.

## Proof result

```text
delete-safe chains: {len(delete_safe)} / {len(chains)}
two-instruction direct-quotient chains: {len(direct_safe)} / {len(chains)}
decision: {result["summary"]["decision"]}
```

The first deletion counterexample is:

```json
{json.dumps(first_delete, indent=2)}
```

The direct `sqrdmulh` quotient candidates fail as well. Representative
counterexamples for multipliers 9 and 10 are:

```json
{json.dumps(first_direct, indent=2)}
```

Consequently, the current three-instruction final Barrett is not removable or
replaceable by a two-instruction direct-quotient form under the active inverse
contract. No ASM candidate is emitted.

## Interpretation

The existing implementation has already removed the intermediate post-DFT3
reductions and folded normalization, untwist, branch merge, and the rminus1
correction into the branchfold constants. The remaining reductions are doing
real representative work. A modulo-q-only deletion is insufficient because
the following `poly_crepmod3` is sensitive to changes by `q`, and `q = 3457`
is congruent to one modulo 3.

The previously tested fused inverse-plus-crep3 path reused the Barrett
quotient and was correct, but its same-path PMU result was slower. Reopening it
would require a new arithmetic DAG with fewer instructions, not another
wrapper or store/load fusion.
"""
    RESULT_MD.write_text(markdown, encoding="ascii")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
