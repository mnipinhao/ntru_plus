#!/usr/bin/env python3
"""Summarize the PROD3 cumulative native SUPERCOP rebase."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

from supercop_workflow import sha256_file


def calls(elf: Path, symbol: str) -> list[str]:
    disassembly = subprocess.run(
        ["objdump", "-d", "-M", "intel", str(elf)], check=True, text=True,
        stdout=subprocess.PIPE,
    ).stdout
    match = re.search(
        rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(?P<body>.*?)(?=\n\n|\Z)",
        disassembly, re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise SystemExit(f"missing linked symbol: {symbol}")
    return re.findall(r"\bcall\s+[0-9a-f]+ <([^>]+)>", match.group("body"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--old-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    official = json.loads((args.result_root / "native-official/stq-summary.json").read_text())
    candidate = json.loads((args.result_root / "native-candidate/stq-summary.json").read_text())
    kat = json.loads((args.result_root / "kat.json").read_text())
    old = json.loads(args.old_summary.read_text())
    operations = {}
    for operation in ("keypair_cycles", "enc_cycles", "dec_cycles"):
        off = official["operations"][operation]["stq2"]
        cand = candidate["operations"][operation]["stq2"]
        operations[operation] = {
            "official_stq2": off,
            "candidate_stq2": cand,
            "delta_cycles": cand - off,
            "delta_percent": 100.0 * (cand - off) / off,
        }
    old_enc_delta = old["native_supercop"]["operations"]["enc_cycles"]["delta_cycles"]
    new_enc_delta = operations["enc_cycles"]["delta_cycles"]
    elf = args.result_root / "native-candidate/measure"
    linked_calls = calls(elf, "crypto_kem_enc_derand")
    expected = {
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta": 2,
        "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4": 1,
        "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q": 2,
        "ntruplus1152_exp001_f0_ma2_native_full": 0,
        "ntruplus1152_exp001_prod3_hash_bytes": 0,
    }
    counts = {name: linked_calls.count(name) for name in expected}
    if counts != expected:
        raise SystemExit(f"cumulative linked call graph changed: {counts}")
    result = {
        "schema": "gt9x16-prod3-cumulative-native-rebase/v1",
        "benchmark_class": "supercop-native-kem",
        "supercop_version": "20260627",
        "parameter": 1152,
        "cpu": 1,
        "frequency_policy": "performance-governor-turbo-disabled",
        "official": official["measure_identity"],
        "candidate": candidate["measure_identity"],
        "fresh_process_launches": 9,
        "observations_per_operation": 864,
        "operations": operations,
        "kat": {
            "passed": kat["passed"],
            "cases": kat["cases"],
            "request_sha256": kat["request_sha256"],
            "response_sha256": kat["response_sha256"],
        },
        "linked_call_graph": {
            "symbol": "crypto_kem_enc_derand",
            "counts": counts,
            "measure_elf_sha256": sha256_file(elf),
        },
        "cross_campaign_coordinate": {
            "old_enc_delta_cycles": old_enc_delta,
            "new_enc_delta_cycles": new_enc_delta,
            "gap_narrowing_cycles": old_enc_delta - new_enc_delta,
            "warning": "different native campaigns; not an additive causal attribution",
        },
        "decision": {
            "native_encap_winner": new_enc_delta < 0,
            "promotion": False,
            "next_checkpoint": "ENCAP-CALLER-ATTRIBUTION-V2",
            "new_asm_authorized": False,
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"summary is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
