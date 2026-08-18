#!/usr/bin/env python3
"""Census reachable production text and find inert intra-symbol tails.

The report is intentionally conservative.  ``executed_body_bytes`` means the
symbol prefix through its last non-padding instruction; it is not a claim that
every branch in that prefix executes on every call.  Only a suffix consisting
entirely of disassembler-recognized NOPs after the final semantic instruction
is classified as zero-cost removable text.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


# Exact successful-Encap multiplicities for the GT polynomial boundary.  The
# crypto/hash descendants are left unweighted because their internal loop
# counts depend on public input lengths and are not needed to rank GT kernels.
ENCAP_CALLS = {
    "crypto_kem_enc_derand_gt32_candidate": 1,
    "gt32_q24_decode_soa_asm": 1,
    "gt32_q24_decode_soa_body_cage": 1,
    "gt32_tile4_frontend_wide_raw_asm": 2,
    "gt32_tile4_attr_forward_all_bm_soa_asm": 2,
    "gt32_tile4_basemul_general_soa_soa_to_soa_asm": 1,
    "gt32_q24_encode_soa_lazy10788_asm": 2,
    "gt32_q24_encode_soa_encap_hr_h1_asm": 1,
    "hash_f": 1,
    "hash_g": 1,
    "hash_h": 1,
}


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def symbols(elf: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    line_re = re.compile(r"^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+\w\s+(\S+)$")
    for line in run("nm", "-S", "--defined-only", str(elf)).splitlines():
        match = line_re.match(line.strip())
        if match:
            address, size, name = match.groups()
            result[name] = {"address": int(address, 16), "symbol_bytes": int(size, 16)}
    return result


def instructions(elf: Path, symbol: str) -> list[dict[str, object]]:
    text = run("objdump", "-d", f"--disassemble={symbol}", str(elf))
    insn_re = re.compile(
        r"^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2}\s+)+)\s*([a-zA-Z][a-zA-Z0-9.]*)"
    )
    output = []
    for line in text.splitlines():
        match = insn_re.match(line)
        if not match:
            continue
        address, raw, mnemonic = match.groups()
        output.append({
            "address": int(address, 16),
            "bytes": len(raw.split()),
            "mnemonic": mnemonic,
        })
    return output


def is_nop(mnemonic: str) -> bool:
    return mnemonic.startswith("nop") or mnemonic in {"xchg"}


def section_bytes(elf: Path, section: str) -> int:
    for line in run("readelf", "-SW", str(elf)).splitlines():
        fields = line.split()
        if len(fields) >= 7 and fields[1] == section:
            return int(fields[5], 16)
    raise ValueError(f"missing {section} in {elf}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--reachability", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    reach = json.loads(args.reachability.read_text())
    encap = reach["operations"]["enc"]["functions"]
    table = symbols(args.elf)
    rows = []
    for name in encap:
        if name not in table:
            continue
        meta = table[name]
        insns = instructions(args.elf, name)
        last_semantic = None
        for insn in insns:
            if not is_nop(str(insn["mnemonic"])):
                last_semantic = insn
        body_end = meta["address"]
        if last_semantic is not None:
            body_end = int(last_semantic["address"]) + int(last_semantic["bytes"])
        symbol_end = meta["address"] + meta["symbol_bytes"]
        trailing = max(0, symbol_end - body_end)
        trailing_insns = [i for i in insns if int(i["address"]) >= body_end]
        zero_cost = trailing > 0 and all(is_nop(str(i["mnemonic"])) for i in trailing_insns)
        calls = ENCAP_CALLS.get(name)
        rows.append({
            "symbol": name,
            **meta,
            "executed_body_bytes_upper_bound": body_end - meta["address"],
            "trailing_padding_bytes": trailing if zero_cost else 0,
            "encap_dynamic_invocations": calls,
            "body_bytes_times_calls": None if calls is None else (body_end - meta["address"]) * calls,
            "classification": (
                "fully-unrolled-q24-serializer" if name == "gt32_q24_encode_soa_lazy10788_asm"
                else "unrolled-gt-frontend" if name == "gt32_tile4_frontend_wide_raw_asm"
                else "q24-codec" if "q24" in name
                else "other-reachable"
            ),
        })

    rows.sort(key=lambda row: (-int(row["symbol_bytes"]), str(row["symbol"])))
    removable = sum(int(row["trailing_padding_bytes"]) for row in rows)
    report = {
        "schema": "ntruplus768-gt32-reachable-hot-text-compaction-v1",
        "experiment": "PRODUCTION-REACHABLE-HOT-TEXT-COMPACTION-001",
        "elf": str(args.elf.resolve()),
        "text_bytes": section_bytes(args.elf, ".text"),
        "encap_reachable_named_bytes": sum(int(row["symbol_bytes"]) for row in rows),
        "zero_cost_trailing_padding_bytes": removable,
        "rows": rows,
        "phase_b_decision": (
            "eligible-zero-cost-closure" if removable else "no-intra-symbol-padding-found"
        ),
        "notes": [
            "executed_body_bytes_upper_bound is a static symbol prefix, not path coverage",
            "only all-NOP suffixes after the last semantic instruction are removable",
            "dynamic counts are exact for the successful GT polynomial boundary; hash descendants are intentionally unweighted",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
