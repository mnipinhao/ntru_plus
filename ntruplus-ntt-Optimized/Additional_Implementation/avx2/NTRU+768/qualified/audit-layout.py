#!/usr/bin/env python3
"""Audit the E0V -> QL2 -> direct-r-hash production layout contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


EXCLUDED = {"ntruplus768_enc_derand_impl",
            "ntruplus768_hash_g_from_m_avx2"}


def out(command: list[str]) -> str:
    return subprocess.check_output(command, text=True)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path: Path) -> dict[str, tuple[int, int, str]]:
    result = {}
    for line in out(["nm", "-S", "-n", str(path)]).splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[2].lower() in {"t", "r"}:
            result[fields[3]] = (int(fields[0], 16), int(fields[1], 16), fields[2])
    return result


def section(path: Path, name: str) -> tuple[int, int, str]:
    for line in out(["readelf", "-SW", str(path)]).splitlines():
        match = re.match(
            r"\s*\[\s*\d+\]\s+(\S+)\s+\S+\s+([0-9a-fA-F]+)\s+"
            r"[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+(\S+)", line)
        if match and match.group(1) == name:
            return int(match.group(2), 16), int(match.group(3), 16), match.group(4)
    raise SystemExit(f"missing section {name} in {path}")


def function_bytes(path: Path, address: int, size: int) -> bytes:
    text = out(["objdump", "-d", f"--start-address={address}",
                f"--stop-address={address + size}", str(path)])
    encoded: list[str] = []
    for line in text.splitlines():
        match = re.match(r"\s*[0-9a-f]+:\s+((?:[0-9a-f]{2}\s+)+)", line)
        if match:
            encoded.extend(match.group(1).split())
    return bytes.fromhex("".join(encoded))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve()
    binaries = {name: build / f"measure-{name}"
                for name in ("e0v", "ql2", "rhash")}
    maps = {name: symbols(path) for name, path in binaries.items()}
    comparison_results = {}
    for control_name, candidate_name in (("e0v", "ql2"),
                                         ("ql2", "rhash")):
        mismatches = []
        checked = 0
        common = set(maps[control_name]) & set(maps[candidate_name])
        for name in sorted(common):
            if name in EXCLUDED or name.startswith(("supercop", "cpucycles")):
                continue
            control = maps[control_name][name]
            candidate = maps[candidate_name][name]
            if control != candidate:
                mismatches.append({"symbol": name,
                                   "reason": "address/size/type",
                                   "control": control,
                                   "candidate": candidate})
                continue
            if control[2].lower() == "t" and control[1]:
                if function_bytes(binaries[control_name], *control[:2]) != \
                        function_bytes(binaries[candidate_name], *candidate[:2]):
                    mismatches.append({"symbol": name,
                                       "reason": "machine bytes"})
                    continue
            checked += 1
        if mismatches:
            raise SystemExit(json.dumps(mismatches[:20], indent=2))
        if checked < 80:
            raise SystemExit(f"only {checked} symbols audited for "
                             f"{control_name}->{candidate_name}")
        comparison_results[f"{control_name}_to_{candidate_name}"] = {
            "symbols_checked": checked, "mismatches": 0}

    helper_name = "ntruplus768_hash_g_from_m_avx2"
    helper = {name: maps[name][helper_name] for name in binaries}
    if len({value[:2] for value in helper.values()}) != 1:
        raise SystemExit(f"helper geometry mismatch: {helper}")
    helper_bytes = {
        name: function_bytes(binaries[name], *value[:2])
        for name, value in helper.items()
    }
    if len(set(helper_bytes.values())) != 1:
        raise SystemExit("helper machine bytes mismatch")

    rodata = {name: section(path, ".rodata")[:2] for name, path in binaries.items()}
    if len(set(rodata.values())) != 1:
        raise SystemExit(f"rodata geometry mismatch: {rodata}")
    rodata_hash = {}
    for name, path in binaries.items():
        dumped = build / f"rodata-{name}.bin"
        subprocess.run(["objcopy", "--dump-section", f".rodata={dumped}", str(path)],
                       check=True)
        rodata_hash[name] = sha(dumped)
    if len(set(rodata_hash.values())) != 1:
        raise SystemExit(f"rodata bytes mismatch: {rodata_hash}")

    tails = {section_name: {name: section(path, section_name)
                            for name, path in binaries.items()}
             for section_name in (".e0v_tail", ".ql2_tail", ".rhash_tail")}
    for section_name, profiles in tails.items():
        for name, (address, _size, flags) in profiles.items():
            if address % 4096 or "A" not in flags or "X" not in flags or "W" in flags:
                raise SystemExit(f"invalid {name} {section_name}: {profiles[name]}")
        if len({value[:2] for value in profiles.values()}) != 1:
            raise SystemExit(f"{section_name} mismatch: {profiles}")
    for name, path in binaries.items():
        if re.search(r"RWE", out(["readelf", "-lW", str(path)])):
            raise SystemExit(f"RWX segment in {name}")

    control_slot = section(build / "objects/encap-e0v.o",
                           ".text.ntruplus768_enc_derand_impl")[1]
    ql2_slot = section(build / "objects/encap-ql2.o",
                       ".text.ntruplus768_enc_derand_impl")[1]
    rhash_slot = section(build / "objects/encap-rhash.o",
                         ".text.ntruplus768_enc_derand_impl")[1]
    if (control_slot, ql2_slot, rhash_slot) != (611, 611, 611):
        raise SystemExit("caller slot contract failed: "
                         f"{control_slot}, {ql2_slot}, {rhash_slot}")

    result = {
        "status": "PASS",
        "comparisons": comparison_results,
        "caller_slot_bytes": {"e0v": control_slot, "ql2": ql2_slot,
                              "rhash": rhash_slot},
        "encap_symbols": {name: maps[name]["ntruplus768_enc_derand_impl"][:2]
                          for name in binaries},
        "rhash_helper": {
            "symbols": {name: value[:2] for name, value in helper.items()},
            "machine_bytes_identical": True,
        },
        "tails": {section_name: {
            name: {"address": value[0], "size": value[1], "flags": value[2]}
            for name, value in profiles.items()}
            for section_name, profiles in tails.items()},
        "rodata": {"geometry": rodata, "sha256": rodata_hash},
        "elf_sha256": {name: sha(path) for name, path in binaries.items()},
        "security": {"rwx_segment": False, "tails_page_aligned_rx": True},
    }
    (build / "layout-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
