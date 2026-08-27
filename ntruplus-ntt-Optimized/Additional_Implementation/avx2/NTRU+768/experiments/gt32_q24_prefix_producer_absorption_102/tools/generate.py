#!/usr/bin/env python3
"""Compose Forward/B3 output formation with the E0V Q24 prefix."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[3]
OUT = EXP / "generated"
GROUPS = 12


def read(name: str) -> str:
    return (ROOT / name).read_text()


def digest(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def macro(source: str, name: str) -> str:
    match = re.search(
        rf"^\s*\.macro\s+{re.escape(name)}\b[^\n]*\n(?P<body>.*?)^\s*\.endm\s*$",
        source, re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise RuntimeError(f"missing source macro: {name}")
    return match.group("body")


def insns(body: str) -> list[str]:
    return [line.strip() for line in body.splitlines()
            if line.strip() and not line.lstrip().startswith(".")]


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


def pshuf_plane(v: list[str]) -> list[str]:
    order = [0, 4, 1, 5, 2, 6, 3, 7, 8, 12, 9, 13, 10, 14, 11, 15]
    return [v[i] for i in order]


def terminal_to_m(v: list[list[str]]) -> list[list[str]]:
    a, b, c, d = [pshuf_plane(x) for x in v]
    d0, d1 = unpack(a, c, 2, False), unpack(a, c, 2, True)
    d2, d3 = unpack(b, d, 2, False), unpack(b, d, 2, True)
    return [unpack(d0, d2, 4, False), unpack(d0, d2, 4, True),
            unpack(d1, d3, 4, False), unpack(d1, d3, 4, True)]


def word_layer(v: list[list[str]]) -> list[list[str]]:
    a, b, c, d = v
    return [unpack(a, b, 1, False), unpack(a, b, 1, True),
            unpack(c, d, 1, False), unpack(c, d, 1, True)]


def dword_layer(v: list[list[str]]) -> list[list[str]]:
    a, b, c, d = v
    return [unpack(a, c, 2, False), unpack(a, c, 2, True),
            unpack(b, d, 2, False), unpack(b, d, 2, True)]


def qword_layer(v: list[list[str]]) -> list[list[str]]:
    a, b, c, d = v
    return [unpack(a, c, 4, False), unpack(a, c, 4, True),
            unpack(b, d, 4, False), unpack(b, d, 4, True)]


def shufps_even_odd(a: list[str], b: list[str], odd: bool) -> list[str]:
    # vshufps $0x88/$0xdd: select even/odd 32-bit words from each source,
    # independently in both 128-bit halves.
    out: list[str] = []
    pick = (1, 3) if odd else (0, 2)
    for base in (0, 8):
        for src in (a, b):
            for dword in pick:
                lo = base + 2 * dword
                out.extend(src[lo:lo + 2])
    return out


def source_audit() -> dict:
    ntt, b3, pack, encap = map(read, ("ntt_m.s", "basemul.s", "pack.s", "encap.c"))
    forward = insns(macro(ntt, "FR_PACKED_TO_PLANES"))
    transpose = insns(macro(pack, "Q24_TRANSPOSE"))
    output = insns(macro(b3, "TILE4_OUTPUT_SOA_LATE_RSQ"))
    sum_body = macro(pack, "Q24_ENCODE_SOA_SUM_BODY")
    if sum(x.startswith(("vpshufb", "vpunpck", "vperm", "vshuf")) for x in forward) != 12:
        raise RuntimeError("Forward T-to-M route count changed")
    if len(transpose) != 12 or [x.split()[0] for x in transpose].count("vpunpcklwd") != 2:
        raise RuntimeError("Q24 W/D/Q shape changed")
    if sum_body.count("Q24_TRANSPOSE") != GROUPS:
        raise RuntimeError("E0V no longer applies twelve full Q24 transposes")
    if not all(f"vmovdqu %ymm{r}, {off}(%rdi)" in output
               for r, off in ((5, 0), (6, 32), (7, 64), (8, 96))):
        raise RuntimeError("B3 final M output registers changed")
    if "ntruplus768_pack_m_sum_highrange12699_avx2" not in encap:
        raise RuntimeError("production Encap is not E0V")
    return {
        "sha256": {name: digest(name) for name in ("ntt_m.s", "basemul.s", "pack.s", "encap.c")},
        "forward_terminal": "post-S5 T in four registers",
        "forward_T_to_M_routes_per_group": 12,
        "B3_final_state": "final e=0 coefficient planes in ymm5..ymm8 before four M stores",
        "B3_output_routes_to_M_per_group": 0,
        "E0V_Q24_prefix": ["W:4", "D:4", "Q:4"],
        "E0V_full_routes_per_group": 12,
        "groups": GROUPS,
    }


def main() -> None:
    audit = source_audit()
    terminal = [[f"t{r}.w{i}" for i in range(16)] for r in range(4)]
    m = terminal_to_m(terminal)
    ql1 = word_layer(m)
    ql2 = dword_layer(ql1)
    packet = qword_layer(ql2)

    # Exact producer-side compositions.
    ql1_direct = [shufps_even_odd(terminal[0], terminal[2], False),
                  shufps_even_odd(terminal[1], terminal[3], False),
                  shufps_even_odd(terminal[0], terminal[2], True),
                  shufps_even_odd(terminal[1], terminal[3], True)]
    if ql1_direct != ql1:
        raise RuntimeError("four-vshufps T-to-QL1 identity failed")
    ql2_direct = [terminal[0], terminal[2], terminal[1], terminal[3]]
    if ql2_direct != ql2:
        raise RuntimeError("zero-route T-to-QL2 identity failed")
    packet_direct = [unpack(terminal[0], terminal[1], 4, False),
                     unpack(terminal[0], terminal[1], 4, True),
                     unpack(terminal[2], terminal[3], 4, False),
                     unpack(terminal[2], terminal[3], 4, True)]
    if packet_direct != packet:
        raise RuntimeError("four-qword-unpack T-to-P identity failed")

    # Costs are exact executed two-source/lane-route instructions per group.
    layouts = [
        ("M", 12, 0, 12, "production control"),
        ("QL1", 4, 4, 8, "T->QL1 is four vshufps; B3 adds W"),
        ("QL2", 0, 8, 4, "T->QL2 is register/store ownership only; B3 adds W+D"),
        ("P", 4, 12, 0, "T->P is four qword unpacks; B3 adds W+D+Q"),
    ]
    control = 24
    candidates = []
    for name, forward, b3, suffix, reason in layouts:
        total = forward + b3 + suffix
        delta = (total - control) * GROUPS
        candidates.append({
            "layout": name,
            "forward_output_routes_per_group": forward,
            "b3_output_routes_per_group": b3,
            "q24_suffix_routes_per_group": suffix,
            "total_routes_per_group": total,
            "total_routes_per_encap": total * GROUPS,
            "delta_routes_per_encap": delta,
            "loads_delta": 0,
            "stores_delta": 0,
            "materialized_bytes_delta": 0,
            "spill_required": False,
            "reason": reason,
        })

    selected = min(candidates, key=lambda x: x["delta_routes_per_encap"])
    if selected["layout"] != "QL2" or selected["delta_routes_per_encap"] != -144:
        raise RuntimeError("unexpected selected presentation")

    report = {
        "schema": "ntruplus768-q24-prefix-producer-absorption-v1",
        "experiment": "GT32-Q24-PREFIX-PRODUCER-ABSORPTION-102",
        "baseline": "b2a4bea",
        "mode": "generator-only",
        "production_modified": False,
        "naming": {
            "QL1": "after Q24 word-unpack prefix",
            "QL2": "after Q24 word+dword prefix",
            "P": "packet-lane state after Q24 W+D+Q",
            "warning": "QL1/QL2 here are Q24-prefix layouts, not the older Forward-to-B3 transpose-cut names",
        },
        "frozen": [
            "current E0V caller topology", "6592-byte h/r/m/c frame", "Ep and Em materialize separately",
            "e=0 and current bounds", "Good-Thomas and NTT32 arithmetic", "quartic B3 mathematics",
            "Q24 reduction and packet stores", "r/hash path", "Keypair and Decap",
        ],
        "source_audit": audit,
        "mapping_proofs": {
            "T_to_QL1": "four vshufps ($0x88/$0xdd)",
            "T_to_QL2": "zero routes; register/store order [t0,t2,t1,t3]",
            "T_to_P": "four qword unpacks (083 identity)",
            "lane_exact": True,
            "layouts": {"M": m, "QL1": ql1, "QL2": ql2, "P": packet},
        },
        "B3_lower_bound": {
            "premise": "final B3 values are four distinct coefficient-plane registers; stores cannot mix lanes",
            "QL1": "four two-source word unpacks are necessary and sufficient",
            "QL2": "QL1 plus four dword unpacks: eight routes are necessary and sufficient",
            "P": "full W+D+Q network: twelve routes",
            "constructive_peak_YMM": 9,
            "spill_required": False,
        },
        "candidates": candidates,
        "selected": {
            **selected,
            "id": "EPM_QL2_SHARED",
            "operation_class_deletion": "three complete 48-route layers per Encap",
            "producer_contract": {
                "Forward_m": "store post-S5 T as QL2 using register order t0,t2,t1,t3",
                "B3_product": "finalize M planes, apply W+D, store QL2",
                "consumer": "load Ep/Em QL2, lane-wise add, apply only Q, then unchanged reduction/pack",
            },
            "decision": "PASS_TO_EXECUTABLE_103",
        },
        "decision": "PASS_TO_EXECUTABLE_103",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "q24-prefix-search.json").write_text(json.dumps(report, indent=2) + "\n")
    fields = ["layout", "forward_output_routes_per_group", "b3_output_routes_per_group",
              "q24_suffix_routes_per_group", "total_routes_per_group",
              "total_routes_per_encap", "delta_routes_per_encap", "loads_delta",
              "stores_delta", "materialized_bytes_delta", "spill_required", "reason"]
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(candidates)
    (OUT / "candidates.csv").write_text(stream.getvalue())
    print(json.dumps({"source_audit": "PASS", "mapping_proofs": "PASS",
                      "selected": selected["layout"], "route_delta": -144,
                      "next": "PASS_TO_EXECUTABLE_103"}, indent=2))


if __name__ == "__main__":
    main()
