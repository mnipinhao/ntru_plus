#!/usr/bin/env python3
"""Generate the symbolic whole-DAG U1 canonical-unpack chunk."""

from pathlib import Path


EXP = Path(__file__).resolve().parent
OUTPUT = EXP / "unpack_chunk_u1.sym.S"
OFFSETS = [312, 288, 360, 336, 264, 240, 192, 216,
           72, 48, 0, 24, 168, 144, 96, 120]


def unpack12() -> list[str]:
    return [
        "    ushr V<sh0>.8h, V<z0>.8h, #12",
        "    shl V<sh1>.8h, V<z1>.8h, #4",
        "    ushr V<sh2>.8h, V<z1>.8h, #8",
        "    shl V<sh3>.8h, V<z2>.8h, #8",
        "    ushr V<sh4>.8h, V<z2>.8h, #4",
        "    ushr V<sh5>.8h, V<z3>.8h, #12",
        "    shl V<sh6>.8h, V<z4>.8h, #4",
        "    ushr V<sh7>.8h, V<z4>.8h, #8",
        "    shl V<sh8>.8h, V<z5>.8h, #8",
        "    ushr V<sh9>.8h, V<z5>.8h, #4",
        "    eor V<m1>.16b, V<sh0>.16b, V<sh1>.16b",
        "    eor V<m2>.16b, V<sh2>.16b, V<sh3>.16b",
        "    eor V<m5>.16b, V<sh5>.16b, V<sh6>.16b",
        "    eor V<m6>.16b, V<sh7>.16b, V<sh8>.16b",
        "    and V<u0>.16b, V<z0>.16b, v0.16b",
        "    and V<u1>.16b, V<m1>.16b, v0.16b",
        "    and V<u2>.16b, V<m2>.16b, v0.16b",
        "    and V<u3>.16b, V<sh4>.16b, v0.16b",
        "    and V<u4>.16b, V<z3>.16b, v0.16b",
        "    and V<u5>.16b, V<m5>.16b, v0.16b",
        "    and V<u6>.16b, V<m6>.16b, v0.16b",
        "    and V<u7>.16b, V<sh9>.16b, v0.16b",
    ]


def unpack_input_transpose() -> list[str]:
    return [
        "    ld1 {V<p0>.8h, V<p1>.8h, V<p2>.8h}, [x1], #48",
        "    ld1 {V<p3>.8h, V<p4>.8h, V<p5>.8h}, [x1], #48",
        "    trn1 V<d0>.2d, V<p0>.2d, V<p3>.2d",
        "    trn2 V<d1>.2d, V<p0>.2d, V<p3>.2d",
        "    trn1 V<d2>.2d, V<p1>.2d, V<p4>.2d",
        "    trn2 V<d3>.2d, V<p1>.2d, V<p4>.2d",
        "    trn1 V<d4>.2d, V<p2>.2d, V<p5>.2d",
        "    trn2 V<d5>.2d, V<p2>.2d, V<p5>.2d",
        "    trn1 V<s0>.4s, V<d0>.4s, V<d3>.4s",
        "    trn2 V<s1>.4s, V<d0>.4s, V<d3>.4s",
        "    trn1 V<s2>.4s, V<d1>.4s, V<d4>.4s",
        "    trn2 V<s3>.4s, V<d1>.4s, V<d4>.4s",
        "    trn1 V<s4>.4s, V<d2>.4s, V<d5>.4s",
        "    trn2 V<s5>.4s, V<d2>.4s, V<d5>.4s",
        "    trn1 V<z0>.8h, V<s0>.8h, V<s3>.8h",
        "    trn2 V<z1>.8h, V<s0>.8h, V<s3>.8h",
        "    trn1 V<z2>.8h, V<s1>.8h, V<s4>.8h",
        "    trn2 V<z3>.8h, V<s1>.8h, V<s4>.8h",
        "    trn1 V<z4>.8h, V<s2>.8h, V<s5>.8h",
        "    trn2 V<z5>.8h, V<s2>.8h, V<s5>.8h",
    ]


def canonical_to_gt_transpose() -> list[str]:
    out: list[str] = []
    for pair in range(4):
        out += [
            f"    trn1 V<h{2 * pair}>.8h, V<u{2 * pair}>.8h, V<u{2 * pair + 1}>.8h",
            f"    trn2 V<h{2 * pair + 1}>.8h, V<u{2 * pair}>.8h, V<u{2 * pair + 1}>.8h",
        ]
    out += [
        "    trn1 V<q0s>.4s, V<h0>.4s, V<h2>.4s",
        "    trn2 V<q2s>.4s, V<h0>.4s, V<h2>.4s",
        "    trn1 V<q1s>.4s, V<h1>.4s, V<h3>.4s",
        "    trn2 V<q3s>.4s, V<h1>.4s, V<h3>.4s",
        "    trn1 V<q4s>.4s, V<h4>.4s, V<h6>.4s",
        "    trn2 V<q6s>.4s, V<h4>.4s, V<h6>.4s",
        "    trn1 V<q5s>.4s, V<h5>.4s, V<h7>.4s",
        "    trn2 V<q7s>.4s, V<h5>.4s, V<h7>.4s",
    ]
    for lane in range(4):
        out += [
            f"    trn1 V<q{lane}>.2d, V<q{lane}s>.2d, V<q{lane + 4}s>.2d",
            f"    trn2 V<q{lane + 4}>.2d, V<q{lane}s>.2d, V<q{lane + 4}s>.2d",
        ]
    return out


def scatter() -> list[str]:
    out: list[str] = []
    for pair in range(8):
        out += [
            f"    str D<q{pair}>, [x0, #{OFFSETS[2 * pair]}]",
            f"    umov x9, V<q{pair}>.d[1]",
            f"    str x9, [x0, #{OFFSETS[2 * pair + 1]}]",
        ]
    return out


def main() -> int:
    lines = [
        "// U1 whole-DAG canonical unpack; experiment only.",
        "// Live-in: x0=GT destination base, x1=canonical source, v0=0x0fff.",
        "// Live-out: x1 advanced by 96; 16 fixed GT blocks stored.",
        "// x9 is a caller-saved lane-transfer temporary.",
        "slothy_start_gt_canonical_unpack_chunk_u1:",
        *unpack_input_transpose(),
        *unpack12(),
        *canonical_to_gt_transpose(),
        *scatter(),
        "slothy_end_gt_canonical_unpack_chunk_u1:",
        "",
    ]
    OUTPUT.write_text("\n".join(lines))
    count = sum(1 for line in lines if line.startswith("    "))
    print(f"{OUTPUT}: {count} instructions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
