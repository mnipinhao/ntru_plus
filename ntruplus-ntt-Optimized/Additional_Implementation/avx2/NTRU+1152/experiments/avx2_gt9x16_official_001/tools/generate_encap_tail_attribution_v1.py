#!/usr/bin/env python3
"""Freeze nested T0/T1/T2 boundaries for ENCAP-TAIL-ATTRIBUTION-V1."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(text: str, fragment: str, source: Path) -> None:
    if fragment not in text:
        raise SystemExit(f"missing {fragment!r} in {source}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--natural-asm", type=Path, required=True)
    parser.add_argument("--cumulative-ma2", type=Path, required=True)
    parser.add_argument("--h1-asm", type=Path, required=True)
    parser.add_argument("--kem", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    natural = args.natural_asm.read_text()
    cumulative = args.cumulative_ma2.read_text()
    h1 = args.h1_asm.read_text()
    kem = args.kem.read_text()
    for text, fragment, source in (
        (natural, "ntruplus1152_exp001_project_h_natural_q", args.natural_asm),
        (cumulative, "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4",
         args.cumulative_ma2),
        (natural, "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
         args.natural_asm),
        (h1, "ntruplus1152_exp001_prod3_ma2_hash_h1", args.h1_asm),
        (kem, "poly_basemul(&c, &h, &r);", args.kem),
        (kem, "poly_add(&c, &c, &m);", args.kem),
        (kem, "poly_tobytes(ct, &c);", args.kem),
    ):
        require(text, fragment, source)

    report = {
        "schema": "gt9x16-encap-tail-attribution-v1/v1",
        "checkpoint": "ENCAP-TAIL-ATTRIBUTION-V1-MAP",
        "frozen_inputs": {
            "producer_timed": False,
            "official_r_m_h": "resident pinned-Official NTT states",
            "gt_r_m": "resident Natural-Q T0-beta MA2 planes",
            "semantic_inputs": "identical modulo-q r/m/h",
        },
        "nested_boundaries": {
            "T0": {
                "official": "resident-h no-op wrapper",
                "gt": "ntruplus1152_exp001_project_h_natural_q",
                "delta": "GT_T0 - Official_T0",
                "meaning": "resident-h projection debt",
            },
            "T1": {
                "official": "poly_basemul + poly_add",
                "gt": "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4",
                "delta": "GT_T1 - Official_T1",
                "increment": "delta_T1 - delta_T0",
                "meaning": "MA2 arithmetic increment after h projection",
            },
            "T2": {
                "official": "poly_basemul + poly_add + poly_tobytes",
                "gt": "scale4 MA2 + Direct H1",
                "delta": "GT_T2 - Official_T2",
                "increment": "delta_T2 - delta_T1",
                "meaning": "ciphertext serializer increment",
            },
        },
        "identity": "delta_T0 + (delta_T1-delta_T0) + (delta_T2-delta_T1) = delta_T2",
        "measurement": {
            "method": "SUPERCOP-derived fixed-common O3GC paired cumulative boundaries",
            "order": "Official GT GT Official / GT Official Official GT",
            "launches": 9, "observations_per_label_per_launch": 96,
            "settings": ["normal-aslr-on", "normal-aslr-off",
                         "reversed-aslr-on", "reversed-aslr-off"],
            "headline": "preselected placement; no post-hoc fastest selection",
        },
        "correctness": {
            "T0": "projected-h raw differential against offline Natural-Q ownership map",
            "T1": "Official and GT result canonicalized to identical polynomial",
            "T2": "ciphertext bytes byte-exact",
        },
        "decision": {"new_arithmetic_asm": False,
                     "measure_source_next": True,
                     "native_kem": False, "promotion": False},
        "sha256": {"natural_asm": sha256(args.natural_asm),
                   "cumulative_ma2": sha256(args.cumulative_ma2),
                   "h1_asm": sha256(args.h1_asm), "kem": sha256(args.kem)},
    }
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != text:
            raise SystemExit(f"generated map is stale: {args.output}")
    else:
        args.output.write_text(text)
    print("ENCAP tail V1 map: nested T0 h / T1 MA2 / T2 serializer boundaries frozen")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
