#!/usr/bin/env python3
"""Prove whether Stage345 outputs can be handed directly to CQ stores.

This analyzer treats the active production forward NTT as the source of truth.
It groups the audited direct-BPQ output sites in four-Q BPQ groups, finds output
registers that are overwritten before each group is complete, allocates safe
parking registers, and checks an exact in-place 4x8 transpose contract.

The first gate is intentionally conservative: no arithmetic/reduction change,
no spill/reload, no recomputation, and no destructive reuse of live inputs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "asm/gt/ntt/poly_ntt.n1.opt.S"
BPQ_MAP = HERE / "direct_bpq_endpoint_map.json"
OUTPUT_JSON = HERE / "direct_cq_endpoint_feasibility.json"
OUTPUT_MD = HERE / "direct_cq_endpoint_feasibility.md"

# All scalar/vector aliases name the same physical Neon register.  In
# particular, Stage345 semantic output sites use `str dN` while arithmetic
# uses `vN`; liveness must unify them.
VECTOR_RE = re.compile(r"\b[qvdsbh](\d+)\b", re.IGNORECASE)
MNEMONIC_RE = re.compile(r"^\s*([a-zA-Z][a-zA-Z0-9.]*)\b")

STORE_MNEMONICS = {"str", "stp", "st1", "st2", "st3", "st4"}
LOAD_MNEMONICS = {"ldr", "ldp", "ld1", "ld2", "ld3", "ld4"}
DESTRUCTIVE_MNEMONICS = {
    "mla", "mls", "smlal", "smlal2", "smlsl", "smlsl2",
    "ins", "bif", "bit", "bsl",
}
FIRST_DEST_MNEMONICS = {
    "add", "sub", "mul", "neg", "mov", "movi", "dup", "ext",
    "trn1", "trn2", "zip1", "zip2", "uzp1", "uzp2", "rev64",
    "sqrdmulh", "sqdmulh", "srshr", "sshr", "shl", "ushr", "and",
    "orr", "eor", "bic", "cmeq", "cmgt", "cmge", "xtn", "xtn2",
    "sqxtn", "sqxtn2", "sqxtun", "sqxtun2", "sxtl", "sxtl2",
}


@dataclass(frozen=True)
class Access:
    defs: frozenset[int]
    uses: frozenset[int]


def code_part(line: str) -> str:
    return line.split("//", 1)[0].strip()


def vector_regs(text: str) -> list[int]:
    return [int(value) for value in VECTOR_RE.findall(text)]


def access_for_line(
    line: str, line_number: int, semantic_output_lines: set[int]
) -> Access:
    code = code_part(line)
    if not code or code.endswith(":") or code.startswith("."):
        return Access(frozenset(), frozenset())
    match = MNEMONIC_RE.match(code)
    if match is None:
        return Access(frozenset(), frozenset())
    mnemonic = match.group(1).lower()
    regs = vector_regs(code)
    if not regs:
        return Access(frozenset(), frozenset())

    if mnemonic in STORE_MNEMONICS:
        # The 96 audited low-D stores are semantic consumption sites even
        # though direct-CQ replaces the physical store.  Keeping those uses in
        # liveness protects values that finish early for the following CQ
        # group.  All other vector stores are removed high-half machinery.
        if line_number in semantic_output_lines:
            return Access(frozenset(), frozenset(regs))
        return Access(frozenset(), frozenset())
    if mnemonic == "umov":
        # S2 umov sites only feed removed high-half stores.
        return Access(frozenset(), frozenset())
    if mnemonic in LOAD_MNEMONICS:
        # Address operands are GPRs, so every vector operand is a destination.
        return Access(frozenset(regs), frozenset())
    if mnemonic in DESTRUCTIVE_MNEMONICS:
        return Access(frozenset({regs[0]}), frozenset(regs))
    if mnemonic in FIRST_DEST_MNEMONICS:
        return Access(frozenset({regs[0]}), frozenset(regs[1:]))

    raise ValueError(
        f"unclassified vector instruction at {SOURCE}:{line_number}: {code}"
    )


def first_future_access(
    accesses: list[Access], start_line: int, reg: int
) -> tuple[int | None, str]:
    for line_number in range(start_line + 1, len(accesses) + 1):
        access = accesses[line_number - 1]
        if reg in access.uses:
            return line_number, "use"
        if reg in access.defs:
            return line_number, "def"
    return None, "none"


def is_live_after(accesses: list[Access], line_number: int, reg: int) -> bool:
    _, kind = first_future_access(accesses, line_number, reg)
    return kind == "use"


def refs_between(
    accesses: list[Access], first_line: int, last_line: int, reg: int
) -> list[dict[str, object]]:
    refs: list[dict[str, object]] = []
    for line_number in range(first_line + 1, last_line + 1):
        access = accesses[line_number - 1]
        if reg in access.defs or reg in access.uses:
            refs.append(
                {
                    "line": line_number,
                    "def": reg in access.defs,
                    "use": reg in access.uses,
                }
            )
    return refs


def allocate_group(
    accesses: list[Access], sites: list[dict[str, object]], group: int
) -> dict[str, object]:
    ordered = sorted(sites, key=lambda site: int(site["source_line"]))
    by_slot = {
        int(site["bpq_slot"]): site
        for site in sites
    }
    expected_slots = list(range(4 * group, 4 * group + 4))
    if sorted(by_slot) != expected_slots:
        raise ValueError(
            f"CQ group {group}: slots {sorted(by_slot)} != {expected_slots}"
        )

    completion_line = max(int(site["source_line"]) for site in sites)
    parking: dict[int, int] = {}
    occupied_parking: set[int] = set()
    site_results: list[dict[str, object]] = []

    for site in ordered:
        source = int(str(site["source_vector"])[1:])
        source_line = int(site["source_line"])
        clobbers = [
            ref for ref in refs_between(accesses, source_line, completion_line, source)
            if bool(ref["def"])
        ]
        needs_parking = bool(clobbers)
        park_reg: int | None = None

        if needs_parking:
            for candidate in range(1, 32):
                if candidate == source or candidate in occupied_parking:
                    continue
                if is_live_after(accesses, source_line, candidate):
                    continue
                if refs_between(accesses, source_line, completion_line, candidate):
                    continue
                # Do not steal another CQ input register even when it is not yet ready.
                input_regs = {
                    int(str(other["source_vector"])[1:]) for other in sites
                }
                if candidate in input_regs:
                    continue
                park_reg = candidate
                parking[int(site["bpq_slot"])] = candidate
                occupied_parking.add(candidate)
                break

        site_results.append(
            {
                **site,
                "ready_line": source_line,
                "clobbered_before_group_complete": needs_parking,
                "clobber_sites": clobbers,
                "parking_register": None if park_reg is None else f"q{park_reg}",
                "parking_feasible": not needs_parking or park_reg is not None,
            }
        )

    inputs: list[int] = []
    for slot in expected_slots:
        source = int(str(by_slot[slot]["source_vector"])[1:])
        inputs.append(parking.get(slot, source))

    live_after = {
        reg for reg in range(32) if is_live_after(accesses, completion_line, reg)
    }
    destructive_inputs: list[int] = []
    for first, second in ((inputs[0], inputs[1]), (inputs[2], inputs[3])):
        if first not in live_after:
            destructive_inputs.append(first)
        elif second not in live_after:
            destructive_inputs.append(second)
        else:
            destructive_inputs.append(-1)
    extra_first_level_temps = sum(reg == -1 for reg in destructive_inputs)
    required_transpose_temps = 4 + extra_first_level_temps
    transpose_pool = [
        reg for reg in range(1, 32)
        if reg not in live_after and reg not in inputs
    ]
    transpose_temps = transpose_pool[:required_transpose_temps]
    parking_ok = all(bool(site["parking_feasible"]) for site in site_results)
    transpose_ok = (
        all(reg != -1 for reg in destructive_inputs)
        and len(transpose_temps) == required_transpose_temps
    )

    return {
        "cq_group": group,
        "row": group // 8,
        "block": (group % 8) // 2,
        "group_in_block": group % 2,
        "bpq_slots": expected_slots,
        "completion_line": completion_line,
        "sites_execution_order": site_results,
        "cq_input_regs_slot_order": [f"q{reg}" for reg in inputs],
        "live_after_completion": [f"q{reg}" for reg in sorted(live_after)],
        "destructive_trn2_inputs": [
            None if reg == -1 else f"q{reg}" for reg in destructive_inputs
        ],
        "required_transpose_temps": required_transpose_temps,
        "transpose_temp_pool": [f"q{reg}" for reg in transpose_pool],
        "selected_transpose_temps": [f"q{reg}" for reg in transpose_temps],
        "parking_moves": sum(
            1 for site in site_results if bool(site["clobbered_before_group_complete"])
        ),
        "parking_feasible": parking_ok,
        "transpose_feasible": transpose_ok,
        "feasible_no_spill": parking_ok and transpose_ok,
    }


def render_markdown(result: dict[str, object]) -> str:
    groups = result["groups"]
    assert isinstance(groups, list)
    rows = []
    for group in groups:
        assert isinstance(group, dict)
        rows.append(
            "| {cq_group} | {row} | {block}.{group_in_block} | {parking_moves} | "
            "{inputs} | {temps} | {status} |".format(
                **group,
                inputs=", ".join(group["cq_input_regs_slot_order"]),
                temps=", ".join(group["selected_transpose_temps"]),
                status="pass" if group["feasible_no_spill"] else "fail",
            )
        )
    failed = [
        int(group["cq_group"]) for group in groups
        if not bool(group["feasible_no_spill"])
    ]
    return "\n".join(
        [
            "# Direct-CQ Stage345 Endpoint Feasibility",
            "",
            "This is a correctness-first, default-off gate. It analyzes the active",
            "production Stage345 schedule without changing arithmetic, reduction, or",
            "register allocation.",
            "",
            "## Hard contract",
            "",
            "- Four BPQ Q outputs form one CQ group.",
            "- An output overwritten before the fourth Q is ready must be parked in a",
            "  vector register untouched for the entire interval.",
            "- The transpose uses four dead vector temporaries. One dead input from each",
            "  input pair receives the first-level `trn2`; no live input is overwritten.",
            "- No spill/reload, recomputation, or arithmetic/reduction change is allowed.",
            "",
            "## Result",
            "",
            f"`feasible_no_spill: {str(result['feasible_no_spill']).lower()}`",
            f"`failed_groups: {failed}`",
            f"`total_parking_moves: {result['total_parking_moves']}`",
            "",
            "| CQ group | row | block.group | parking moves | CQ inputs | transpose temps | gate |",
            "|---:|---:|---:|---:|---|---|---|",
            *rows,
            "",
            "The JSON artifact records every output-ready line, intervening clobber,",
            "parking assignment, completion live set, and temporary-register pool.",
            "",
        ]
    )


def main() -> None:
    lines = SOURCE.read_text().splitlines()
    bpq_map = json.loads(BPQ_MAP.read_text())
    sites = bpq_map["sites"]
    semantic_output_lines = {int(site["source_line"]) for site in sites}
    accesses = [
        access_for_line(line, line_number, semantic_output_lines)
        for line_number, line in enumerate(lines, start=1)
    ]
    groups: list[dict[str, object]] = []
    for group in range(24):
        group_sites = [
            site for site in sites
            if 4 * group <= int(site["bpq_slot"]) < 4 * group + 4
        ]
        if len(group_sites) != 4:
            raise ValueError(f"CQ group {group}: expected 4 sites, got {len(group_sites)}")
        groups.append(allocate_group(accesses, group_sites, group))

    result = {
        "candidate": "direct_cq_endpoint_feasibility",
        "source": str(SOURCE.relative_to(ROOT)),
        "bpq_map": str(BPQ_MAP.relative_to(ROOT)),
        "hard_contract": {
            "arithmetic_changed": False,
            "reduction_changed": False,
            "spills_allowed": False,
            "recomputation_allowed": False,
            "destructive_live_input_reuse_allowed": False,
            "transpose_temporary_count": 4,
            "destructive_input_rule": "one dead input per BPQ pair receives trn2",
        },
        "groups": groups,
        "total_parking_moves": sum(int(group["parking_moves"]) for group in groups),
        "failed_groups": [
            int(group["cq_group"]) for group in groups
            if not bool(group["feasible_no_spill"])
        ],
        "feasible_no_spill": all(bool(group["feasible_no_spill"]) for group in groups),
        "production_default_changed": False,
    }
    OUTPUT_JSON.write_text(json.dumps(result, indent=2) + "\n")
    OUTPUT_MD.write_text(render_markdown(result))
    print(
        "direct-CQ feasibility:",
        "pass" if result["feasible_no_spill"] else "fail",
        f"parking_moves={result['total_parking_moves']}",
        f"failed_groups={result['failed_groups']}",
    )


if __name__ == "__main__":
    main()
