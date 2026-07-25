#!/usr/bin/env python3
"""Generate development-only compact GT serialization candidates."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parent
SCHEME = Path(__file__).resolve().parents[2]
WORKTREE = SCHEME.parents[3]
RELEASE = (
    WORKTREE
    / "ntruplus-GT-Production"
    / "Additional_Implementation"
    / "aarch64"
    / "NTRU+768"
)
GENERATED = EXPERIMENT / "generated"
GENERIC_COMPACT = SCHEME / "asm/gt/experiment/poly_canonical_pack_compact.S"
OPTIMIZED_PACK = SCHEME / "asm/gt/support/poly_canonical_pack.S"
KEYGEN_PACK = RELEASE / "asm/internal/keygen_pack.S"
SUPPORT = RELEASE / "asm/support.S"

INSTRUCTION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.]*\s+")


def normalized_instruction(line: str) -> str | None:
    stripped = line.split("//", 1)[0].strip()
    if (
        not stripped
        or stripped.startswith((".", "#", "/*", "*"))
        or stripped.endswith(":")
        or not INSTRUCTION_RE.match(stripped)
    ):
        return None
    return re.sub(r"\s+", " ", stripped.lower())


def instruction_lines(lines: list[str]) -> list[tuple[int, str]]:
    result = []
    for index, line in enumerate(lines):
        instruction = normalized_instruction(line)
        if instruction is not None:
            result.append((index, instruction))
    return result


def exact_ranges(lines: list[str], needle: list[str]) -> list[tuple[int, int]]:
    stream = instruction_lines(lines)
    result = []
    for start in range(len(stream) - len(needle) + 1):
        if [instruction for _, instruction in stream[start : start + len(needle)]] == needle:
            result.append((stream[start][0], stream[start + len(needle) - 1][0]))
    return result


def generate_generic(source: str, symbol: str, production: bool = False) -> str:
    old = "poly_tobytes_gt_canonical_compact"
    generated = source.replace(old, symbol)
    description = (
        "// Production compact shared-core canonical pack."
        if production
        else "// Generated shared-core canonical-pack candidate; experiment only."
    )
    generated = generated.replace(
        "// Generated compact canonical-pack candidate; experiment only.",
        description,
        1,
    )
    return generated


def generate_keygen(
    source: str, core_lines: list[str], symbol: str, production: bool = False
) -> str:
    lines = source.splitlines()
    core = [
        instruction
        for line in core_lines
        if (instruction := normalized_instruction(line)) is not None
    ]
    if len(core) != 60:
        raise RuntimeError(f"expected 60-instruction pack64 core, found {len(core)}")

    ranges = exact_ranges(lines, core)
    shared_call = "bl .lgt_keygen_shared_pack64_core"
    shared_calls = sum(normalized_instruction(line) == shared_call for line in lines)
    if shared_calls == 12:
        helper_start = next(
            (
                index
                for index, line in enumerate(lines)
                if line.strip() == ".Lgt_keygen_shared_pack64_core:"
            ),
            None,
        )
        if helper_start is None:
            raise RuntimeError("shared keygen pack64 helper label not found")
        helper_instructions = []
        for line in lines[helper_start + 1 :]:
            instruction = normalized_instruction(line)
            if instruction == "ret":
                break
            if instruction is not None:
                helper_instructions.append(instruction)
        if helper_instructions != core:
            raise RuntimeError("existing shared keygen pack64 helper does not match support core")
        if (
            "sub sp, sp, #80" not in source
            or "str x30, [sp, #64]" not in source
            or "ldr x30, [sp, #64]" not in source
            or "add sp, sp, #80" not in source
        ):
            raise RuntimeError("existing shared keygen pack does not preserve LR")
        generated = source.replace("gt_keygen_tobytes_cq", symbol)
        description = (
            "// Production CQ pack with shared 60-instruction pack64 core."
            if production
            else "// Generated CQ pack shared-core candidate; experiment only."
        )
        generated = re.sub(r"^// .*CQ pack.*shared.*core\\.$", description, generated, count=1)
        return generated
    if len(ranges) != 12:
        raise RuntimeError(f"expected 12 keygen pack64 copies, found {len(ranges)}")
    starts = {start: end for start, end in ranges}

    output = [
        (
            "// Production CQ pack with shared 60-instruction pack64 core."
            if production
            else "// Generated CQ pack shared-core candidate; experiment only."
        ),
        "// The layout frontend and 60-instruction pack64 semantics are unchanged.",
    ]
    index = 0
    helper_inserted = False
    while index < len(lines):
        if index in starts:
            output.append("    bl .Lgt_keygen_shared_pack64_core")
            index = starts[index] + 1
            continue

        line = lines[index]
        line = line.replace("gt_keygen_tobytes_cq", symbol)
        if line.strip() == "sub sp, sp, #64":
            line = "    sub sp, sp, #80"
        output.append(line)
        if line.strip() == "stp d14, d15, [sp, #48]":
            output.append("    str x30, [sp, #64]")
        if line.strip() == "ldp d8, d9, [sp, #0]":
            output.insert(len(output) - 1, "    ldr x30, [sp, #64]")
        if line.strip() == "add sp, sp, #64":
            output[-1] = "    add sp, sp, #80"

        if line.strip() == ".Lbpq_cq_pack_indexes:":
            if helper_inserted:
                raise RuntimeError("duplicate helper insertion")
            output[-1:] = [
                ".p2align 4",
                ".Lgt_keygen_shared_pack64_core:",
                *[
                    f"    {normalized_instruction(core_line)}"
                    for core_line in core_lines
                    if normalized_instruction(core_line) is not None
                ],
                "    ret",
                "",
                ".p2align 4",
                ".Lbpq_cq_pack_indexes:",
            ]
            helper_inserted = True
        index += 1

    if not helper_inserted:
        raise RuntimeError("keygen table label not found")
    return "\n".join(output) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    generic_source = GENERIC_COMPACT.read_text()
    optimized_pack_source = OPTIMIZED_PACK.read_text()
    keygen_source = KEYGEN_PACK.read_text()
    support_lines = SUPPORT.read_text().splitlines()[209:270]
    legacy_unpack_marker = "#ifndef GT_PRODUCTION_USE_CANONICAL_UNPACK_U1"
    if legacy_unpack_marker not in optimized_pack_source:
        raise RuntimeError("optimized compatibility unpack marker not found")
    optimized_legacy_unpack = (
        legacy_unpack_marker
        + optimized_pack_source.split(legacy_unpack_marker, 1)[1]
    )

    outputs = {
        "poly_tobytes_shared_compact_namespaced.S": generate_generic(
            generic_source, "poly_tobytes_shared_compact_candidate"
        ),
        "poly_tobytes_shared_compact_replacement.S": generate_generic(
            generic_source, "poly_tobytes", production=True
        ),
        "poly_canonical_pack_optimized_production.S": (
            generate_generic(
                generic_source, "poly_tobytes_gt_canonical", production=True
            )
            + "\n"
            + optimized_legacy_unpack
        ),
        "keygen_pack_shared_core_namespaced.S": generate_keygen(
            keygen_source, support_lines, "gt_keygen_tobytes_cq_shared_candidate"
        ),
        "keygen_pack_shared_core_replacement.S": generate_keygen(
            keygen_source, support_lines, "gt_keygen_tobytes_cq", production=True
        ),
    }
    for name, contents in outputs.items():
        (GENERATED / name).write_text(contents)

    manifest = {
        "inputs": {
            str(path): sha256(path)
            for path in (GENERIC_COMPACT, OPTIMIZED_PACK, KEYGEN_PACK, SUPPORT)
        },
        "outputs": {
            name: hashlib.sha256(contents.encode()).hexdigest()
            for name, contents in outputs.items()
        },
        "keygen_shared_core": {
            "instructions": 60,
            "call_sites": 12,
            "lr_preserved": True,
        },
    }
    (GENERATED / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
