#!/usr/bin/env python3
from __future__ import annotations

import json
import itertools
import re
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
EXPERIMENTS = EXP.parent
OUT = EXP / "generated"
OUT.mkdir(exist_ok=True)

Q = 3457
R = pow(2, 16, Q)
REPAYMENT = 218.12


def signed(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def naf(n: int) -> list[int]:
    """Least-significant-first non-adjacent signed-digit expansion."""
    out = []
    while n:
        if n & 1:
            digit = 2 - (n & 3)
            out.append(digit)
            n -= digit
        else:
            out.append(0)
        n //= 2
    return out


def generate_em1_asm() -> None:
    source = (EXPERIMENTS / "gt32_ql2_native_b3_135/src/ql2_native_b3.S").read_text()
    source = source.replace("gt135_basemul_general_ql2_native_e0",
                            "gt136_basemul_general_ql2_native_em1")
    source = source.replace(
        '#include "../generated/ql2_lambda.inc"',
        '#include "../../gt32_ql2_native_b3_135/generated/ql2_lambda.inc"')
    source = re.sub(
        r'\n\t/\* Mandatory general-B3 scale repayment:.*?\n'
        r'\tvmovdqu %ymm9, \(%rdi\)',
        '\n\t/* Natural qword-local product: e=-1. */\n'
        '\tvmovdqu %ymm9, (%rdi)',
        source,
        flags=re.S,
    )
    if "Mandatory general-B3 scale repayment" in source:
        raise RuntimeError("failed to remove e=0 finalizer")
    (OUT / "ql2_native_b3_e_minus1.S").write_text(source)


def main() -> None:
    pmu135 = json.loads((EXPERIMENTS / "gt32_ql2_native_b3_135/results/pmu.json").read_text())
    pmu133 = json.loads((EXPERIMENTS / "gt32_ql2_residual_attribution_133/results/pmu-analysis-32.json").read_text())
    rows = {(r["implementation"], r["event_class"]): r for r in pmu133["rows"]}
    official_pending = rows[("official", "load_pending")]["estimated_events_per_encap"]
    ql2_pending = rows[("gt", "load_pending")]["estimated_events_per_encap"]

    # Direct positive leaf deltas from Experiment 133.  Treating every one as
    # fully removable is intentionally much more generous than a load-stall budget.
    positive_leaf_debts = {
        "decode": 30.0,
        "cbd": 25.0,
        "serialize_r": 45.0,
        "sotp": 13.0,
        "ql2_basemul": 12.75,
    }
    optimistic_all_leaf = sum(positive_leaf_debts.values())

    r_centered = signed(R)
    digits = naf(abs(r_centered))
    signed_terms = [(-1 if r_centered < 0 else 1) * d * (1 << i)
                    for i, d in enumerate(digits) if d]
    assert sum(signed_terms) == r_centered

    # Exhaust the cheap layout-only subfamily.  For output k, the direct
    # quartic dot pairs a_i with b_(k-i mod 4); terms that wrap additionally
    # carry lambda.  A fixed asymmetric A/B coefficient order can make at
    # most one of the four output dots use the stored B word order directly.
    layout_rows = []
    maximum_native_outputs = 0
    for a_order in itertools.permutations(range(4)):
        for b_order in itertools.permutations(range(4)):
            native = []
            for k in range(4):
                if all(b_order[p] == ((k - a_order[p]) & 3)
                       for p in range(4)):
                    native.append(k)
            maximum_native_outputs = max(maximum_native_outputs, len(native))
            layout_rows.append((a_order, b_order, native))
    assert len(layout_rows) == 24 * 24
    assert maximum_native_outputs == 1

    result = {
        "schema": "ntruplus768-gt32-ql2-reopen-survey-v1",
        "experiment": "GT32-QL2-REOPEN-SURVEY-136",
        "production_modified": False,
        "gate135_loss_cycles": REPAYMENT,
        "routing_operation_class": {
            "measured_port_5_11_delta_per_call": pmu135["delta_per_call"]["cpu_core/uops_dispatched.port_5_11/u"],
            "arithmetic_floor": "four vpmaddwd diagonal products per QL2 vector; each quartic output depends on all four input coefficients",
            "coefficient_order_exhaustion": {
                "asymmetric_A_B_orders_checked": len(layout_rows),
                "maximum_outputs_using_native_B_order": maximum_native_outputs,
                "minimum_non_native_output_packets": 4 - maximum_native_outputs,
                "qualification": "this exhausts coefficient reorderings only, not new bilinear/evaluation bases"
            },
            "audited_families": {
                "D0_D3_qword_local": "measured Gate 135 loss; routing remains dynamic",
                "producer_preexpanded_diagonals": "moves routing into a larger producer ABI and adds representation stores/loads; no operation class is deleted",
                "rank7_tensor": "Experiment 059E executable late exit loses +237/+398 TSC because the consumer map becomes dense",
                "current_SoA": "avoids qword-local routing and remains the consumer control"
            },
            "result": "NO_NEW_EXECUTABLE_CANDIDATE",
            "family_closed": False,
            "reopen_requires": "producer-native evaluation coordinates whose BaseMul and Q24 exits are both sparse; not another D0-D3 schedule"
        },
        "scale_absorption": {
            "natural_native_b3_output_exponent": -1,
            "required_ciphertext_exponent": 0,
            "R_mod_q": R,
            "R_centered": r_centered,
            "minimal_shift_add_view": signed_terms,
            "observation": "multiplication by centered R=-147 needs a widened value (for |x| near the established bounds); it cannot be folded into the existing three-instruction i16 Q24 quotient estimator",
            "exact_existing_gate": "GT32-SCALE-CONSUMER-FUSION-001 proves algebraic fusion but retains 48 Montgomery chains; concrete whole-edge static delta only -24 instructions",
            "new_executable_bound": "benchmark natural e=-1 B3 against the identical e=0 B3 to measure the maximum credit of making scale repayment free",
            "result_before_benchmark": "BOUNDED_EXECUTABLE_CEILING_REQUIRED"
        },
        "load_dependency_repayment": {
            "estimated_pending_cycles_per_encap": {
                "official": official_pending,
                "ql2": ql2_pending,
                "delta": ql2_pending - official_pending
            },
            "positive_direct_leaf_debts_cycles": positive_leaf_debts,
            "optimistic_all_positive_leaf_debts": optimistic_all_leaf,
            "fraction_of_218_repayment": optimistic_all_leaf / REPAYMENT,
            "result": "REJECTED_BY_MEASURED_UPPER_BOUND",
            "reason": "even misclassifying every positive direct leaf delta as removable load debt yields less than 218 cycles; sampled pending-cycle delta is only directional and about 13 cycles",
            "reopen_requires": "PEBS/LBR evidence for a new specific dependency chain with more than 218 cycles of removable caller credit"
        }
    }
    (OUT / "reopen-survey.json").write_text(json.dumps(result, indent=2) + "\n")
    generate_em1_asm()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
