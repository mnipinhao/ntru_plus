#!/usr/bin/env python3
"""Generate a direct-BPQ endpoint from the active production forward NTT.

The arithmetic, reduction, register allocation, and scalar scatter-address
stream remain byte-for-byte source-identical.  Only the final Stage345 stores
change: each split low/high output pair becomes one fixed-offset Q store in the
keygen BPQ order.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "asm/gt/ntt/poly_ntt.n1.opt.S"
OUTPUT = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_to_bpq_endpoint.S"
MAP = HERE / "direct_bpq_endpoint_map.json"

SYMBOL = "gt_experiment_poly_ntt_to_bpq"

OUTPUTS = {
    0: [3, 17, 18, 2, 14, 1, 26, 4],
    1: [17, 2, 9, 1, 6, 3, 5, 4],
    2: [19, 9, 10, 19, 11, 1, 14, 28],
    3: [2, 9, 10, 19, 12, 14, 1, 3],
}

SLOTS = {
    # Store execution order is not k32 order.  These permutations were
    # recovered by uniquely matching each complete Q record against the
    # production blockmajor_to_bpq oracle.
    0: [0, 1, 3, 2, 4, 5, 6, 7],
    1: list(range(8, 16)),
    2: [16, 17, 18, 19, 20, 22, 21, 23],
    3: [25, 24, 26, 27, 28, 29, 30, 31],
}

SLOT_FOR_K32 = [
    3, 7, 1, 0, 6, 2, 5, 4,
    *range(8, 32),
]
K32_FOR_SLOT = {slot: k32 for k32, slot in enumerate(SLOT_FOR_K32)}

# These four ext results remain live for scheduling reasons in production S2.
# Keep the ext instruction, but remove its old split high-half memory store.
KEPT_EXT = {
    0: [(5, 3), (8, 17), (2, 1)],
    1: [],
    2: [(6, 19)],
    3: [],
}

SECTION_RE = re.compile(r"^\s*// ---- row([0-2]): Stage345 block([0-3]) ")
STR_D_RE = re.compile(r"^(\s*)str\s+d(\d+),")
UMOV_RE = re.compile(r"^\s*umov\s+x(\d+),\s*v(\d+)\.d\[1\]")
STR_X_RE = re.compile(r"^\s*str\s+x(\d+),")
EXT_RE = re.compile(
    r"^\s*ext\s+v(\d+)\.16B,\s*v(\d+)\.16B,\s*v\2\.16B,\s*#8"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def next_code(lines: list[str], start: int) -> int:
    for idx in range(start, len(lines)):
        if lines[idx].split("//", 1)[0].strip():
            return idx
    raise ValueError("missing executable instruction after umov")


def transform_section(
    section: list[str], row: int, block: int, base_line: int
) -> tuple[list[str], list[dict[str, object]], dict[str, int]]:
    remove: set[int] = set()
    kept_high: set[int] = set()
    safe_high_sources: list[int] = []

    # Mark the retained ext+str high-half sites.
    for tmp, src in KEPT_EXT[block]:
        ext_idx = next(
            (
                idx
                for idx, line in enumerate(section)
                if (match := EXT_RE.match(line))
                and int(match.group(1)) == tmp
                and int(match.group(2)) == src
            ),
            None,
        )
        if ext_idx is None:
            raise ValueError(f"row{row} block{block}: missing ext v{tmp}, v{src}")
        store_idx = next(
            (
                idx
                for idx in range(ext_idx + 1, len(section))
                if (match := STR_D_RE.match(section[idx]))
                and int(match.group(2)) == tmp
            ),
            None,
        )
        if store_idx is None:
            raise ValueError(f"row{row} block{block}: missing high str d{tmp}")
        kept_high.add(store_idx)
        remove.add(store_idx)

    # Mark all audited S2 umov+str high-half sites.
    safe_high = 0
    for idx, line in enumerate(section):
        match = UMOV_RE.match(line)
        if match is None:
            continue
        xtmp, source = int(match.group(1)), int(match.group(2))
        store_idx = next_code(section, idx + 1)
        store = STR_X_RE.match(section[store_idx])
        if store is None or int(store.group(1)) != xtmp:
            raise ValueError(
                f"row{row} block{block}: umov x{xtmp} not followed by matching str"
            )
        if "highhalf_umov_str" not in section[store_idx]:
            raise ValueError(
                f"row{row} block{block}: unrecognized umov+str at source line "
                f"{base_line + store_idx}"
            )
        remove.update((idx, store_idx))
        safe_high_sources.append(source)
        safe_high += 1

    expected_high = 8 - len(KEPT_EXT[block])
    if safe_high != expected_high:
        raise ValueError(
            f"row{row} block{block}: expected {expected_high} S2 high stores, got {safe_high}"
        )

    out = list(section)
    output_idx = 0
    sites: list[dict[str, object]] = []
    for idx, line in enumerate(section):
        if idx in kept_high:
            continue
        match = STR_D_RE.match(line)
        if match is None:
            continue
        source = int(match.group(2))
        if output_idx >= 8:
            raise ValueError(
                f"row{row} block{block}: unexpected str d{source} at "
                f"source line {base_line + idx}"
            )
        expected = OUTPUTS[block][output_idx]
        if source != expected:
            raise ValueError(
                f"row{row} block{block}: output {output_idx} expected v{expected}, "
                f"found str d{source} at source line {base_line + idx}"
            )
        slot = 32 * row + SLOTS[block][output_idx]
        offset = 16 * slot
        indent = match.group(1)
        out[idx] = (
            f"{indent}str q{source}, [x19, #{offset}]"
            f"  // direct BPQ row{row} block{block} output{output_idx} slot{slot}"
        )
        sites.append(
            {
                "row": row,
                "block": block,
                "output_index": output_idx,
                "k32": K32_FOR_SLOT[SLOTS[block][output_idx]],
                "bpq_slot_in_row": SLOTS[block][output_idx],
                "bpq_slot": slot,
                "source_vector": f"q{source}",
                "source_line": base_line + idx,
                "store_offset_bytes": offset,
            }
        )
        output_idx += 1

    if output_idx != 8:
        raise ValueError(f"row{row} block{block}: found {output_idx} outputs")
    if len(remove) != 2 * safe_high + len(KEPT_EXT[block]):
        raise ValueError(f"row{row} block{block}: inconsistent removal accounting")

    transformed = [line for idx, line in enumerate(out) if idx not in remove]
    stats = {
        "safe_umov_str_pairs_removed": safe_high,
        "retained_ext_high_stores_removed": len(KEPT_EXT[block]),
        "q_stores_emitted": output_idx,
        "instructions_removed": len(remove),
    }
    return transformed, sites, stats


def rename_function(text: str, source_hash: str) -> str:
    old = """.global poly_ntt
.global _poly_ntt
.global gt_block_major_poly_ntt
.global _gt_block_major_poly_ntt
.type poly_ntt, %function
poly_ntt:
_poly_ntt:
gt_block_major_poly_ntt:
_gt_block_major_poly_ntt:"""
    new = f""".global {SYMBOL}
.type {SYMBOL}, %function
{SYMBOL}:"""
    if text.count(old) != 1:
        raise ValueError("production NTT entry contract changed")
    text = text.replace(old, new)
    old_end = ".size poly_ntt, .-poly_ntt\n.global poly_ntt_end\npoly_ntt_end:"
    new_end = f".size {SYMBOL}, .-{SYMBOL}\n.global {SYMBOL}_end\n{SYMBOL}_end:"
    if text.count(old_end) != 1:
        raise ValueError("production NTT end contract changed")
    text = text.replace(old_end, new_end)
    banner = (
        "/* Experiment-only direct-BPQ endpoint generated from production. */\n"
        f"/* source_sha256={source_hash} */\n"
        "/* Arithmetic/reduction/register allocation are unchanged. */\n"
    )
    return banner + text


def main() -> None:
    source_hash = sha256(SOURCE)
    lines = SOURCE.read_text().splitlines()
    result: list[str] = []
    sites: list[dict[str, object]] = []
    stats: list[dict[str, object]] = []
    cursor = 0
    sections = 0

    while cursor < len(lines):
        match = SECTION_RE.match(lines[cursor])
        if match is None:
            result.append(lines[cursor])
            cursor += 1
            continue
        row, block = int(match.group(1)), int(match.group(2))
        end = cursor + 1
        while end < len(lines) and SECTION_RE.match(lines[end]) is None:
            if lines[end].lstrip().startswith("ldp d14, d15, [sp, #112]"):
                break
            end += 1
        transformed, section_sites, section_stats = transform_section(
            lines[cursor:end], row, block, cursor + 1
        )
        result.extend(transformed)
        sites.extend(section_sites)
        stats.append({"row": row, "block": block, **section_stats})
        sections += 1
        cursor = end

    if sections != 12 or len(sites) != 96:
        raise ValueError(f"expected 12 sections/96 sites, got {sections}/{len(sites)}")
    offsets = [int(site["store_offset_bytes"]) for site in sites]
    if sorted(offsets) != list(range(0, 1536, 16)):
        raise ValueError("direct BPQ offsets are not an exact 0..1520 permutation")

    output_text = rename_function("\n".join(result) + "\n", source_hash)
    OUTPUT.write_text(output_text)
    MAP.write_text(
        json.dumps(
            {
                "candidate": SYMBOL,
                "source": str(SOURCE.relative_to(ROOT)),
                "source_sha256": source_hash,
                "output": str(OUTPUT.relative_to(ROOT)),
                "output_sha256": hashlib.sha256(output_text.encode()).hexdigest(),
                "contract": "complete Stage345 Q -> fixed-offset BPQ",
                "production_default_changed": False,
                "sections": stats,
                "sites": sites,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"generated {OUTPUT.relative_to(ROOT)}")
    print(f"mapped {len(sites)} direct Q stores; source_sha256={source_hash}")


if __name__ == "__main__":
    main()
