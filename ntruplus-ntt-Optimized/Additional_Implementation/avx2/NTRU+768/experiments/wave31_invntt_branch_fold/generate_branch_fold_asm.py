#!/usr/bin/env python3
"""Generate same-body Wave31 R^-1 inverse tail endpoints."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import re


PRIVATE_INCLUDED_GLOBALS = (
    "gt_invntt_soa_ntt32_asm",
    "gt_invntt_soa_ntt32_lazy_asm",
    "gt_invntt_soa_dft3_asm",
    "gt_invntt_soa_postprocess_asm",
    "gt_invntt_soa_postprocess_algebraic_asm",
    "gt_invntt_soa_postprocess_rminus1_asm",
)


BRANCH_FOLD_MACRO = r"""

/*
 * Two fixed YMM linear maps replace:
 *   untwist -> branch sum/difference -> normalization/correction.
 *
 * The table row is:
 *   +0 low-output qinv, +32 low-output factor,
 *   +64 high-output qinv, +96 high-output factor.
 */
.macro W31_BRANCH_FOLD_GROUP exact=0
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3

	/* Low canonical half: preserve all four inputs for the second map. */
	vmovdqa  0(%r8), %ymm12
	vmovdqa 32(%r8), %ymm13
	vpmullw %ymm12, %ymm0, %ymm4
	vpmullw %ymm12, %ymm1, %ymm5
	vpmullw %ymm12, %ymm2, %ymm6
	vpmullw %ymm12, %ymm3, %ymm7
	vpmulhw %ymm13, %ymm0, %ymm8
	vpmulhw %ymm13, %ymm1, %ymm9
	vpmulhw %ymm13, %ymm2, %ymm10
	vpmulhw %ymm13, %ymm3, %ymm11
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm4, %ymm8, %ymm8
	vpsubw %ymm5, %ymm9, %ymm9
	vpsubw %ymm6, %ymm10, %ymm10
	vpsubw %ymm7, %ymm11, %ymm11

	/* High canonical half: inputs may now be overwritten by result highs. */
	vmovdqa 64(%r8), %ymm12
	vmovdqa 96(%r8), %ymm13
	vpmullw %ymm12, %ymm0, %ymm4
	vpmullw %ymm12, %ymm1, %ymm5
	vpmullw %ymm12, %ymm2, %ymm6
	vpmullw %ymm12, %ymm3, %ymm7
	vpmulhw %ymm13, %ymm0, %ymm0
	vpmulhw %ymm13, %ymm1, %ymm1
	vpmulhw %ymm13, %ymm2, %ymm2
	vpmulhw %ymm13, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm4, %ymm0, %ymm0
	vpsubw %ymm5, %ymm1, %ymm1
	vpsubw %ymm6, %ymm2, %ymm2
	vpsubw %ymm7, %ymm3, %ymm3

	/* Sum the two input-branch halves for each output row. */
	vextracti128 $1, %ymm8, %xmm4
	vextracti128 $1, %ymm9, %xmm5
	vextracti128 $1, %ymm10, %xmm6
	vextracti128 $1, %ymm11, %xmm7
	vpaddw %xmm4, %xmm8, %xmm8
	vpaddw %xmm5, %xmm9, %xmm9
	vpaddw %xmm6, %xmm10, %xmm10
	vpaddw %xmm7, %xmm11, %xmm11
	vextracti128 $1, %ymm0, %xmm4
	vextracti128 $1, %ymm1, %xmm5
	vextracti128 $1, %ymm2, %xmm6
	vextracti128 $1, %ymm3, %xmm7
	vpaddw %xmm4, %xmm0, %xmm0
	vpaddw %xmm5, %xmm1, %xmm1
	vpaddw %xmm6, %xmm2, %xmm2
	vpaddw %xmm7, %xmm3, %xmm3
	vinserti128 $1, %xmm0, %ymm8, %ymm0
	vinserti128 $1, %xmm1, %ymm9, %ymm1
	vinserti128 $1, %xmm2, %ymm10, %ymm2
	vinserti128 $1, %xmm3, %ymm11, %ymm3

	.if \exact
	/*
	 * The full signed-int16-input raw bound is 5053, below 1.5q.  One
	 * magnitude test and a signed q correction therefore select the unique
	 * centered representative in [-1728,1728].
	 */
	W31_CENTER_EXACT %ymm0
	W31_CENTER_EXACT %ymm1
	W31_CENTER_EXACT %ymm2
	W31_CENTER_EXACT %ymm3
	.endif

	POST_TRANSPOSE4X8
	POST_STORE_PAIR 0, 0
	POST_STORE_PAIR 1, 2
	POST_STORE_PAIR 2, 4
	POST_STORE_PAIR 3, 6
.endm

.macro W31_CENTER_EXACT value
	vpabsw \value, %ymm4
	vpcmpgtw .Lw31_center_hi(%rip), %ymm4, %ymm4
	vpand .Lpost_q(%rip), %ymm4, %ymm4
	vpsignw \value, %ymm4, %ymm4
	vpsubw %ymm4, \value, \value
.endm
"""


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def format_row(values: list[int]) -> str:
    return "\n".join(f"\t.short {value}" for value in values)


def factor_rodata(analysis) -> str:
    rows = analysis.untwist_rows()
    folded = [
        analysis.fold_row(row, *analysis.NORM["rminus1_input"]) for row in rows
    ]
    body = [".section .rodata", ".p2align 5", ".Lw31_rminus_factors:"]
    for row in folded:
        body.extend(
            (
                format_row(row["low_output_qinv"]),
                format_row(row["low_output"]),
                format_row(row["high_output_qinv"]),
                format_row(row["high_output"]),
            )
        )
    body.extend(
        (
            ".p2align 5",
            ".Lw31_center_hi:",
            "\t.rept 16\n\t.short 1728\n\t.endr",
        )
    )
    return "\n".join(body) + "\n"


def make_function(template: str, symbol: str, label: str, post: str) -> str:
    text = template.replace(
        "wave20_invntt_native_three_child_avx2", symbol
    ).replace(".Lwave20_native_three_child", label)
    start_marker = "\tmovq %r10, %rdi\n\tmovq %rsp, %rsi\n"
    start = text.index(start_marker)
    end = text.index("\n\tmovq %r11, %rsp", start)
    return text[:start] + post + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--native-generator", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    preamble = "".join(
        f"#define {name} wave31_private_{name}\n"
        for name in PRIVATE_INCLUDED_GLOBALS
    )
    globals_ = re.findall(
        r"^\s*\.globl\s+([A-Za-z0-9_]+)\s*$", source, re.MULTILINE
    )
    if len(globals_) < 10:
        raise RuntimeError("upstream global-symbol audit changed")
    for name in globals_:
        source = re.sub(
            rf"\b{re.escape(name)}\b", f"wave31_private_{name}", source
        )

    native_generator = args.native_generator.read_text(encoding="utf-8")
    match = re.search(
        r'CUSTOM_FUNCTION = r"""(?P<body>.*?)"""\n\n\ndef main',
        native_generator,
        re.DOTALL,
    )
    if match is None:
        raise RuntimeError("Wave20 native function template audit changed")
    template = match.group("body")

    baseline_post = r"""	movq %r10, %rdi
	movq %rsp, %rsi
	vmovdqa .Lpost_q(%rip), %ymm15
	leaq gt_inv_untwist(%rip), %r8
	leaq gt_inv_untwist_qinv(%rip), %r9
	leaq gt_inv_output_block(%rip), %rdx
	movl $12, %ecx
.p2align 5
.Lw31_baseline_post:
	POSTPROCESS_GROUP_ALGEBRAIC .Lpost_ninv_rminus1_pair, .Lpost_zninv_rminus1_pair, 1
	addq $128, %rsi
	addq $32, %r8
	addq $32, %r9
	addq $8, %rdx
	decl %ecx
	jne .Lw31_baseline_post
"""
    fold_post_template = r"""	movq %r10, %rdi
	movq %rsp, %rsi
	vmovdqa .Lpost_q(%rip), %ymm15
	leaq .Lw31_rminus_factors(%rip), %r8
	leaq gt_inv_output_block(%rip), %rdx
	movl $12, %ecx
.p2align 5
{label}:
	W31_BRANCH_FOLD_GROUP {exact}
	addq $128, %rsi
	addq $128, %r8
	addq $8, %rdx
	decl %ecx
	jne {label}
"""
    baseline = make_function(
        template,
        "wave31_invntt_native_rminus1_algebraic_avx2",
        ".Lw31_baseline",
        baseline_post,
    )
    lazy = make_function(
        template,
        "wave31_invntt_native_rminus1_branch_fold_lazy_avx2",
        ".Lw31_lazy",
        fold_post_template.format(label=".Lw31_lazy_post", exact=0),
    )
    exact = make_function(
        template,
        "wave31_invntt_native_rminus1_branch_fold_exact_avx2",
        ".Lw31_exact",
        fold_post_template.format(label=".Lw31_exact_post", exact=1),
    )
    analysis = load_module(args.analysis, "wave31_analysis")
    output = (
        preamble
        + source
        + BRANCH_FOLD_MACRO
        + baseline
        + lazy
        + exact
        + factor_rodata(analysis)
        + "\n.section .note.GNU-stack,\"\",@progbits\n"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
