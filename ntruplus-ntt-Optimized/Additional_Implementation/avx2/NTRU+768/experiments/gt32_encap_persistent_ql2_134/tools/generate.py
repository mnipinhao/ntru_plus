#!/usr/bin/env python3
"""Gate 134: persistent QL2 and a QL2-native general BaseMul.

This is deliberately a mapping/cost/correctness gate.  It does not claim
cycles and it does not modify the production implementation.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = HERE.parents[3]
OUT = EXP / "generated"
Q = 3457
GROUPS = 12
LANES = 16


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
    return [x for row in v for x in row]


def permute(values: list[int], source_labels: list[object], target_labels: list[object]) -> list[int]:
    by_label = dict(zip(source_labels, values, strict=True))
    return [by_label[label] for label in target_labels]


def quartic_mul(a: list[int], b: list[int], lam: int) -> list[int]:
    assert len(a) == len(b) == 4
    return [
        (a[0] * b[0] + lam * (a[1] * b[3] + a[2] * b[2] + a[3] * b[1])) % Q,
        (a[1] * b[0] + a[0] * b[1] + lam * (a[3] * b[2] + a[2] * b[3])) % Q,
        (a[2] * b[0] + a[1] * b[1] + a[0] * b[2] + lam * a[3] * b[3]) % Q,
        (a[3] * b[0] + a[2] * b[1] + a[1] * b[2] + a[0] * b[3]) % Q,
    ]


def mul_m(a_m: list[int], b_m: list[int], lambdas: list[int]) -> list[int]:
    out = [0] * (4 * LANES)
    for leaf in range(LANES):
        a = [a_m[c * LANES + leaf] for c in range(4)]
        b = [b_m[c * LANES + leaf] for c in range(4)]
        c = quartic_mul(a, b, lambdas[leaf])
        for coefficient in range(4):
            out[coefficient * LANES + leaf] = c[coefficient]
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correctness(m_labels: list[object], ql2_labels: list[object]) -> dict:
    rng = random.Random(0x134_51A)
    impulses = 0
    for position in range(4 * LANES):
        m = [0] * (4 * LANES)
        m[position] = 1
        ql2 = permute(m, m_labels, ql2_labels)
        recovered = permute(ql2, ql2_labels, m_labels)
        assert recovered == m
        impulses += 1

    trials = 1000
    for _ in range(trials):
        a_m = [rng.randrange(Q) for _ in range(4 * LANES)]
        b_m = [rng.randrange(Q) for _ in range(4 * LANES)]
        lambdas = [rng.randrange(1, Q) for _ in range(LANES)]
        reference_m = mul_m(a_m, b_m, lambdas)
        a_ql2 = permute(a_m, m_labels, ql2_labels)
        b_ql2 = permute(b_m, m_labels, ql2_labels)

        # Semantic QL2-native execution: each qword contains one complete
        # quartic leaf, so no persistent coefficient-plane object is needed.
        native_ql2 = [0] * (4 * LANES)
        label_to_value_a = dict(zip(ql2_labels, a_ql2, strict=True))
        label_to_value_b = dict(zip(ql2_labels, b_ql2, strict=True))
        label_to_output: dict[object, int] = {}
        for leaf in range(LANES):
            av = [label_to_value_a[(c, leaf)] for c in range(4)]
            bv = [label_to_value_b[(c, leaf)] for c in range(4)]
            cv = quartic_mul(av, bv, lambdas[leaf])
            for c in range(4):
                label_to_output[(c, leaf)] = cv[c]
        for index, label in enumerate(ql2_labels):
            native_ql2[index] = label_to_output[label]
        assert permute(native_ql2, ql2_labels, m_labels) == reference_m
    return {
        "mapping_impulses": impulses,
        "random_quartic_products": trials,
        "modulus": Q,
        "mapping_bijective": True,
        "native_ql2_product_mod_q_exact": True,
    }


def main() -> None:
    m = [[(coefficient, leaf) for leaf in range(LANES)] for coefficient in range(4)]
    ql2 = dword_layer(word_layer(m))
    packet = qword_layer(ql2)
    m_labels = flatten(m)
    ql2_labels = flatten(ql2)
    packet_labels = flatten(packet)
    assert set(m_labels) == set(ql2_labels) == set(packet_labels)

    # Every four adjacent words in QL2 must be one complete quartic leaf.
    quartics = []
    for register, row in enumerate(ql2):
        for qword in range(4):
            labels = row[4 * qword:4 * qword + 4]
            coefficients = [label[0] for label in labels]
            leaves = {label[1] for label in labels}
            assert coefficients == [0, 1, 2, 3] and len(leaves) == 1
            quartics.append({"register": register, "qword": qword,
                             "leaf": next(iter(leaves))})

    checks = correctness(m_labels, ql2_labels)

    # Exact boundary-routing ledger.  It intentionally excludes arithmetic-
    # internal shuffles in the native kernel; those are charged separately by
    # the executable gate rather than hidden in a presentation number.
    current = {
        "decode_h_P_to_M": 12,
        "forward_r_T_to_M": 12,
        "serialize_r_M_to_P": 12,
        "B3_output_M_to_QL2": 8,
        "final_QL2_to_P": 4,
    }
    persistent_native = {
        "decode_h_P_to_QL2": 4,
        "forward_r_T_to_QL2": 0,
        "serialize_r_QL2_to_P": 4,
        "B3_output_native_QL2": 0,
        "final_QL2_to_P": 4,
    }
    current_total = sum(current.values())
    persistent_total = sum(persistent_native.values())
    assert current_total == 48 and persistent_total == 12

    old_root = ROOT / "experiments/avx2_gt32_tile4_official_001"
    old_proof = json.loads((old_root / "generated/tile4_aos_dot_redc16_gate.json").read_text())
    assert old_proof["modes"]["R1-U"]["representative"] == "bit-exact-R0"
    assert old_proof["static_kernel"]["estimated_loop_instructions_R1"] == 30

    source_paths = [
        ROOT / "ntt_m.s",
        ROOT / "basemul.s",
        ROOT / "pack.s",
        old_root / "src/tile4_aos_dot_redc16_asm.S",
        old_root / "generated/tile4_aos_dot_redc16_gate.json",
        ROOT / "experiments/gt32_encap_persistent_t_101/RESULTS.md",
        ROOT / "experiments/gt32_ql2_shared_convergence_103/RESULTS.md",
    ]
    report = {
        "schema": "ntruplus768-gt32-encap-persistent-ql2-134-v1",
        "experiment": "GT32-ENCAP-PERSISTENT-QL2-134",
        "mode": "generator-and-existing-executable-evidence",
        "production_modified": False,
        "baseline": {
            "production": "b2a4bea",
            "encap_research": "104 QL2",
        },
        "mapping": {
            "QL2_definition": "Q24 state after W+D and before Q",
            "physical_shape": "four YMM; each qword is one complete [c0,c1,c2,c3] quartic leaf",
            "quartics": quartics,
            "bijection": True,
            "warning": "QL2 is a presentation, not a new algebraic or Montgomery domain",
        },
        "correctness": checks,
        "boundary_route_ledger_per_group": {
            "current_104": current,
            "persistent_QL2_native_B3": persistent_native,
            "current_total": current_total,
            "candidate_total": persistent_total,
            "delta_per_group": persistent_total - current_total,
            "groups": GROUPS,
            "delta_per_encap": (persistent_total - current_total) * GROUPS,
            "operation_class_deletion": "36 of 48 boundary routes/group; 432 executed routes/Encap",
        },
        "native_B3_evidence": {
            "existing_kernel": "gt32_tile4_basemul_aos_dot_r1u_asm",
            "compatible_physical_idea": "qword-local quartic AoS with vpmaddwd dot products",
            "existing_scale": "e=0 x e=0 -> e=-1",
            "required_encap_scale": "e=0 x e=0 -> e=0",
            "existing_peak_ymm": old_proof["static_kernel"]["peak_ymm"],
            "existing_spill_required": old_proof["static_kernel"]["spill_required"],
            "existing_loop_instructions_per_vector": 30,
            "existing_measured_scope": "scale-B3/inverse consumer only; not general-B3/Q24",
            "existing_paired_advantage_vs_B3_tsc": "about 49--52 in its qualified scale-B3 scope",
        },
        "scale_repayment": {
            "cannot_be_omitted": True,
            "reason": "Q24 consumes e=0 product and message; old R1-U emits e=-1",
            "constructive_e0_finish": "apply the same Mont(R^2) correction used by general B3 after each packed AoS vector",
            "dynamic_vectors": 48,
            "instructions_per_vector": 4,
            "dynamic_instructions": 192,
            "additional_vector_multiply_chains": 48,
            "expected_peak_ymm": 15,
            "expected_spill": False,
            "cycle_claim": None,
        },
        "rejected_shortcuts": [
            {
                "name": "persistent QL2 plus immediate QL2-to-M conversion",
                "reason": "same search class as 101; it does not absorb the BaseMul conversion and has already failed full Encap",
            },
            {
                "name": "reuse old R1-U cycle result as general-B3 credit",
                "reason": "wrong output scale and different inverse consumer; the mandatory e=0 finish was not measured",
            },
            {
                "name": "count 432 deleted routes as cycles",
                "reason": "native qword-local B3 introduces its own blend/shuffle/reduction DAG",
            },
        ],
        "selected_next_executable": {
            "id": "PQL2_NATIVE_E0",
            "region": "QL2 x QL2 -> QL2 general B3, including mandatory e=0 finish",
            "control": "current M x M -> QL2 general B3",
            "candidate": "qword-local vpmaddwd AoS B3 -> REDC16 -> Mont(R^2) -> QL2",
            "input_conversion_charged": False,
            "reason": "both sides start in their native persistent representation; producer/serializer boundary credit is accounted separately",
            "benchmark": "same-ELF paired normal/reversed, TSC + core cycles + instructions + multiplier pressure + port 5/11",
            "decision_rule": "do not reject on instruction count; measure whether native B3 cost is small enough to repay the 432-route boundary credit",
        },
        "decision": "PASS_TO_EXECUTABLE_135",
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in source_paths},
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "persistent-ql2-gate.json").write_text(json.dumps(report, indent=2) + "\n")
    print("mapping=PASS")
    print("quartic_products=PASS")
    print("boundary_route_delta=-432/Encap")
    print("scale_repayment=48 Mont(R^2) chains, 192 instructions")
    print("decision=PASS_TO_EXECUTABLE_135")


if __name__ == "__main__":
    main()
