#!/usr/bin/env python3
"""Replace only the V3 shared helper with the Slothy-scheduled region."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
NTRU768 = HERE.parents[2]
SOURCE = (
    NTRU768
    / "asm/gt/experiment/decap/verify_pointwise_group_pipeline_v3.S"
)
OPT = HERE / "helper_v3.opt.S"
OUTPUT = (
    NTRU768
    / "asm/gt/experiment/decap/"
    "verify_pointwise_group_pipeline_v3_slothy.S"
)
METADATA = HERE / "integrated-candidate.json"
OPT_START = "slothy_start_decap_verify_helper_v3:"
OPT_END = "slothy_end_decap_verify_helper_v3:"
SOURCE_START = ".Lfused_gather_mul_group:"
INSTRUCTION_RE = re.compile(r"^\s*([a-z][a-z0-9.]*)\b", re.IGNORECASE)
VECTOR_RE = re.compile(r"\bv([0-9]|[12][0-9]|3[01])\b", re.IGNORECASE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_opt_region() -> list[str]:
    lines = OPT.read_text(encoding="ascii").splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == OPT_START)
    end = next(i for i, line in enumerate(lines) if line.strip() == OPT_END)
    code: list[str] = []
    for line in lines[start + 1 : end]:
        instruction = line.split("//", 1)[0].rstrip()
        if INSTRUCTION_RE.match(instruction):
            code.append("    " + instruction.strip().lower())
    if len(code) != 100:
        raise SystemExit(f"expected 100 optimized instructions, found {len(code)}")
    return code


def extract_source_helper(lines: list[str]) -> tuple[int, int, list[str]]:
    start = next(i for i, line in enumerate(lines) if line.strip() == SOURCE_START)
    end = next(
        i
        for i, line in enumerate(lines[start + 1 :], start + 1)
        if line.strip() == "ret"
    )
    code = [
        line
        for line in lines[start + 1 : end]
        if INSTRUCTION_RE.match(line)
    ]
    if len(code) != 100:
        raise SystemExit(f"expected 100 source instructions, found {len(code)}")
    return start, end, code


def mnemonic_counter(lines: list[str]) -> Counter[str]:
    return Counter(
        match.group(1).lower()
        for line in lines
        if (match := INSTRUCTION_RE.match(line))
    )


def main() -> int:
    optimized = extract_opt_region()
    source_lines = SOURCE.read_text(encoding="ascii").splitlines()
    start, end, original = extract_source_helper(source_lines)
    if mnemonic_counter(original) != mnemonic_counter(optimized):
        raise SystemExit("optimized helper changed the mnemonic multiset")

    used_vectors = {
        int(match.group(1))
        for line in optimized
        for match in VECTOR_RE.finditer(line)
    }
    reserved_touches = sorted(used_vectors.intersection(range(24, 32)))
    if reserved_touches:
        raise SystemExit(f"optimized helper touches q24-q31: {reserved_touches}")

    candidate_lines = [
        *source_lines[: start + 1],
        "    // Slothy N1 schedule; q24-q31 are live-through and untouched.",
        *optimized,
        *source_lines[end:],
    ]
    candidate = "\n".join(candidate_lines) + "\n"
    candidate = candidate.replace(
        "gt_decap_verify_pointwise_group_pipeline_v3\n",
        "gt_decap_verify_pointwise_group_pipeline_v3_slothy\n",
        1,
    )
    candidate = candidate.replace(
        "_gt_decap_verify_pointwise_group_pipeline_v3\n",
        "_gt_decap_verify_pointwise_group_pipeline_v3_slothy\n",
        1,
    )
    OUTPUT.write_text(candidate, encoding="ascii")
    METADATA.write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(NTRU768)),
                "source_sha256": sha256(SOURCE.read_bytes()),
                "slothy_output": str(OPT.relative_to(NTRU768)),
                "slothy_output_sha256": sha256(OPT.read_bytes()),
                "candidate": str(OUTPUT.relative_to(NTRU768)),
                "candidate_sha256": sha256(OUTPUT.read_bytes()),
                "helper_instruction_count": len(optimized),
                "mnemonic_multiset_unchanged": True,
                "q24_q31_touches": reserved_touches,
                "production_default_changed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="ascii",
    )
    print(f"candidate={OUTPUT}")
    print(f"metadata={METADATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
