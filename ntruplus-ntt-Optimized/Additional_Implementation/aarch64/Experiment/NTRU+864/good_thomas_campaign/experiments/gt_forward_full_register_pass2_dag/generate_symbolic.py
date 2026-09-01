#!/usr/bin/env python3
"""Generate the M5R 620-instruction full-register one-bank candidate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "gt_forward_one_bank_slothy/gt864_forward_one_bank.sym.S"
OUTPUT = ROOT / "gt864_forward_one_bank_full_register.sym.S"

REPLACEMENTS = {
    "a_saved": "f0_raw",
    "b_saved": "f1",
    "c_saved": "f8",
    "g0_saved": "a0",
    "g1_saved": "a1",
    "g2_saved": "a2",
    "second_a_saved": "hold0",
    "second_b_saved": "h1",
    "second_c_saved": "h8",
    "second_g0_saved": "second_a0",
    "second_g1_saved": "second_a1",
    "second_g2_saved": "second_a2",
}


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    text = text.replace("/* M5M: exact one-bank pass-2 producer and M5K consumer. */",
                        "/* M5R: full-register one-bank Pass-2 DAG. */")
    text = text.replace("gt864_forward_one_bank_slothy_start",
                        "gt864_forward_one_bank_full_register_slothy_start")
    text = text.replace("gt864_forward_one_bank_slothy_end",
                        "gt864_forward_one_bank_full_register_slothy_end")
    text = text.replace(
        "// reserved physical registers: v8-v15; fixed v17/v16 hold the two tails.",
        "// reserved physical registers: fixed v17/v16 hold the two tails; all other v0-v31 are allocatable.",
    )

    lines = []
    removed = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("orr ") and any(f"V<{name}>" in line for name in REPLACEMENTS):
            removed.append(stripped)
            continue
        if stripped.startswith("orr V<hold8>"):
            removed.append(stripped)
            continue
        for old, new in REPLACEMENTS.items():
            line = line.replace(f"V<{old}>", f"V<{new}>")
            line = line.replace(f"Q<{old}>", f"Q<{new}>")
        line = line.replace("V<hold8>", "v16")
        line = line.replace("Q<hold8>", "q16")
        lines.append(line)

    assert len(removed) == 13, removed
    candidate = "\n".join(lines) + "\n"
    assert candidate.count("orr ") == 0
    OUTPUT.write_text(candidate, encoding="utf-8")
    print(f"removed_copy_instructions={len(removed)}")
    print("candidate_instruction_count=620")


if __name__ == "__main__":
    main()
