#!/usr/bin/env python3
"""Audit the 104 caller slot, frozen common image, and RX tails."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
BIN = {name: BUILD / f"measure-{name}" for name in ("control", "ql2")}
EXCLUDED = {"ntruplus768_enc_derand_impl"}


def out(command: list[str]) -> str:
    return subprocess.check_output(command, text=True)


def symbols(path: Path) -> dict[str, tuple[int, int, str]]:
    result = {}
    for line in out(["nm", "-S", "-n", str(path)]).splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[2].lower() in {"t", "r"}:
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16), fields[2])
    return result


def section(path: Path, name: str) -> tuple[int, int, str]:
    for line in out(["readelf", "-SW", str(path)]).splitlines():
        match = re.match(r"\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+"
                         r"[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+(\S+)", line)
        if match and match.group(1) == name:
            return int(match.group(2), 16), int(match.group(3), 16), match.group(4)
    raise SystemExit(f"missing {name} in {path}")


def bytes_at(path: Path, address: int, size: int) -> bytes:
    text = out(["objdump", "-d", f"--start-address={address}",
                f"--stop-address={address + size}", str(path)])
    encoded = []
    for line in text.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)", line)
        if match:
            encoded.extend(match.group(1).split())
    return bytes.fromhex("".join(encoded))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    maps = {name: symbols(path) for name, path in BIN.items()}
    mismatches = []
    checked = 0
    for name in sorted(set(maps["control"]) & set(maps["ql2"])):
        if name in EXCLUDED or name.startswith(("supercop", "cpucycles")):
            continue
        a, b = maps["control"][name], maps["ql2"][name]
        if a != b:
            mismatches.append({"symbol": name, "reason": "geometry", "control": a, "ql2": b})
        elif a[2].lower() == "t" and a[1] and bytes_at(BIN["control"], *a[:2]) != bytes_at(BIN["ql2"], *b[:2]):
            mismatches.append({"symbol": name, "reason": "bytes"})
        else:
            checked += 1
    if mismatches or checked < 80:
        raise SystemExit(json.dumps({"checked": checked, "mismatches": mismatches[:20]}, indent=2))
    tails = {section_name: {name: section(path, section_name)
                            for name, path in BIN.items()}
             for section_name in (".e0v_tail", ".ql2_tail")}
    for section_name, profiles in tails.items():
        if profiles["control"][:2] != profiles["ql2"][:2]:
            raise SystemExit(f"{section_name} geometry differs: {profiles}")
        for profile, (address, _size, flags) in profiles.items():
            if address % 4096 or "A" not in flags or "X" not in flags or "W" in flags:
                raise SystemExit(f"invalid {section_name} {profile}: {profiles[profile]}")
    for name, path in BIN.items():
        if re.search(r"RWE", out(["readelf", "-lW", str(path)])):
            raise SystemExit(f"RWX segment in {name}")
    slots = {name: section(BUILD / f"objects/encap-{name}.o",
                           ".text.ntruplus768_enc_derand_impl")[1]
             for name in BIN}
    if set(slots.values()) != {611}:
        raise SystemExit(f"caller slot mismatch: {slots}")
    anchor_path = BUILD / "anchor/measure-e0v"
    anchor_map = symbols(anchor_path)
    anchor_mismatches = []
    anchor_checked = 0
    for name in sorted(set(anchor_map) & set(maps["control"])):
        if name.startswith(("supercop", "cpucycles", "ntruplus768_ntt_ql2",
                            "ntruplus768_basemul_general_ql2",
                            "ntruplus768_pack_ql2")):
            continue
        a, b = anchor_map[name], maps["control"][name]
        if a != b:
            anchor_mismatches.append({"symbol": name, "reason": "geometry",
                                      "anchor": a, "control": b})
        elif a[2].lower() == "t" and a[1] and bytes_at(anchor_path, *a[:2]) != bytes_at(BIN["control"], *b[:2]):
            anchor_mismatches.append({"symbol": name, "reason": "bytes"})
        else:
            anchor_checked += 1
    if anchor_mismatches or anchor_checked < 80:
        raise SystemExit(json.dumps({"anchor_checked": anchor_checked,
                                     "anchor_mismatches": anchor_mismatches[:20]}, indent=2))
    result = {"status": "PASS", "preexisting_symbols_checked": checked,
              "preexisting_symbol_mismatches": 0, "caller_slots": slots,
              "b2a4bea_anchor_symbols_checked": anchor_checked,
              "b2a4bea_anchor_symbol_mismatches": 0,
              "encap_symbols": {name: maps[name]["ntruplus768_enc_derand_impl"][:2]
                                for name in BIN},
              "tails": {section_name: {name: {"address": value[0], "size": value[1], "flags": value[2]}
                                        for name, value in profiles.items()}
                        for section_name, profiles in tails.items()},
              "ql2_symbols": {name: maps["ql2"][name][:2] for name in
                              ("ntruplus768_ntt_ql2_avx2",
                               "ntruplus768_basemul_general_ql2_avx2",
                               "ntruplus768_pack_ql2_sum_avx2")},
              "security": {"rwx_segment": False, "tails_page_aligned_rx": True},
              "elf_sha256": {name: sha(path.read_bytes()) for name, path in BIN.items()}}
    (EXP / "generated/audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
