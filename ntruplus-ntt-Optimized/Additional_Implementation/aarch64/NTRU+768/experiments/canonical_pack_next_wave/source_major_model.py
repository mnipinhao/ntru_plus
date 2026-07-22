#!/usr/bin/env python3
"""Model GT-source-major canonical packing without emitting assembly."""

import json
import re
from pathlib import Path


EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
MAP_SOURCE = ROOT / "poly_gt_canonical.c"
JSON_OUT = EXP / "source_major_model.json"
MD_OUT = EXP / "source_major_model.md"


def block_map() -> list[int]:
    text = MAP_SOURCE.read_text()
    body = re.search(
        r"gt_kpqc_block_to_gt_block\[.*?\]\s*=\s*\{(.*?)\};", text, re.S
    )
    if body is None:
        raise ValueError("canonical block map not found")
    values = [int(x) for x in re.findall(r"\b\d+\b", body.group(1))]
    if len(values) != 192 or sorted(values) != list(range(192)):
        raise ValueError("map is not a 192-block permutation")
    return values


def runs(indices: list[int]) -> list[list[int]]:
    ordered = sorted(indices)
    result = [[ordered[0]]]
    for value in ordered[1:]:
        if value == result[-1][-1] + 1:
            result[-1].append(value)
        else:
            result.append([value])
    return result


def scalar_store_lower_bound(byte_count: int) -> int:
    count = 0
    for width in (16, 8, 4, 2, 1):
        count += byte_count // width
        byte_count %= width
    return count


def evaluate(group_size: int, inverse: list[int]) -> dict[str, object]:
    groups = []
    for first in range(0, 192, group_size):
        last = min(first + group_size, 192)
        canonical = inverse[first:last]
        output_runs = runs(canonical)
        groups.append(
            {
                "gt_first": first,
                "gt_last": last - 1,
                "canonical_in_gt_order": canonical,
                "output_runs": [
                    {
                        "first": run[0],
                        "last": run[-1],
                        "blocks": len(run),
                        "bytes": 6 * len(run),
                        "scalar_store_lower_bound": scalar_store_lower_bound(6 * len(run)),
                    }
                    for run in output_runs
                ],
                "run_count": len(output_runs),
                "contiguous_q_loads": (last - first + 1) // 2,
                "ld3_2d_full_groups": (last - first) // 6,
                "ld3_tail_blocks": (last - first) % 6,
                "input_q_vectors": (last - first + 1) // 2,
                "estimated_peak_vectors_before_pack": (last - first + 1) // 2
                + len(output_runs),
            }
        )
    return {
        "group_size": group_size,
        "groups": groups,
        "run_count_total": sum(group["run_count"] for group in groups),
        "run_count_max": max(group["run_count"] for group in groups),
        "scalar_store_lower_bound_total": sum(
            run["scalar_store_lower_bound"]
            for group in groups
            for run in group["output_runs"]
        ),
        "estimated_peak_vectors": max(
            group["estimated_peak_vectors_before_pack"] for group in groups
        ),
    }


def main() -> int:
    forward = block_map()
    inverse = [0] * 192
    for canonical, physical in enumerate(forward):
        inverse[physical] = canonical

    candidates = [evaluate(size, inverse) for size in (6, 8, 12, 16, 24)]
    report = {
        "status": "model_only",
        "production_changed": False,
        "baseline_canonical_major": {
            "blocks_per_chunk": 16,
            "chunks": 12,
            "gather_instructions_per_chunk": 24,
            "output_store_instructions_per_chunk": 2,
            "note": "Two st1 multi-register stores write 96 sequential bytes.",
        },
        "assumptions": [
            "Source-major groups load contiguous 8-byte GT quartic blocks.",
            "Store lower bounds use 16/8/4/2/1-byte scalar-width stores and exclude shuffle cost.",
            "ld3 counts are ISA instruction counts, not Cortex-A76 micro-op or cycle estimates.",
            "No candidate is eligible for assembly from this model alone.",
        ],
        "candidates": candidates,
    }
    JSON_OUT.write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# GT-source-major canonical pack model",
        "",
        "This is a model-only artifact. It does not authorize or emit assembly.",
        "",
        "| GT group | groups | output runs | max runs/group | scalar store lower bound | estimated peak vectors |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for candidate in candidates:
        lines.append(
            f"| {candidate['group_size']} | {len(candidate['groups'])} | "
            f"{candidate['run_count_total']} | {candidate['run_count_max']} | "
            f"{candidate['scalar_store_lower_bound_total']} | "
            f"{candidate['estimated_peak_vectors']} |"
        )
    lines += [
        "",
        "The current canonical-major baseline uses 24 gather/assembly instructions and",
        "two sequential multi-register stores per 16 blocks. Source-major candidates",
        "replace those gathers with contiguous or structured loads, but they must pay",
        "for stream permutation and fragmented 6-byte-block output runs. The scalar",
        "store column is only a lower bound and intentionally excludes shuffle cost.",
        "",
        "Decision gate: build source-major assembly only after an instruction-level",
        "shuffle/store plan fits the available vector registers and has a modeled",
        "advantage over the canonical-major fixed-offset chunk.",
    ]
    MD_OUT.write_text("\n".join(lines) + "\n")
    print(JSON_OUT)
    print(MD_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
