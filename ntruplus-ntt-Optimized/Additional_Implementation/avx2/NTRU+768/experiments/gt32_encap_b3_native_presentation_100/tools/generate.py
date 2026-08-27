#!/usr/bin/env python3
"""Audit and price asymmetric Eh/Er presentation cuts for GT32 Encap."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve()
EXPERIMENT = HERE.parents[1]
ROOT = HERE.parents[3]
OUT = EXPERIMENT / "generated"
GROUPS = 12
VECTORS = 48


def read(name: str) -> str:
    return (ROOT / name).read_text()


def digest(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def macro(source: str, name: str) -> str:
    found = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}\b[^\n]*\n(?P<body>.*?)^\s*\.endm\s*$",
        source,
        re.MULTILINE | re.DOTALL,
    )
    if found is None:
        raise RuntimeError(f"missing source macro: {name}")
    return found.group("body")


def instructions(body: str) -> list[str]:
    return [
        line.strip() for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith(".")
    ]


def unpack(a: list[str], b: list[str], words: int, high: bool) -> list[str]:
    out: list[str] = []
    for base in (0, 8):
        units = 8 // words
        begin = units // 2 if high else 0
        end = units if high else units // 2
        for index in range(begin, end):
            lo = base + index * words
            out.extend(a[lo:lo + words])
            out.extend(b[lo:lo + words])
    return out


def pshuf_plane(value: list[str]) -> list[str]:
    order = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]
    return [value[index] for index in order]


def terminal_to_m(values: list[list[str]]) -> list[list[str]]:
    v0, v1, v2, v3 = [pshuf_plane(value) for value in values]
    d0 = unpack(v0, v2, 2, False)
    d1 = unpack(v0, v2, 2, True)
    d2 = unpack(v1, v3, 2, False)
    d3 = unpack(v1, v3, 2, True)
    return [
        unpack(d0, d2, 4, False),
        unpack(d0, d2, 4, True),
        unpack(d1, d3, 4, False),
        unpack(d1, d3, 4, True),
    ]


def m_to_wire_packets(values: list[list[str]]) -> list[list[str]]:
    m0, m1, m2, m3 = values
    w0 = unpack(m0, m1, 1, False)
    w1 = unpack(m0, m1, 1, True)
    w2 = unpack(m2, m3, 1, False)
    w3 = unpack(m2, m3, 1, True)
    d0 = unpack(w0, w2, 2, False)
    d1 = unpack(w0, w2, 2, True)
    d2 = unpack(w1, w3, 2, False)
    d3 = unpack(w1, w3, 2, True)
    return [
        unpack(d0, d2, 4, False),
        unpack(d0, d2, 4, True),
        unpack(d1, d3, 4, False),
        unpack(d1, d3, 4, True),
    ]


def terminal_to_wire_packets(values: list[list[str]]) -> list[list[str]]:
    v0, v1, v2, v3 = values
    return [
        unpack(v0, v1, 4, False),
        unpack(v0, v1, 4, True),
        unpack(v2, v3, 4, False),
        unpack(v2, v3, 4, True),
    ]


def source_audit() -> dict:
    ntt = read("ntt_m.s")
    b3 = read("basemul.s")
    pack = read("pack.s")
    encap = read("encap.c")

    plane = instructions(macro(ntt, "FR_PACKED_TO_PLANES"))
    b3a = instructions(macro(b3, "TILE4_INPUT_A_SOA"))
    b3b = instructions(macro(b3, "TILE4_INPUT_B_SOA"))
    transpose = instructions(macro(pack, "Q24_TRANSPOSE"))
    decode = macro(pack, "Q24_DECODE_SOA_BODY")

    if len(plane) != 16 or len(transpose) != 12:
        raise RuntimeError("production routing macro shape changed")
    if len(b3a) != 4 or len(b3b) != 4:
        raise RuntimeError("production B3 M-input macro shape changed")
    if any(not line.startswith("vmovdqu") for line in b3a + b3b):
        raise RuntimeError("production B3 M input is no longer load-only")
    if decode.count("Q24_TRANSPOSE") != GROUPS:
        raise RuntimeError("production Decode(h) no longer has twelve M transposes")
    required = [
        r"ntruplus768_pack_m_lazy10788_avx2\(ct, scratch\.r\)",
        r"ntruplus768_basemul_general_m_avx2\(scratch\.c, scratch\.h, scratch\.r\)",
        r"ntruplus768_pack_m_sum_highrange12699_avx2",
    ]
    if any(re.search(pattern, encap) is None for pattern in required):
        raise RuntimeError("production b2 Encap graph changed")

    return {
        "source_sha256": {name: digest(name) for name in ("ntt_m.s", "basemul.s", "pack.s", "encap.c")},
        "FR_PACKED_TO_PLANES": {
            "instructions_per_group_including_stores": len(plane),
            "routing_per_group": 12,
            "stores_per_group": 4,
        },
        "Q24_TRANSPOSE": {"routing_per_group": len(transpose)},
        "B3_M_input": {
            "loads_per_operand_per_group": 4,
            "routing_per_operand_per_group": 0,
        },
        "Decode_h_to_M": {"groups": GROUPS, "routing_per_group": 12},
    }


def main() -> None:
    audit = source_audit()
    terminal = [[f"t{reg}.w{lane}" for lane in range(16)] for reg in range(4)]
    via_m = m_to_wire_packets(terminal_to_m(terminal))
    direct = terminal_to_wire_packets(terminal)
    if via_m != direct:
        raise RuntimeError("terminal-to-WIRE12 composition identity failed")

    candidates = [
        {
            "id": "C0_EhM_ErM",
            "Eh": "M", "Er": "M", "status": "PRODUCTION_CONTROL",
            "forward_r_routes": 144, "wire_r_routes": 144,
            "b3_h_routes": 0, "b3_r_routes": 0,
            "reason": "current coefficient-plane producers and load-only B3 inputs",
        },
        {
            "id": "H_PACKET_EhT_ErM",
            "Eh": "decoded packet", "Er": "M", "status": "NO_DELETION",
            "forward_r_routes": 144, "wire_r_routes": 144,
            "b3_h_routes": 144, "b3_r_routes": 0,
            "decode_h_saved_routes": 144,
            "reason": "moves the same 4x16 transpose from Decode(h) to B3",
        },
        {
            "id": "R_TERMINAL_EhM_ErT",
            "Eh": "M", "Er": "post-S5 terminal T", "status": "PASS_TO_EXECUTABLE_101",
            "forward_r_routes": 0, "wire_r_routes": 48,
            "b3_h_routes": 0, "b3_r_routes": 144,
            "reason": "persistent boundary preserves scheduling and deletes the composite T->M->WIRE routing overlap",
        },
    ]
    control = sum(candidates[0].get(key, 0) for key in
                  ("forward_r_routes", "wire_r_routes", "b3_h_routes", "b3_r_routes"))
    for item in candidates:
        total = sum(item.get(key, 0) for key in
                    ("forward_r_routes", "wire_r_routes", "b3_h_routes", "b3_r_routes"))
        # Decode(h) packet form saves exactly what B3 later repays.
        total -= item.get("decode_h_saved_routes", 0)
        item["net_route_total_vs_current_decode_baseline"] = total
        item["delta_routes_vs_control"] = total - control
        item["loads_delta"] = 0
        item["stores_delta"] = 0
        item["materialized_bytes_delta"] = 0

    report = {
        "schema": "ntruplus768-encap-b3-native-presentation-v1",
        "experiment": "GT32-ENCAP-B3-NATIVE-PRESENTATION-100",
        "baseline": "b2a4bea",
        "mode": "generator-only",
        "production_modified": False,
        "frozen": [
            "current caller topology", "E0V two-source Q24", "6592-byte frame",
            "e=0", "Good-Thomas and NTT32 arithmetic", "quartic B3 mathematics",
            "B3 output M", "Keypair and Decap executable geometry",
        ],
        "source_audit": audit,
        "mapping_proof": {
            "identity": "Q24_TRANSPOSE(FR_PACKED_TO_PLANES(T)) == four qword unpacks(T)",
            "symbolic_words": 64,
            "proof": "PASS",
            "direct_packet_lanes": direct,
        },
        "partial_cut_audit": {
            "cuts": [
                "F1: after the per-register vpshufb layer",
                "F2: after the dword-unpack layer",
            ],
            "producer_to_B3": "each omitted Forward routing layer must be completed before the unchanged load-only B3 arithmetic; this moves work but does not delete it",
            "serializer": "only the raw T cut has an existing exact four-route/group WIRE12 proof (083); no partial cut has a stronger proven operation-class deletion",
            "decision": "do not emit a second candidate until a partial-cut serializer synthesis proves more than the selected 96-route deletion",
        },
        "candidates": candidates,
        "selected": {
            "id": "R_TERMINAL_EhM_ErT",
            "Eh": "M",
            "Er": "post-S5 terminal T",
            "operation_class_deletion": "96 executed vector routing instructions per Encap",
            "entrypoints_for_101": ["ntt_r_T", "pack_r_T", "B3_M_T"],
            "conversion_schedule": {
                "peak_YMM_before_B3_arithmetic": 15,
                "existing_B3_arithmetic_peak_YMM": 16,
                "spills_required": 0,
                "note": "T routing temporaries and mask die before loading/entering the existing arithmetic body",
            },
            "why_083_does_not_close_it": "083 coupled Q24 immediately to each live Forward tile; persistent T restores separate producer, serializer and B3 scheduling windows",
            "decision": "PASS_TO_EXECUTABLE_101",
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "presentation-search.json").write_text(json.dumps(report, indent=2) + "\n")

    fields = ["id", "Eh", "Er", "status", "net_route_total_vs_current_decode_baseline",
              "delta_routes_vs_control", "loads_delta", "stores_delta",
              "materialized_bytes_delta", "reason"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    for item in candidates:
        writer.writerow({key: item.get(key, "") for key in fields})
    (OUT / "candidates.csv").write_text(stream.getvalue())

    print(json.dumps({
        "source_contract_audit": "PASS",
        "mapping_proof": "PASS",
        "selected": report["selected"]["id"],
        "route_delta": -96,
        "next": report["selected"]["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
