#!/usr/bin/env python3
"""Model-only U01v3 F01 producer-granularity tradeoff.

This is a Track G first-wave artifact.  It does not emit assembly.  The model
compares producer-granularity shapes for the F01 block0+block1 boundary using
the shared semantic IR plus the existing liveness/clobber lower bound.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHARED_IR = ROOT / "u01v3_f01_shared_semantic_ir.json"
LIVENESS = ROOT / "u01v3_f01_liveness_clobber.json"
OUT_JSON = ROOT / "u01v3_f01_granularity_candidates.json"
OUT_MD = ROOT / "u01v3_f01_granularity_tradeoff.md"

ROWS = 3
STRIPES_PER_ROW = 8
BLOCK1_SCRATCH_STORES_PER_ROW = 8
BLOCK1_SCRATCH_LOADS_PER_ROW = 8
Q11_HANDOFF_MOVES_TOTAL = ROWS


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    name: str
    description: str
    raw_q_reloads: int
    duplicate_stage12: bool
    extra_arithmetic_total: int
    extra_loads_total: int
    extra_stores_total: int
    removed_scratch_loads_total: int
    removed_scratch_stores_total: int
    extra_vector_moves_total: int
    removed_vector_moves_total: int
    max_live_vector_regs_at_block0_boundary: int
    removed_scratch_ops_total: int
    estimated_net_instruction_delta: int
    primary_memory_preservation_vectors_per_row: int
    plausible_win: bool
    status: str
    reason: str


def load_inputs() -> tuple[dict[str, object], dict[str, object]]:
    return json.loads(SHARED_IR.read_text()), json.loads(LIVENESS.read_text())


def block1_scratch_ops_total() -> int:
    return ROWS * (BLOCK1_SCRATCH_LOADS_PER_ROW + BLOCK1_SCRATCH_STORES_PER_ROW)


def prefix_checkpoint_candidate() -> Candidate:
    """Delayed block1 without raw reloads.

    The final out1 value is `prefix_a - prefix_b` for each stripe.  Once
    Stage345 block0 has run, the raw inputs are not allowed to be reloaded and
    block0 has clobbered the useful vector register set.  Avoiding raw reloads
    therefore requires checkpointing two vector intermediates per stripe before
    block0, then loading them after block0 and doing the final subtract.
    """

    prefix_stores = ROWS * STRIPES_PER_ROW * 2
    prefix_loads = ROWS * STRIPES_PER_ROW * 2
    delayed_subs = ROWS * STRIPES_PER_ROW
    removed_stores = ROWS * BLOCK1_SCRATCH_STORES_PER_ROW
    removed_loads = ROWS * BLOCK1_SCRATCH_LOADS_PER_ROW
    net = (
        delayed_subs
        + prefix_stores
        + prefix_loads
        - removed_stores
        - removed_loads
        - Q11_HANDOFF_MOVES_TOTAL
    )
    return Candidate(
        candidate_id="G0b",
        name="delayed_block1_prefix_checkpoint",
        description=(
            "Produce block0, checkpoint two out1-producing prefixes per stripe, "
            "run Stage345 block0, then form block1 directly in Stage345 block1 "
            "consumer registers."
        ),
        raw_q_reloads=0,
        duplicate_stage12=False,
        extra_arithmetic_total=delayed_subs,
        extra_loads_total=prefix_loads,
        extra_stores_total=prefix_stores,
        removed_scratch_loads_total=removed_loads,
        removed_scratch_stores_total=removed_stores,
        extra_vector_moves_total=0,
        removed_vector_moves_total=Q11_HANDOFF_MOVES_TOTAL,
        max_live_vector_regs_at_block0_boundary=8,
        removed_scratch_ops_total=removed_loads + removed_stores,
        estimated_net_instruction_delta=net,
        primary_memory_preservation_vectors_per_row=16,
        plausible_win=False,
        status="stop",
        reason=(
            "No raw q reloads, but the replacement is two prefix stores plus "
            "two prefix loads per stripe.  Net instruction estimate is positive "
            "and memory checkpointing becomes the primary mechanism."
        ),
    )


def current_shared_prefix_candidate() -> Candidate:
    return Candidate(
        candidate_id="G0a",
        name="current_shared_prefix",
        description=(
            "Existing F0-like shared-prefix shape: block0 is register-handoff "
            "fused, while block1 remains behind the row-scratch boundary."
        ),
        raw_q_reloads=0,
        duplicate_stage12=False,
        extra_arithmetic_total=0,
        extra_loads_total=0,
        extra_stores_total=0,
        removed_scratch_loads_total=0,
        removed_scratch_stores_total=0,
        extra_vector_moves_total=0,
        removed_vector_moves_total=0,
        max_live_vector_regs_at_block0_boundary=8,
        removed_scratch_ops_total=0,
        estimated_net_instruction_delta=0,
        primary_memory_preservation_vectors_per_row=0,
        plausible_win=False,
        status="baseline",
        reason=(
            "This is the comparison baseline.  It is already correctness-safe "
            "and measured at the F0 envelope, but it does not remove block1 "
            "scratch traffic."
        ),
    )


def partial_shared_prefix_candidate(liveness: dict[str, object]) -> Candidate:
    summary = liveness["summary"]
    clobbered = int(summary["block1_liveins_clobbered_per_row"])
    parking = int(summary["usable_vector_parking_regs_per_row"])
    preserved_in_place = int(summary["block1_liveins_preserved_in_original_regs_per_row"])
    memory_preserved = clobbered - parking
    memory_stores = ROWS * memory_preserved
    memory_loads = ROWS * memory_preserved
    parking_moves = ROWS * parking * 2
    removed_stores = ROWS * BLOCK1_SCRATCH_STORES_PER_ROW
    removed_loads = ROWS * BLOCK1_SCRATCH_LOADS_PER_ROW
    net = (
        memory_stores
        + memory_loads
        + parking_moves
        - removed_stores
        - removed_loads
        - Q11_HANDOFF_MOVES_TOTAL
    )
    return Candidate(
        candidate_id="G0c",
        name="partial_shared_prefix_q9_q21",
        description=(
            "Use q9 plus q21 as the only no-rewrite block0 survivors, and "
            "preserve the remaining block1 live-ins through memory."
        ),
        raw_q_reloads=0,
        duplicate_stage12=False,
        extra_arithmetic_total=0,
        extra_loads_total=memory_loads,
        extra_stores_total=memory_stores,
        removed_scratch_loads_total=removed_loads,
        removed_scratch_stores_total=removed_stores,
        extra_vector_moves_total=parking_moves,
        removed_vector_moves_total=Q11_HANDOFF_MOVES_TOTAL,
        max_live_vector_regs_at_block0_boundary=8 + preserved_in_place + parking,
        removed_scratch_ops_total=removed_loads + removed_stores,
        estimated_net_instruction_delta=net,
        primary_memory_preservation_vectors_per_row=memory_preserved,
        plausible_win=False,
        status="stop",
        reason=(
            "The theoretical best case is only a small negative instruction "
            "delta, requires a new producer liveness contract for q9/q21, and "
            "still relies on six memory-preserved vectors per row.  That is too "
            "weak after the measured B8/Bmin result matched F0."
        ),
    )


def recompute_small_prefix_candidate() -> Candidate:
    base = prefix_checkpoint_candidate()
    return Candidate(
        candidate_id="G0d",
        name="recompute_small_prefix",
        description=(
            "After Stage345 block0, recompute only the small prefix needed for "
            "block1.  Under the no-raw-q-reload rule, this collapses to the "
            "same two-vector prefix checkpoint as G0b; allowing raw reloads "
            "would duplicate Stage12 input loads and is disallowed."
        ),
        raw_q_reloads=0,
        duplicate_stage12=False,
        extra_arithmetic_total=base.extra_arithmetic_total,
        extra_loads_total=base.extra_loads_total,
        extra_stores_total=base.extra_stores_total,
        removed_scratch_loads_total=base.removed_scratch_loads_total,
        removed_scratch_stores_total=base.removed_scratch_stores_total,
        extra_vector_moves_total=base.extra_vector_moves_total,
        removed_vector_moves_total=base.removed_vector_moves_total,
        max_live_vector_regs_at_block0_boundary=base.max_live_vector_regs_at_block0_boundary,
        removed_scratch_ops_total=base.removed_scratch_ops_total,
        estimated_net_instruction_delta=base.estimated_net_instruction_delta,
        primary_memory_preservation_vectors_per_row=base.primary_memory_preservation_vectors_per_row,
        plausible_win=False,
        status="stop",
        reason=(
            "With raw q reloads forbidden, recomputation needs saved prefixes "
            "and has the same cost as G0b.  With raw q reloads allowed, it would "
            "violate Track G's G1 rule and repeat the known negative two-pass "
            "shape."
        ),
    )


def build_model() -> dict[str, object]:
    shared, liveness = load_inputs()
    candidates = [
        current_shared_prefix_candidate(),
        prefix_checkpoint_candidate(),
        partial_shared_prefix_candidate(liveness),
        recompute_small_prefix_candidate(),
    ]
    plausible = [c for c in candidates if c.plausible_win]
    return {
        "candidate_family": "u01v3_f01_granularity_tradeoff",
        "date": "2026-07-09",
        "production_default_changed": False,
        "scope": "F01 block0+block1 only",
        "inputs": {
            "shared_ir": SHARED_IR.name,
            "liveness": LIVENESS.name,
            "shared_candidate_family": shared.get("candidate_family"),
        },
        "constraints": {
            "no_s2_s4_mix": True,
            "no_twiddle1_lazy_reduction_touch": True,
            "no_slothy_first_wave": True,
            "no_raw_q_reloads_in_g1": True,
            "no_stack_spill_as_primary_mechanism": True,
            "do_not_combine_with_track_e": True,
        },
        "model_units": {
            "rows": ROWS,
            "stripes_per_row": STRIPES_PER_ROW,
            "instruction_delta_baseline": "G0a current_shared_prefix",
            "removed_scratch_ops_are_block1_boundary_ops_relative_to_G0a": True,
            "q11_handoff_moves_removed_when_block1_is_formed_directly": Q11_HANDOFF_MOVES_TOTAL,
            "block1_scratch_ops_total_in_G0a": block1_scratch_ops_total(),
        },
        "candidates": [asdict(candidate) for candidate in candidates],
        "decision": {
            "g0_status": "negative",
            "g1_status": "not_emitted",
            "plausible_candidates": [c.candidate_id for c in plausible],
            "stop_reason": (
                "No modeled Track G candidate clears the plausibility bar under "
                "the first-wave constraints.  The only negative-delta option is "
                "a six-vector memory-preservation variant with a small estimated "
                "gain and a dependency on a new q9/q21 producer liveness "
                "contract; the delayed/recompute shapes are clearly positive "
                "instruction deltas."
            ),
        },
    }


def write_markdown(model: dict[str, object]) -> None:
    candidates = model["candidates"]
    decision = model["decision"]
    lines: list[str] = [
        "# U01v3 F01 Granularity Tradeoff",
        "",
        "Date: 2026-07-09",
        "",
        "Status: Track G model-only result.  Production default is unchanged.",
        "No S2/S4 mixing, no twiddle1 lazy-reduction change, no Slothy, and no",
        "Track E combination are used here.",
        "",
        "## Scope",
        "",
        "Only the F01 block0+block1 boundary is modeled:",
        "",
        "```text",
        "Stage12 block0 Q0..Q7",
        "Stage12 block1 Q8..Q15",
        "Stage345 block0 final scatter",
        "Stage345 block1 final scatter",
        "```",
        "",
        "The instruction deltas below are relative to G0a, the current",
        "F0-like shared-prefix shape where block0 is fused and block1 remains",
        "behind the row-scratch boundary.",
        "",
        "## Candidate Matrix",
        "",
        "| id | candidate | extra arithmetic | extra loads | extra stores | max live vector regs | removed scratch ops | net instruction delta | status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for c in candidates:
        lines.append(
            "| {candidate_id} | {name} | {extra_arithmetic_total} | "
            "{extra_loads_total} | {extra_stores_total} | "
            "{max_live_vector_regs_at_block0_boundary} | "
            "{removed_scratch_ops_total} | {estimated_net_instruction_delta:+d} | "
            "{status} |".format(**c)
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    for c in candidates:
        lines.extend(
            [
                f"### {c['candidate_id']} {c['name']}",
                "",
                c["description"],
                "",
                f"Reason: {c['reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Stop Decision",
            "",
            f"G0 status: `{decision['g0_status']}`.",
            f"G1 status: `{decision['g1_status']}`.",
            "",
            decision["stop_reason"],
            "",
            "No G1 delayed-block1 assembly or test artifact was emitted, because",
            "the model does not show a plausible first-wave Track G win.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines))


def main() -> int:
    model = build_model()
    OUT_JSON.write_text(json.dumps(model, indent=2) + "\n")
    write_markdown(model)
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"G0 status: {model['decision']['g0_status']}")
    print(f"G1 status: {model['decision']['g1_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
