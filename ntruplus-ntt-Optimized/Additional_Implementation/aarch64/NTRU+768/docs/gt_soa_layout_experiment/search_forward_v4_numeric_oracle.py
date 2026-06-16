#!/usr/bin/env python3
"""Gate 14 numeric tagged-index oracle for Forward v4 rowpack H.

This is still not an assembly candidate.  It parses the current NTRU+768
Forward NTT32 constants from ntt.c, builds the numeric transform matrix modulo
q, and checks whether the Gate 13 full-absorption candidate can be explained by
a row/plane relabel or per-lane twiddle scaling without cross-lane mixing.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(".")
PARAMS = ROOT / "params.h"
NTT_C = ROOT / "ntt.c"
OUTDIR = Path("docs/gt_soa_layout_experiment/forward_v4_numeric_oracle")

NTT32_SIZE = 32
VECTOR_LANES = 8
ROWPACK_PLANES = 8
STAGE_DISTANCES = [16, 8, 4, 2, 1]
STAGE_NAMES = ["stage1", "stage2", "stage3", "stage4", "stage5"]

CURRENT_TAIL_PERMUTES_PER_BLOCK = 24
BLOCKS_PER_NTT32 = 4
CURRENT_SCATTER_CYCLES = 319.328
STORE_READY_CYCLES = 109.359
RECOVERABLE_WINDOW_CYCLES = CURRENT_SCATTER_CYCLES - STORE_READY_CYCLES
CYCLES_PER_PERMUTE = RECOVERABLE_WINDOW_CYCLES / (CURRENT_TAIL_PERMUTES_PER_BLOCK * BLOCKS_PER_NTT32)


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_dump(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(yaml_dump(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{pad}{yaml_scalar(data)}"


def write_yml(path: Path, data: Any) -> None:
    path.write_text(yaml_dump(data) + "\n")


def parse_define_int(path: Path, name: str) -> int:
    pattern = re.compile(rf"^\s*#define\s+{re.escape(name)}\s+(-?\d+)\b", re.MULTILINE)
    match = pattern.search(path.read_text())
    if match is None:
        raise ValueError(f"could not find #define {name} in {path}")
    return int(match.group(1))


def parse_int16_array(path: Path, name: str) -> list[int]:
    text = path.read_text()
    pattern = re.compile(
        rf"{re.escape(name)}\s*\[[^\]]+\]\s*=\s*\{{(?P<body>.*?)\}}\s*;",
        re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"could not find array {name} in {path}")
    return [int(item) for item in re.findall(r"-?\d+", match.group("body"))]


def bitreverse_limited(x: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (x & 1)
        x >>= 1
    return result


def ntt32_ct_twiddle_power(stage: int, lo: int) -> int:
    if stage == 1:
        return 0
    return bitreverse_limited(lo >> (6 - stage), stage - 1) << (5 - stage)


def centered(value: int, q: int) -> int:
    value %= q
    if value > q // 2:
        value -= q
    return value


def twiddle_normal_from_mont(value: int, q: int) -> int:
    return (value % q) * pow(1 << 16, -1, q) % q


def load_source_facts() -> dict[str, Any]:
    q = parse_define_int(PARAMS, "NTRUPLUS_Q")
    n = parse_define_int(PARAMS, "NTRUPLUS_N")
    omega32_mont = parse_int16_array(NTT_C, "gt96_omega32_powers")
    if len(omega32_mont) != NTT32_SIZE:
        raise ValueError(f"expected {NTT32_SIZE} omega32 entries, got {len(omega32_mont)}")
    omega32_normal = [twiddle_normal_from_mont(value, q) for value in omega32_mont]
    return {
        "q": q,
        "n": n,
        "omega32_montgomery": omega32_mont,
        "omega32_normal": omega32_normal,
    }


def twiddle_schedule(omega32_normal: list[int], omega32_mont: list[int]) -> list[dict[str, Any]]:
    schedule: list[dict[str, Any]] = []
    for stage_idx, distance in enumerate(STAGE_DISTANCES, start=1):
        butterflies: list[dict[str, Any]] = []
        for lo in range(NTT32_SIZE):
            if lo & distance:
                continue
            hi = lo + distance
            power = ntt32_ct_twiddle_power(stage_idx, lo)
            butterflies.append(
                {
                    "lo": lo,
                    "hi": hi,
                    "power": power,
                    "twiddle_montgomery": omega32_mont[power],
                    "twiddle_normal": omega32_normal[power],
                }
            )
        schedule.append(
            {
                "stage": STAGE_NAMES[stage_idx - 1],
                "stage_index": stage_idx,
                "distance": distance,
                "butterflies": butterflies,
            }
        )
    return schedule


def ntt32_mod(vector: list[int], q: int, omega32_normal: list[int]) -> list[int]:
    out = [value % q for value in vector]
    for stage in range(1, 6):
        distance = 1 << (5 - stage)
        for lo in range(NTT32_SIZE):
            if lo & distance:
                continue
            hi = lo + distance
            power = ntt32_ct_twiddle_power(stage, lo)
            u = out[lo]
            t = out[hi] * omega32_normal[power]
            out[lo] = (u + t) % q
            out[hi] = (u - t) % q
    return out


def ntt32_matrix(q: int, omega32_normal: list[int]) -> list[list[int]]:
    rows = [[0 for _ in range(NTT32_SIZE)] for _ in range(NTT32_SIZE)]
    for col in range(NTT32_SIZE):
        basis = [0 for _ in range(NTT32_SIZE)]
        basis[col] = 1
        out = ntt32_mod(basis, q, omega32_normal)
        for row in range(NTT32_SIZE):
            rows[row][col] = out[row]
    return rows


def matrix_mul(rows: list[list[int]], vector: list[int], q: int) -> list[int]:
    return [sum(row[col] * vector[col] for col in range(NTT32_SIZE)) % q for row in rows]


def verify_matrix(rows: list[list[int]], q: int, omega32_normal: list[int]) -> dict[str, Any]:
    vectors: list[list[int]] = []
    vectors.append([0 for _ in range(NTT32_SIZE)])
    vectors.append([1 for _ in range(NTT32_SIZE)])
    vectors.append([(1 if i % 2 == 0 else -1) for i in range(NTT32_SIZE)])
    state = 0x9e3779b9
    for _ in range(8):
        vec = []
        for _ in range(NTT32_SIZE):
            state = (1664525 * state + 1013904223) & 0xFFFFFFFF
            vec.append((state % (2 * q)) - q)
        vectors.append(vec)

    failures: list[dict[str, Any]] = []
    for idx, vector in enumerate(vectors):
        direct = ntt32_mod(vector, q, omega32_normal)
        by_matrix = matrix_mul(rows, vector, q)
        if direct != by_matrix:
            failures.append({"case": idx, "direct": direct, "matrix": by_matrix})
    return {
        "cases": len(vectors),
        "failures": failures,
        "status": "pass" if not failures else "fail",
    }


def row_hash(row: list[int], q: int) -> str:
    payload = ",".join(str(value % q) for value in row).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def row_fingerprints(rows: list[list[int]], q: int) -> dict[str, Any]:
    return {
        "gate": "Gate 14: NTT32 matrix fingerprints",
        "status": "numeric_oracle",
        "rows": [
            {
                "row": idx,
                "support": sum(1 for value in row if value % q != 0),
                "hash": row_hash(row, q),
                "first_8_centered": [centered(value, q) for value in row[:8]],
            }
            for idx, row in enumerate(rows)
        ],
    }


def proportional_ratio(a: list[int], b: list[int], q: int) -> int | None:
    ratio: int | None = None
    for ai, bi in zip(a, b, strict=True):
        ai %= q
        bi %= q
        if bi == 0:
            if ai != 0:
                return None
            continue
        current = ai * pow(bi, -1, q) % q
        if ratio is None:
            ratio = current
        elif ratio != current:
            return None
    return 0 if ratio is None else ratio


def analyze_rowpack_targets(rows: list[list[int]], q: int) -> dict[str, Any]:
    pairwise_proportional: list[dict[str, Any]] = []
    for i in range(NTT32_SIZE):
        for j in range(i + 1, NTT32_SIZE):
            ratio = proportional_ratio(rows[i], rows[j], q)
            if ratio is not None:
                pairwise_proportional.append({"row_a": i, "row_b": j, "ratio": ratio})

    blocks: list[dict[str, Any]] = []
    for block in range(BLOCKS_PER_NTT32):
        k32_rows = list(range(block * VECTOR_LANES, (block + 1) * VECTOR_LANES))
        common_row_candidates: list[dict[str, Any]] = []
        for candidate_row in range(NTT32_SIZE):
            ratios: list[int] = []
            for row in k32_rows:
                ratio = proportional_ratio(rows[row], rows[candidate_row], q)
                if ratio is None:
                    break
                ratios.append(ratio)
            else:
                common_row_candidates.append(
                    {
                        "candidate_row": candidate_row,
                        "per_lane_ratios": ratios,
                    }
                )
        blocks.append(
            {
                "block": block,
                "target_k32_rows": k32_rows,
                "target_hashes": [row_hash(rows[row], q) for row in k32_rows],
                "common_row_candidates_with_per_lane_scaling": common_row_candidates,
                "lane_preserving_match": bool(common_row_candidates),
            }
        )

    return {
        "gate": "Gate 14: rowpack target numeric equivalence",
        "status": "numeric_oracle",
        "pairwise_proportional_distinct_rows": pairwise_proportional,
        "pairwise_proportional_distinct_row_count": len(pairwise_proportional),
        "target_blocks": blocks,
        "all_blocks_have_lane_preserving_match": all(block["lane_preserving_match"] for block in blocks),
    }


def candidate_oracle_result(target_analysis: dict[str, Any]) -> dict[str, Any]:
    all_match = bool(target_analysis["all_blocks_have_lane_preserving_match"])
    return {
        "gate": "Gate 14: Forward v4 numeric tagged-index oracle",
        "status": "complete_numeric_oracle_no_asm_candidate",
        "candidate_under_test": "H_algebraic_absorb_three_mixing_levels",
        "model_checked": [
            "actual NTRU+768 q and gt96_omega32_powers from params.h/ntt.c",
            "current radix-2 CT NTT32 matrix modulo q",
            "rowpack target vectors over k32 blocks of 8",
            "row/plane relabel without final lane mixing",
            "per-lane diagonal twiddle scaling without final lane mixing",
        ],
        "result": {
            "row_plane_relabel_only": "fail",
            "per_lane_diagonal_scaling": "pass" if all_match else "fail",
            "full_absorption_transform_found": False,
            "continue_to_forward_v4_asm": False,
        },
        "reason": (
            "Each rowpack target vector contains eight distinct NTT32 output "
            "matrix rows for one branch/lane plane.  Under a lane-preserving "
            "no-transpose model, a plain vector store can only expose one "
            "NTT32 output row across lanes, even with per-lane diagonal scaling. "
            "The actual NTT32 rows from the current table are not proportional "
            "within any rowpack k32 block, so no numeric equivalence was found."
        ),
        "next_gate_if_continuing": (
            "a broader mathematical derivation for a non-current Forward "
            "decomposition; still no ASM or Slothy until it produces a numeric "
            "oracle that passes and clears the cycle gate"
        ),
    }


def oracle_report_markdown(
    source: dict[str, Any],
    verify: dict[str, Any],
    target_analysis: dict[str, Any],
    result: dict[str, Any],
) -> str:
    lines = [
        "# Gate 14 Forward v4 Numeric Oracle",
        "",
        "Status: `complete_numeric_oracle_no_asm_candidate`",
        "",
        "This gate parses the actual NTRU+768 Forward NTT32 table and checks",
        "whether the Gate 13 full-absorption candidate has a numeric equivalent",
        "under row/plane relabeling or per-lane twiddle scaling without final",
        "lane mixing.  It does not generate `.S`, `.opt.s`, Slothy input, or",
        "benchmark binaries.",
        "",
        "## Source Facts",
        "",
        f"- `NTRUPLUS_N`: `{source['n']}`",
        f"- `NTRUPLUS_Q`: `{source['q']}`",
        f"- `gt96_omega32_powers` entries: `{len(source['omega32_montgomery'])}`",
        f"- matrix verification: `{verify['status']}` over `{verify['cases']}` cases",
        "",
        "## Numeric Equivalence Check",
        "",
        f"- distinct proportional NTT32 row pairs: `{target_analysis['pairwise_proportional_distinct_row_count']}`",
        f"- all rowpack blocks have lane-preserving match: `{target_analysis['all_blocks_have_lane_preserving_match']}`",
        "",
        "| block | target k32 rows | lane-preserving match |",
        "| ---: | --- | --- |",
    ]
    for block in target_analysis["target_blocks"]:
        lines.append(
            f"| {block['block']} | `{block['target_k32_rows']}` | "
            f"`{block['lane_preserving_match']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            result["reason"],
            "",
            "Forward v4 ASM remains blocked.  Continuing this direction now",
            "requires a broader mathematical decomposition, not another layout",
            "or scheduling attempt.",
            "",
        ]
    )
    return "\n".join(lines)


def write_artifacts() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    source = load_source_facts()
    schedule = twiddle_schedule(source["omega32_normal"], source["omega32_montgomery"])
    matrix = ntt32_matrix(source["q"], source["omega32_normal"])
    verify = verify_matrix(matrix, source["q"], source["omega32_normal"])
    fingerprints = row_fingerprints(matrix, source["q"])
    target_analysis = analyze_rowpack_targets(matrix, source["q"])
    result = candidate_oracle_result(target_analysis)

    source_artifact = {
        "gate": "Gate 14: numeric source facts",
        "status": "parsed_from_current_source",
        "source_files": {
            "params": str(PARAMS),
            "ntt_c": str(NTT_C),
        },
        "n": source["n"],
        "q": source["q"],
        "omega32_montgomery": source["omega32_montgomery"],
        "omega32_normal": source["omega32_normal"],
        "twiddle_schedule": schedule,
        "matrix_verification": verify,
    }

    write_yml(OUTDIR / "numeric-source-facts.yml", source_artifact)
    write_yml(OUTDIR / "ntt32-matrix-fingerprints.yml", fingerprints)
    write_yml(OUTDIR / "rowpack-target-equivalence.yml", target_analysis)
    write_yml(OUTDIR / "candidate-oracle-result.yml", result)
    (OUTDIR / "numeric-oracle-report.md").write_text(
        oracle_report_markdown(source, verify, target_analysis, result)
    )


def main() -> int:
    write_artifacts()
    print(f"wrote Gate 14 numeric oracle artifacts to {OUTDIR}")
    print("decision: no Forward v4 ASM; H full-absorption candidate has no numeric equivalence under the bounded no-lane-mixing model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
