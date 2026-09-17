#!/usr/bin/env python3
"""Freeze the current scale-1 wire r fanout contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


N = 1152


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wire-layout", type=Path, required=True)
    parser.add_argument("--serializer", type=Path, required=True)
    parser.add_argument("--h4", type=Path, required=True)
    parser.add_argument("--forward-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    wire = json.loads(args.wire_layout.read_text())
    serializer = json.loads(args.serializer.read_text())
    h4 = json.loads(args.h4.read_text())
    forward = json.loads(args.forward_audit.read_text())
    source_to_wire = wire["source_to_wire"]
    if len(source_to_wire) != N or sorted(source_to_wire) != list(range(N)):
        raise SystemExit("wire layout is not a 1152-cell bijection")
    if serializer.get("symbol") != "ntruplus1152_exp001_direct_serializer_wire":
        raise SystemExit("unexpected wire serializer")
    producer = h4["symbols"]["producer_scale1"]
    expected_producer = (
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_"
        "wire_monotone_scale1_lazy_reduce")
    if producer != expected_producer:
        raise SystemExit("H4 does not consume the current scale-1 wire producer")

    contract = {
        "schema": "scale1-r-dual-output-fanout-contract/v1",
        "semantic_value": "Forward(r) modulo q",
        "producer": producer,
        "representation": {
            "cells": N,
            "owner": "(branch,p,q,terminal-coefficient)",
            "physical_order": "wire-monotone",
            "scale": 1,
            "montgomery_exponent": 0,
            "raw_representative": "lazy signed-i16; residue is normative",
            "mapping_bijection": True,
        },
        "consumers": {
            "ma2": {
                "symbol": h4["symbols"]["h4_m3b"],
                "requires_input_unchanged": True,
                "semantic_role": "r operand of h*r+m",
            },
            "hash_fanout": {
                "symbol": serializer["symbol"],
                "output": "1728 exact Official poly_tobytes bytes",
                "then": ["hash_g", "poly_sotp_encode"],
                "requires_input_unchanged": True,
            },
        },
        "alias_contract": {
            "r_state_distinct_from_hash_bytes": True,
            "serializer_must_not_mutate_r_state": True,
            "ma2_may_read_r_after_hash_fanout": True,
        },
        "correctness_gates": [
            "canonical Forward differential",
            "exact 1728-byte serializer differential",
            "r state immutability across serializer/hash fanout",
            "complete ciphertext and KAT byte equality",
        ],
        "benchmark_boundary": {
            "start": "coefficient-domain CBD1 r",
            "end": "wire r state retained for MA2 plus completed hash_g/SOTP m",
            "must_include": ["top split", "Forward", "serializer", "hash_g", "SOTP"],
            "must_not_claim": "isolated serializer timing as caller credit",
        },
        "linked_forward": {
            "instructions": forward["control"]["instructions"],
            "data_loads": forward["control"]["rdi_data_loads"],
            "data_stores": forward["control"]["rdi_data_stores"],
        },
        "decision": {
            "contract_frozen": True,
            "new_dual_output_asm_authorized": False,
            "next": "current wire tail T0/T1/T2 attribution",
        },
    }
    rendered = json.dumps(contract, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"stale contract: {args.output}")
    else:
        args.output.write_text(rendered)
    print("scale-1 r dual-output/fanout contract frozen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
