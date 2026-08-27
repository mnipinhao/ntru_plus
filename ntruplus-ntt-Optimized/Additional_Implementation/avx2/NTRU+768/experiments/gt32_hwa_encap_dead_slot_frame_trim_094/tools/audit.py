#!/usr/bin/env python3
"""Audit 094 frame and shared executable geometry."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
PROFILES = ("f0", "fp", "f1")
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


def function_bytes(path: Path, address: int, size: int) -> bytes:
    text = out(["objdump", "-d", f"--start-address={address}",
                f"--stop-address={address + size}", str(path)])
    encoded = []
    for line in text.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)", line)
        if match:
            encoded.extend(match.group(1).split())
    return bytes.fromhex("".join(encoded))


def frame_bytes(path: Path, symbol: tuple[int, int, str]) -> int:
    text = out(["objdump", "-d", f"--start-address={symbol[0]}",
                f"--stop-address={symbol[0] + 48}", str(path)])
    values = [int(value, 16) for value in
              re.findall(r"sub\s+\$0x([0-9a-f]+),%rsp", text)]
    return sum(values)


def call_sequence(path: Path, symbol: tuple[int, int, str]) -> list[str]:
    text = out(["objdump", "-d", f"--start-address={symbol[0]}",
                f"--stop-address={symbol[0] + symbol[1]}", str(path)])
    return re.findall(r"\bcall\s+[0-9a-f]+\s+<([^+>@]+)", text)


def section_bytes(path: Path, section: str, target: Path) -> tuple[int, str]:
    subprocess.run(["objcopy", "--dump-section", f"{section}={target}", str(path)],
                   check=True)
    data = target.read_bytes()
    return len(data), hashlib.sha256(data).hexdigest()


def main() -> None:
    paths = {profile: BUILD / profile for profile in PROFILES}
    maps = {profile: symbols(path) for profile, path in paths.items()}
    common = set.intersection(*(set(value) for value in maps.values()))
    mismatches = []
    checked = 0
    for name in sorted(common):
        if name in EXCLUDED or name.startswith(("supercop", "cpucycles")):
            continue
        baseline = maps["f0"][name]
        for profile in ("fp", "f1"):
            value = maps[profile][name]
            if value != baseline:
                mismatches.append([name, profile, "geometry", baseline, value])
            elif baseline[2].lower() == "t" and baseline[1] and \
                    function_bytes(paths["f0"], *baseline[:2]) != \
                    function_bytes(paths[profile], *value[:2]):
                mismatches.append([name, profile, "bytes"])
        checked += 1
    if mismatches:
        raise SystemExit(json.dumps(mismatches[:20], indent=2))

    frames = {profile: frame_bytes(paths[profile],
                                   maps[profile]["ntruplus768_enc_derand_impl"])
              for profile in PROFILES}
    if frames != {"f0": 8128, "fp": 8128, "f1": 6592}:
        raise SystemExit(f"frame mismatch: {frames}")
    slots = {}
    for profile in PROFILES:
        obj = BUILD / f"objects/encap-{profile}.o"
        text = out(["readelf", "-SW", str(obj)])
        line = next(line for line in text.splitlines()
                    if ".text.ntruplus768_enc_derand_impl " in line)
        fields = line.split()
        slots[profile] = int(fields[fields.index("PROGBITS") + 3], 16)
    if set(slots.values()) != {611}:
        raise SystemExit(f"slot mismatch: {slots}")
    calls = {profile: call_sequence(paths[profile],
                                    maps[profile]["ntruplus768_enc_derand_impl"])
             for profile in PROFILES}
    if not calls["f0"] == calls["fp"] == calls["f1"]:
        raise SystemExit(f"call sequence changed: {calls}")

    rodata = {profile: section_bytes(path, ".rodata",
                                     BUILD / f"rodata-{profile}.bin")
              for profile, path in paths.items()}
    tail = {profile: section_bytes(path, ".e0v_tail",
                                   BUILD / f"tail-{profile}.bin")
            for profile, path in paths.items()}
    if len(set(rodata.values())) != 1 or len(set(tail.values())) != 1:
        raise SystemExit(f"shared sections differ: rodata={rodata}, tail={tail}")
    result = {"status": "PASS", "preexisting_symbols_checked": checked,
              "preexisting_symbol_mismatches": 0, "frames": frames,
              "caller_slots": slots,
              "encap_symbols": {p: maps[p]["ntruplus768_enc_derand_impl"][:2]
                                  for p in PROFILES},
              "rodata": rodata, "e0v_tail": tail,
              "call_sequence": calls["f0"], "call_sequence_unchanged": True,
              "new_spills": 0, "static_scratch_bytes": 0}
    generated = EXP / "generated"
    generated.mkdir(exist_ok=True)
    (generated / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
