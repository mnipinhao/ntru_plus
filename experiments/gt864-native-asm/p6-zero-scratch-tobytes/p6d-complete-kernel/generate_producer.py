#!/usr/bin/env python3
"""Generate P6-D1 saved-pair producer regions from the committed pair DAG."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = "experiments/gt864-native-asm/tobytes_block/candidate.sym.S"
P = [0, 3, 6, 1, 4, 7, 2, 5, 8]


def committed_body() -> list[str]:
    text = subprocess.check_output(["git", "show", "HEAD:" + SOURCE], cwd=ROOT, text=True)
    lines = text.splitlines()
    lo = next(i for i, x in enumerate(lines) if x.strip() == "byte_pair_block_slothy_start:") + 1
    hi = next(i for i, x in enumerate(lines) if x.strip() == "byte_pair_block_slothy_end:")
    return [x.strip() for x in lines[lo:hi] if x.startswith("    ")]


def fixed_loads(line: str, first: int, second: int) -> str | None:
    if line in ("mov w8, #3457", "mov w8, #9"):
        return None
    if line == "dup V<q>.8h, w8":
        return "ldr Q<q>, [x30, #336]"
    if line == "dup V<recip>.8h, w8":
        return "ldr Q<recip>, [x30, #352]"
    if re.fullmatch(r"add x5, x0, #\d+", line):
        return None
    for old, add in (("x1", first), ("x2", second)):
        m = re.fullmatch(r"ldr (Q<[^>]+>), \[" + old + r"(?:, #(\d+))?\]", line)
        if m:
            off = add + int(m.group(2) or 0)
            return f"ldr {m.group(1)}, [x29, #{off}]"
    for old, add in (("x3", 0), ("x4", 160)):
        m = re.fullmatch(r"ldr (Q<[^>]+>), \[" + old + r"(?:, #(\d+))?\]", line)
        if m:
            off = add + int(m.group(2) or 0)
            return f"ldr {m.group(1)}, [x30, #{off}]"
    return line


def interleave(row: int, prefix: str) -> list[str]:
    return [
        f"ldr Q<{prefix}idx0_{row}>, [x30, #304]",
        f"tbl V<{prefix}stream0_{row}>.16b, {{V<lo{row}>.16b, V<mid{row}>.16b, V<hi{row}>.16b}}, V<{prefix}idx0_{row}>.16b",
        f"ldr Q<{prefix}idx1_{row}>, [x30, #320]",
        f"tbl V<{prefix}stream1_{row}>.16b, {{V<lo{row}>.16b, V<mid{row}>.16b, V<hi{row}>.16b}}, V<{prefix}idx1_{row}>.16b",
    ]


def pair0() -> list[str]:
    out = []
    for raw in committed_body():
        m = re.fullmatch(r"st3 \{V<lo(\d+)>.8b, V<mid\1>.8b, V<hi\1>.8b\}, \[x5\]", raw)
        if m:
            row = int(m.group(1)); phys = P[row]
            out += interleave(row, "p0")
            out += [
                f"umov X<p0d{3*phys}>, V<p0stream0_{row}>.d[0]",
                f"umov X<p0d{3*phys+1}>, V<p0stream0_{row}>.d[1]",
                f"umov X<p0d{3*phys+2}>, V<p0stream1_{row}>.d[0]",
            ]
            continue
        line = fixed_loads(raw, 0, 16)
        if line: out.append(line)
    out += [f"str X<p0d{i}>, [sp, #{8*i}]" for i in range(27)]
    return out


def q_from_gprs(name: str, lo: str, hi: str) -> list[str]:
    return [f"movi V<{name}>.16b, #0",
            f"mov V<{name}>.d[0], X<{lo}>", f"mov V<{name}>.d[1], X<{hi}>"]


def pair1() -> list[str]:
    out = [f"ldr X<p0d{i}>, [sp, #{8*i}]" for i in range(27)]
    remaining_gprs: dict[int, str] = {}
    saved_q: dict[int, str] = {}
    for raw in committed_body():
        m = re.fullmatch(r"st3 \{V<lo(\d+)>.8b, V<mid\1>.8b, V<hi\1>.8b\}, \[x5\]", raw)
        if m:
            row = int(m.group(1)); phys = P[row]
            out += interleave(row, "p1")
            base = 3 * phys
            if phys < 4:
                q0, q1, q2 = (f"saved{3*phys+i}" for i in range(3))
                out += q_from_gprs(q0, f"p0d{base}", f"p0d{base+1}")
                out += [f"movi V<{q1}>.16b, #0",
                        f"mov V<{q1}>.d[0], X<p0d{base+2}>",
                        f"mov V<{q1}>.d[1], V<p1stream0_{row}>.d[0]",
                        f"movi V<{q2}>.16b, #0",
                        f"mov V<{q2}>.d[0], V<p1stream0_{row}>.d[1]",
                        f"mov V<{q2}>.d[1], V<p1stream1_{row}>.d[0]"]
                saved_q.update({3 * phys: q0, 3 * phys + 1: q1, 3 * phys + 2: q2})
            elif phys == 4:
                out += q_from_gprs("saved12", f"p0d{base}", f"p0d{base+1}")
                saved_q[12] = "saved12"
                remaining_gprs[26] = f"p0d{base+2}"
                for d, src in enumerate((f"V<p1stream0_{row}>.d[0]", f"V<p1stream0_{row}>.d[1]", f"V<p1stream1_{row}>.d[0]")):
                    name = f"p1d{base+d}"; out.append(f"umov X<{name}>, {src}"); remaining_gprs[27+d] = name
            else:
                for i in range(3): remaining_gprs[6*phys+i] = f"p0d{base+i}"
                for d, src in enumerate((f"V<p1stream0_{row}>.d[0]", f"V<p1stream0_{row}>.d[1]", f"V<p1stream1_{row}>.d[0]")):
                    name = f"p1d{base+d}"; out.append(f"umov X<{name}>, {src}"); remaining_gprs[6*phys+3+d] = name
            continue
        line = fixed_loads(raw, 32, 432)
        if line: out.append(line)
    assert sorted(saved_q) == list(range(13))
    assert sorted(remaining_gprs) == list(range(26, 54))
    out += [f"str Q<{saved_q[i]}>, [sp, #{16*i}]" for i in range(13)]
    out += [f"str X<{remaining_gprs[i]}>, [sp, #{208+8*(i-26)}]" for i in range(26, 54)]
    return out


def main() -> None:
    lines = [".text", ".global gt864_p6d_pair0", "gt864_p6d_pair0:",
             "// synthetic allocation region; x29 coefficient base, x30 combined-table base, sp live-out sink.",
             "gt864_p6d_pair0_start:"]
    lines += ["    " + x for x in pair0()]
    lines += ["gt864_p6d_pair0_end:", "    ret", ".global gt864_p6d_pair1", "gt864_p6d_pair1:",
              "// synthetic allocation region; exact 13-Q plus 28-GPR saved-state frontier.",
              "gt864_p6d_pair1_start:"]
    lines += ["    " + x for x in pair1()]
    lines += ["gt864_p6d_pair1_end:", "    ret"]
    (HERE / "producer.sym.S").write_text("\n".join(lines) + "\n")
    print(f"pair0={len(pair0())} pair1={len(pair1())}")


if __name__ == "__main__":
    main()
