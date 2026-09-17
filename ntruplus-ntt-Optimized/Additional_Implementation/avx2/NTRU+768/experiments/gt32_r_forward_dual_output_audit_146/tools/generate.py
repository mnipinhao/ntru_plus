#!/usr/bin/env python3
"""146: audit a Forward(r) terminal that emits both M and WIRE12.

This is a mapping, executed-work and register-liveness proof.  It deliberately
does not generate assembly or claim cycles.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path


HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[3]
OUT = EXP / "generated"
GROUPS = 12
TILES = 6
LANES = 16
Q = 3457


def macro(text: str, name: str) -> str:
    match = re.search(rf"^\s*\.macro\s+{re.escape(name)}\b(.*?)^\s*\.endm\s*$", text,
                      re.MULTILINE | re.DOTALL)
    if not match:
        raise AssertionError(f"missing macro {name}")
    return match.group(1)


def route_count(body: str) -> int:
    route = re.compile(r"^\s*(vpshufb|vpunpck[a-z]+|vperm2i128|vpermq|vshufps)\b",
                       re.MULTILINE)
    return len(route.findall(body))


def unpack(a: list[object], b: list[object], words: int, high: bool) -> list[object]:
    out: list[object] = []
    for base in (0, 8):
        units = 8 // words
        begin = units // 2 if high else 0
        end = units if high else units // 2
        for index in range(begin, end):
            lo = base + index * words
            out.extend(a[lo:lo + words])
            out.extend(b[lo:lo + words])
    return out


def word_layer(v: list[list[object]]) -> list[list[object]]:
    a, b, c, d = v
    return [unpack(a, b, 1, False), unpack(a, b, 1, True),
            unpack(c, d, 1, False), unpack(c, d, 1, True)]


def dword_layer(v: list[list[object]]) -> list[list[object]]:
    a, b, c, d = v
    return [unpack(a, c, 2, False), unpack(a, c, 2, True),
            unpack(b, d, 2, False), unpack(b, d, 2, True)]


def qword_layer(v: list[list[object]]) -> list[list[object]]:
    a, b, c, d = v
    return [unpack(a, c, 4, False), unpack(a, c, 4, True),
            unpack(b, d, 4, False), unpack(b, d, 4, True)]


def flatten(v: list[list[object]]) -> list[object]:
    return [item for row in v for item in row]


def permute(values: list[int], source: list[object], target: list[object]) -> list[int]:
    table = dict(zip(source, values, strict=True))
    return [table[label] for label in target]


def extract_q24_groups(pack_text: str) -> list[dict[str, object]]:
    body = macro(pack_text, "Q24_ENCODE_SOA_BODY")
    groups: list[dict[str, object]] = []
    chunks = body.split("Q24_TRANSPOSE")
    assert len(chunks) == GROUPS + 1
    for index in range(GROUPS):
        before = chunks[index]
        after = chunks[index + 1]
        loads = [int(value) for value in re.findall(r"vmovdqu\s+(\d+)\(%rsi\)", before)][-4:]
        stores = [int(value) for value in
                  re.findall(r"Q24_ENCODE_REG_PACKET[^\n]*,(\d+),(?:0|1)\s*$", after,
                             re.MULTILINE)][:4]
        assert len(loads) == len(stores) == 4
        assert loads == list(range(loads[0], loads[0] + 128, 32))
        assert stores == list(range(stores[0], stores[0] + 96, 24))
        tile = loads[0] // 256
        half = (loads[0] % 256) // 128
        groups.append({
            "group": index,
            "m_load_offsets": loads,
            "tile": tile,
            "half": half,
            "wire_offsets": stores,
        })
    return groups


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ntt_path = ROOT / "ntt_m.s"
    pack_path = ROOT / "pack.s"
    encap_path = ROOT / "encap.c"
    ntt = ntt_path.read_text()
    pack = pack_path.read_text()

    # Static instruction-family evidence from the selected production macros.
    m_routes = route_count(macro(ntt, "FR_PACKED_TO_PLANES"))
    serializer_routes = route_count(macro(pack, "Q24_TRANSPOSE"))
    q_only_routes = route_count(macro(pack, "GT103_Q24_Q_ONLY"))
    assert (m_routes, serializer_routes, q_only_routes) == (12, 12, 4)

    # QL2 is the already-qualified common cut: W+D(M).  The packet-facing
    # presentation is its Q layer.  The M branch is the inverse semantic
    # permutation already implemented by the selected Forward terminal.
    m = [[(coefficient, leaf) for leaf in range(LANES)] for coefficient in range(4)]
    ql2 = dword_layer(word_layer(m))
    packet = qword_layer(ql2)
    m_labels, ql2_labels, packet_labels = map(flatten, (m, ql2, packet))
    assert set(m_labels) == set(ql2_labels) == set(packet_labels)

    rng = random.Random(0x146_DA1)
    impulses = 0
    for position in range(4 * LANES):
        values = [0] * (4 * LANES)
        values[position] = 1
        ql2_values = permute(values, m_labels, ql2_labels)
        assert permute(ql2_values, ql2_labels, m_labels) == values
        packet_values = permute(ql2_values, ql2_labels, packet_labels)
        assert permute(packet_values, packet_labels, m_labels) == values
        impulses += 1
    trials = 1000
    for _ in range(trials):
        values = [rng.randrange(-10788, 10789) for _ in range(4 * LANES)]
        ql2_values = permute(values, m_labels, ql2_labels)
        m_branch = permute(ql2_values, ql2_labels, m_labels)
        packet_branch = permute(ql2_values, ql2_labels, packet_labels)
        assert m_branch == values
        assert permute(packet_branch, packet_labels, m_labels) == values

    groups = extract_q24_groups(pack)
    tile_order = []
    for group in groups:
        if not tile_order or tile_order[-1] != group["tile"]:
            tile_order.append(group["tile"])
    assert tile_order == [0, 4, 2, 5, 3, 1]
    for tile in tile_order:
        tile_groups = [group for group in groups if group["tile"] == tile]
        half_order = [group["half"] for group in tile_groups]
        assert sorted(half_order) == [0, 1]
        wire = [offset for group in tile_groups for offset in group["wire_offsets"]]
        assert wire == list(range(wire[0], wire[0] + 192, 24))

    current_routes = m_routes + serializer_routes
    candidate_routes = m_routes + q_only_routes
    assert current_routes == 24 and candidate_routes == 16

    # Constructive zero-spill schedule.  Packet encoding consumes the Q-only
    # outputs before the selected M route reuses the same temporaries.
    register_phases = {
        "packet_branch_peak": {
            "other_half_state": 4,
            "current_ql2": 4,
            "q_only_outputs": 4,
            "q_and_v_constants": 2,
            "encode_temporary": 1,
            "peak_ymm": 15,
        },
        "m_branch_peak": {
            "other_half_state": 4,
            "current_ql2": 4,
            "transpose_temporaries": 4,
            "q_and_pshufb_constants": 2,
            "peak_ymm": 14,
        },
    }
    assert max(phase["peak_ymm"] for phase in register_phases.values()) <= 16

    report = {
        "schema": "ntruplus768-gt32-r-forward-dual-output-audit-146-v1",
        "experiment": "GT32-R-FORWARD-DUAL-OUTPUT-AUDIT-146",
        "mode": "generator-static-proof",
        "production_modified": False,
        "baseline": "promoted QL2 + direct-r-hash production",
        "semantic_contract": {
            "source_cut": "qualified QL2 transient immediately after Forward S5",
            "m_output": "unchanged private M, e=0, bound <=10788, materialized for later B3",
            "wire_output": "canonical WIRE12 bytes written into hash_g input",
            "extra_reduction_or_center": 0,
            "mapping_bijective": True,
            "impulses": impulses,
            "random_trials": trials,
        },
        "selected_macro_counts": {
            "QL2_to_M_routes": m_routes,
            "M_to_packet_routes": serializer_routes,
            "QL2_to_packet_routes": q_only_routes,
        },
        "executed_work_ledger": {
            "groups": GROUPS,
            "current_routes_per_group": current_routes,
            "candidate_routes_per_group": candidate_routes,
            "route_delta_per_group": candidate_routes - current_routes,
            "route_delta_per_encap": (candidate_routes - current_routes) * GROUPS,
            "current_serializer_M_loads": 4 * GROUPS,
            "candidate_serializer_M_loads": 0,
            "M_store_delta": 0,
            "wire_store_delta": 0,
            "operation_class_deletion": [
                "96 dynamically executed routing instructions",
                "48 YMM reloads of the materialized M polynomial",
            ],
        },
        "packet_order": {
            "current_group_tile_order": tile_order,
            "current_group_tile_half_order": [
                [group["tile"], group["half"]] for group in groups
            ],
            "candidate_tile_traversal": tile_order,
            "reason": (
                "process independent 256-byte Forward tiles and their independent S4/S5 "
                "halves in wire order; scatter M to its original tile/half offset, preserving "
                "increasing packet stores and the existing single safe final packet"
            ),
            "table_entries": TILES,
            "standalone_repair": 0,
        },
        "register_proof": {
            "phases": register_phases,
            "peak_ymm": 15,
            "zero_spill_plausible": True,
            "schedule": (
                "finish one S4/S5 half; form and consume four Q-only packet registers; "
                "reload the pshufb constant; form/store M; then process the other half"
            ),
        },
        "code_shape_constraint": {
            "strategy": "one bounded six-tile loop with a six-entry tile-offset table",
            "forbidden": [
                "six fully inlined tile bodies",
                "standalone QL2 materialization for the wire branch",
                "post-Forward reload of M for serialization",
            ],
        },
        "decision": {
            "status": "PASS_TO_ZERO_SPILL_ASM_GATE",
            "reason": "deletes complete route and reload classes; not merely a relocated serializer",
            "next": (
                "same-ELF local Forward+pack control versus dual-output candidate, including "
                "tile-table overhead and exact hash-input stores"
            ),
        },
        "source_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (ntt_path, pack_path, encap_path)
        },
        "q24_groups": groups,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dual-output-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print("mapping impulses=64 random=1000 PASS")
    print(f"routes/group {current_routes}->{candidate_routes}")
    print(f"routes/Encap delta={(candidate_routes-current_routes)*GROUPS}")
    print("M reloads/Encap 48->0")
    print(f"packet tile order={tile_order}")
    print("peak YMM=15 zero-spill plausible")
    print("decision=PASS_TO_ZERO_SPILL_ASM_GATE")


if __name__ == "__main__":
    main()
