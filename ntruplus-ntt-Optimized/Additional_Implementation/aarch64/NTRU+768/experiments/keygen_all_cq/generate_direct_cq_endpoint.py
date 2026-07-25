#!/usr/bin/env python3
"""Generate a direct-CQ endpoint from the audited direct-BPQ candidate.

The direct-BPQ candidate already freezes the production arithmetic, reduction,
register allocation, and exact 96-output semantic map.  This generator replaces
its fixed BPQ stores with proof-backed parking moves and an in-register 4x8
transpose for each CQ group.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_to_bpq_endpoint.S"
BPQ_MAP = HERE / "direct_bpq_endpoint_map.json"
FEASIBILITY = HERE / "direct_cq_endpoint_feasibility.json"
OUTPUT = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_to_cq_endpoint.S"
OUTPUT_MAP = HERE / "direct_cq_endpoint_map.json"

OLD_SYMBOL = "gt_experiment_poly_ntt_to_bpq"
SYMBOL = "gt_experiment_poly_ntt_to_cq"

STORE_RE = re.compile(
    r"^(\s*)str\s+q(\d+),\s*\[x19,\s*#(\d+)\]\s*"
    r"// direct BPQ row(\d+) block(\d+) output(\d+) slot(\d+)\s*$"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def qnum(name: str) -> int:
    if not re.fullmatch(r"q(?:[12]?\d|3[01]|[0-9])", name):
        raise ValueError(f"invalid vector register {name}")
    return int(name[1:])


def transpose_lines(group: dict[str, object], indent: str) -> list[str]:
    group_id = int(group["cq_group"])
    inputs = [qnum(name) for name in group["cq_input_regs_slot_order"]]
    temps = [qnum(name) for name in group["selected_transpose_temps"]]
    destructive = [
        qnum(name) if name is not None else -1
        for name in group["destructive_trn2_inputs"]
    ]
    if len(inputs) != 4 or len(temps) != 4 or len(destructive) != 2:
        raise ValueError(f"CQ group {group_id}: invalid transpose allocation")
    if any(reg <= 0 or reg >= 32 for reg in inputs + temps + destructive):
        raise ValueError(f"CQ group {group_id}: q0/out-of-range register used")
    if len(set(inputs)) != 4 or len(set(temps)) != 4:
        raise ValueError(f"CQ group {group_id}: aliased input/temp allocation")
    if set(inputs) & set(temps):
        raise ValueError(f"CQ group {group_id}: temp aliases input")
    if destructive[0] not in inputs[:2] or destructive[1] not in inputs[2:]:
        raise ValueError(f"CQ group {group_id}: invalid destructive input")

    a, b, c, d = inputs
    even01, even23, c0, c1 = temps
    odd01, odd23 = destructive
    base = 64 * group_id
    return [
        f"{indent}trn1 v{even01}.8h, v{a}.8h, v{b}.8h",
        f"{indent}trn2 v{odd01}.8h, v{a}.8h, v{b}.8h",
        f"{indent}trn1 v{even23}.8h, v{c}.8h, v{d}.8h",
        f"{indent}trn2 v{odd23}.8h, v{c}.8h, v{d}.8h",
        f"{indent}trn1 v{c0}.4s, v{even01}.4s, v{even23}.4s",
        f"{indent}trn2 v{even01}.4s, v{even01}.4s, v{even23}.4s",
        f"{indent}trn1 v{c1}.4s, v{odd01}.4s, v{odd23}.4s",
        f"{indent}trn2 v{odd01}.4s, v{odd01}.4s, v{odd23}.4s",
        f"{indent}str q{c0}, [x19, #{base}]"
        f"  // direct CQ group{group_id} c0",
        f"{indent}str q{c1}, [x19, #{base + 16}]"
        f"  // direct CQ group{group_id} c1",
        f"{indent}str q{even01}, [x19, #{base + 32}]"
        f"  // direct CQ group{group_id} c2",
        f"{indent}str q{odd01}, [x19, #{base + 48}]"
        f"  // direct CQ group{group_id} c3",
    ]


def main() -> None:
    source_text = SOURCE.read_text()
    source_hash = sha256(SOURCE)
    bpq_map = json.loads(BPQ_MAP.read_text())
    if source_hash != bpq_map["output_sha256"]:
        raise ValueError("direct-BPQ source no longer matches its audited map")

    feasibility = json.loads(FEASIBILITY.read_text())
    if not feasibility["feasible_no_spill"] or feasibility["failed_groups"]:
        raise ValueError("direct-CQ feasibility gate has not passed")
    groups = {
        int(group["cq_group"]): group for group in feasibility["groups"]
    }
    if sorted(groups) != list(range(24)):
        raise ValueError("direct-CQ feasibility map must contain groups 0..23")

    sites_by_slot = {int(site["bpq_slot"]): site for site in bpq_map["sites"]}
    completion_slots = {
        group_id: max(
            range(4 * group_id, 4 * group_id + 4),
            key=lambda slot: int(sites_by_slot[slot]["source_line"]),
        )
        for group_id in range(24)
    }
    feasibility_sites = {
        int(site["bpq_slot"]): site
        for group in groups.values()
        for site in group["sites_execution_order"]
    }

    output_lines: list[str] = []
    matched_slots: set[int] = set()
    parking_moves = 0
    cq_stores = 0
    transpose_instructions = 0
    for line in source_text.splitlines():
        match = STORE_RE.match(line)
        if match is None:
            output_lines.append(line)
            continue
        indent, source_reg_s, offset_s, row_s, block_s, output_s, slot_s = (
            match.groups()
        )
        source_reg = int(source_reg_s)
        offset = int(offset_s)
        row = int(row_s)
        block = int(block_s)
        output_index = int(output_s)
        slot = int(slot_s)
        site = sites_by_slot.get(slot)
        if site is None:
            raise ValueError(f"unexpected direct-BPQ slot {slot}")
        if (
            source_reg != qnum(str(site["source_vector"]))
            or offset != int(site["store_offset_bytes"])
            or row != int(site["row"])
            or block != int(site["block"])
            or output_index != int(site["output_index"])
        ):
            raise ValueError(f"direct-BPQ store contract changed at slot {slot}")
        matched_slots.add(slot)

        feasibility_site = feasibility_sites[slot]
        park_name = feasibility_site["parking_register"]
        if park_name is not None:
            park = qnum(str(park_name))
            output_lines.append(
                f"{indent}mov v{park}.16b, v{source_reg}.16b"
                f"  // direct CQ park slot{slot}"
            )
            parking_moves += 1

        group_id = slot // 4
        if slot == completion_slots[group_id]:
            generated = transpose_lines(groups[group_id], indent)
            output_lines.extend(generated)
            transpose_instructions += 8
            cq_stores += 4
        elif park_name is None:
            output_lines.append(
                f"{indent}// direct CQ retain q{source_reg} for group{group_id}"
            )

    if matched_slots != set(range(96)):
        raise ValueError(
            f"expected direct-BPQ slots 0..95, got {sorted(matched_slots)}"
        )
    if parking_moves != int(feasibility["total_parking_moves"]):
        raise ValueError("parking move count does not match feasibility contract")
    if transpose_instructions != 24 * 8 or cq_stores != 24 * 4:
        raise ValueError("direct-CQ transpose/store count mismatch")

    output_text = "\n".join(output_lines) + "\n"
    if output_text.count(OLD_SYMBOL) < 3:
        raise ValueError("direct-BPQ symbol contract changed")
    output_text = output_text.replace(OLD_SYMBOL, SYMBOL)
    old_banner = (
        "/* Experiment-only direct-BPQ endpoint generated from production. */\n"
        f"/* source_sha256={bpq_map['source_sha256']} */\n"
        "/* Arithmetic/reduction/register allocation are unchanged. */\n"
    )
    new_banner = (
        "/* Experiment-only direct-CQ endpoint generated from direct-BPQ. */\n"
        f"/* direct_bpq_sha256={source_hash} */\n"
        "/* Arithmetic/reduction/register allocation are unchanged. */\n"
    )
    if output_text.count(old_banner) != 1:
        raise ValueError("direct-BPQ generated banner changed")
    output_text = output_text.replace(old_banner, new_banner)
    OUTPUT.write_text(output_text)

    result = {
        "candidate": SYMBOL,
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_hash,
        "bpq_map_sha256": sha256(BPQ_MAP),
        "feasibility_sha256": sha256(FEASIBILITY),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": sha256_bytes(output_text.encode()),
        "contract": "complete Stage345 Q -> in-register transpose -> CQ",
        "groups": 24,
        "parking_moves": parking_moves,
        "transpose_instructions": transpose_instructions,
        "cq_stores": cq_stores,
        "spills": 0,
        "raw_q_reloads": 0,
        "recomputation": 0,
        "arithmetic_changed": False,
        "reduction_changed": False,
        "production_default_changed": False,
    }
    OUTPUT_MAP.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"generated {OUTPUT.relative_to(ROOT)}: groups=24 "
        f"parks={parking_moves} trn={transpose_instructions} stores={cq_stores}"
    )


if __name__ == "__main__":
    main()
