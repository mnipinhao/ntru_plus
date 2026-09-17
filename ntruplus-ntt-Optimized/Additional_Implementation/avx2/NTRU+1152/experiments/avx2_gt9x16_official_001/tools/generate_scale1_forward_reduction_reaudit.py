#!/usr/bin/env python3
"""Re-run the 512-mask Forward reduction proof with scale-1 alpha ranges."""
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-generator", type=Path, required=True)
    parser.add_argument("--tables", type=Path, required=True)
    parser.add_argument("--scale-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    base = runpy.run_path(str(args.base_generator))
    parse_array = base["parse_array"]
    mask_record = base["mask_record"]
    table_text = args.tables.read_text()
    kappa = parse_array(table_text, "ntruplus1152_exp001_paper_kappa")[0]
    zetas = parse_array(table_text, "ntruplus1152_exp001_ntt9_zeta")
    rhoinv = parse_array(table_text, "ntruplus1152_exp001_paper_rhoinv")[0]
    scale_audit = json.loads(args.scale_audit.read_text())
    branches = scale_audit["producer_scale1"]["branches"]

    records = [
        mask_record(mask, branches, kappa, zetas[4], rhoinv)
        for mask in range(512)
    ]
    valid = [record for record in records if record["valid"]]
    minimum = min(record["kept_per_branch_qblock"] for record in valid)
    minima = [
        record for record in valid
        if record["kept_per_branch_qblock"] == minimum
    ]
    selected = min(
        minima, key=lambda record: (record["peak_absolute_bound"], record["mask"])
    )
    report = {
        "schema": "scale1-forward-reduction-reaudit/v1",
        "contract": {
            "producer": "persistent-AoS + T0-beta + caller-wide scale-1",
            "input_domain": "branch-specific KEM-small scale-1 proof",
            "paper_R2_DAG": "unchanged",
            "NTT16_DAG": "unchanged",
            "output_scale": 1,
        },
        "search": {
            "masks": len(records),
            "valid_masks": len(valid),
            "mask_bit_one_means": "retain existing Barrett vector",
        },
        "minimum": {
            "retained_per_branch_qblock": minimum,
            "retained_per_forward": minimum * 8,
            "valid_minimum_masks": len(minima),
            "selected_mask": selected["mask"],
            "selected_registers": selected["kept_registers"],
            "peak_absolute_bound": selected["peak_absolute_bound"],
        },
        "decision": {
            "can_delete_more_under_current_interval_DAG": False,
            "next_freedom_needed": "radix-3 role/orientation change, correlated proof, or reduction fusion",
        },
    }
    text = json.dumps(report, indent=2) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit("stale scale-1 Forward reduction re-audit")
    else:
        args.output.write_text(text)
    print(json.dumps(report["minimum"], sort_keys=True))


if __name__ == "__main__":
    main()
