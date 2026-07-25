#!/usr/bin/env python3
"""Reject generic/reference symbols from a selected GT full-KEM binary."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


FORBIDDEN = {
    "baseinv",
    "basemul",
    "poly_basemul_normal",
    "basemul_add",
    "gt_kpqc_block_to_gt_block",
    "invntt",
    "poly_invntt_normal",
    "invntt_gt_rowbitrevlayout",
    "invntt_gt_rowbitrevlayout_exact",
    "ntt",
    "ntt_gt_rowbitrevlayout",
    "poly_frombytes_gt_canonical_ref",
    "poly_tobytes_gt_canonical_p1",
    "poly_tobytes_gt_canonical_ref",
}

COMMON_REQUIRED = {
    "crypto_kem_dec",
    "crypto_kem_enc",
    "crypto_kem_keypair",
    "gt_decap_verify_pointwise",
    "poly_basemul_add_encap_direct32_q31_tobytes_contract",
    "poly_basemul",
    "poly_frombytes_gt_canonical_u1",
    "poly_invntt",
    "poly_ntt",
    "poly_tobytes_gt_canonical",
    "poly_triple",
}

KEYGEN_REQUIRED = {
    "mixed": {
        "gt_keygen_baseinv_bpq_to_cq_scaled_r",
        "gt_keygen_basemul_bpq_cq_to_cq_scaled_r",
        "gt_keygen_blockmajor_to_bpq",
        "gt_keygen_tobytes_bpq_p1",
        "gt_keygen_tobytes_cq",
    },
    "cq": {
        "gt_keygen_baseinv_cq_to_cq_scaled_r",
        "gt_keygen_basemul_cq_cq_to_cq_scaled_r",
        "gt_keygen_poly_ntt_to_cq",
        "gt_keygen_tobytes_cq",
    },
}

KEYGEN_FORBIDDEN = {
    "mixed": {
        "gt_keygen_baseinv_cq_to_cq_scaled_r",
        "gt_keygen_basemul_cq_cq_to_cq_scaled_r",
        "gt_keygen_poly_ntt_to_cq",
    },
    "cq": {
        "gt_keygen_baseinv_bpq_to_cq_scaled_r",
        "gt_keygen_basemul_bpq_cq_to_cq_scaled_r",
        "gt_keygen_blockmajor_to_bpq",
        "gt_keygen_tobytes_bpq_p1",
    },
}


def defined_symbols(binary: Path, nm: str) -> set[str]:
    output = subprocess.run(
        [nm, "--defined-only", str(binary)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout
    return {line.split()[-1].lstrip("_") for line in output.splitlines() if line.split()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--nm", default="nm")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--keygen-layout", choices=sorted(KEYGEN_REQUIRED),
                        default="mixed")
    args = parser.parse_args()

    symbols = defined_symbols(args.binary, args.nm)
    forbidden = FORBIDDEN | KEYGEN_FORBIDDEN[args.keygen_layout]
    required = COMMON_REQUIRED | KEYGEN_REQUIRED[args.keygen_layout]
    forbidden_present = sorted(forbidden & symbols)
    required_missing = sorted(required - symbols)
    result = {
        "binary": str(args.binary),
        "keygen_layout": args.keygen_layout,
        "forbidden_present": forbidden_present,
        "required_missing": required_missing,
        "status": "pass" if not forbidden_present and not required_missing else "fail",
    }

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
