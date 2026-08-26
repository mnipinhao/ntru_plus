#!/usr/bin/env python3
"""Check H1 ASM0 contract, linked audit, and corrected pack-layout provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    contract_path = ROOT / "generated/gt9x16-prod3-ma2-hash-h1-asm.json"
    audit_path = ROOT / "generated/gt9x16-prod3-ma2-hash-h1-audit.json"
    direct_path = ROOT / "generated/gt9x16-prod3-ma2-hash-direct-map.json"
    schedule_path = ROOT / "generated/gt9x16-prod3-ma2-hash-direct-schedule.json"
    contract = json.loads(contract_path.read_text())
    audit = json.loads(audit_path.read_text())
    direct = json.loads(direct_path.read_text())
    schedule = json.loads(schedule_path.read_text())

    assert contract["schema"] == "gt9x16-prod3-ma2-hash-h1-asm/v1"
    assert audit["schema"] == "gt9x16-prod3-ma2-hash-h1-audit/v1"
    assert direct["bijection_and_ownership_proof"]["all_pairs_same_ma2_vector"] is False
    assert direct["movement_ledger"]["H2-packing-oriented"]["status"].startswith("invalidated")
    assert schedule["H2"]["status"].startswith("invalidated")
    assert schedule["decision"]["H1_asm0_authorized"]
    assert not schedule["decision"]["H2_asm_authorized"]
    assert not schedule["decision"]["benchmark_authorized"]

    wanted = {
        "data_loads": 272,
        "constant_vector_loads": 27,
        "constant_memory_operands": 136,
        "coefficient_reorder_routes": 336,
        "inv4_montgomery_instructions": 288,
        "sign_canonicalization_instructions": 216,
        "pack_bit_instructions": 144,
        "pack_transpose_routes": 324,
        "byte_store_instructions": 54,
        "vector_spill_reloads": 0,
    }
    for name, expected in wanted.items():
        entry = audit["scheduled_vs_linked"][name]
        assert entry == {"scheduled": expected, "linked": expected}
    assert audit["instruction_count"] == 1662
    assert audit["abi"] == {
        "branches": 0, "calls": 0, "distinct_ymm": list(range(16)),
        "peak_ymm": 16, "stack_references": 0, "vector_spills": 0,
        "vzeroupper": 0,
    }
    assert audit["range_and_pack"]["post_inv4"] == [-1998, 1998]
    assert audit["range_and_pack"]["canonical"] == [0, 3456]
    assert audit["range_and_pack"]["saturating_pack_instructions"] == 0
    assert audit["alignment"]["object_mod32"] == 0
    assert audit["alignment"]["elf_mod32"] == 0
    assert audit["alignment"]["symbol_text_size"] == 10133
    assert audit["alignment"]["sections"]["object_rodata"]["size"] == 640
    assert contract["source_sha256"]["schedule"] == sha256(schedule_path)
    assert contract["source_sha256"]["direct_map"] == sha256(direct_path)
    assert direct["source_sha256"]["pinned_pack_layout"] == sha256(
        ROOT / "generated/official-pack-layout.json")
    assert not audit["authorization"]["H2"]
    assert not audit["authorization"]["benchmark"]
    assert not audit["authorization"]["KEM"]

    print("H1 ASM0 evidence: raw contract, exact linked ledger, range, alignment, and H2 withdrawal passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
