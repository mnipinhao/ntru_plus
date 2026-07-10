#!/usr/bin/env python3
"""Model Track H1 delayed-out3-overwrite candidates.

The model deliberately reasons about semantic values (A/B/C/D, t0/t1/t2/t3,
and Q outputs).  Physical register names from generated assembly are used only
to validate that the model is attached to the current G1/E3 artifacts.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
NTRU_ROOT = ROOT.parents[1]

OUT_JSON = ROOT / "u01v3_track_h_h1_candidates.json"
OUT_MD = ROOT / "u01v3_track_h_h1_model.md"

G1_ASM = NTRU_ROOT / "asm/gt/experiment/u01v3_f0123_g1_delayed_block3.S"
G1_MAP = ROOT / "u01v3_f0123_g1_delayed_block3_map.json"
E3_MAP = ROOT / "u01v3_stage345_semantic_e3_map.json"
E4_FEASIBILITY = ROOT / "u01v3_f0123_liveness_clobber.json"
E3_GENERATOR = ROOT / "generate_u01v3_stage345_e3_f012.py"
G1_GENERATOR = ROOT / "generate_u01v3_f0123_track_g.py"

ROWS = 3
STRIPES = 8
TOTAL_Q_REGS = 32
Q0_RESERVED = 1
DATA_Q_REGS = TOTAL_Q_REGS - Q0_RESERVED
FIXED_STAGE12_VALUES = (
    "q0_modular_constant",
    "stage12_twiddle_t0",
    "stage12_twiddle_t1_mul",
    "stage12_twiddle_t1_quotient",
)


class ModelError(RuntimeError):
    pass


@dataclass(frozen=True)
class SemanticOp:
    name: str
    uses: tuple[str, ...] = ()
    defines: tuple[str, ...] = ()
    memory_effect: str | None = None


def qualify(stripe: int, name: str) -> str:
    if name.startswith("const_"):
        return name
    return f"s{stripe}_{name}"


def stripe_ops(stripe: int, *, make_out3: bool = True, store_out3: bool = True) -> list[SemanticOp]:
    q = lambda name: qualify(stripe, name)
    ops = [
        SemanticOp("load_B", defines=(q("B"),), memory_effect="load raw B"),
        SemanticOp("load_D", defines=(q("D"),), memory_effect="load raw D"),
        SemanticOp("t0_raw=B+D", uses=(q("B"), q("D")), defines=(q("t0_raw"),)),
        SemanticOp("t1_raw=B-D", uses=(q("B"), q("D")), defines=(q("t1_raw"),)),
        SemanticOp("t0_quotient", uses=(q("t0_raw"),), defines=(q("t0_quotient"),)),
        SemanticOp(
            "t0_reduced",
            uses=(q("t0_raw"), q("t0_quotient")),
            defines=(q("t0_reduced"),),
        ),
        SemanticOp("t1_quotient", uses=(q("t1_raw"),), defines=(q("t1_quotient"),)),
        SemanticOp("t1_scaled", uses=(q("t1_raw"),), defines=(q("t1_scaled"),)),
        SemanticOp(
            "t1_reduced",
            uses=(q("t1_scaled"), q("t1_quotient")),
            defines=(q("t1_reduced"),),
        ),
        SemanticOp("load_A", defines=(q("A"),), memory_effect="load raw A"),
        SemanticOp("load_C", defines=(q("C"),), memory_effect="load raw C"),
        SemanticOp("t3=A-C", uses=(q("A"), q("C")), defines=(q("t3"),)),
        SemanticOp("t2=A+C", uses=(q("A"), q("C")), defines=(q("t2"),)),
    ]
    if make_out3:
        ops.append(
            SemanticOp(
                "out3=t3-t1",
                uses=(q("t3"), q("t1_reduced")),
                defines=(q("Q3"),),
            )
        )
    ops.extend(
        [
            SemanticOp(
                "out2=t3+t1",
                uses=(q("t3"), q("t1_reduced")),
                defines=(q("Q2"),),
            ),
            SemanticOp(
                "out1=t2-t0",
                uses=(q("t2"), q("t0_reduced")),
                defines=(q("Q1"),),
            ),
            SemanticOp(
                "out0=t2+t0",
                uses=(q("t2"), q("t0_reduced")),
                defines=(q("Q0"),),
            ),
        ]
    )
    if store_out3:
        if not make_out3:
            raise ModelError("cannot store out3 when out3 is not produced")
        ops.append(
            SemanticOp(
                "store_out3_over_raw_D_slot",
                uses=(q("Q3"),),
                memory_effect="raw D scratch slot := Q3",
            )
        )
    return ops


def last_uses(ops: list[SemanticOp]) -> dict[str, int]:
    result: dict[str, int] = {}
    for index, op in enumerate(ops):
        for value in op.uses:
            result[value] = index
    return result


def semantic_peak(
    *,
    make_out3: bool,
    store_out3: bool,
    retained_suffixes: set[str],
) -> dict[str, object]:
    all_ops: list[SemanticOp] = []
    for stripe in range(STRIPES):
        all_ops.extend(stripe_ops(stripe, make_out3=make_out3, store_out3=store_out3))

    retained = {
        qualify(stripe, suffix)
        for stripe in range(STRIPES)
        for suffix in retained_suffixes
    }
    uses = last_uses(all_ops)
    live = set(FIXED_STAGE12_VALUES)
    peak = len(live)
    peak_op = "entry"

    for index, op in enumerate(all_ops):
        missing = [value for value in op.uses if value not in live]
        if missing:
            raise ModelError(f"{op.name}: semantic use before def: {missing}")
        after = set(live)
        for value in op.uses:
            if uses[value] == index and value not in retained:
                after.remove(value)
        for value in op.defines:
            if value in after:
                raise ModelError(f"{op.name}: duplicate semantic def: {value}")
            after.add(value)
        live = after
        if len(live) > peak:
            peak = len(live)
            peak_op = f"op{index}:{op.name}"

    retained_live = sorted(value for value in live if value not in FIXED_STAGE12_VALUES)
    return {
        "max_simultaneous_q_live_under_e3_order": peak,
        "peak_site": peak_op,
        "stage12_exit_live_with_twiddles": len(live),
        "stage12_exit_data_or_basis_values": len(retained_live),
        "post_twiddle_release_lower_bound_with_q0": len(retained_live) + Q0_RESERVED,
        "retained_semantic_values": retained_live,
    }


def semantic_contract() -> dict[str, object]:
    ops = stripe_ops(0)
    uses = last_uses(ops)
    by_name = {op.name: index for index, op in enumerate(ops)}
    source_names = ("A", "B", "C", "D")
    source_last_use = {}
    for source in source_names:
        value = qualify(0, source)
        last = uses[value]
        source_last_use[source] = {
            "semantic_op_index": last,
            "operation": ops[last].name,
        }

    return {
        "per_stripe_ops": [
            {
                "index": index,
                "name": op.name,
                "uses": list(op.uses),
                "defines": list(op.defines),
                "memory_effect": op.memory_effect,
            }
            for index, op in enumerate(ops)
        ],
        "source_last_use": source_last_use,
        "out3_dependency_cone": {
            "raw": ["A", "B", "C", "D"],
            "direct_intermediates": ["t3=A-C", "t1_reduced=reduce_twist(B-D)"],
            "equations": [
                "Q16+s = out2 = t3 + t1_reduced",
                "Q24+s = out3 = t3 - t1_reduced",
                "out3 = out2 - 2*t1_reduced",
                "out3 = 2*t3 - out2",
            ],
            "minimum_extra_rank_with_Q16_Q23_already_live": 1,
            "minimum_extra_vectors_for_eight_stripes": STRIPES,
        },
        "current_overwrite_is_after_source_last_use": (
            by_name["store_out3_over_raw_D_slot"] > source_last_use["D"]["semantic_op_index"]
        ),
        "first_current_semantic_loss": {
            "register_value": "D",
            "replacement": "t3=A-C",
            "safe_because": "D's final current consumer is t1_raw=B-D, earlier in the DAG",
        },
        "first_persistent_memory_loss": {
            "value": "raw D scratch image",
            "replacement": "Q24+s/out3",
            "operation": "store_out3_over_raw_D_slot",
        },
    }


STAGE12_MARKER_RE = re.compile(
    r"Stage12 row(?P<row>[0-2]) stripe(?P<stripe>[0-7]):.*Q(?P<out3>2[4-9]|3[01]) stored\."
)
OUT3_STORE_RE = re.compile(
    r"str q(?P<reg>\d+), \[x21, #(?P<offset>\d+)\]\s+// block3 Q(?P<q>2[4-9]|3[01])"
)


def validate_current_artifacts() -> dict[str, object]:
    required = (G1_ASM, G1_MAP, E3_MAP, E4_FEASIBILITY, E3_GENERATOR, G1_GENERATOR)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise ModelError(f"missing source artifacts: {missing}")

    g1_map = json.loads(G1_MAP.read_text())
    e3_map = json.loads(E3_MAP.read_text())
    e4 = json.loads(E4_FEASIBILITY.read_text())
    asm_lines = G1_ASM.read_text().splitlines()

    sites: list[dict[str, object]] = []
    markers = [
        (index, STAGE12_MARKER_RE.search(line))
        for index, line in enumerate(asm_lines)
        if STAGE12_MARKER_RE.search(line)
    ]
    if len(markers) != ROWS * STRIPES:
        raise ModelError(f"expected 24 G1 Stage12 markers, found {len(markers)}")

    semantic_markers = (
        "// D / later t3 / out3",
        "// t1 raw = B - D",
        "// t3 = A - C",
        "// out3 = t3 - t1",
        "// block3 Q",
    )
    for marker_number, (start, match) in enumerate(markers):
        assert match is not None
        end = markers[marker_number + 1][0] if marker_number + 1 < len(markers) else len(asm_lines)
        for probe in range(start + 1, min(end, start + 40)):
            if "Stage345 block" in asm_lines[probe]:
                end = probe
                break
        block = asm_lines[start:end]
        positions = []
        for semantic_marker in semantic_markers:
            hits = [i for i, line in enumerate(block) if semantic_marker in line]
            if len(hits) != 1:
                raise ModelError(
                    f"row{match['row']} stripe{match['stripe']}: marker {semantic_marker!r} hits={hits}"
                )
            positions.append(hits[0])
        if positions != sorted(positions):
            raise ModelError(
                f"row{match['row']} stripe{match['stripe']}: semantic sequence changed: {positions}"
            )
        store_matches = [OUT3_STORE_RE.search(line) for line in block]
        store_matches = [store for store in store_matches if store]
        if len(store_matches) != 1:
            raise ModelError(
                f"row{match['row']} stripe{match['stripe']}: expected one concrete out3 store"
            )
        store = store_matches[0]
        row = int(match["row"])
        stripe = int(match["stripe"])
        q_index = 24 + stripe
        offset = row * 512 + q_index * 16
        if int(match["out3"]) != q_index or int(store["q"]) != q_index or int(store["offset"]) != offset:
            raise ModelError(
                f"row{row} stripe{stripe}: out3 scratch contract mismatch"
            )
        sites.append(
            {
                "row": row,
                "stripe": stripe,
                "semantic_source_overwritten": f"row{row}.raw_D[{stripe}]",
                "semantic_output_written": f"row{row}.Q{q_index}",
                "scratch_offset": offset,
                "asm_store_register_evidence": f"q{store['reg']}",
                "asm_marker_line": start + 1,
                "asm_store_line": start + positions[-1] + 1,
                "source_last_use": "t1_raw=B-D",
                "overwrite_after_source_last_use": True,
            }
        )

    stage12_reports = g1_map["stage12_reports"]
    if len(stage12_reports) != ROWS or any(len(row["stripes"]) != STRIPES for row in stage12_reports):
        raise ModelError("G1 map does not contain three rows of eight Stage12 stripes")
    if any(row["max_live_outputs"] != 24 for row in stage12_reports):
        raise ModelError("G1 map no longer reports 24 F012 live outputs")
    if g1_map["block3_stage345_q_loads_retained"] != ROWS * STRIPES:
        raise ModelError("G1 retained block3 load count changed")

    e3_b0 = e3_map["block0_allocator"]
    e3_b1 = e3_map["block1_allocator"]
    return {
        "validated": True,
        "inputs": [str(path.relative_to(NTRU_ROOT)) for path in required],
        "g1": {
            "stage12_rows": len(stage12_reports),
            "stage12_stripes_per_row": STRIPES,
            "f012_live_outputs_per_row": stage12_reports[0]["max_live_outputs"],
            "out3_overwrite_sites": len(sites),
            "block3_q_loads_retained": g1_map["block3_stage345_q_loads_retained"],
            "raw_q_reloads": g1_map["raw_q_reloads"],
            "duplicate_stage12": g1_map["duplicate_stage12"],
        },
        "e3_allocator": {
            "block0_same_as_interference_count": e3_b0["same_as_interference_count"],
            "block0_allocator_interference_count": e3_b0["interference_count"],
            "block0_max_live": e3_b0["max_live"],
            "block1_same_as_interference_count": e3_b1["same_as_interference_count"],
            "block1_allocator_interference_count": e3_b1["interference_count"],
            "block1_max_live": e3_b1["max_live"],
        },
        "e4_live_all_blocker": e4["blocker"],
        "out3_overwrite_sites": sites,
    }


def gate(
    *,
    raw_q_reloads: int,
    prefix_stores: int,
    prefix_loads: int,
    duplicate_full_stage12: bool,
    max_q_live: int,
    same_as_feasible: bool,
    allocator_feasible: bool,
    first_consume_feasible: bool,
    source_last_use_safe: bool,
    block3_scratch_loads_removed: int,
) -> dict[str, object]:
    checks = {
        "raw_q_reloads_zero": raw_q_reloads == 0,
        "new_prefix_stores_zero": prefix_stores == 0,
        "new_prefix_loads_zero": prefix_loads == 0,
        "duplicate_full_stage12_false": not duplicate_full_stage12,
        "max_q_live_lte_32": max_q_live <= TOTAL_Q_REGS,
        "same_as_feasible": same_as_feasible,
        "allocator_feasible": allocator_feasible,
        "first_consume_feasible": first_consume_feasible,
        "source_last_use_safe": source_last_use_safe,
        "removes_block3_scratch_consumption": block3_scratch_loads_removed == ROWS * STRIPES,
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "failed": [name for name, passed in checks.items() if not passed],
    }


def build_candidates() -> dict[str, object]:
    baseline = semantic_peak(
        make_out3=True,
        store_out3=True,
        retained_suffixes={"Q0", "Q1", "Q2"},
    )
    h1a_live = semantic_peak(
        make_out3=True,
        store_out3=False,
        retained_suffixes={"Q0", "Q1", "Q2", "Q3"},
    )
    h1b_min_basis = semantic_peak(
        make_out3=False,
        store_out3=False,
        retained_suffixes={"Q0", "Q1", "Q2", "t1_reduced"},
    )
    h1b_full_basis = semantic_peak(
        make_out3=False,
        store_out3=False,
        retained_suffixes={"Q0", "Q1", "Q2", "t1_reduced", "t3"},
    )
    h1c_raw_d_live = semantic_peak(
        make_out3=False,
        store_out3=False,
        retained_suffixes={"Q0", "Q1", "Q2", "D"},
    )

    total_block3_values = ROWS * STRIPES
    raw_abcd_reloads = ROWS * STRIPES * 4

    h1a_gate = gate(
        raw_q_reloads=0,
        prefix_stores=0,
        prefix_loads=0,
        duplicate_full_stage12=False,
        max_q_live=int(h1a_live["max_simultaneous_q_live_under_e3_order"]),
        same_as_feasible=True,
        allocator_feasible=False,
        first_consume_feasible=False,
        source_last_use_safe=True,
        block3_scratch_loads_removed=total_block3_values,
    )
    h1b_gate = gate(
        raw_q_reloads=0,
        prefix_stores=0,
        prefix_loads=0,
        duplicate_full_stage12=False,
        max_q_live=int(h1b_min_basis["max_simultaneous_q_live_under_e3_order"]),
        same_as_feasible=True,
        allocator_feasible=False,
        first_consume_feasible=False,
        source_last_use_safe=True,
        block3_scratch_loads_removed=total_block3_values,
    )
    h1c_gate = gate(
        raw_q_reloads=0,
        prefix_stores=0,
        prefix_loads=0,
        duplicate_full_stage12=False,
        max_q_live=int(baseline["max_simultaneous_q_live_under_e3_order"]),
        same_as_feasible=True,
        allocator_feasible=True,
        first_consume_feasible=True,
        source_last_use_safe=True,
        block3_scratch_loads_removed=0,
    )

    return {
        "baseline_G1": {
            "shape": "F012 live; out3 stored over raw D scratch; block3 later reloads out3",
            "semantic_liveness": baseline,
            "new_memory_ops_vs_G1": {"q_loads": 0, "q_stores": 0},
            "block3_q_loads_retained": total_block3_values,
        },
        "H1a_last_destructive_out3_write_delay": {
            "status": "hard_gate_fail",
            "semantic_shape": "Compute out3 at the current point but delay/elide its store, retaining Q24..Q31 through Stage345 blocks0..2.",
            "overwritten_sources": ["raw D scratch slot for each row/stripe; overwrite would be delayed"],
            "source_last_use": "raw D is already dead after t1_raw=B-D; the delay only creates a future reconstruction lifetime",
            "semantic_liveness": h1a_live,
            "best_case_assumption": "The delayed store is ultimately elided and out3 is handed directly to block3. Merely moving the store would retain G1's memory boundary.",
            "new_memory_ops_vs_G1": {"q_loads": -total_block3_values, "q_stores": -total_block3_values},
            "duplicate_stage12": False,
            "raw_q_reloads": 0,
            "metrics": {
                "max_simultaneous_q_live": h1a_live["max_simultaneous_q_live_under_e3_order"],
                "new_q_loads_vs_G1": -total_block3_values,
                "new_q_stores_vs_G1": -total_block3_values,
                "duplicate_stage12": False,
                "raw_q_reloads": 0,
            },
            "feasibility": {
                "same_as": "pass/inherited",
                "allocator": "fail",
                "first_consume": "fail/not assignable",
            },
            "same_as_feasibility": "inherited E3 Stage345 arithmetic is unchanged, but coloring is not reached",
            "allocator_feasibility": "fail: 32 data outputs plus reserved q0 already require 33 q registers; E4 cardinality blocker recurs",
            "first_consume_feasibility": "fail/not assignable: no complete cross-block handoff coloring exists",
            "hard_gate": h1a_gate,
        },
        "H1b_full_out3_producer_after_block2": {
            "status": "hard_gate_fail",
            "semantic_shape": "Do not form out3 early; retain enough semantic state across blocks0..2, then form Q24..Q31 and hand off directly.",
            "overwritten_sources": ["no raw D scratch overwrite before block2 in the delayed-producer shape"],
            "source_last_use": "moving the producer extends one independent block3 basis value per stripe past block2",
            "minimum_no_memory_basis": {
                "retained": "one of t1_reduced or t3 per stripe, because Q16..Q23/out2 is already live",
                "vectors_per_row": STRIPES,
                "reconstruction": "out3=out2-2*t1_reduced or out3=2*t3-out2",
            },
            "semantic_liveness_minimum_basis": h1b_min_basis,
            "semantic_liveness_full_t1_t3_basis": h1b_full_basis,
            "new_memory_ops_vs_G1": {"q_loads": -total_block3_values, "q_stores": -total_block3_values},
            "duplicate_stage12": False,
            "raw_q_reloads": 0,
            "metrics": {
                "max_simultaneous_q_live": h1b_min_basis["max_simultaneous_q_live_under_e3_order"],
                "new_q_loads_vs_G1": -total_block3_values,
                "new_q_stores_vs_G1": -total_block3_values,
                "duplicate_stage12": False,
                "raw_q_reloads": 0,
            },
            "feasibility": {
                "same_as": "pass/inherited",
                "allocator": "fail",
                "first_consume": "fail/not assignable",
            },
            "same_as_feasibility": "same_as can remain inherited, but the live-state cardinality fails before coloring",
            "allocator_feasibility": "fail: the minimum eight-vector basis plus F012 gives 32 data values while q0 remains reserved",
            "first_consume_feasibility": "fail/not assignable under no-spill/no-reload rules",
            "fallback_recompute_after_block2": {
                "raw_q_reloads": raw_abcd_reloads,
                "duplicate_stage12": "24 partial out3 dependency cones; not a duplicate full Stage12",
                "new_memory_ops_vs_G1": {"q_loads": raw_abcd_reloads - total_block3_values, "q_stores": -total_block3_values},
                "allocator_feasibility": "locally feasible after block2",
                "same_as_feasibility": "feasible; no Stage345 semantic change required",
                "first_consume_feasibility": "feasible with direct block3 destination contract",
                "hard_gate_status": "fail: raw q reloads return to the rejected G3a/G3c shape",
            },
            "hard_gate": h1b_gate,
        },
        "H1c_raw_D_preserving_destination_layout": {
            "status": "hard_gate_fail",
            "semantic_shape": "Preserve raw D either in registers or in a separate scratch destination while producing out3.",
            "overwritten_sources": ["raw D is preserved; out3 must use another register or memory slot"],
            "source_last_use": "D has no current consumer after t1_raw=B-D; preserving it is useful only if a new delayed consumer is added",
            "register_resident_variant": {
                "semantic_liveness": h1c_raw_d_live,
                "new_memory_ops_vs_G1": {"q_loads": -total_block3_values, "q_stores": -total_block3_values},
                "duplicate_stage12": False,
                "raw_q_reloads": 0,
                "allocator_feasibility": "fail: eight retained D basis vectors plus F012 reproduce the 32-data-value cardinality blocker",
            },
            "alternate_scratch_variant": {
                "semantic_liveness": baseline,
                "new_memory_ops_vs_G1": {"q_loads": 0, "q_stores": 0},
                "duplicate_stage12": False,
                "raw_q_reloads": 0,
                "block3_q_loads_retained": total_block3_values,
                "extra_scratch_footprint_bytes_if_no_existing_alias_safe_space": total_block3_values * 16,
                "allocator_feasibility": "pass: register pressure stays G1-like",
                "objective_feasibility": "fail: it merely relocates the same 24 out3 stores and 24 block3 loads",
            },
            "same_as_feasibility": "pass for the scratch-relocation form; register-resident form is blocked before coloring",
            "allocator_feasibility": "only the no-win scratch-relocation form is allocatable",
            "first_consume_feasibility": "pass via the existing scratch load; direct handoff remains infeasible",
            "metrics": {
                "selected_gate_mode": "alternate_scratch",
                "max_simultaneous_q_live": baseline["max_simultaneous_q_live_under_e3_order"],
                "new_q_loads_vs_G1": 0,
                "new_q_stores_vs_G1": 0,
                "duplicate_stage12": False,
                "raw_q_reloads": 0,
                "block3_q_loads_removed": 0,
            },
            "feasibility": {
                "same_as": "pass/inherited",
                "allocator": "pass for alternate scratch; fail for register-resident",
                "first_consume": "pass through scratch; direct handoff unavailable",
            },
            "hard_gate": h1c_gate,
        },
    }


def build_model() -> dict[str, object]:
    evidence = validate_current_artifacts()
    contract = semantic_contract()
    candidates = build_candidates()
    passing = [name for name, item in candidates.items() if item.get("hard_gate", {}).get("status") == "pass"]
    return {
        "artifact": "u01v3_track_h_h1_model",
        "scope": "model-only H1 delayed out3 overwrite",
        "production_default_changed": False,
        "physical_asm_emitted": False,
        "slothy_run": False,
        "semantic_not_physical_reasoning": True,
        "source_evidence": evidence,
        "semantic_contract": contract,
        "register_budget": {
            "total_q_regs": TOTAL_Q_REGS,
            "q0_reserved": True,
            "data_q_regs": DATA_Q_REGS,
            "e3_f012_outputs": 24,
            "free_data_regs_after_e3_outputs": DATA_Q_REGS - 24,
            "minimum_extra_block3_rank_vectors": STRIPES,
            "minimum_data_values_for_no_memory_H1": 24 + STRIPES,
            "global_data_deficit": 24 + STRIPES - DATA_Q_REGS,
        },
        "candidates": candidates,
        "decision": {
            "passing_h1_candidates": passing,
            "emit_h1_asm": False,
            "key_fact": "The current out3 store overwrites raw D only after D's semantic last-use. H1 must create a new future lifetime; it cannot recover a free lifetime that already existed.",
            "reason": "Every direct no-memory H1 form needs one additional independent vector per stripe. F012 already retains 24 values, so the minimum is 32 data vectors while q0 leaves only 31 data-capable registers. The only allocatable H1c form retains the same 24-store/24-load block3 scratch boundary and therefore does not meet Track H's objective.",
            "next_scope": "H1 has no physical candidate. A producer/consumer interleave (Track H2) or a smaller algebraic state with a different lifetime (Track H3) is required to avoid the G1 boundary.",
        },
    }


def write_md(model: dict[str, object]) -> None:
    evidence = model["source_evidence"]
    contract = model["semantic_contract"]
    candidates = model["candidates"]
    budget = model["register_budget"]
    lines = [
        "# U01v3 Track H1 Delayed-out3-overwrite Model",
        "",
        "Status: model-only; no H1 ASM emitted. Production is unchanged and Slothy was not run.",
        "",
        "## Verified Current Contract",
        "",
        "The model validated the concrete G1 assembly, G1 map, E3 allocator map, and E4 feasibility report. It found exactly 24 row/stripe sites where `Q24..Q31` is stored into the same scratch slot that previously held raw `D`.",
        "",
        "Per stripe, the semantic chain is:",
        "",
        "```text",
        "t0 = reduce(B + D)",
        "t1 = reduce_twist(B - D)",
        "t2 = A + C",
        "t3 = A - C",
        "out0 = t2 + t0",
        "out1 = t2 - t0",
        "out2 = t3 + t1",
        "out3 = t3 - t1",
        "```",
        "",
        f"Raw `D`'s last current semantic use is `{contract['source_last_use']['D']['operation']}`. The persistent scratch overwrite happens later, so the current code is not clobbering a still-live source. The Track H lifetime appears only if we add a future delayed block3 consumer.",
        "",
        "## Register Lower Bound",
        "",
        "```text",
        f"q registers total:                         {budget['total_q_regs']}",
        f"q0 reserved for modular constants:         {budget['q0_reserved']}",
        f"data-capable q registers:                  {budget['data_q_regs']}",
        f"E3 F012 retained outputs:                  {budget['e3_f012_outputs']}",
        f"minimum extra block3 rank values:          {budget['minimum_extra_block3_rank_vectors']}",
        f"minimum no-memory H1 data values:           {budget['minimum_data_values_for_no_memory_H1']}",
        f"data-register deficit:                     {budget['global_data_deficit']}",
        "```",
        "",
        "Knowing `out2` still leaves one independent vector per stripe to recover `out3`: retain either `t1` (`out3 = out2 - 2*t1`) or `t3` (`out3 = 2*t3 - out2`). Across eight stripes that is eight extra vectors. Therefore every direct H1 form recreates the E4 32-data-vector versus 31-register blocker.",
        "",
        "## Candidate Results",
        "",
        "```text",
        f"H1a delay final out3 write:     {candidates['H1a_last_destructive_out3_write_delay']['hard_gate']['status']}",
        f"  max live under E3 order:      {candidates['H1a_last_destructive_out3_write_delay']['semantic_liveness']['max_simultaneous_q_live_under_e3_order']}",
        "  reason: retain Q24..Q31 across block0..2; allocator cardinality fails",
        f"H1b move out3 producer:         {candidates['H1b_full_out3_producer_after_block2']['hard_gate']['status']}",
        f"  min-basis max live:           {candidates['H1b_full_out3_producer_after_block2']['semantic_liveness_minimum_basis']['max_simultaneous_q_live_under_e3_order']}",
        "  reason: one retained basis vector per stripe still gives 32 data values",
        "  recompute fallback:           96 raw q reloads; rejected G3 shape",
        f"H1c preserve raw D layout:      {candidates['H1c_raw_D_preserving_destination_layout']['hard_gate']['status']}",
        "  register form:                same cardinality failure",
        "  alternate-scratch form:       allocatable, but retains all 24 block3 q loads",
        "```",
        "",
        "All candidates preserve the existing Stage345 arithmetic, so destructive `same_as` constraints are not the primary blocker. H1a/H1b and register-resident H1c fail before allocator/first-consume assignment. Scratch-resident H1c is safe but produces no Track H load-boundary win.",
        "",
        "## Decision",
        "",
        "```text",
        "emit_h1_asm: false",
        "passing_h1_candidates: none",
        "```",
        "",
        model["decision"]["reason"],
        "",
        "The useful next design space is Track H2 producer/consumer interleaving or Track H3 minimal state with a shorter lifetime. H1 cannot solve the boundary by delaying only the current out3 overwrite.",
        "",
        "## Evidence Summary",
        "",
        "```text",
        f"validated overwrite sites: {evidence['g1']['out3_overwrite_sites']}",
        f"G1 retained block3 loads:  {evidence['g1']['block3_q_loads_retained']}",
        f"E3 block0 same_as/interference: {evidence['e3_allocator']['block0_same_as_interference_count']}/{evidence['e3_allocator']['block0_allocator_interference_count']}",
        f"E3 block1 same_as/interference: {evidence['e3_allocator']['block1_same_as_interference_count']}/{evidence['e3_allocator']['block1_allocator_interference_count']}",
        "```",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n")


def main() -> int:
    model = build_model()
    OUT_JSON.write_text(json.dumps(model, indent=2) + "\n")
    write_md(model)
    print(OUT_JSON)
    print(OUT_MD)
    print(f"emit_h1_asm={model['decision']['emit_h1_asm']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
