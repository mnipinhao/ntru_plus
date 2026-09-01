#!/usr/bin/env python3
"""Compose M5L, the exact main NTT16 producer, and frozen M5K."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5L = ROOT.parent / "gt_forward_tail_ntt16_slothy/gt864_forward_tail_ntt16.sym.S"
M5K = ROOT.parent / "gt_forward_two_ntt9_blocks_slothy/gt864_forward_two_ntt9_blocks.sym.S"
OUTPUT = ROOT / "gt864_forward_one_bank.sym.S"
BR4 = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)


def region(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    return text[text.index(start + ":") + len(start) + 1:text.index(end + ":")].strip("\n")


def main_producer() -> str:
    lines = [
        "    // Main P8 branch twist: four packed tables, four (b,bprime) pairs each.",
    ]
    for group in range(4):
        lines.append(f"    ldr Q<branch_pack{group}>, [x2], #16")
        for slot in range(4):
            t = 4 * group + slot
            state = BR4[t]
            lane = 2 * slot
            lines.extend([
                f"    ldr Q<input_t{t}>, [x0], #16",
                f"    sqrdmulh V<branch_q{t}>.8h, V<input_t{t}>.8h, V<branch_pack{group}>.h[{lane + 1}]",
                f"    mul V<state{state}>.8h, V<input_t{t}>.8h, V<branch_pack{group}>.h[{lane}]",
                f"    mls V<state{state}>.8h, V<branch_q{t}>.8h, V<modq>.8h",
            ])

    current = [f"state{i}" for i in range(16)]
    for stage, length in enumerate((2, 4, 8, 16), start=1):
        half = length // 2
        pack_count = 2 if length == 16 else 1
        next_names = [None] * 16
        lines.extend(["", f"    // Main NTT16 DIT length {length}."])
        for pack in range(pack_count):
            pack_name = f"stage{length}_pack{pack}"
            lines.append(f"    ldr Q<{pack_name}>, [x2], #16")
            j_start = 4 * pack
            j_end = min(half, j_start + 4)
            for start in range(0, 16, length):
                for j in range(j_start, j_end):
                    left = start + j
                    right = left + half
                    lane = 2 * (j & 3)
                    out_left = f"c{left}" if length == 16 else f"l{length}_{left}"
                    out_right = f"c{right}" if length == 16 else f"l{length}_{right}"
                    lines.extend([
                        f"    sqrdmulh V<q{length}_{start}_{j}>.8h, V<{current[right]}>.8h, V<{pack_name}>.h[{lane + 1}]",
                        f"    mul V<p{length}_{start}_{j}>.8h, V<{current[right]}>.8h, V<{pack_name}>.h[{lane}]",
                        f"    mls V<p{length}_{start}_{j}>.8h, V<q{length}_{start}_{j}>.8h, V<modq>.8h",
                        f"    add V<{out_left}>.8h, V<{current[left]}>.8h, V<p{length}_{start}_{j}>.8h",
                        f"    sub V<{out_right}>.8h, V<{current[left]}>.8h, V<p{length}_{start}_{j}>.8h",
                    ])
                    next_names[left] = out_left
                    next_names[right] = out_right
        assert all(next_names)
        current = list(next_names)
    return "\n".join(lines)


tail = region(M5L, "gt864_forward_tail_ntt16_slothy_start", "gt864_forward_tail_ntt16_slothy_end")
tail = tail.replace(
    "tbl V<tail0>.16b, { V<raw_lo>.16b }, V<bitrev3_bytes>.16b",
    "tbl v17.16b, { V<raw_lo>.16b }, V<bitrev3_bytes>.16b",
)
tail = tail.replace(
    "tbl V<tail1>.16b, { V<raw_hi>.16b }, V<bitrev3_bytes>.16b",
    "tbl v16.16b, { V<raw_hi>.16b }, V<bitrev3_bytes>.16b",
)
assert "V<tail0>" not in tail and "V<tail1>" not in tail
consumer = region(M5K, "gt864_forward_two_ntt9_blocks_slothy_start", "gt864_forward_two_ntt9_blocks_slothy_end")
consumer = consumer.replace("V<tail0>", "v17")

header = """/* M5M: exact one-bank pass-2 producer and M5K consumer. */
// x0 main P8, x1 strided tail, x2 NTT16 table, x3 NTT9 table.
// x4 is public stride 16; x5 points to modq then roots.
// live-in: x0,x1 coefficient pointers and public x2,x3,x4,x5.
// live-out: symbolic Q<out0> through Q<out17> plus updated public pointers.
// coefficient range: P8 <=15752, NTT16 <=9342, NTT9 <=28568.
// reserved physical registers: v8-v15; fixed v17/v16 hold the two tails.

gt864_forward_one_bank_slothy_start:
    ldr Q<modq>, [x5], #16
"""
footer = "\ngt864_forward_one_bank_slothy_end:\n"
text = (header + tail + "\n\n" + main_producer()
        + "\n\n    // Delay roots until all sixteen main columns exist.\n"
        + "    ldr Q<roots>, [x5], #16\n\n" + consumer + footer)
OUTPUT.write_text(text, encoding="utf-8")
