#!/usr/bin/env python3
"""Conservative range model for caller-specific loose Forward NTT contracts.

This is an audit helper only.  It intentionally refuses to mark a candidate
safe unless both the producer bound and the downstream consumer precondition are
known from the current code or from an explicit proof note.
"""

from __future__ import annotations

from dataclasses import dataclass

Q = 3457
CENTER = Q // 2
INT16_MIN = -32768
INT16_MAX = 32767


@dataclass(frozen=True)
class Bound:
    lo: int
    hi: int
    proof: str

    @property
    def absmax(self) -> int:
        return max(abs(self.lo), abs(self.hi))

    def within(self, other: "Bound") -> bool:
        return self.lo >= other.lo and self.hi <= other.hi

    def text(self) -> str:
        return f"[{self.lo}, {self.hi}]"


@dataclass(frozen=True)
class Consumer:
    name: str
    machine_bound: Bound
    semantic_bound: Bound | None
    note: str


@dataclass(frozen=True)
class ProducerVariant:
    name: str
    removed_reductions: str
    output_bound: Bound
    expected_instr_reduction: str
    cycle_estimate: str
    note: str


PRODUCERS = [
    ProducerVariant(
        name="baseline_full_reduction",
        removed_reductions="none",
        output_bound=Bound(-CENTER, CENTER, "current production final store"),
        expected_instr_reduction="0",
        cycle_estimate="0",
        note="Known production contract.  This is the reference, not a loose candidate.",
    ),
    ProducerVariant(
        name="representative_contract_only",
        removed_reductions="none; consumer accepts current reduced residues",
        output_bound=Bound(-CENTER, CENTER, "same bytes/register values as production"),
        expected_instr_reduction="0",
        cycle_estimate="0",
        note="Only changes caller contract wording.  No implementation win.",
    ),
    ProducerVariant(
        name="reduced_non_centered",
        removed_reductions="hypothetical final centering only",
        output_bound=Bound(-(Q - 1), Q - 1, "generic reduced residue envelope"),
        expected_instr_reduction="unknown/likely 0",
        cycle_estimate="unknown",
        note=(
            "No separate centering tail exists in the current NTT32 stage345 "
            "schedule, so this is a proof target, not an immediate patch."
        ),
    ),
    ProducerVariant(
        name="stage345_pre_final_barrett",
        removed_reductions=(
            "all stage345 final output reduction chains "
            "(sqdmulh/srshr/mls before D-half stores)"
        ),
        output_bound=Bound(
            INT16_MIN + 1,
            INT16_MAX,
            "my_32ntt comment: lazy CT stays below signed int16",
        ),
        expected_instr_reduction=(
            "192 reduction chains per full poly_ntt call "
            "(3 rows * 4 blocks * 16 chains), about 576 vector instructions"
        ),
        cycle_estimate="large if safe, but safety currently fails for key consumers",
        note="This is the only candidate with obvious instruction removal.",
    ),
    ProducerVariant(
        name="keygen_baseinv_machine_limited",
        removed_reductions=(
            "proof-only selected stage345 final chains; every stored lane "
            "would need a per-store proof inside the baseinv prepare bound"
        ),
        output_bound=Bound(
            -16383,
            16383,
            "target bound equal to baseinv signed vneg/vshl #1 machine precondition",
        ),
        expected_instr_reduction=(
            "3 vector instructions per proven removed chain; upper bound 576 "
            "if all 192 final chains meet this bound"
        ),
        cycle_estimate=(
            "0 now because no proof exists; if proven, proportional to removed "
            "chains and must be measured"
        ),
        note=(
            "Machine-limited keygen proof target only. It still needs baseinv "
            "semantic equivalence for wider residues."
        ),
    ),
    ProducerVariant(
        name="decap_poly_sub_no_wrap_limited",
        removed_reductions=(
            "proof-only selected stage345 final chains; every stored lane "
            "would need a per-store proof inside the decap poly_sub no-wrap bound"
        ),
        output_bound=Bound(
            -(INT16_MAX - CENTER),
            INT16_MAX - CENTER,
            "target bound equal to decap poly_sub no-wrap machine precondition",
        ),
        expected_instr_reduction=(
            "3 vector instructions per proven removed chain; upper bound 576 "
            "if all 192 final chains meet this bound"
        ),
        cycle_estimate=(
            "0 now because no proof exists; if proven, proportional to removed "
            "chains and must be measured"
        ),
        note=(
            "Machine-limited decap proof target only. It still needs verify "
            "basemul semantic range proof for wider c_minus_m2."
        ),
    ),
    ProducerVariant(
        name="selected_stage345_reductions_removed",
        removed_reductions="some stage345 final chains",
        output_bound=Bound(
            INT16_MIN + 1,
            INT16_MAX,
            "no per-store bound available",
        ),
        expected_instr_reduction="proportional to removed chains",
        cycle_estimate="unknown",
        note="Needs per-store symbolic bounds; no such bounds exist yet.",
    ),
]

CONSUMERS = [
    Consumer(
        name="keygen_g_baseinv_prepare",
        machine_bound=Bound(-16383, 16383, "vneg/vshl #1 in baseinv_8_prepare must not wrap signed 16-bit lanes"),
        semantic_bound=Bound(-CENTER, CENTER, "production-proven representative contract"),
        note=(
            "Even if int16 doubling is machine-safe, reduce_mul2/reduce_mul3 "
            "equivalence for wider residues still needs a separate proof."
        ),
    ),
    Consumer(
        name="keygen_g_scaled_basemul_input",
        machine_bound=Bound(INT16_MIN + 1, INT16_MAX, "ld4 int16 into widening base_gt products"),
        semantic_bound=Bound(-CENTER, CENTER, "production-proven operand contract"),
        note=(
            "This consumer is less restrictive than baseinv for machine range, "
            "but keygen_g must satisfy baseinv first."
        ),
    ),
    Consumer(
        name="encap_m_q31_addend",
        machine_bound=Bound(INT16_MIN + 1, INT16_MAX, "saddw/saddw2 widens int16 addend to s32"),
        semantic_bound=Bound(-CENTER, CENTER, "existing Q31 byte-contract proof used production addend range"),
        note=(
            "Q31 direct32 proof must be rerun for any wider m addend bound.  "
            "Do not assume the byte-contract reducer covers loose NTT output."
        ),
    ),
    Consumer(
        name="encap_m_generic_basemul_add_addend",
        machine_bound=Bound(INT16_MIN + 1, INT16_MAX, "generic add path can load int16 addend"),
        semantic_bound=Bound(-CENTER, CENTER, "production arithmetic-correct contract"),
        note="Generic path is not the current production default when Q31 is enabled.",
    ),
    Consumer(
        name="decap_m1_poly_sub_then_verify_basemul",
        machine_bound=Bound(-(INT16_MAX - CENTER), INT16_MAX - CENTER, "poly_sub computes c - m2 in signed 16-bit lanes; c is bounded by production ciphertext range"),
        semantic_bound=Bound(-CENTER, CENTER, "production verify basemul contract after poly_sub"),
        note=(
            "If m2 can approach signed-int16 extremes, c - m2 can wrap as a "
            "16-bit subtract before the verify basemul sees it."
        ),
    ),
]

CANDIDATES = {
    "poly_ntt_loose_for_keygen_g": [
        "keygen_g_baseinv_prepare",
        "keygen_g_scaled_basemul_input",
    ],
    "poly_ntt_loose_for_encap_m": [
        "encap_m_q31_addend",
        "encap_m_generic_basemul_add_addend",
    ],
    "poly_ntt_loose_for_decap_m1": [
        "decap_m1_poly_sub_then_verify_basemul",
    ],
}

PROOF_ONLY_ROWS = [
    (
        "keygen_g_baseinv_machine_limited",
        "poly_ntt_loose_for_keygen_g",
        "keygen_baseinv_machine_limited",
        "keygen_g_baseinv_prepare",
        "no",
        "machine-safe, but baseinv semantic proof is still production-range only",
    ),
    (
        "encap_m_reduced_non_centered",
        "poly_ntt_loose_for_encap_m",
        "reduced_non_centered",
        "encap_m_q31_addend",
        "no",
        "machine-safe, but Q31 byte-contract proof is still production-range only",
    ),
    (
        "decap_m1_poly_sub_no_wrap_limited",
        "poly_ntt_loose_for_decap_m1",
        "decap_poly_sub_no_wrap_limited",
        "decap_m1_poly_sub_then_verify_basemul",
        "no",
        "poly_sub machine-safe, but verify basemul proof is still production-range only",
    ),
]


def decide(producer: ProducerVariant, consumer: Consumer) -> tuple[str, str]:
    machine_safe = producer.output_bound.within(consumer.machine_bound)
    semantic_safe = (
        consumer.semantic_bound is not None
        and producer.output_bound.within(consumer.semantic_bound)
    )

    if not machine_safe:
        return (
            "no",
            f"producer {producer.output_bound.text()} exceeds machine bound {consumer.machine_bound.text()}",
        )
    if not semantic_safe:
        return (
            "needs_proof",
            f"machine-safe but exceeds semantic proof bound {consumer.semantic_bound.text() if consumer.semantic_bound else 'n/a'}",
        )
    return ("yes", "within current production-proven contract")


def main() -> None:
    print("# Loose NTT Range Model")
    print()
    print(f"q={Q}, centered=[{-CENTER}, {CENTER}], int16=[{INT16_MIN}, {INT16_MAX}]")
    print()

    print("## Producer variants")
    for p in PRODUCERS:
        print(f"- {p.name}: bound={p.output_bound.text()}, removed={p.removed_reductions}")
    print()

    print("## Consumer bounds")
    for c in CONSUMERS:
        sem = c.semantic_bound.text() if c.semantic_bound else "none"
        print(f"- {c.name}: machine={c.machine_bound.text()}, semantic={sem}")
    print()

    print("## Candidate matrix")
    header = (
        "| candidate | producer | consumer | safe? | reason | expected instr reduction | cycle estimate |"
    )
    print(header)
    print("|---|---|---|---|---|---|---|")
    for candidate, consumer_names in CANDIDATES.items():
        for p in PRODUCERS:
            for cname in consumer_names:
                consumer = next(c for c in CONSUMERS if c.name == cname)
                safe, reason = decide(p, consumer)
                print(
                    f"| {candidate} | {p.name} {p.output_bound.text()} | "
                    f"{consumer.name} | {safe} | {reason} | "
                    f"{p.expected_instr_reduction} | {p.cycle_estimate} |"
                )

    print()
    print("## Wave 4 proof-only variants")
    print(
        "| proof-only variant | candidate | producer bound | consumer bound | "
        "machine safe? | implementation safe? | expected instr reduction | "
        "cycle estimate | blocker |"
    )
    print("|---|---|---|---|---|---|---|---|---|")
    for label, candidate, producer_name, consumer_name, impl_safe, blocker in PROOF_ONLY_ROWS:
        producer = next(p for p in PRODUCERS if p.name == producer_name)
        consumer = next(c for c in CONSUMERS if c.name == consumer_name)
        machine_safe = "yes" if producer.output_bound.within(consumer.machine_bound) else "no"
        print(
            f"| {label} | {candidate} | {producer.output_bound.text()} | "
            f"{consumer.name} machine {consumer.machine_bound.text()} | "
            f"{machine_safe} | {impl_safe} | {producer.expected_instr_reduction} | "
            f"{producer.cycle_estimate} | {blocker} |"
        )


if __name__ == "__main__":
    main()
