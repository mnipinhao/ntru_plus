#!/usr/bin/env python3
"""Verify that H0/H1/H2 differ only in linked function geometry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_hot_function_reachability import functions
from analyze_production_hot_code_closure import normalized_disassembly, sections, symbols


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("h0", type=Path)
    parser.add_argument("h1", type=Path)
    parser.add_argument("h2", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    images = {"H0": args.h0, "H1": args.h1, "H2": args.h2}
    image_symbols = {label: symbols(path) for label, path in images.items()}
    typed_functions = {label: functions(path) for label, path in images.items()}
    common_functions = sorted(set.intersection(*(set(items) for items in typed_functions.values())) - {"main", "measure"})
    equality = {}
    all_equal = True
    for name in common_functions:
        bodies = {label: normalized_disassembly(path, name) for label, path in images.items()}
        equal = bodies["H0"] == bodies["H1"] == bodies["H2"]
        all_equal &= equal
        equality[name] = {"equal": equal, "instruction_counts": {label: len(body) for label, body in bodies.items()}}
    hot = [
        "crypto_kem_enc_derand_gt32_candidate", "gt32_q24_decode_soa_asm",
        "hash_f", "hash_h", "poly_cbd1", "poly_sotp_encode",
        "gt32_tile4_frontend_wide_raw_asm", "gt32_tile4_attr_forward_all_bm_soa_asm",
        "gt32_q24_encode_soa_lazy10788_asm", "hash_g",
        "gt32_tile4_basemul_general_soa_soa_to_soa_asm", "poly_add",
        "gt32_q24_encode_soa_encap_hr_h1_asm",
    ]
    report = {
        "schema": "gt32-production-hot-function-grouping-static-v1",
        "sections": {label: sections(path) for label, path in images.items()},
        "common_function_count": len(common_functions),
        "all_common_function_bodies_equal": all_equal,
        "function_equivalence": equality,
        "hot_function_addresses": {
            label: {name: image_symbols[label][name]["address"] for name in hot if name in image_symbols[label]}
            for label in images
        },
        "acceptance": {
            "text_size_identical": len({sections(path)[".text"] for path in images.values()}) == 1,
            "common_bodies_identical": all_equal,
            "addresses_changed": any(
                image_symbols["H0"].get(name, {}).get("address") != image_symbols["H1"].get(name, {}).get("address")
                for name in hot
            ),
        },
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
