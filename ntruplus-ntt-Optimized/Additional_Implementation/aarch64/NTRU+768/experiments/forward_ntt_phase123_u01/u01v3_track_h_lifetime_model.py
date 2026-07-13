#!/usr/bin/env python3
"""Extract the Track H Phase123/Stage12/block3 semantic lifetime contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

from analyze_u01v3_stage345_e4_f0123 import first_consume_sites
from generate_stage12_block0_first import qoff


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]
G1_ASM = NTRU_ROOT / "asm/gt/experiment/u01v3_f0123_g1_delayed_block3.S"
PHASE123 = NTRU_ROOT / "asm/slothy/inputs/ntt768_gt_frontend.sym.S"

OUT_IR = ROOT / "u01v3_track_h_semantic_ir.json"
OUT_OVERWRITE = ROOT / "u01v3_track_h_overwrite_map.json"
OUT_MD = ROOT / "u01v3_track_h_lifetime_model.md"

ROWS = ("row0", "row1", "row2")
STRIPES = range(8)

STAGE12_HEADER_RE = re.compile(
    r"Stage12 (row[0-2]) stripe([0-7]): Q(\d+)->q(\d+), "
    r"Q(\d+)->q(\d+), Q(\d+)->q(\d+); Q(\d+) stored\."
)
VREG_RE = re.compile(r"(?:v(\d+)\.8h|q(\d+))")


def executable(code: str) -> bool:
    stripped = code.split("//", 1)[0].strip()
    return bool(stripped) and not stripped.endswith(":") and not stripped.startswith(".")


def extract_stage12_sites() -> list[dict[str, object]]:
    lines = G1_ASM.read_text().splitlines()
    sites: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        match = STAGE12_HEADER_RE.search(line)
        if not match:
            continue
        row = match.group(1)
        stripe = int(match.group(2))
        q0, r0 = int(match.group(3)), int(match.group(4))
        q8, r1 = int(match.group(5)), int(match.group(6))
        q16, r2 = int(match.group(7)), int(match.group(8))
        q24 = int(match.group(9))
        body: list[dict[str, object]] = []
        cursor = index + 1
        while cursor < len(lines):
            code = lines[cursor].split("//", 1)[0].strip()
            comment = lines[cursor].split("//", 1)[1].strip() if "//" in lines[cursor] else ""
            if cursor > index + 1 and "Stage12 row" in lines[cursor]:
                break
            if not lines[cursor].strip() and cursor > index + 1 and body:
                break
            if executable(lines[cursor]):
                body.append(
                    {
                        "asm_line": cursor + 1,
                        "instruction": code,
                        "comment": comment,
                        "vector_regs": [
                            f"q{v or q}" for v, q in VREG_RE.findall(code)
                        ],
                    }
                )
            cursor += 1
        if len(body) != 18:
            raise ValueError(f"{row} stripe{stripe}: expected 18 Stage12 ops, got {len(body)}")
        regs = {
            "out0": f"q{r0}",
            "out1": f"q{r1}",
            "out2": f"q{r2}",
            "raw_D_t3": body[1]["vector_regs"][0],
            "t0": body[2]["vector_regs"][0],
            "red": body[4]["vector_regs"][0],
        }
        sites.append(
            {
                "row": row,
                "stripe": stripe,
                "header_asm_line": index + 1,
                "q_indices": {"A": q0, "B": q8, "C": q16, "D": q24},
                "scratch_offsets": {
                    name: qoff(row, qidx)
                    for name, qidx in (("A", q0), ("B", q8), ("C", q16), ("D", q24))
                },
                "physical_regs": regs,
                "instructions": body,
            }
        )
    expected = {(row, stripe) for row in ROWS for stripe in STRIPES}
    actual = {(str(site["row"]), int(site["stripe"])) for site in sites}
    if actual != expected:
        raise ValueError(f"incomplete Stage12 extraction: missing={expected - actual}, extra={actual - expected}")
    return sites


def semantic_values(site: dict[str, object]) -> list[dict[str, object]]:
    row = str(site["row"])
    stripe = int(site["stripe"])
    qidx = site["q_indices"]
    offsets = site["scratch_offsets"]
    regs = site["physical_regs"]
    prefix = f"{row}.s{stripe}"
    return [
        {
            "semantic": f"{prefix}.raw_A",
            "producer": "Phase123 scratch store",
            "consumers": ["t3=A-C", "t2=A+C"],
            "first_use": 10,
            "last_use": 11,
            "current_location": {"scratch_offset": offsets["A"], "loaded_reg": regs["out0"]},
            "overwrite_site": "physical register at Stage12 op11; scratch slot remains raw",
        },
        {
            "semantic": f"{prefix}.raw_B",
            "producer": "Phase123 scratch store",
            "consumers": ["t0=B+D", "t1_raw=B-D"],
            "first_use": 2,
            "last_use": 3,
            "current_location": {"scratch_offset": offsets["B"], "loaded_reg": regs["out1"]},
            "overwrite_site": "physical register at Stage12 op3; scratch slot remains raw",
        },
        {
            "semantic": f"{prefix}.raw_C",
            "producer": "Phase123 scratch store",
            "consumers": ["t3=A-C", "t2=A+C"],
            "first_use": 10,
            "last_use": 11,
            "current_location": {"scratch_offset": offsets["C"], "loaded_reg": regs["out2"]},
            "overwrite_site": "physical register at Stage12 op13; scratch slot remains raw",
        },
        {
            "semantic": f"{prefix}.raw_D",
            "producer": "Phase123 scratch store",
            "consumers": ["t0=B+D", "t1_raw=B-D"],
            "first_use": 2,
            "last_use": 3,
            "current_location": {"scratch_offset": offsets["D"], "loaded_reg": regs["raw_D_t3"]},
            "overwrite_site": "physical register at Stage12 op10; scratch slot at Stage12 op18",
        },
        {
            "semantic": f"{prefix}.t0_reduced",
            "producer": "reduce(B+D)",
            "consumers": ["Q8=t2-t0", "Q0=t2+t0"],
            "first_use": 14,
            "last_use": 15,
            "current_location": {"reg": regs["t0"]},
            "overwrite_site": "dead after Q0",
        },
        {
            "semantic": f"{prefix}.t1_reduced",
            "producer": "twisted_reduce(B-D)",
            "consumers": ["Q24=t3-t1", "Q16=t3+t1"],
            "first_use": 12,
            "last_use": 13,
            "current_location": {"reg": regs["out1"]},
            "overwrite_site": "physical register at Stage12 op14",
        },
        {
            "semantic": f"{prefix}.t3",
            "producer": "A-C",
            "consumers": ["Q24=t3-t1", "Q16=t3+t1"],
            "first_use": 12,
            "last_use": 13,
            "current_location": {"reg": regs["raw_D_t3"]},
            "overwrite_site": "dead after Q16",
        },
        {
            "semantic": f"{prefix}.Q{qidx['D']}",
            "producer": "t3-t1",
            "consumers": ["Stage345 block3 first input use"],
            "first_use": 18,
            "last_use": "Stage345 block3",
            "current_location": {"scratch_offset": offsets["D"], "producer_reg": regs["red"]},
            "overwrite_site": "Stage345 block3 consumes and clobbers its handoff register",
        },
    ]


def make_overwrite_map(sites: list[dict[str, object]]) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    for site in sites:
        row = str(site["row"])
        stripe = int(site["stripe"])
        ins = site["instructions"]
        q24 = int(site["q_indices"]["D"])
        entries.append(
            {
                "row": row,
                "stripe": stripe,
                "block3_q": q24,
                "raw_D_register_last_safe_point": {
                    "before_asm_line": ins[9]["asm_line"],
                    "overwrite_instruction": ins[9]["instruction"],
                    "reason": "the register loaded with D is destructively reused for t3=A-C",
                },
                "raw_D_scratch_last_safe_point": {
                    "before_asm_line": ins[17]["asm_line"],
                    "overwrite_instruction": ins[17]["instruction"],
                    "scratch_offset": site["scratch_offsets"]["D"],
                    "reason": "Q24..Q31 is stored over the Phase123 raw-D slot",
                },
                "other_raw_scratch_survives": [
                    site["scratch_offsets"]["A"],
                    site["scratch_offsets"]["B"],
                    site["scratch_offsets"]["C"],
                ],
            }
        )
    return {
        "artifact": "u01v3_track_h_overwrite_map",
        "source": str(G1_ASM.relative_to(NTRU_ROOT)),
        "block3_source_last_safe_point": "per stripe: raw-D register before t3=A-C; raw-D scratch before Q24..Q31 store",
        "block3_source_overwrite_sites": entries,
        "minimum_values_needed_to_reconstruct_Q24_Q31": {
            "per_stripe_raw_basis": ["A", "B", "C", "D"],
            "per_stripe_intermediate_basis": ["t1_reduced", "t3"],
            "per_stripe_final_basis": ["Q24_plus_stripe"],
            "vectors_per_row": {"raw": 32, "intermediate": 16, "final": 8},
            "vectors_all_rows": {"raw": 96, "intermediate": 48, "final": 24},
            "note": "The existing G1 Q24..Q31 scratch image is already the rank-1-per-stripe final basis.",
        },
    }


def build_ir(sites: list[dict[str, object]]) -> dict[str, object]:
    phase_lines = PHASE123.read_text().splitlines()
    phase_store_lines = [
        {"asm_line": i + 1, "instruction": line.strip()}
        for i, line in enumerate(phase_lines)
        if re.match(r"^\s*str\s+q(?:9|10|11),", line)
    ]
    block3_contract = []
    for site in first_consume_sites(3):
        block3_contract.append(
            {
                "q_index": int(site["q_index"]),
                "consumer_instruction_index": int(site["op_index"]),
                "expected_physical_reg": site["original_dest"],
                "preclobbers": site["preclobbers"],
                "same_reg_handoff_safe": site["original_dest"] not in site["preclobbers"],
            }
        )
    values = [value for site in sites for value in semantic_values(site)]
    return {
        "artifact": "u01v3_track_h_semantic_ir",
        "production_default_changed": False,
        "sources": {
            "phase123": str(PHASE123.relative_to(NTRU_ROOT)),
            "g1": str(G1_ASM.relative_to(NTRU_ROOT)),
        },
        "mechanical_extraction": {
            "phase123_raw_store_count": len(phase_store_lines),
            "phase123_raw_store_sites": phase_store_lines,
            "stage12_stripe_count": len(sites),
            "stage12_executable_ops_per_stripe": 18,
        },
        "semantic_values": values,
        "stage12_sites": sites,
        "block3_dependency_cone": {
            "formula_per_stripe": "Q24+s = (A_s-C_s) - twisted_reduce(B_s-D_s)",
            "leaves": ["raw_A", "raw_B", "raw_C", "raw_D", "q", "Stage12 twiddle constants"],
            "intermediates": ["t1_raw", "t1_reduced", "t3"],
            "outputs": [f"Q{q}" for q in range(24, 32)],
        },
        "stage345_block3_consumer_contract": block3_contract,
    }


def write_md(ir: dict[str, object], overwrite: dict[str, object]) -> None:
    contract = ir["stage345_block3_consumer_contract"]
    safe = sum(bool(site["same_reg_handoff_safe"]) for site in contract)
    OUT_MD.write_text(
        "# U01v3 Track H Semantic Lifetime Model\n\n"
        "Status: mechanically extracted from the current G1 assembly and the "
        "production Phase123 symbolic source. Production default unchanged.\n\n"
        "The important lifetime is per Stage12 stripe:\n\n"
        "```text\n"
        "Phase123 scratch: A, B, C, D\n"
        "Stage12:           t0/t1/t2/t3\n"
        "outputs:           Q0, Q8, Q16, Q24\n"
        "Q24 formula:       (A-C) - twisted_reduce(B-D)\n"
        "```\n\n"
        "The physical D register stops being recoverable when it is reused for "
        "`t3=A-C`. The raw D scratch slot survives longer, but G1 then stores "
        "Q24 over that same slot. A/B/C raw scratch slots are not overwritten "
        "by the compact F012 producer.\n\n"
        "This gives three reconstruction contracts:\n\n"
        "```text\n"
        "raw basis per stripe:          A, B, C, D       (4 vectors)\n"
        "intermediate basis per stripe: t1_reduced, t3   (2 vectors)\n"
        "final basis per stripe:        Q24+s            (1 vector)\n"
        "final basis for all 3 rows:                       24 vectors\n"
        "```\n\n"
        "G1 already stores the smallest final basis: one vector for every "
        "block3 stripe. A proposed 1-4-vector global H3 basis therefore cannot "
        "represent all 24 independent block3 vectors unless it exploits a new "
        "algebraic dependency not present in this def-use graph.\n\n"
        "Stage345 block3 is not the main blocker: "
        f"{safe}/{len(contract)} same-destination handoffs are safe before first "
        "consumer. The difficult boundary is keeping or producing the 24 "
        "independent Q24..Q31 row values at the right time.\n\n"
        "Machine-readable details:\n\n"
        "- `u01v3_track_h_semantic_ir.json`\n"
        "- `u01v3_track_h_overwrite_map.json`\n"
    )


def main() -> int:
    sites = extract_stage12_sites()
    ir = build_ir(sites)
    overwrite = make_overwrite_map(sites)
    OUT_IR.write_text(json.dumps(ir, indent=2) + "\n")
    OUT_OVERWRITE.write_text(json.dumps(overwrite, indent=2) + "\n")
    write_md(ir, overwrite)
    print(OUT_IR)
    print(OUT_OVERWRITE)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
