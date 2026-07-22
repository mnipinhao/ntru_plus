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
    "basemul_add",
    "gt_kpqc_block_to_gt_block",
    "invntt",
    "invntt_gt_rowbitrevlayout",
    "invntt_gt_rowbitrevlayout_exact",
    "ntt",
    "ntt_gt_rowbitrevlayout",
    "poly_frombytes_gt_canonical_ref",
    "poly_tobytes_gt_canonical_p1",
    "poly_tobytes_gt_canonical_ref",
    "poly_triple",
}

REQUIRED = {
    "crypto_kem_dec",
    "crypto_kem_enc",
    "crypto_kem_keypair",
    "gt_decap_verify_pointwise",
    "gt_keygen_baseinv_bpq_to_cq_scaled_r",
    "gt_keygen_basemul_bpq_cq_to_cq_scaled_r",
    "poly_basemul_add_encap_direct32_q31_tobytes_contract",
    "poly_basemul_rminus1",
    "poly_frombytes_gt_canonical_u1",
    "poly_invntt_from_rminus1",
    "poly_ntt",
    "poly_tobytes_gt_canonical",
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
    args = parser.parse_args()

    symbols = defined_symbols(args.binary, args.nm)
    forbidden_present = sorted(FORBIDDEN & symbols)
    required_missing = sorted(REQUIRED - symbols)
    result = {
        "binary": str(args.binary),
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
