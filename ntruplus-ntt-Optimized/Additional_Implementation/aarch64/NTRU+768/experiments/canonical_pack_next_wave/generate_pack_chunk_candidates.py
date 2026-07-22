#!/usr/bin/env python3
"""Generate symbolic P1/P2/P3 canonical-pack chunk candidates."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
OUTPUT = EXP / "pack_chunk_candidates.sym.S"
OFFSETS = [312, 288, 360, 336, 264, 240, 192, 216,
           72, 48, 0, 24, 168, 144, 96, 120]


def gather() -> list[str]:
    out: list[str] = []
    for pair in range(8):
        out += [
            f"    ldr D<g{pair}>, [x1, #{OFFSETS[2 * pair]}]",
            f"    ldr D<g{pair}_hi>, [x1, #{OFFSETS[2 * pair + 1]}]",
            f"    mov V<g{pair}>.d[1], V<g{pair}_hi>.d[0]",
        ]
    return out


def normalize(variant: str) -> tuple[list[str], list[str]]:
    out: list[str] = []
    names: list[str] = []
    for lane in range(8):
        if variant == "p1":
            out += [
                f"    sshr V<sign{lane}>.8h, V<g{lane}>.8h, #15",
                f"    and V<corr{lane}>.16b, V<sign{lane}>.16b, v0.16b",
                f"    add V<ng{lane}>.8h, V<g{lane}>.8h, V<corr{lane}>.8h",
            ]
            names.append(f"ng{lane}")
        elif variant == "p2":
            out += [
                f"    sshr V<sign{lane}>.8h, V<g{lane}>.8h, #15",
                f"    mls V<g{lane}>.8h, V<sign{lane}>.8h, v0.8h",
            ]
            names.append(f"g{lane}")
        elif variant == "p3":
            out += [
                f"    ushr V<sign{lane}>.8h, V<g{lane}>.8h, #15",
                f"    mla V<g{lane}>.8h, V<sign{lane}>.8h, v0.8h",
            ]
            names.append(f"g{lane}")
        else:
            raise ValueError(variant)
    return out, names


def transpose(inputs: list[str]) -> list[str]:
    out: list[str] = []
    for pair in range(4):
        out += [
            f"    trn1 V<h{2 * pair}>.8h, V<{inputs[2 * pair]}>.8h, V<{inputs[2 * pair + 1]}>.8h",
            f"    trn2 V<h{2 * pair + 1}>.8h, V<{inputs[2 * pair]}>.8h, V<{inputs[2 * pair + 1]}>.8h",
        ]
    out += [
        "    trn1 V<s0>.4s, V<h0>.4s, V<h2>.4s",
        "    trn2 V<s2>.4s, V<h0>.4s, V<h2>.4s",
        "    trn1 V<s1>.4s, V<h1>.4s, V<h3>.4s",
        "    trn2 V<s3>.4s, V<h1>.4s, V<h3>.4s",
        "    trn1 V<s4>.4s, V<h4>.4s, V<h6>.4s",
        "    trn2 V<s6>.4s, V<h4>.4s, V<h6>.4s",
        "    trn1 V<s5>.4s, V<h5>.4s, V<h7>.4s",
        "    trn2 V<s7>.4s, V<h5>.4s, V<h7>.4s",
    ]
    for lane in range(4):
        out += [
            f"    trn1 V<n{lane}>.2d, V<s{lane}>.2d, V<s{lane + 4}>.2d",
            f"    trn2 V<n{lane + 4}>.2d, V<s{lane}>.2d, V<s{lane + 4}>.2d",
        ]
    return out


def pack12() -> list[str]:
    return [
        "    ushr V<p0>.8h, V<n1>.8h, #4",
        "    ushr V<p1>.8h, V<n2>.8h, #8",
        "    ushr V<p2>.8h, V<n5>.8h, #4",
        "    ushr V<p3>.8h, V<n6>.8h, #8",
        "    shl V<p4>.8h, V<n1>.8h, #12",
        "    shl V<p5>.8h, V<n2>.8h, #8",
        "    shl V<p6>.8h, V<n3>.8h, #4",
        "    shl V<p7>.8h, V<n5>.8h, #12",
        "    shl V<p8>.8h, V<n6>.8h, #8",
        "    shl V<p9>.8h, V<n7>.8h, #4",
        "    eor V<u0>.16b, V<n0>.16b, V<p4>.16b",
        "    eor V<u1>.16b, V<p0>.16b, V<p5>.16b",
        "    eor V<u2>.16b, V<p1>.16b, V<p6>.16b",
        "    eor V<u3>.16b, V<n4>.16b, V<p7>.16b",
        "    eor V<u4>.16b, V<p2>.16b, V<p8>.16b",
        "    eor V<u5>.16b, V<p3>.16b, V<p9>.16b",
        "    trn1 V<b0>.8h, V<u0>.8h, V<u1>.8h",
        "    trn1 V<b1>.8h, V<u2>.8h, V<u3>.8h",
        "    trn1 V<b2>.8h, V<u4>.8h, V<u5>.8h",
        "    trn2 V<b3>.8h, V<u0>.8h, V<u1>.8h",
        "    trn2 V<b4>.8h, V<u2>.8h, V<u3>.8h",
        "    trn2 V<b5>.8h, V<u4>.8h, V<u5>.8h",
        "    trn1 V<c0>.4s, V<b0>.4s, V<b1>.4s",
        "    trn1 V<c1>.4s, V<b2>.4s, V<b3>.4s",
        "    trn1 V<c2>.4s, V<b4>.4s, V<b5>.4s",
        "    trn2 V<c3>.4s, V<b0>.4s, V<b1>.4s",
        "    trn2 V<c4>.4s, V<b2>.4s, V<b3>.4s",
        "    trn2 V<c5>.4s, V<b4>.4s, V<b5>.4s",
        "    trn1 V<out0>.2d, V<c0>.2d, V<c1>.2d",
        "    trn1 V<out1>.2d, V<c2>.2d, V<c3>.2d",
        "    trn1 V<out2>.2d, V<c4>.2d, V<c5>.2d",
        "    trn2 V<out3>.2d, V<c0>.2d, V<c1>.2d",
        "    trn2 V<out4>.2d, V<c2>.2d, V<c3>.2d",
        "    trn2 V<out5>.2d, V<c4>.2d, V<c5>.2d",
        "    st1 {V<out0>.8h, V<out1>.8h, V<out2>.8h}, [x0], #48",
        "    st1 {V<out3>.8h, V<out4>.8h, V<out5>.8h}, [x0], #48",
    ]


def region(variant: str) -> list[str]:
    norm, inputs = normalize(variant)
    return [
        f"// {variant.upper()} live-in: x0=dst, x1=GT source base, v0=q.",
        "// Live-out: x0 advanced by 96 and canonical blocks 0..15 stored.",
        "// Range: input [-3457,3456], normalized output [0,3456].",
        "// Reserved physical registers: x2-x30, sp, and fixed v0.",
        "// Checker declarations: V<p4>, V<p5>, V<p6>, V<p7>, V<p8>, and V<p9> are defined by shl instructions below; they are not live-ins.",
        f"slothy_start_gt_canonical_pack_chunk_{variant}:",
        *gather(),
        *norm,
        *transpose(inputs),
        *pack12(),
        f"slothy_end_gt_canonical_pack_chunk_{variant}:",
        "",
    ]


def main() -> int:
    lines = ["// Generated symbolic source; experiment only.", ""]
    for variant in ("p1", "p2", "p3"):
        lines += region(variant)
    OUTPUT.write_text("\n".join(lines))
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
