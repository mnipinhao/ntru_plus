#!/usr/bin/env python3
"""Generate two-iteration Q31 baseline and Slothy symbolic candidates."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "asm/gt/basemul/poly_basemul_add_encap_tobytes_q31.S"
OLD = "poly_basemul_add_encap_direct32_q31_tobytes_contract"
U2 = "poly_basemul_add_encap_direct32_q31_pair_u2"
S2 = "poly_basemul_add_encap_direct32_q31_pair_slothy"


def renamed(lines, symbol):
    text = "\n".join(lines)
    text = text.replace('#include "../support/common.inc"',
                        '#include "../../asm/gt/support/common.inc"')
    text = text.replace(OLD, symbol)
    text = text.replace("Ldirect32_q31_loop", f"L{symbol}_loop")
    text = text.replace("Ldirect32_q31_consts", f"L{symbol}_consts")
    return text.splitlines()


def emit(symbol, symbolic):
    source = SOURCE.read_text(encoding="ascii").splitlines()
    loop = source.index("Ldirect32_q31_loop:")
    subs = next(i for i in range(loop, len(source))
                if source[i].strip() == "subs x6, x6, #1")
    branch = subs + 1
    body = source[loop + 1:subs]
    split = next(i for i, line in enumerate(body) if "P0=v31/v10" in line)
    core = body[:split]
    finalizer = body[split:]
    lines = source[:loop]
    lines.append("Ldirect32_q31_loop:")
    lines.extend(core)
    if symbolic:
        lines.extend([
            "\t// live-in: x0-x4, v11, and iteration-N accumulators/c vectors",
            "\t// live-out: advanced x0-x4 and iteration-N+1 Q31 accumulators/c vectors",
            "\t// coefficient range: identical to the audited production Q31 byte contract",
            "\t// reserved physical registers: x7-x30 and sp; physical vector allocation fixed",
            "q31_pair_xover_slothy_start:",
        ])
    lines.extend(finalizer)
    lines.extend(core)
    if symbolic:
        lines.extend([
            "q31_pair_xover_slothy_end:",
            "\t// live-in: x0, v11, and iteration-N+1 accumulators/c vectors",
            "\t// live-out: two stored Q31 byte-contract groups and advanced x0",
            "\t// coefficient range: identical to the audited production Q31 byte contract",
            "\t// reserved physical registers: x7-x30 and sp; physical vector allocation fixed",
            "q31_pair_tail_slothy_start:",
        ])
    lines.extend(finalizer)
    if symbolic:
        lines.append("q31_pair_tail_slothy_end:")
    lines.extend([
        "\tsubs x6, x6, #2",
        "\tb.ne Ldirect32_q31_loop",
    ])
    lines.extend(source[branch + 1:])
    if symbolic:
        body_start = next(i for i, line in enumerate(lines)
                          if "LOAD_ADDR_PAGE" in line)
        lines[body_start:body_start] = [
            "\tsub sp, sp, #64",
            "\tstp d8, d9, [sp, #0]",
            "\tstp d10, d11, [sp, #16]",
            "\tstp d12, d13, [sp, #32]",
            "\tstp d14, d15, [sp, #48]",
        ]
        return_site = max(i for i, line in enumerate(lines)
                          if line.strip() == "ret")
        lines[return_site:return_site] = [
            "\tldp d14, d15, [sp, #48]",
            "\tldp d12, d13, [sp, #32]",
            "\tldp d10, d11, [sp, #16]",
            "\tldp d8, d9, [sp, #0]",
            "\tadd sp, sp, #64",
        ]
    lines = renamed(lines, symbol)
    return "\n".join(lines) + "\n"


def main():
    (HERE / "q31_pair_u2.S").write_text(emit(U2, False), encoding="ascii")
    (HERE / "q31_pair_pipeline.sym.S").write_text(
        emit(S2, True), encoding="ascii")


if __name__ == "__main__":
    main()
