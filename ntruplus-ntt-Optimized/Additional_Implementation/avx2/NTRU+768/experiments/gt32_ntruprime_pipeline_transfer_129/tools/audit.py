#!/usr/bin/env python3
"""Audit direct NTRU Prime AVX2 pipeline transfers into GT Clean NTRU+768.

The external implementation is a design reference, not vendored source.  This
script fails closed when the local production contracts or retained experiment
ledger no longer match the source-backed audit in README.md.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve()
EXPERIMENT = HERE.parents[1]
ROOT = HERE.parents[3]
GENERATED = EXPERIMENT / "generated"


def read(name: str) -> str:
    return (ROOT / name).read_text()


def require(text: str, pattern: str, description: str) -> None:
    if re.search(pattern, text, re.MULTILINE | re.DOTALL) is None:
        raise RuntimeError(f"local source contract changed: {description}")


def sha256(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main() -> None:
    implementation = read("IMPLEMENTATION.md")
    layouts = read("LAYOUTS.md")
    frontend = read("ntt.s")
    ntt_m = read("ntt_m.s")
    basemul = read("basemul.s")
    invntt = read("invntt.s")
    encap = read("encap.c")
    decap = read("decap.c")
    keygen = read("keygen.c")
    ledger = read("experiments/GT32_EXPERIMENT_INDEX_072_128.md")
    late_soa = read("experiments/gt32_late_soa_065/README.md")

    # Selected production facts used by the transfer decision.
    require(frontend, r"\.macro FRONTEND_WIDE_ITER_BODY.*?DFT3_WIDE_STORE", "fused frontend/DFT3 deposit")
    require(frontend, r"ntruplus768_ntt_frontend_avx2:.*?FRONTEND_WIDE_ITER_0", "selected wide frontend")
    require(ntt_m, r"ntruplus768_ntt_m_avx2:.*?FR_PACKED_TO_PLANES", "M terminal formation")
    require(basemul, r"ntruplus768_basemul_scale_m_avx2,\s*TILE4_OUTPUT_SOA.*?TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA", "M-native scale BaseMul")
    require(basemul, r"ntruplus768_basemul_general_m_avx2,\s*TILE4_OUTPUT_SOA.*?TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA", "M-native general BaseMul")
    require(invntt, r"ntruplus768_invntt_m_avx2:", "M inverse")
    require(layouts, r"M is the persistent private coefficient-plane SoA", "M typed layout")
    require(layouts, r"P is the key-generation physical placement", "P typed layout")
    require(implementation, r"semantic sum is never a memory-resident", "E0V virtual sum")
    require(encap, r"pack_m_sum_highrange12699_avx2", "Encap consumer-native pack")
    require(decap, r"basemul_scale_m_avx2.*?invntt_m_avx2", "Decap B3-to-inverse seam")
    require(keygen, r"ntt_p_avx2.*?baseinv_j1_avx2", "Keygen P/J1 seam")
    require(late_soa, r"FULL_ARITHMETIC_CHAIN_PASS", "Late-SoA evidence")
    require(ledger, r"102--104 established QL2", "QL2 evidence")
    require(ledger, r"083 D1 dual-terminal", "dual-terminal evidence")

    matrix = [
        {
            "ntru_prime_mechanism": "radix_3x2 permutation encoded in load/store offsets",
            "ntruplus768_equivalent": "wide frontend plus DFT3_WIDE_STORE deposits the six GT branches directly",
            "coverage": "ALREADY_ABSORBED",
            "new_asm": False,
        },
        {
            "ntru_prime_mechanism": "radix_3x2 pre/post fused with diagonal twist",
            "ntruplus768_equivalent": "FRONTEND_WIDE_ITER_BODY combines top split, twist/Montgomery work, DFT3 and branch deposit",
            "coverage": "ALREADY_ABSORBED_FORWARD_SIDE",
            "new_asm": False,
        },
        {
            "ntru_prime_mechanism": "twist_transpose_pre/post around a persistent leaf-lane multiplication island",
            "ntruplus768_equivalent": "TILE4 inside NTT32, then typed M/P coefficient planes consumed natively by B3/BaseInv/inverse/Q24",
            "coverage": "ALREADY_ABSORBED_AND_EXTENSIVELY_SEARCHED",
            "evidence": ["030", "061-067", "100-105"],
            "new_asm": False,
        },
        {
            "ntru_prime_mechanism": "two Forward operands, BaseMul and inverse share one coefficient-to-coefficient polymul workspace",
            "ntruplus768_equivalent": "no standard KEM caller has this exact graph",
            "coverage": "CALL_GRAPH_MISMATCH",
            "details": {
                "encap": "two Forward paths but no inverse; r crosses a hash boundary",
                "decap": "scale BaseMul to inverse exists, but operands arrive decoded in M rather than through two Forward transforms",
                "keygen": "Forward values feed BaseInv and two serialized products; no inverse transform",
            },
            "new_asm": False,
        },
        {
            "ntru_prime_mechanism": "post transpose followed by one final scale/fold at coefficient endpoint",
            "ntruplus768_equivalent": "typed e=0/e=-1/J1/SP1 scales terminate at different KEM consumers",
            "coverage": "NOT_DIRECTLY_TRANSFERABLE",
            "evidence": ["072-078 normalized-D4", "026-029 scale propagation"],
            "new_asm": False,
        },
        {
            "ntru_prime_mechanism": "dual terminal from live transform registers",
            "ntruplus768_equivalent": "ENC-R retain M for B3 while forming WIRE12 for hash_g",
            "coverage": "EXECUTED_ALREADY",
            "evidence": ["082 audit", "083 executable D1 dual terminal"],
            "result": "composite-map credit existed, but immediate coupling was below continuation value",
            "new_asm": False,
        },
    ]

    result = {
        "schema": "ntruplus768-ntruprime-pipeline-transfer-v1",
        "experiment": "GT32-NTRUPRIME-PIPELINE-TRANSFER-129",
        "mode": "source-backed-generator-audit",
        "production_modified": False,
        "assembly_emitted": False,
        "reference": {
            "repository": "https://github.com/vector-polymul-ntru-ntrup/NTRU_Prime_truncation",
            "branch_inspected": "main",
            "access_date": "2026-09-15",
            "files": [
                "avx2/avx2/radix_3x2.S",
                "avx2/avx2/__avx2.c",
                "avx2/avx2/basemul.S",
            ],
            "observed_pipeline": [
                "Rader17/truncated front transform",
                "radix 3x2 with pre-twist",
                "twist plus 16x16 transpose into plus/minus leaf batches",
                "cyclic/negacyclic FFT16 BaseMul",
                "inverse transpose plus post-twist",
                "inverse radix 3x2 and Rader17",
                "single final coefficient fold and FINAL_SCALE_Rmod",
            ],
        },
        "local_source_sha256": {
            name: sha256(name)
            for name in [
                "IMPLEMENTATION.md", "LAYOUTS.md", "ntt.s", "ntt_m.s",
                "basemul.s", "invntt.s", "encap.c", "decap.c", "keygen.c",
                "experiments/GT32_EXPERIMENT_INDEX_072_128.md",
                "experiments/gt32_late_soa_065/README.md",
            ]
        },
        "transfer_matrix": matrix,
        "decision": {
            "direct_port": "NO_NEW_EXECUTABLE_GATE",
            "reason": "Every direct mechanism is already absorbed, already measured, or lacks a matching NTRU+768 KEM caller graph.",
            "do_not_repeat": [
                "standalone GT permutation pass",
                "standalone M/P transpose",
                "generic persistent coefficient-plane ABI",
                "ENC-R immediate dual terminal",
                "untyped final-scale deferral",
            ],
            "reopen_only_if": [
                "a real KEM caller seam deletes a complete materialization or reduction beyond the existing M/P/E0V/QL2 contracts",
                "a new factorization changes the leaf arithmetic rather than only relocating permutation/twist work",
                "a private coefficient-to-coefficient polymul API becomes an actual measured target",
            ],
        },
    }

    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "transfer_matrix.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print("GT32-NTRUPRIME-PIPELINE-TRANSFER-129: PASS")
    print("direct executable transfer: none")
    print("production modified: no")


if __name__ == "__main__":
    main()
