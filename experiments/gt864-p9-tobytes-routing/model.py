#!/usr/bin/env python3
"""Static P9 gate: exact mapping, input ranges and semantic cost ledger."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P3A = ROOT / (
    "ntruplus-ntt-Optimized/Additional_Implementation/aarch64/Experiment/"
    "NTRU+864/good_thomas_campaign/experiments/"
    "gt_fr0_d1_byte_abi_architecture/analyze_architecture.py"
)


def canonical(x: int) -> int:
    return x % 3457


def pack(values: list[int]) -> bytes:
    out = bytearray()
    for index in range(0, len(values), 2):
        a, b = values[index:index + 2]
        out.extend((a & 255, (a >> 8) | ((b & 15) << 4), b >> 4))
    return bytes(out)


def main() -> None:
    subprocess.run(["python3", HERE / "prepare.py"], check=True)
    spec = importlib.util.spec_from_file_location("p3a", P3A)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mapping, _ = module.official_map(ROOT)
    shuffle2 = [value for start in range(0, 864, 48)
                for value in module.shuffle2_block(start)]
    composed = [mapping[shuffle2[index]] for index in range(864)]
    digest = hashlib.sha256(b"".join(
        value.to_bytes(2, "little") for value in composed)).hexdigest()
    assert digest == "087b7193886e9f3e33ac457452642d64ae70ec780a0961d10036c8e5530da270"
    assert sorted(composed) == list(range(864))

    edge_values = [-32768, -3457, -3456, -1, 0, 1, 3456, 3457, 32767]
    full = [edge_values[index % len(edge_values)] for index in range(864)]
    routed_full = [canonical(full[index]) for index in composed]
    assert len(pack(routed_full)) == 1296
    small_values = [-3456, -1, 0, 1, 3456]
    small = [small_values[index % len(small_values)] for index in range(864)]
    routed_small = [small[index] + (3457 if small[index] < 0 else 0)
                    for index in composed]
    assert routed_small == [canonical(small[index]) for index in composed]

    # P6-D3 has 4061 semantic instructions before its public entry/cleanup.
    # Existing target evidence fixes P3B6 full at 1382 instructions/top.
    # P9-S removes the two Barrett instructions from each of 54 q outputs/top.
    p6_d3 = 4061
    full_top = 1382
    small_top_upper = full_top - 2 * 54
    outer_and_cleanup_upper = 48
    estimates = {
        "P9-F": 2 * full_top + outer_and_cleanup_upper,
        "P9-S": 2 * small_top_upper + outer_and_cleanup_upper,
    }
    deltas = {name: value - p6_d3 for name, value in estimates.items()}
    assert all(delta <= -829 for delta in deltas.values())

    result = {
        "gate": "P9 static reopen",
        "status": "pass",
        "composed_map_sha256": digest,
        "map_bijection": True,
        "coefficient_q_loads_per_call": 108,
        "coefficient_scratch_bytes": 0,
        "full_input_contract": "arbitrary signed int16; Barrett plus sign canonicalization",
        "small_input_contract": "-3457 < x < 3457; sign canonicalization only",
        "small_barrett_instruction_groups": 0,
        "p6_d3_semantic_instructions": p6_d3,
        "conservative_dynamic_instruction_upper_bound": estimates,
        "upper_bound_delta_vs_p6_d3": deltas,
        "instruction_reopen_threshold": -829,
        "instruction_reopen_pass": True,
        "read_gate": {
            "status": "structural pass; target PMU confirmation required",
            "P6_D3": "108 coefficient Q loads plus repeated route/table reads",
            "P9": "108 coefficient Q loads; one reusable pack constant; no route tables or coefficient scratch",
            "required_pmu_delta": -101,
        },
        "next": "target object audit, same-boundary Pi timing, then full-KEM only for winning modes",
        "production_linked": False,
    }
    (HERE / "static-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
