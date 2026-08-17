#!/usr/bin/env python3
"""Exact algebra and retry-cost gate for eliminating one keygen BaseMul."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "generated/tile4_keygen_bm_elimination_gate.json"


def main() -> None:
    out = {
        "schema": "ntruplus768-keygen-bm-elimination-v1",
        "experiment": "GT32-KEYGEN-BM-ELIMINATION-001",
        "scope": "polynomial-keygen-algebra",
        "control": [
            "finv=BaseInv(f)",
            "ginv=BaseInv(g)",
            "h=BM(g,finv)",
            "hinv=BM(f,ginv)",
        ],
        "candidate": [
            "finv=BaseInv(f)",
            "h=BM(g,finv)",
            "hinv=BaseInv(h)",
        ],
        "proof": {
            "assumption": "f is a unit after its existing retry loop",
            "h_definition": "h=g*f^-1",
            "invertibility_equivalence": "h is a unit iff g is a unit",
            "accepted_path_identity": "h^-1=f*g^-1",
            "serialized_pk_sk_semantics_unchanged": True,
        },
        "retry_cost_model": {
            "p": "probability that sampled g is invertible",
            "expected_attempts": "1/p",
            "control_after_f": "E[A]*BaseInv + 2*BM",
            "candidate_after_f": "E[A]*(BaseInv+BM)",
            "candidate_minus_control": "(1/p-2)*BM",
            "candidate_wins_iff": "p>1/2",
            "observed_production_corpus": {
                "natural_attempts_per_success": 1.0,
                "multi_retry_cases_observed": 0,
                "classification": "supporting evidence only; not a probability proof",
            },
        },
        "constant_time_and_failure": {
            "same_public_retry_branch": True,
            "failed_candidate_attempt_executes_one_extra_BM": True,
            "required_tests": [
                "forced-zero-g",
                "forced-noninvertible-leaf",
                "multi-attempt-deterministic-corpus",
                "accepted-pk-sk-byte-exact",
                "retry-count-exact",
            ],
        },
        "gate": {
            "bounded_C_caller_probe_eligible": True,
            "assembly_changes_required": False,
            "primary_benchmark": "accepted-polynomial-keygen-region",
            "secondary_benchmark": "forced-failure-and-realistic-retry-distribution",
            "decision": "continue-with-caller-level-correctness-and-cycle-probe",
            "stop_if": [
                "accepted-output-is-not-byte-exact",
                "retry-semantics-differ",
                "measured-invertibility-probability-at-or-below-one-half",
            ],
        },
    }
    OUTPUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["retry_cost_model"], indent=2))


if __name__ == "__main__":
    main()
