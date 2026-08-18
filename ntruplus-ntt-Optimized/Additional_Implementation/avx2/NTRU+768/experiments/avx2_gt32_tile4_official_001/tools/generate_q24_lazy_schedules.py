#!/usr/bin/env python3
"""Generate matched L1/L2/L3 schedules from the frozen Q24 SoA route."""

import argparse
import json
import re
from pathlib import Path


CALL = re.compile(
    r"\s*Q24_ENCODE_REG_PACKET\s+(%ymm\d+),(%xmm\d+),(\d+),(\d+),(\d+)")


def parse_groups(source: Path):
    lines = source.read_text().splitlines()
    begin = lines.index(".macro Q24_ENCODE_SOA_BODY") + 1
    end = lines.index(".endm", begin)
    groups = []
    loads = []
    packets = []
    for line in lines[begin:end]:
        match = CALL.fullmatch(line)
        if match:
            packets.append(match.groups())
            if len(packets) == 4:
                groups.append((loads, packets))
                loads = []
                packets = []
        else:
            loads.append(line)
    if loads or packets or len(groups) != 12:
        raise RuntimeError("unexpected frozen Q24 SoA body shape")
    return groups


def args(packet):
    return ",".join(packet)


def tf1_packet(packet):
    """Return a packet after absorbing/removing symmetric qword routing."""
    ymm, xmm, perm, offset, safe = packet
    if int(perm) in (0xB1, 0xE4):
        perm = str(0xE4)
    return ymm, xmm, perm, offset, safe


def emit_tf1_body(name, groups):
    out = [f".macro {name}"]
    removed = 0
    for loads, packets in groups:
        by_register = {int(packet[0][4:]): packet for packet in packets}
        orientations = [
            int(int(by_register[reg][2]) == 0xB1) for reg in range(4, 8)
        ]
        if not loads[-1].lstrip().startswith("Q24_TRANSPOSE "):
            raise RuntimeError("unexpected frozen transpose position")
        out.extend(loads[:-1])
        out.append(
            "\tQ24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,"
            "ymm4,ymm5,ymm6,ymm7," + ",".join(map(str, orientations)))
        transformed = [tf1_packet(packet) for packet in packets]
        removed += sum(int(int(packet[2]) in (0xB1, 0xE4))
                       for packet in packets)
        out.append(f"\tQ24_LAZY_PAIR_TF1 {args(transformed[0])},"
                   f"{args(transformed[1])}")
        out.append(f"\tQ24_LAZY_PAIR_TF1 {args(transformed[2])},"
                   f"{args(transformed[3])}")
    out.append(".endm")
    return out, removed


def emit_serial_tf1_body(name, groups):
    out = [f".macro {name}"]
    for loads, packets in groups:
        by_register = {int(packet[0][4:]): packet for packet in packets}
        orientations = [
            int(int(by_register[reg][2]) == 0xB1) for reg in range(4, 8)
        ]
        out.extend(loads[:-1])
        out.append(
            "\tQ24_TRANSPOSE_TF1 ymm0,ymm1,ymm2,ymm3,"
            "ymm4,ymm5,ymm6,ymm7," + ",".join(map(str, orientations)))
        for packet in map(tf1_packet, packets):
            out.append(f"\tQ24_ENCODE_TF1_PACKET {args(packet)}")
    out.append(".endm")
    return out


def emit_body(name, groups, schedule):
    out = [f".macro {name}"]
    for loads, packets in groups:
        out.extend(loads)
        if schedule == "pair":
            out.append(f"\tQ24_LAZY_PAIR {args(packets[0])},{args(packets[1])}")
            out.append(f"\tQ24_LAZY_PAIR {args(packets[2])},{args(packets[3])}")
        elif schedule == "reduce-first":
            out.append("\tQ24_LAZY_QUAD_REDUCE "
                       + ",".join(args(packet) for packet in packets))
            for packet in packets:
                out.append(f"\tQ24_ENCODE_CANONICAL_REG_PACKET {args(packet)}")
        elif schedule == "pipeline":
            out.append("\tQ24_LAZY_QUAD_PIPELINE "
                       + ",".join(args(packet) for packet in packets))
        else:
            raise AssertionError(schedule)
    out.append(".endm")
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path("generated/tile4_q24_codec.inc"))
    parser.add_argument("--asm-output", type=Path,
                        default=Path("generated/tile4_q24_lazy_schedules.inc"))
    parser.add_argument("--json-output", type=Path,
                        default=Path("generated/tile4_q24_lazy_schedules.json"))
    args_ns = parser.parse_args()

    groups = parse_groups(args_ns.source)
    tf1_body, tf1_removed = emit_tf1_body(
        "Q24_ENCODE_SOA_L1_TF1_BODY", groups)
    if tf1_removed != 25:
        raise RuntimeError(f"unexpected TF1 removal count: {tf1_removed}")
    output = [
        "/* Generated from the frozen Q24 SoA packet route. */",
        *emit_body("Q24_ENCODE_SOA_L1_BODY", groups, "pair"),
        "",
        *emit_serial_tf1_body("Q24_ENCODE_SOA_TF1_BODY", groups),
        "",
        *tf1_body,
        "",
        *emit_body("Q24_ENCODE_SOA_L2_BODY", groups, "reduce-first"),
        "",
        *emit_body("Q24_ENCODE_SOA_L3_BODY", groups, "pipeline"),
        "",
    ]
    args_ns.asm_output.parent.mkdir(parents=True, exist_ok=True)
    args_ns.asm_output.write_text("\n".join(output))
    metadata = {
        "schema": "ntruplus768-gt32-q24-lazy-schedules-v1",
        "source": str(args_ns.source),
        "groups": len(groups),
        "packets": sum(len(group[1]) for group in groups),
        "variants": {
            "L0": "serial packet reduce-pack-store control",
            "L1": "two-packet operation-class interleave",
            "L1_TF1": "L1 with final qword orientation absorbed",
            "L2": "four-packet reduce-first then serial pack",
            "L3": "four-packet operation-class software pipeline",
        },
        "frozen": ["reducer", "mapping", "packet stores", "range", "scale"],
        "matched_code_cage_bytes": 5120,
        "tf1": {
            "removed_vpermq_per_pack": tf1_removed,
            "expected_removed": 25,
            "remaining_vpermq_per_pack": 48 - tf1_removed,
        },
    }
    args_ns.json_output.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"generated {args_ns.asm_output} and {args_ns.json_output}")


if __name__ == "__main__":
    main()
