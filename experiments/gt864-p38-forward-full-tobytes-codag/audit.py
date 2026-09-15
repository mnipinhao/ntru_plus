#!/usr/bin/env python3
"""P38 static gate: can direct Forward make Full ToBytes normalization cheaper?"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
BUILD = HERE / "build"
Q = 3457


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args: list[object], **kwargs: object) -> None:
    subprocess.run([str(x) for x in args], check=True, **kwargs)


def opcode_count(path: Path, opcode: str) -> int:
    return len(re.findall(rf"^\s*{re.escape(opcode)}\s", path.read_text(), re.M))


def canonical_full(x: int) -> int:
    quotient = (x * 9 + 16384) // 32768
    residual = x - quotient * Q
    return residual + (Q if residual < 0 else 0)


def canonical_small(x: int) -> int:
    return x + (Q if x < 0 else 0)


def b3_reuse_counterexample() -> dict[str, object]:
    """Show that the rho-product quotient does not determine output quotients."""
    rho = -723
    rho_hat = -6853
    by_qd: dict[int, list[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {}
    for x0 in range(-16, 17):
        for x1 in range(-16, 17):
            for x2 in range(-16, 17):
                d = x1 - x2
                qd = (d * rho_hat + 16384) // 32768
                r = d * rho - qd * Q
                y = (x0 + x1 + x2, x0 - x2 + r, x0 - x1 - r)
                output_q = tuple(v // Q for v in y)
                by_qd.setdefault(qd, []).append(((x0, x1, x2), output_q))
    for qd, rows in by_qd.items():
        first = rows[0]
        for row in rows[1:]:
            if row[1] != first[1]:
                return {"rho_product_quotient": qd,
                        "input_a": first[0], "output_quotients_a": first[1],
                        "input_b": row[0], "output_quotients_b": row[1]}
    raise AssertionError("unexpected: product quotient determines all outputs")


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    sources = [
        PROD / "gt864_forward_poly_ntt.S",
        PROD / "gt864_forward_six_bank.S",
        PROD / "gt864_top_split.s",
        PROD / "tail_variants.S",
        HERE / "audit.py",
        HERE / "witness.c",
    ]
    objects = []
    for source in sources[:4]:
        obj = BUILD / (source.name + ".o")
        run(["cc", "-O3", "-x", "assembler-with-cpp", "-c", source, "-o", obj])
        objects.append(obj)
    exe = BUILD / "witness"
    run(["cc", "-O3", HERE / "witness.c", *objects, "-o", exe])
    witness_path = BUILD / "witness.json"
    with witness_path.open("w") as stream:
        run([exe], stdout=stream)
    witness = json.loads(witness_path.read_text())
    modes = witness["modes"]
    assert set(modes) == {"small", "keygen_f"}
    assert all(mode["trials"] == 32768 for mode in modes.values())
    for mode in modes.values():
        assert mode["coordinates_observed_outside_small_contract"] == 864
        assert len(mode["outside_witnesses"]) == 864
        assert all(row["value"] <= -Q or row["value"] >= Q
                   for row in mode["outside_witnesses"])
        assert all(canonical_full(row["value"]) == row["value"] % Q and
                   canonical_small(row["value"]) != row["value"] % Q
                   for row in mode["outside_witnesses"])

    full = PROD / "gt864_p18_tobytes_full.S"
    small = PROD / "gt864_p18_tobytes_small.S"
    full_static = {op: opcode_count(full, op) for op in ("sqrdmulh", "mls")}
    small_static = {op: opcode_count(small, op) for op in ("sqrdmulh", "mls")}
    assert full_static == {"sqrdmulh": 54, "mls": 54}
    assert full.read_text().count("bl p24_top_full") == 2
    full_counts = {op: 2 * count for op, count in full_static.items()}
    small_counts = {op: 2 * count for op, count in small_static.items()}
    assert small_counts == {"sqrdmulh": 0, "mls": 0}

    exhaustive = {"full_mismatches": 0, "small_mismatches": 0,
                  "full_output": [Q, 0], "full_residual": [32767, -32768]}
    for x in range(-32768, 32768):
        got = canonical_full(x)
        if got != x % Q:
            exhaustive["full_mismatches"] += 1
        if canonical_small(x) != x % Q:
            exhaustive["small_mismatches"] += 1
        quotient = (x * 9 + 16384) // 32768
        residual = x - quotient * Q
        exhaustive["full_output"][0] = min(exhaustive["full_output"][0], got)
        exhaustive["full_output"][1] = max(exhaustive["full_output"][1], got)
        exhaustive["full_residual"][0] = min(exhaustive["full_residual"][0], residual)
        exhaustive["full_residual"][1] = max(exhaustive["full_residual"][1], residual)
    assert exhaustive["full_mismatches"] == 0
    assert exhaustive["small_mismatches"] > 0

    families = {
        "unchanged_forward_selective_small": {
            "removed_full_only_instructions": 0,
            "reason": "every coordinate has a constructive valid-input witness outside the Small contract",
        },
        "canonical_postpass_then_small": {
            "removed_full_only_instructions": 216,
            "added_forward_instructions": 216,
            "net_removed_instructions": 0,
            "added_coefficient_memory_pass": True,
        },
        "canonicalize_before_existing_forward_stores_then_small": {
            "removed_full_only_instructions": 216,
            "added_forward_instructions": 216,
            "net_removed_instructions": 0,
            "fr0_representation_changed": True,
        },
        "reuse_one_product_rho_quotient": {
            "removed_full_only_instructions": 0,
            "reason": "the existing rho-product quotient does not determine the three output quotients",
            "counterexample": b3_reuse_counterexample(),
        },
    }

    result = {
        "experiment": "GT864-P38-FORWARD-FULL-TOBYTES-CODAG-20260915",
        "status": "reject_static",
        "baseline_revision": subprocess.check_output(
            ["git", "rev-parse", "18091661"], cwd=ROOT, text=True).strip(),
        "production_symbols": {
            "forward": "gt864_forward_poly_ntt_p41_k1_kem_only",
            "full": "gt864_p18_tobytes_full_asm",
            "small": "gt864_p18_tobytes_small_asm",
        },
        "full_only_instruction_delta": {
            "full": full_counts, "small": small_counts,
            "total": sum(full_counts.values()),
        },
        "valid_input_diagnostic": {
            name: {
                "trials": mode["trials"],
                "coordinates_observed_outside_small_contract":
                    mode["coordinates_observed_outside_small_contract"],
                "observed_output_range": mode["observed_output_range"],
                "latest_first_witness_trial":
                    max(row["trial"] for row in mode["outside_witnesses"]),
            }
            for name, mode in modes.items()
        } | {
            "sha256": sha256(witness_path),
        },
        "normalization_exhaustive_i16": exhaustive,
        "candidate_families": families,
        "hard_gate": {
            "required_removed_instructions": 108,
            "best_net_removed_instructions": 0,
            "passed": False,
        },
        "execution": {
            "slothy": "not run: no candidate passed the arithmetic gate",
            "pi5": "not run: no candidate passed the arithmetic gate",
            "production_changed": False,
        },
        "source_hashes": {str(path.relative_to(ROOT)): sha256(path)
                          for path in [*sources, full, small, PROD / "kem.c"]},
    }
    (HERE / "audit-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
