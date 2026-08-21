#!/usr/bin/env python3
"""Conservative per-packet range audit for the two Encap Q24 producers.

This is a generator-only experiment.  It models the selected production
frontend, progressive-M NTT, general B3, add(m), and M-to-Q24 transpose.
It deliberately does not use the stale lazy10788/highrange12699 symbol names
as range contracts.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

Q = 3457
HALF_Q_CORRECTION = (Q + 1) // 2


def label_values(source: str, label: str, directive: str) -> list[int]:
    marker = f"{label}:"
    if marker not in source:
        raise ValueError(f"missing {label}")
    values: list[int] = []
    for line in source.split(marker, 1)[1].splitlines():
        s = line.strip()
        if s.startswith(".section") or (s.startswith(".L") and s.endswith(":")):
            break
        if directive in line:
            values.extend(int(x) for x in re.findall(r"-?\d+", line.split(directive, 1)[1]))
        elif ".rept" in line:
            # All selected constants used here are written explicitly except
            # scalar replicated constants, which are read separately.
            continue
    if not values:
        raise ValueError(f"no values at {label}")
    return values


def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def mont(a: int, factor: int) -> int:
    """Absolute bound for selected signed 16-bit Montgomery multiply."""
    return ceil_div(a * abs(factor), 1 << 16) + HALF_Q_CORRECTION


def runtime_mont(a: int, b: int) -> int:
    return ceil_div(a * b, 1 << 16) + HALF_Q_CORRECTION


def unpack_dq(a: list[int], b: list[int], high: bool) -> list[int]:
    out: list[int] = []
    for lane in (0, 8):
        start = lane + (4 if high else 0)
        out += a[start:start + 2] + b[start:start + 2]
        out += a[start + 2:start + 4] + b[start + 2:start + 4]
    return out


def unpack_q(a: list[int], b: list[int], high: bool) -> list[int]:
    out: list[int] = []
    for lane in (0, 8):
        start = lane + (4 if high else 0)
        out += a[start:start + 4] + b[start:start + 4]
    return out


def transpose4(v: list[list[int]]) -> list[list[int]]:
    # Exact word-level form of Q24_TRANSPOSE/TILE4_TRANSPOSE.
    s0, s1, s2, s3 = v
    t0 = [x for i in range(0, 8) for x in (s0[i], s1[i])] + [x for i in range(8, 16) for x in (s0[i], s1[i])]
    t1 = [x for i in range(8, 16) for x in (s0[i], s1[i])]  # overwritten below
    # Word-unpack is lane local: split low/high 8 words in each 128-bit lane.
    def uw(a: list[int], b: list[int], high: bool) -> list[int]:
        out: list[int] = []
        for lane in (0, 8):
            start = lane + (4 if high else 0)
            for i in range(start, start + 4):
                out += [a[i], b[i]]
        return out
    t0, t1 = uw(s0, s1, False), uw(s0, s1, True)
    t2, t3 = uw(s2, s3, False), uw(s2, s3, True)
    a0, a1 = unpack_dq(t0, t2, False), unpack_dq(t0, t2, True)
    a2, a3 = unpack_dq(t1, t3, False), unpack_dq(t1, t3, True)
    return [unpack_q(a0, a2, False), unpack_q(a0, a2, True),
            unpack_q(a1, a3, False), unpack_q(a1, a3, True)]


def pshufb_plane(v: list[int]) -> list[int]:
    p = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]
    return [v[i] for i in p]


def packed_to_planes(v: list[list[int]]) -> list[list[int]]:
    a, b, c, d = [pshufb_plane(x) for x in v]
    x0, x1 = unpack_dq(a, c, False), unpack_dq(a, c, True)
    x2, x3 = unpack_dq(b, d, False), unpack_dq(b, d, True)
    return [unpack_q(x0, x2, False), unpack_q(x0, x2, True),
            unpack_q(x1, x3, False), unpack_q(x1, x3, True)]


def half_pair(a: list[int], b: list[int], factors: list[int]) -> tuple[list[int], list[int]]:
    low = a[:8] + b[:8]
    high = a[8:] + b[8:]
    out = [low[i] + mont(high[i], factors[i]) for i in range(16)]
    # sum and difference have the same absolute bound.
    return out[:8] + out[:8], out[8:] + out[8:]


def qword_pair(a: list[int], b: list[int], factors: list[int]) -> tuple[list[int], list[int]]:
    low = unpack_q(a, b, False)
    high = unpack_q(a, b, True)
    out = [low[i] + mont(high[i], factors[i]) for i in range(16)]
    return out, out.copy()


def forward_bounds(ntt: str, ntt_m: str) -> list[list[int]]:
    twist = label_values(ntt, ".Ltile4_frontend_wide_twist_factor", ".short")
    assert len(twist) == 8 * 96
    omega = 886
    # Six branch streams, eight YMM each, exactly matching frontend stores.
    branches: list[list[list[int]]] = [[] for _ in range(6)]
    for it in range(8):
        fs = twist[it * 96:(it + 1) * 96]
        first = [[mont(723, f) for f in fs[j * 16:(j + 1) * 16]] for j in range(3)]
        second = [[mont(724, f) for f in fs[(j + 3) * 16:(j + 4) * 16]] for j in range(3)]
        for group, base in ((first, 0), (second, 1)):
            x, y, z = group
            w = [mont(y[i] + z[i], omega) for i in range(16)]
            outs = [[x[i] + y[i] + z[i] for i in range(16)],
                    [x[i] + z[i] + w[i] for i in range(16)],
                    [x[i] + y[i] + w[i] for i in range(16)]]
            branches[base].append(outs[0])
            branches[base + 2].append(outs[1])
            branches[base + 4].append(outs[2])

    s2 = label_values(ntt_m, ".Ltile4_fwd_s2_factor", ".short")
    s3 = label_values(ntt_m, ".Ltile4_fwd_s3_factor", ".short")
    s4 = label_values(ntt_m, ".Ltile4_fwd_s4_pair_factor", ".short")
    s5 = label_values(ntt_m, ".Ltile4_fwd_s5_pair_factor", ".short")
    assert [len(x) for x in (s2, s3, s4, s5)] == [64, 64, 64, 64]

    result: list[list[int]] = []
    for regs in branches:
        # S1 raw cross.
        v = [None] * 8
        for k, (lo, hi) in enumerate(((0, 4), (1, 5), (2, 6), (3, 7))):
            b = [regs[lo][i] + regs[hi][i] for i in range(16)]
            v[lo] = b
            v[hi] = b.copy()
        # S2 and S3 cross butterflies.
        for pairs, factors in [(((0, 2), (1, 3), (4, 6), (5, 7)), s2),
                               (((0, 1), (2, 3), (4, 5), (6, 7)), s3)]:
            nv = v.copy()
            for k, (lo, hi) in enumerate(pairs):
                b = [v[lo][i] + mont(v[hi][i], factors[k * 16 + i]) for i in range(16)]
                nv[lo], nv[hi] = b, b.copy()
            v = nv
        for k, (a, b) in enumerate(((0, 1), (2, 3), (4, 5), (6, 7))):
            v[a], v[b] = half_pair(v[a], v[b], s4[k * 16:(k + 1) * 16])
        for k, (a, b) in enumerate(((0, 1), (2, 3), (4, 5), (6, 7))):
            v[a], v[b] = qword_pair(v[a], v[b], s5[k * 16:(k + 1) * 16])
        result += packed_to_planes(v[:4]) + packed_to_planes(v[4:])
    assert len(result) == 48
    return result


Q24_GROUPS = [
    (0, [3, 2, 0, 1]), (4, [3, 2, 0, 1]),
    (36, [0, 1, 2, 3]), (32, [2, 3, 1, 0]),
    (16, [1, 0, 3, 2]), (20, [1, 0, 3, 2]),
    (44, [2, 3, 1, 0]), (40, [1, 0, 3, 2]),
    (24, [3, 2, 0, 1]), (28, [3, 2, 0, 1]),
    (12, [0, 1, 2, 3]), (8, [2, 3, 1, 0]),
]


def parse_q24_groups(pack: str) -> list[tuple[int, list[int]]]:
    body = pack.split(".macro Q24_ENCODE_SOA_BODY", 1)[1].split(".endm", 1)[0]
    lines = body.splitlines()
    groups: list[tuple[int, list[int]]] = []
    for i, line in enumerate(lines):
        m = re.search(r"vmovdqu\s+(\d+)\(%rsi\),\s+%ymm0", line)
        if not m:
            continue
        following = "\n".join(lines[i:i + 12])
        regs = [int(x) - 4 for x in re.findall(
            r"Q24_ENCODE_REG_PACKET\s+%ymm([4567])", following)]
        if len(regs) != 4:
            raise ValueError("could not bind one Q24 packet group")
        groups.append((int(m.group(1)) // 32, regs))
    return groups


def packets_from_m(vectors: list[list[int]]) -> list[list[int]]:
    packets: list[list[int]] = []
    for start, order in Q24_GROUPS:
        t = transpose4(vectors[start:start + 4])
        packets += [t[i] for i in order]
    assert len(packets) == 48 and all(len(p) == 16 for p in packets)
    return packets


def final_sum_bounds(forward: list[list[int]], basemul: str) -> list[list[int]]:
    lambdas = label_values(basemul, ".Ltile4_bm_lambda", ".short")
    assert len(lambdas) == 12 * 16
    out: list[list[int]] = []
    for tile in range(12):
        r = forward[tile * 4:(tile + 1) * 4]
        planes = [[0] * 16 for _ in range(4)]
        for lane in range(16):
            p = [[runtime_mont(Q - 1, r[j][lane]) for j in range(4)] for _ in range(4)]
            lam = lambdas[tile * 16 + lane]
            raw = [
                p[0][0] + mont(p[1][3] + p[2][2] + p[3][1], lam),
                p[1][0] + p[0][1] + mont(p[3][2] + p[2][3], lam),
                p[2][0] + p[1][1] + p[0][2] + mont(p[3][3], lam),
                p[3][0] + p[2][1] + p[1][2] + p[0][3],
            ]
            for d in range(4):
                planes[d][lane] = mont(raw[d], 867) + r[d][lane]
        out += planes
    return out


def classify(bound: int) -> str:
    if bound < Q:
        return "class1_sign_only"
    if bound < 2 * Q:
        return "class2_one_conditional_q"
    return "class3_full_reducer"


def summarize(packets: list[list[int]]) -> dict[str, object]:
    maxima = [max(p) for p in packets]
    minima = [min(p) for p in packets]
    classes = [classify(x) for x in maxima]
    lane_classes = [classify(x) for p in packets for x in p]
    return {
        "packet_maxima": maxima,
        "global_maximum": max(maxima),
        "global_minimum_bound": min(minima),
        "minimum_packet_maximum": min(maxima),
        "class_counts": {c: classes.count(c) for c in sorted(set(classes))},
        "lane_class_counts": {c: lane_classes.count(c) for c in sorted(set(lane_classes))},
        "packet_classes": classes,
        "all_require_full_reducer": all(c == "class3_full_reducer" for c in classes),
        "all_768_lanes_require_full_reducer_under_proof": all(
            c == "class3_full_reducer" for c in lane_classes),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    ntt = (args.root / "ntt.s").read_text()
    ntt_m = (args.root / "ntt_m.s").read_text()
    basemul = (args.root / "basemul.s").read_text()
    pack = (args.root / "pack.s").read_text()
    # Bind the hand-written packet order to the selected macro.
    assert parse_q24_groups(pack) == Q24_GROUPS

    fwd = forward_bounds(ntt, ntt_m)
    final = final_sum_bounds(fwd, basemul)
    result = {
        "schema": "gt32-encap-q24-packet-range-051-v1",
        "production_modified": False,
        "method": "per-lane conservative absolute-bound propagation over selected production ASM",
        "classes": {
            "class0": "proven [0,q); unavailable from absolute-only propagation",
            "class1_sign_only": "|x| < q",
            "class2_one_conditional_q": "|x| < 2q",
            "class3_full_reducer": "otherwise",
        },
        "producer_rhat": summarize(packets_from_m(fwd)),
        "producer_ciphertext": summarize(packets_from_m(final)),
        "selected_contract_correction": {
            "lazy10788_highrange12699_names": "stale names, not executable contracts",
            "actual_selected_body": "full signed-int16 reducer",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
