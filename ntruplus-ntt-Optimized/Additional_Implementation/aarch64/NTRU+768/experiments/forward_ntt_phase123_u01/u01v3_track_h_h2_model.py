#!/usr/bin/env python3
"""Model Track H2 consumer-driven Stage12 producer orders.

This is a model-only artifact.  It derives the Phase123 slot topology and the
current one-pass Stage12 costs from generated U01v2/U01v3 assembly, then
evaluates strict block-major, pair-major, and E3/F012 + delayed-out3 shapes.
It never emits assembly or changes a production path.
"""

from __future__ import annotations

from collections import Counter
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]

PHASE123_FLAT = NTRU_ROOT / "asm/slothy/inputs/ntt768_gt_frontend.sym.S"
U01V2_SYMBOLIC = ROOT / "phase123_shared_prefix_v2_allrows.sym.s"
U01V2_GENERATOR = ROOT / "generate_phase123_shared_prefix_v2.py"
E3_GENERATOR = ROOT / "generate_u01v3_stage345_e3_f012.py"
G1_ASM = NTRU_ROOT / "asm/gt/experiment/u01v3_f0123_g1_delayed_block3.S"
G1_MAP = ROOT / "u01v3_f0123_g1_delayed_block3_map.json"
TRACK_G_MODEL = ROOT / "u01v3_f0123_track_g_candidates.json"
G3_MODEL = ROOT / "u01v3_f0123_g3_candidates.json"

OUT_JSON = ROOT / "u01v3_track_h_h2_candidates.json"
OUT_MD = ROOT / "u01v3_track_h_h2_model.md"

ROWS = 3
STRIPES = 8
BLOCKS = 4
STAGE12_INVOCATIONS = ROWS * STRIPES
Q0_RESERVED = True
DATA_Q_REGS = 31


class ModelError(RuntimeError):
    pass


def code_part(line: str) -> str:
    code = line.split("//", 1)[0].strip()
    if not code or code.endswith(":") or code.startswith("."):
        return ""
    return code


def op_count(lines: list[str]) -> Counter[str]:
    return Counter(code.split()[0].lower() for line in lines if (code := code_part(line)))


def extract_region(lines: list[str], start: str, end: str) -> list[str]:
    try:
        first = next(i for i, line in enumerate(lines) if line.strip() == f"{start}:")
        last = next(i for i, line in enumerate(lines[first + 1 :], first + 1) if line.strip() == f"{end}:")
    except StopIteration as exc:
        raise ModelError(f"missing region {start}..{end}") from exc
    return lines[first + 1 : last]


def phase123_facts() -> dict[str, object]:
    lines = PHASE123_FLAT.read_text().splitlines()
    iterations: list[dict[str, object]] = []
    for iteration in range(8):
        region = extract_region(
            lines,
            f"slothy_start_ntt_phase123_iter{iteration}",
            f"slothy_end_ntt_phase123_iter{iteration}",
        )
        codes = [code_part(line) for line in region if code_part(line)]
        try:
            slot_start = next(
                i for i, code in enumerate(codes) if re.match(r"sub\s+v6\.8h,", code)
            )
            tail_start = next(i for i, code in enumerate(codes) if code == "add x1, x1, #32")
        except StopIteration as exc:
            raise ModelError(f"could not split Phase123 iter{iteration}") from exc

        prefix = codes[:slot_start]
        slots = codes[slot_start:tail_start]
        tail = codes[tail_start:]
        slot_ops = Counter(code.split()[0].lower() for code in slots)
        raw_load_codes = [
            code
            for code in prefix
            if code.split()[0].lower() in {"ldr", "ldp"} and "[x1" in code
        ]
        raw_q_vectors = sum(2 if code.startswith("ldp ") else 1 for code in raw_load_codes)
        twist_load_codes = [code for code in prefix if code.startswith("ldp ") and "[x3" in code]

        if len(prefix) != 104 or len(slots) != 52 or len(tail) != 4:
            raise ModelError(
                f"unexpected Phase123 iter{iteration} shape: "
                f"prefix={len(prefix)} slots={len(slots)} tail={len(tail)}"
            )
        if slot_ops["str"] != 12 or sum(slot_ops.values()) - slot_ops["str"] != 40:
            raise ModelError(f"unexpected Phase123 iter{iteration} slot operation counts")
        if raw_q_vectors != 12 or len(twist_load_codes) != 12:
            raise ModelError(f"unexpected Phase123 iter{iteration} input/twist load shape")

        iterations.append(
            {
                "iteration": iteration,
                "raw_q_indices": list(range(4 * iteration, 4 * iteration + 4)),
                "prefix_instructions": len(prefix),
                "slot_groups": 4,
                "slot_instructions": len(slots),
                "slot_arithmetic": sum(slot_ops.values()) - slot_ops["str"],
                "slot_stores": slot_ops["str"],
                "tail_pointer_instructions": len(tail),
                "wrapper_fixed_base_setup_instructions": 5,
                "total_with_u01_wrapper_setup": len(codes) + 5,
                "raw_input_load_instructions": len(raw_load_codes),
                "raw_input_q_vectors": raw_q_vectors,
                "twist_ldp_instructions": len(twist_load_codes),
                "zip_instructions": sum(1 for code in prefix if code.startswith(("zip1 ", "zip2 "))),
            }
        )

    first = iterations[0]
    invariant_fields = (
        "prefix_instructions",
        "slot_groups",
        "slot_instructions",
        "slot_arithmetic",
        "slot_stores",
        "tail_pointer_instructions",
        "total_with_u01_wrapper_setup",
        "raw_input_load_instructions",
        "raw_input_q_vectors",
        "twist_ldp_instructions",
        "zip_instructions",
    )
    for item in iterations[1:]:
        for field in invariant_fields:
            if item[field] != first[field]:
                raise ModelError(f"Phase123 field {field} differs at iter{item['iteration']}")

    v2 = U01V2_SYMBOLIC.read_text()
    if "iter0, shared prefix once" not in v2 or "iter7, shared prefix once" not in v2:
        raise ModelError("U01v2 symbolic body does not expose all shared-prefix iterations")
    v2_generator = U01V2_GENERATOR.read_text()
    for required in (
        "for iteration in (0, 2, 4, 6):",
        "for iteration in (1, 3, 5, 7):",
        "emit_stage12_group(lines, range(0, 4)",
        "emit_stage12_group(lines, range(4, 8)",
    ):
        if required not in v2_generator:
            raise ModelError(f"U01v2 generator contract missing: {required}")

    return {
        "source": str(PHASE123_FLAT.relative_to(NTRU_ROOT)),
        "u01v2_cross_check": str(U01V2_SYMBOLIC.relative_to(NTRU_ROOT)),
        "u01v2_generator_cross_check": str(U01V2_GENERATOR.relative_to(NTRU_ROOT)),
        "iteration_count": len(iterations),
        "iteration_order_in_u01v2": [0, 2, 4, 6, 1, 3, 5, 7],
        "per_iteration": first | {"iteration": "invariant", "raw_q_indices": "4*i..4*i+3"},
        "total_phase123_instructions": sum(int(item["total_with_u01_wrapper_setup"]) for item in iterations),
        "total_raw_input_q_vectors": sum(int(item["raw_input_q_vectors"]) for item in iterations),
        "iterations": iterations,
    }


def stage12_dependency_facts() -> dict[str, object]:
    stripes: list[dict[str, object]] = []
    for stripe in range(STRIPES):
        raw_q = [stripe + 8 * k for k in range(4)]
        stripes.append(
            {
                "stripe": stripe,
                "raw_values": {"A": raw_q[0], "B": raw_q[1], "C": raw_q[2], "D": raw_q[3]},
                "phase123_iterations": [q // 4 for q in raw_q],
                "slot_within_iteration": stripe % 4,
                "outputs": [stripe, stripe + 8, stripe + 16, stripe + 24],
            }
        )

    g1_lines = G1_ASM.read_text().splitlines()
    e3_generator = E3_GENERATOR.read_text()
    for required in (
        "// t0 = B + D",
        "// t1 raw = B - D",
        "// t3 = A - C",
        "// t2 = A + C",
        "// out3 = t3 - t1",
        "// out2 = t3 + t1",
        "// out1 = t2 - t0",
        "// out0 = t2 + t0",
    ):
        if required not in e3_generator:
            raise ModelError(f"E3 generator semantic contract missing: {required}")
    marker = re.compile(r"^\s*// Stage12 (row\d) stripe(\d):")
    observed: list[dict[str, object]] = []
    for index, line in enumerate(g1_lines):
        match = marker.match(line)
        if not match:
            continue
        body: list[str] = []
        for candidate in g1_lines[index + 1 :]:
            if not candidate.strip():
                break
            body.append(candidate)
        ops = op_count(body)
        observed.append(
            {
                "row": match.group(1),
                "stripe": int(match.group(2)),
                "raw_q_loads": ops["ldr"],
                "arithmetic": sum(ops[op] for op in ("add", "sub", "sqrdmulh", "mul", "mls")),
                "out3_stores": ops["str"],
            }
        )

    if len(observed) != STAGE12_INVOCATIONS:
        raise ModelError(f"expected {STAGE12_INVOCATIONS} G1 Stage12 stripes, found {len(observed)}")
    expected_observed = {"raw_q_loads": 4, "arithmetic": 13, "out3_stores": 1}
    for item in observed:
        for field, expected in expected_observed.items():
            if item[field] != expected:
                raise ModelError(f"unexpected G1 Stage12 {item['row']} stripe{item['stripe']} {field}")

    return {
        "source": str(G1_ASM.relative_to(NTRU_ROOT)),
        "generator_cross_check": str(E3_GENERATOR.relative_to(NTRU_ROOT)),
        "semantic_dag_per_stripe": {
            "inputs": ["A=raw_Qs", "B=raw_Qs+8", "C=raw_Qs+16", "D=raw_Qs+24"],
            "t0": "reduce(B + D)",
            "t1": "twiddle_reduce(B - D)",
            "t2": "A + C",
            "t3": "A - C",
            "out0": "t2 + t0",
            "out1": "t2 - t0",
            "out2": "t3 + t1",
            "out3": "t3 - t1",
        },
        "shared_subexpressions": {
            "block_pair_01": ["t0", "t2"],
            "block_pair_23": ["t1", "t3"],
            "all_four_outputs_require_same_raw_basis": True,
        },
        "cost_per_stripe": {
            "one_pass_all_outputs_arithmetic": 13,
            "out0_only_arithmetic": 5,
            "out1_only_arithmetic": 5,
            "out2_only_arithmetic": 6,
            "out3_only_arithmetic": 6,
            "pair01_arithmetic": 6,
            "pair23_arithmetic": 7,
            "raw_q_loads_per_pass": 4,
        },
        "twiddle_loads_per_row_per_stage12_pass": 3,
        "stripes": stripes,
        "g1_observed_stage12_stripes": len(observed),
        "g1_observed_cost_per_stripe": expected_observed,
    }


def hard_gate(raw_q_reloads: int, expected_delta: int, live_all: bool = False) -> dict[str, object]:
    checks = {
        "no_raw_q_reload": raw_q_reloads == 0,
        "no_large_new_memory_boundary": raw_q_reloads == 0,
        "no_live_all_violation": not live_all,
        "expected_instruction_delta_plausible": expected_delta <= 0,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "failed": [name for name, passed in checks.items() if not passed],
    }


def build_candidates(
    stage12: dict[str, object],
    stage345_live: dict[str, int],
    g1_map: dict[str, object],
    g3a: dict[str, object],
) -> dict[str, dict[str, object]]:
    cost = stage12["cost_per_stripe"]
    removed_loads = int(g1_map["block3_stage345_q_loads_retained"])
    removed_stores = STAGE12_INVOCATIONS

    h2a_arithmetic = (
        int(cost["out0_only_arithmetic"])
        + int(cost["out1_only_arithmetic"])
        + int(cost["out2_only_arithmetic"])
        + int(cost["out3_only_arithmetic"])
        - int(cost["one_pass_all_outputs_arithmetic"])
    ) * STAGE12_INVOCATIONS
    h2a_raw_reloads = int(cost["raw_q_loads_per_pass"]) * STAGE12_INVOCATIONS * (BLOCKS - 1)
    h2a_twiddles = int(stage12["twiddle_loads_per_row_per_stage12_pass"]) * ROWS * (BLOCKS - 1)
    h2a_delta = h2a_arithmetic + h2a_raw_reloads + h2a_twiddles - removed_loads - removed_stores

    h2b_arithmetic = (
        int(cost["pair01_arithmetic"])
        + int(cost["pair23_arithmetic"])
        - int(cost["one_pass_all_outputs_arithmetic"])
    ) * STAGE12_INVOCATIONS
    h2b_raw_reloads = int(cost["raw_q_loads_per_pass"]) * STAGE12_INVOCATIONS
    h2b_twiddles = int(stage12["twiddle_loads_per_row_per_stage12_pass"]) * ROWS
    h2b_delta = h2b_arithmetic + h2b_raw_reloads + h2b_twiddles - removed_loads - removed_stores

    h2c_delta = int(g3a["expected_instruction_delta_vs_G1"])
    h2c_raw_reloads = int(g3a["raw_q_reloads"])
    h2c_arithmetic = int(g3a["extra_arithmetic_instructions"])

    return {
        "H2a_strict_block_major": {
            "status": "hard_gate_fail",
            "shape": "Keep Phase123 raw scratch intact; run four branch-specific Stage12 passes and consume Stage345 block0, block1, block2, block3 immediately after each pass.",
            "extra_arithmetic": h2a_arithmetic,
            "removed_q_loads": removed_loads,
            "removed_q_stores": removed_stores,
            "raw_q_reloads": h2a_raw_reloads,
            "extra_twiddle_loads": h2a_twiddles,
            "max_live_q_regs": 16,
            "max_live_derivation": "At most 7 completed block outputs + 4 fixed q0/q2/q3/q4 + 4 destructive raw/basis registers + 1 reduction temp. The inherited Stage345 semantic max-live table separately peaks at 16.",
            "shared_prefix_reuse_lost": {
                "phase123_replays": 0,
                "stage12_arithmetic_recomputed": h2a_arithmetic,
                "reason": "out0/out1 recompute t0/t2 independently and out2/out3 recompute t1/t3 independently",
            },
            "expected_instruction_delta_vs_G1": h2a_delta,
            "instruction_delta_breakdown": {
                "extra_arithmetic": h2a_arithmetic,
                "extra_raw_q_loads": h2a_raw_reloads,
                "extra_twiddle_loads": h2a_twiddles,
                "removed_block3_q_loads": -removed_loads,
                "removed_out3_q_stores": -removed_stores,
                "net": h2a_delta,
            },
            "hard_gate": hard_gate(h2a_raw_reloads, h2a_delta),
            "no_raw_reload_alternative": {
                "required_extra_phase123_passes": 3,
                "extra_phase123_instructions": 3 * 8 * 165,
                "reason": "Without rereading raw scratch, each later block must regenerate the common Phase123 raw basis or retain all raw values across Stage345.",
            },
        },
        "H2b_pair_major_01_then_23": {
            "status": "hard_gate_fail",
            "shape": "Produce block0+block1 from one Stage12 raw-read pass, consume both, then reread the unchanged raw scratch once to produce block2+block3 and consume both.",
            "extra_arithmetic": h2b_arithmetic,
            "removed_q_loads": removed_loads,
            "removed_q_stores": removed_stores,
            "raw_q_reloads": h2b_raw_reloads,
            "extra_twiddle_loads": h2b_twiddles,
            "max_live_q_regs": 29,
            "max_live_derivation": "The existing block01 producer proves a 16-output pair can be formed with a conservative 29-register peak; Stage345 block2 preserving 8 block3 inputs is estimated at q0 + 8 future + block2 SSA max-live 16 = 25.",
            "shared_prefix_reuse_lost": {
                "phase123_replays": 0,
                "stage12_arithmetic_recomputed": h2b_arithmetic,
                "reason": "pair01 preserves t0/t2 sharing and pair23 preserves t1/t3 sharing; only the four raw vectors per stripe are loaded twice",
            },
            "expected_instruction_delta_vs_G1": h2b_delta,
            "instruction_delta_breakdown": {
                "extra_arithmetic": h2b_arithmetic,
                "extra_raw_q_loads": h2b_raw_reloads,
                "extra_twiddle_loads": h2b_twiddles,
                "removed_block3_q_loads": -removed_loads,
                "removed_out3_q_stores": -removed_stores,
                "net": h2b_delta,
            },
            "structural_feasibility": "register-count plausible but not allocator/correctness proven",
            "hard_gate": hard_gate(h2b_raw_reloads, h2b_delta),
        },
        "H2c_hybrid_E3_F012_reordered_out3": {
            "status": "hard_gate_fail",
            "shape": "Keep E3/F012, leave raw D un-overwritten, then regenerate out3 after block0/1/2 and hand it directly to Stage345 block3.",
            "extra_arithmetic": h2c_arithmetic,
            "removed_q_loads": int(g3a["removed_block3_q_loads"]),
            "removed_q_stores": int(g3a["removed_block3_q_stores_if_applicable"]),
            "raw_q_reloads": h2c_raw_reloads,
            "extra_twiddle_loads": int(g3a["extra_q_loads"]) - h2c_raw_reloads,
            "max_live_q_regs": 31,
            "max_live_derivation": "The retained E3/F012 producer already reaches 24 live outputs plus q0/twiddles/temps. Delayed out3 is locally small, but a register-retained out3 basis would reserve 24 future vectors at block0 and leave only 7 colors for a 15-live SSA block.",
            "shared_prefix_reuse_lost": {
                "phase123_replays": 0,
                "stage12_arithmetic_recomputed": h2c_arithmetic,
                "reason": "the t1/t3 -> out3 dependency cone is rebuilt after E3 because raw D was otherwise overwritten",
            },
            "expected_instruction_delta_vs_G1": h2c_delta,
            "instruction_delta_breakdown": {
                "extra_arithmetic": h2c_arithmetic,
                "extra_raw_q_loads": h2c_raw_reloads,
                "extra_twiddle_loads": int(g3a["extra_q_loads"]) - h2c_raw_reloads,
                "removed_block3_q_loads": -int(g3a["removed_block3_q_loads"]),
                "removed_out3_q_stores": -int(g3a["removed_block3_q_stores_if_applicable"]),
                "net": h2c_delta,
            },
            "equivalent_existing_model": "G3a_delayed_block3_producer_after_E3",
            "register_retained_alternative": {
                "future_values_at_block0": 24,
                "available_block0_colors": DATA_Q_REGS - 24,
                "block0_ssa_max_live": stage345_live["block0"],
                "allocator_deficit": DATA_Q_REGS - 24 - stage345_live["block0"],
                "feasible": False,
            },
            "hard_gate": hard_gate(h2c_raw_reloads, h2c_delta),
        },
    }


def build_model() -> dict[str, object]:
    phase123 = phase123_facts()
    stage12 = stage12_dependency_facts()
    g1_map = json.loads(G1_MAP.read_text())
    track_g = json.loads(TRACK_G_MODEL.read_text())
    g3 = json.loads(G3_MODEL.read_text())
    stage345_live = {
        key: int(value) for key, value in track_g["stage345_semantic_max_live"].items()
    }
    g3a = g3["candidates"]["G3a_delayed_block3_producer_after_E3"]
    candidates = build_candidates(stage12, stage345_live, g1_map, g3a)

    passing = [name for name, item in candidates.items() if item["hard_gate"]["status"] == "pass"]
    deltas = {name: int(item["expected_instruction_delta_vs_G1"]) for name, item in candidates.items()}
    least_bad = min(deltas, key=deltas.get)

    return {
        "artifact": "u01v3_track_h_h2_consumer_driven_producer_order_model",
        "model_only": True,
        "production_default_changed": False,
        "asm_emitted": False,
        "sources": [
            str(PHASE123_FLAT.relative_to(NTRU_ROOT)),
            str(U01V2_SYMBOLIC.relative_to(NTRU_ROOT)),
            str(U01V2_GENERATOR.relative_to(NTRU_ROOT)),
            str(E3_GENERATOR.relative_to(NTRU_ROOT)),
            str(G1_ASM.relative_to(NTRU_ROOT)),
            str(G1_MAP.relative_to(NTRU_ROOT)),
            str(TRACK_G_MODEL.relative_to(NTRU_ROOT)),
            str(G3_MODEL.relative_to(NTRU_ROOT)),
        ],
        "baseline": {
            "name": "G1",
            "shape": g1_map["shape"],
            "removed_q_stores_vs_v": g1_map["removed_q_stores_vs_v"],
            "removed_q_loads_vs_v": g1_map["removed_q_loads_vs_v"],
            "block3_q_loads_retained": g1_map["block3_stage345_q_loads_retained"],
            "raw_q_reloads": g1_map["raw_q_reloads"],
        },
        "phase123_facts": phase123,
        "stage12_facts": stage12,
        "stage345_semantic_max_live": stage345_live,
        "candidates": candidates,
        "decision": {
            "hard_gate_passing_candidates": passing,
            "emit_h2_asm": False,
            "least_bad_model": least_bad,
            "least_bad_instruction_delta_vs_G1": deltas[least_bad],
            "reason": "No H2 candidate avoids both the block3 scratch boundary and a replacement raw/prefix boundary. H2b is the smallest estimate, but it exactly reintroduces the rejected 96-vector raw-q reload pass.",
            "track_h_implication": "Consumer order alone is insufficient. A viable next model must change the semantic source lifetime (H1) or find a smaller register-resident reconstruction basis (H3).",
        },
    }


def write_md(model: dict[str, object]) -> None:
    phase = model["phase123_facts"]
    stage = model["stage12_facts"]
    candidates = model["candidates"]
    rows = []
    for name, item in candidates.items():
        rows.append(
            f"| {name.split('_', 1)[0]} | {item['extra_arithmetic']} | "
            f"{item['removed_q_loads']} / {item['removed_q_stores']} | "
            f"{item['raw_q_reloads']} | {item['max_live_q_regs']} | "
            f"{item['expected_instruction_delta_vs_G1']:+d} | {item['hard_gate']['status']} |"
        )

    stripe_lines = []
    for item in stage["stripes"]:
        raw = item["raw_values"]
        stripe_lines.append(
            f"stripe{item['stripe']}: A/B/C/D=Q{raw['A']}/Q{raw['B']}/Q{raw['C']}/Q{raw['D']} "
            f"from iter {item['phase123_iterations']} slot {item['slot_within_iteration']}"
        )

    OUT_MD.write_text(
        "# U01v3 Track H2 Consumer-Driven Producer-Order Model\n\n"
        "Status: model-only. No ASM emitted, no Slothy run, and production defaults are unchanged.\n\n"
        "## Derived producer contract\n\n"
        "The existing U01v2 symbolic body executes Phase123 iterations in "
        "`0,2,4,6,1,3,5,7` order. Each iteration computes one shared prefix "
        "and four DFT3 raw slots. Mechanically extracted per iteration:\n\n"
        "```text\n"
        f"shared prefix instructions: {phase['per_iteration']['prefix_instructions']}\n"
        f"four raw-slot groups: {phase['per_iteration']['slot_instructions']} instructions "
        f"({phase['per_iteration']['slot_arithmetic']} arithmetic + {phase['per_iteration']['slot_stores']} stores)\n"
        f"fixed-base wrapper setup: {phase['per_iteration']['wrapper_fixed_base_setup_instructions']} instructions\n"
        f"tail pointer instructions: {phase['per_iteration']['tail_pointer_instructions']}\n"
        f"total per iteration in U01v2/G1 shape: {phase['per_iteration']['total_with_u01_wrapper_setup']}\n"
        "```\n\n"
        "One Stage12 stripe always needs four raw values produced by four "
        "different Phase123 iterations:\n\n"
        "```text\n"
        + "\n".join(stripe_lines)
        + "\n```\n\n"
        "The Stage12 semantic split is:\n\n"
        "```text\n"
        "t0 = reduce(B + D)       out0 = t2 + t0\n"
        "t1 = twist_reduce(B-D)   out1 = t2 - t0\n"
        "t2 = A + C               out2 = t3 + t1\n"
        "t3 = A - C               out3 = t3 - t1\n"
        "```\n\n"
        "This is why pair-major is the natural split: blocks0/1 share `t0,t2`, "
        "and blocks2/3 share `t1,t3`. Strict block-major throws away that sharing.\n\n"
        "## Candidate comparison\n\n"
        "All counts cover three rows and eight stripes. Removed loads/stores "
        "are the 24 G1 block3 Stage345 loads and 24 Stage12 out3 stores.\n\n"
        "| Candidate | Extra arithmetic | Removed q load/store | Raw q reloads | Max live q | Instr delta vs G1 | Gate |\n"
        "|---|---:|---:|---:|---:|---:|---|\n"
        + "\n".join(rows)
        + "\n\n"
        "### H2a strict block-major\n\n"
        "Four branch-specific Stage12 passes cost 22 arithmetic instructions "
        "per stripe instead of 13. It reloads A/B/C/D three extra times, so "
        "the result is `+483` instructions versus G1 even after removing the "
        "block3 store/load boundary. Regenerating Phase123 instead would be "
        "worse: three extra full passes cost about 3960 instructions.\n\n"
        "### H2b pair-major 01 then 23\n\n"
        "This preserves all Stage12 arithmetic sharing: `6 + 7 = 13` "
        "instructions per stripe. Its blocker is memory lifetime. After "
        "Stage345 blocks0/1 consume the first pair, the second pair needs the "
        "same A/B/C/D again, adding exactly 96 raw-q reloads and 9 twiddle "
        "loads. Net estimate is `+57` instructions versus G1. Register count "
        "looks plausible, but the candidate fails Track H's explicit no-96-reload gate.\n\n"
        "### H2c hybrid E3/F012 plus reordered out3\n\n"
        "Under the existing lifetime this is the already-modelled G3a shape. "
        "E3 leaves raw A/B/C in scratch but overwrites D with out3. Delaying "
        "out3 preserves D, then later reloads all A/B/C/D and rebuilds the "
        "out3 cone: 96 raw reloads, 144 arithmetic instructions, and `+201` "
        "instructions versus G1. Keeping an eight-vector basis in registers "
        "instead reserves 24 future values at Stage345 block0, leaving 7 "
        "colors for a block whose SSA needs 15.\n\n"
        "## Decision\n\n"
        "```text\n"
        "hard-gate passing H2 candidates: none\n"
        "emit H2 ASM: no\n"
        "least-bad model: H2b pair-major, +57 instructions vs G1\n"
        "reason: H2b still reintroduces the rejected 96-vector raw-q reload pass\n"
        "```\n\n"
        "Consumer order by itself does not solve the source lifetime. A viable "
        "Track H candidate must either delay the destructive source overwrite "
        "without extending 24 future live values (H1), or identify a smaller "
        "register-resident reconstruction basis (H3).\n"
    )


def main() -> int:
    model = build_model()
    OUT_JSON.write_text(json.dumps(model, indent=2) + "\n")
    write_md(model)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
