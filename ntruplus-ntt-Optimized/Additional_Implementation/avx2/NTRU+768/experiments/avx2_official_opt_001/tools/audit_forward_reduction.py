#!/usr/bin/env python3
"""Mechanical Official Forward opcode/reducer census, not a range proof."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "upstream/supercop-avx2/ntt.s"
STAGES = (("top_split", "#level0", "#level 1", 8),
          ("radix3", "#level 1", "#level 2", 16),
          ("radix2_first", "#level 2", "#level3", 6),
          ("radix2_d8", "#level3", "#level4", 6),
          ("radix2_d4", "#level4", "#level5", 6),
          ("radix2_d2", "#level5", "#level6", 6),
          ("radix2_d1", "#level6", "ret", 6))


def opcode_counts(source):
    result = {}
    for name, begin, end, iterations in STAGES:
        if source.count(begin) != 1 or source.count(end) != 1:
            raise ValueError(f"stage marker changed: {name}")
        body = source.split(begin, 1)[1].split(end, 1)[0]
        static = Counter(re.findall(r"(?m)^([a-z][a-z0-9]+)\b", body))
        opcodes = ("vpmullw", "vpmulhw", "vpmulhrsw", "vpaddw", "vpsubw")
        result[name] = {
            "inner_iterations": iterations,
            "inner_arithmetic_static": {op: static[op] for op in opcodes},
            "inner_arithmetic_dynamic": {op: static[op] * iterations for op in opcodes},
            "scope_note": "stage-1 outer constant broadcasts are not multiplied by inner trips",
        }
    return result


def rounded_mulhi(x, v):
    # VPMULHRSW: signed rounded high word, saturation does not occur for v=9.
    return (x * v + (1 << 14)) >> 15


def reducer_domain():
    q, v = 3457, ((1 << 15) + 3457 // 2) // 3457
    outputs = [(x - q * rounded_mulhi(x, v)) for x in range(-32768, 32768)]
    if not all(-32768 <= y <= 32767 for y in outputs):
        raise ValueError("Official Barrett overflows signed word")
    return {"q": q, "v": v, "input": [-32768, 32767],
            "output": [min(outputs), max(outputs)],
            "mod_q_preserved": all((y - x) % q == 0
                                   for x, y in zip(range(-32768, 32768), outputs))}


def main():
    source = SOURCE.read_text()
    stages = opcode_counts(source)
    terminal_barrett = stages["radix2_d1"]["inner_arithmetic_dynamic"]["vpmulhrsw"]
    chains = sum(stage["inner_arithmetic_dynamic"]["vpmullw"]
                 for name, stage in stages.items() if name != "top_split") - terminal_barrett
    if terminal_barrett != 48 or chains != 168:
        raise ValueError("Official Forward arithmetic census changed")
    result = {
        "class": "source-level dynamic opcode census; not linked timing or range proof",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "stages": stages,
        "fixed_twiddle_montgomery_chains": chains,
        "top_split_raw_multiply_vectors": stages["top_split"]["inner_arithmetic_dynamic"]["vpmullw"],
        "terminal_barrett_vectors": terminal_barrett,
        "terminal_barrett_instructions": 3 * terminal_barrett,
        "terminal_barrett_full_signed_word": reducer_domain(),
        "unproven": ["per-lane pre-reduction bounds", "consumer acceptance of lazy output",
                     "BaseInv and BaseMul no-overflow if terminal reduction removed"],
    }
    output = ROOT / "results/officialopt-forward-reduction-audit-20260921.json"
    if output.exists():
        raise SystemExit(f"refusing overwrite: {output}")
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"chains": result["fixed_twiddle_montgomery_chains"],
                      "terminal_reducer": result["terminal_barrett_full_signed_word"]},
                     indent=2))


if __name__ == "__main__":
    main()
