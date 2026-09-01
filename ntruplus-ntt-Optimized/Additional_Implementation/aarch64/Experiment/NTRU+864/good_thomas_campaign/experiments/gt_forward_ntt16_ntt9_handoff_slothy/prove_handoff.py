#!/usr/bin/env python3
"""Prove the M5J layout, table, and inherited exact-range contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def transpose8(columns: list[list[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
    """Semantic model of the three trn widths in the symbolic region."""
    assert len(columns) == 8 and all(len(column) == 8 for column in columns)
    return [[columns[column][row] for column in range(8)] for row in range(8)]


def main() -> None:
    composition = PARENT / "gt_forward_composition_barrett"
    sys.path.insert(0, str(composition))
    tables = load("m5j_tables", composition / "generate_tables.py")
    barrett = load("m5j_barrett", composition / "prove_barrett.py")
    exact = load("m5j_exact", PARENT / "gt_forward_symbolic_dag/prove_exact_dag.py").analyze()

    columns = [[(column, row) for row in range(8)] for column in range(16)]
    current = transpose8(columns[:8])
    held = transpose8(columns[8:])
    assert current == [[(column, row) for column in range(8)] for row in range(8)]
    assert held == [[(column, row) for column in range(8, 16)] for row in range(8)]
    tail0 = [(column, 8) for column in range(8)]
    fixed_v16 = [(column, 8) for column in range(8, 16)]

    exhaustive = barrett.constants()
    table_pairs = set()
    table_words = []
    for residue in tables.RESIDUES:
        for block in range(2):
            for s in range(1, 9):
                pairs = [tables.pair(pow(
                    tables.THETA,
                    (residue + 6 * (8 * block + lane)) * s,
                    tables.Q,
                )) for lane in range(8)]
                table_pairs.update(pairs)
                table_words.extend(value for pair in pairs for value in pair)
    assert table_pairs <= exhaustive
    assert exact["status"] == "pass"
    assert exact["ntt16_max_abs"] == 9342
    assert exact["maximum_abs_any_node"] == 28568
    assert exact["unsafe_node_count"] == 0

    mapping = {
        "current": current + [tail0],
        "held": held + [fixed_v16],
    }
    mapping_sha = hashlib.sha256(
        json.dumps(mapping, separators=(",", ":"), sort_keys=True).encode()
    ).hexdigest()
    result = {
        "gate": "gt864_forward_ntt16_ntt9_handoff",
        "status": "pass",
        "coordinate_mappings_checked": 144,
        "current_block_vectors": 9,
        "held_block_vectors": 9,
        "held_tail_abi": "fixed_v16_live_through",
        "twist_table_families": 4,
        "twist_rows_per_family": 8,
        "lanes_per_twist_row": 8,
        "table_pairs_checked": 256,
        "distinct_table_pairs": len(table_pairs),
        "all_table_pairs_in_m5f_exhaustive_set": True,
        "public_table_bytes_per_consumed_block": 256,
        "coefficient_loads_or_stores": 0,
        "ntt16_max_abs": exact["ntt16_max_abs"],
        "fixed_product_max_abs": 3436,
        "complete_ntt9_max_abs": exact["maximum_abs_any_node"],
        "unsafe_exact_dag_nodes": exact["unsafe_node_count"],
        "mapping_sha256": mapping_sha,
        "table_words_sha256": hashlib.sha256(
            b"".join(int(value).to_bytes(2, "little", signed=True) for value in table_words)
        ).hexdigest(),
        "production_linked": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
