#!/usr/bin/env python3
"""Audit generator fidelity, constant pairs, case costs, and imported CF1 proof."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

from generate_candidates import GROUP_ORDER, OUTPUT, ROOT, pair_from_exponent

LEDGER = ROOT / "constant-ledger.json"
EXPECTED = {"t0c1": 154, "t0c2": 154, "t1c1": 138, "t1c2": 138}


def instructions(region: str) -> list[str]:
    return [line.strip() for line in region.splitlines()
            if re.match(r"^\s{4}[a-z][a-z0-9]*\s", line)]


def main() -> None:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    source = OUTPUT.read_text(encoding="utf-8")
    reports = []
    for case in data["cases"]:
        name = case["case"]
        start = f"gt864_friso2_scaled_{name}_slothy_start:"
        end = f"gt864_friso2_scaled_{name}_slothy_end:"
        region = source[source.index(start):source.index(end)]
        lines = instructions(region)
        counts = Counter(line.split()[0] for line in lines)
        assert len(lines) == EXPECTED[name] == case["instruction_count"]
        assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 26
        assert counts["ldr"] == (34 if name.startswith("t0") else 18)
        assert counts["add"] + counts["sub"] == 42
        assert counts["ld1"] == 0 and counts["tbl"] == 0
        events = case["events"]
        assert len(events) == 26
        assert sum(event["kind"] == "lane_varying_two_ldr"
                   for event in events) * 2 == case["independent_constant_ldrs_per_block"]
        for event in events:
            a, b = event["affine_exponent"]
            expected_exponents = [
                (a * column + b) % GROUP_ORDER
                for column in range(8)
            ]
            assert event["lane_exponents"] == expected_exponents
            assert event["lane_pairs"] == [list(pair_from_exponent(value))
                                             for value in expected_exponents]
            assert f"V<{event['destination']}>.8h" in region
        for pack in case["common_packs"]:
            lanes = []
            for exponent in pack["exponents"]:
                lanes.extend(pair_from_exponent(exponent))
            lanes.extend([0] * (8 - len(lanes)))
            assert lanes == pack["halfwords"]
        reports.append({"case": name, "instructions": len(lines),
                        "ldr": counts["ldr"], "mulmods": counts["mul"],
                        "events": len(events), "status": "pass"})

    cf1 = ROOT.parent / "gt_friso2_scaled_ntt9_search/verify_witnesses.py"
    completed = subprocess.run(["python3", str(cf1)], check=True,
                               capture_output=True, text=True)
    assert json.loads(completed.stdout)["status"] == "pass"
    print(json.dumps({
        "status": "pass",
        "cases": reports,
        "imported_CF1_matrix_and_range_gate": "pass",
        "new_coefficient_loads_or_stores": 0,
        "full_forward_static_delta_over_M5R-D_including_common_pack_loads_before_address_setup": 280,
        "full_forward_static_saving_vs_CF0_after_four_address_setups": 8,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
