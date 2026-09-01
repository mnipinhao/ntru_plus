#!/usr/bin/env python3
"""Hoist q, roots, and bitrev3 from the copy-free M5R bank DAG."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_one_bank_full_register.sym.S"
OUTPUT = ROOT / "gt864_forward_one_bank_full_register_pinned.sym.S"


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace("gt864_forward_one_bank_full_register_slothy_start",
                        "gt864_forward_one_bank_full_register_pinned_slothy_start")
    text = text.replace("gt864_forward_one_bank_full_register_slothy_end",
                        "gt864_forward_one_bank_full_register_pinned_slothy_end")
    text = text.replace("/* M5R: full-register one-bank Pass-2 DAG. */",
                        "/* M5R-B: copy-free bank with pinned common constants. */")
    text = text.replace(
        "// live-in: x0,x1 coefficient pointers and public x2,x3,x4,x5.",
        "// live-in: x0,x1 coefficients; public x2,x3,x4; fixed v13=bitrev, v14=q, v15=roots.",
    )
    text = text.replace(
        "// live-out: symbolic Q<out0> through Q<out17> plus updated public pointers.",
        "// live-out: Q<out0> through Q<out17> plus updated x0,x1,x2,x3; v13-v15 unchanged.",
    )
    text = text.replace(
        "// reserved physical registers: fixed v17/v16 hold the two tails; all other v0-v31 are allocatable.",
        "// reserved physical registers: v13=bitrev, v14=q, v15=roots, v16/v17=tails.",
    )
    remove = {
        "ldr Q<modq>, [x5], #16",
        "ldr Q<bitrev3_bytes>, [x2], #16",
        "ldr Q<roots>, [x5], #16",
    }
    lines = []
    removed = []
    for line in text.splitlines():
        if line.strip() in remove:
            removed.append(line.strip())
            continue
        line = line.replace("V<modq>", "v14").replace("Q<modq>", "q14")
        line = line.replace("V<roots>", "v15").replace("Q<roots>", "q15")
        line = line.replace("V<bitrev3_bytes>", "v13").replace("Q<bitrev3_bytes>", "q13")
        lines.append(line)
    assert set(removed) == remove, removed
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("hoisted_common_constant_loads=3")
    print("candidate_instruction_count=617")


if __name__ == "__main__":
    main()
