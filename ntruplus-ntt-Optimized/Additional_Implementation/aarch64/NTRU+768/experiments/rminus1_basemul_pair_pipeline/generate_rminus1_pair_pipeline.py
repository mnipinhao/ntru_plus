#!/usr/bin/env python3
"""Generate physical U2 and symbolic two-iteration rminus1 basemul kernels."""

from collections import Counter
from pathlib import Path
import re

from extract_baseline import extract_body


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEMANTIC_SOURCE = ROOT / "asm/slothy/inputs/base_gt_add32_full_pipeline.sym.S"
BASELINE = HERE / "baseline-region.S"
U2_OUTPUT = HERE / "rminus1_pair_u2.S"
SYMBOLIC_OUTPUT = HERE / "rminus1_pair_pipeline.sym.S"


def mnemonic_counter(lines: list[str]) -> Counter[str]:
    result: Counter[str] = Counter()
    for line in lines:
        code = line.split("//", 1)[0].strip()
        if code and not code.startswith(".") and not code.endswith(":"):
            result[code.split(None, 1)[0].lower()] += 1
    return result


def semantic_iteration() -> list[str]:
    lines = SEMANTIC_SOURCE.read_text(encoding="ascii").splitlines()
    start = next(i for i, line in enumerate(lines) if "ldr Q<lam>" in line)
    end = next(
        i for i, line in enumerate(lines[start:], start)
        if "uzp2 V<raw3>" in line
    ) + 1
    body = []
    for line in lines[start:end]:
        code = line.split("//", 1)[0].strip()
        if not code or code.startswith("ld4 {V<c0>"):
            continue
        if code.startswith("ldr Q<lam>"):
            code = "ld1 {V<lam>.8h}, [x4], #16"
        code = code.replace("V<const>", "v0")
        body.append(code)
    body.append(
        "st4 {V<raw0>.8h, V<raw1>.8h, V<raw2>.8h, V<raw3>.8h}, "
        "[x0], #64"
    )
    if len(body) != 77:
        raise SystemExit(f"unexpected semantic iteration size: {len(body)}")
    return body


def suffix_symbols(line: str, iteration: int) -> str:
    return re.sub(
        r"<([A-Za-z_][A-Za-z0-9_]*)>",
        lambda match: f"<i{iteration}_{match.group(1)}>",
        line,
    )


def function_scaffold(symbol: str, body: list[str], symbolic: bool) -> str:
    lines = [
        ".text",
        ".align 4",
        f".global {symbol}",
        f".global _{symbol}",
        f"{symbol}:",
        f"_{symbol}:",
        "    sub sp, sp, #64",
        "    stp d8, d9, [sp, #0]",
        "    stp d10, d11, [sp, #16]",
        "    stp d12, d13, [sp, #32]",
        "    stp d14, d15, [sp, #48]",
        "    adr x3, .Lrminus1_pair_consts",
        "    ld1 {v0.8h}, [x3]",
        "    adrp x4, gt_rowbitrev_lambda",
        "    add x4, x4, :lo12:gt_rowbitrev_lambda",
        "    mov x8, #12",
        f".L{symbol}_loop:",
    ]
    if symbolic:
        lines.extend([
            "    // live-in: x0, x1, x2, x4, and fixed v0 constants",
            "    // live-out: x0/x1/x2 +128, x4 +32, and two output groups",
            "    // range: unchanged production raw R^-1 basemul contract",
            "    // reserved physical registers: v0, x5-x30, and sp",
            "    // ld4 outputs: Q<i0_a0>, Q<i0_a1>, Q<i0_a2>, Q<i0_a3>,",
            "    // Q<i0_b0>, Q<i0_b1>, Q<i0_b2>, Q<i0_b3>, Q<i1_a0>,",
            "    // Q<i1_a1>, Q<i1_a2>, Q<i1_a3>, Q<i1_b0>, Q<i1_b1>,",
            "    // Q<i1_b2>, Q<i1_b3>.",
            "rminus1_pair_slothy_start:",
        ])
    lines.extend(f"    {line}" for line in body)
    if symbolic:
        lines.append("rminus1_pair_slothy_end:")
    lines.extend([
        "    subs x8, x8, #1",
        f"    b.ne .L{symbol}_loop",
        "    ldp d14, d15, [sp, #48]",
        "    ldp d12, d13, [sp, #32]",
        "    ldp d10, d11, [sp, #16]",
        "    ldp d8, d9, [sp, #0]",
        "    add sp, sp, #64",
        "    ret",
        "",
        ".align 4",
        ".Lrminus1_pair_consts:",
        "    .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d",
        "    .hword 0xfa8f, 0xf9dd, 0xc5d5, 0x0000",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    physical = extract_body()
    semantic = semantic_iteration()
    baseline_counter = mnemonic_counter(physical)
    semantic_counter = mnemonic_counter(semantic)
    if baseline_counter != semantic_counter:
        raise SystemExit(
            f"semantic/production mnemonic mismatch: "
            f"{baseline_counter - semantic_counter} / "
            f"{semantic_counter - baseline_counter}"
        )

    u2_body = physical + physical
    iteration0 = [suffix_symbols(line, 0) for line in semantic]
    iteration1 = [suffix_symbols(line, 1) for line in semantic]
    tail = next(
        i for i, line in enumerate(iteration0)
        if "V<i0_r0_mlow>" in line
    )
    symbolic_body = [
        *iteration0[:tail],
        *iteration1[:3],
        *iteration0[tail:],
        *iteration1[3:],
    ]
    if mnemonic_counter(u2_body) != mnemonic_counter(symbolic_body):
        raise SystemExit("two-iteration mnemonic multiset mismatch")

    U2_OUTPUT.write_text(
        function_scaffold("poly_basemul_rminus1_pair_u2", u2_body, False),
        encoding="ascii",
    )
    SYMBOLIC_OUTPUT.write_text(
        function_scaffold(
            "poly_basemul_rminus1_pair_slothy", symbolic_body, True
        ),
        encoding="ascii",
    )
    print(f"u2_instructions={len(u2_body)}")
    print(f"symbolic_instructions={len(symbolic_body)}")
    print(f"baseline_sha_source={BASELINE}")


if __name__ == "__main__":
    main()
