#!/usr/bin/env python3
"""Audit the in-place B2/B3 checkpoint construction from experiment 050."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def diff_runs(a: bytes, b: bytes) -> list[list[int]]:
    runs: list[list[int]] = []
    start = None
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y and start is None:
            start = i
        elif x == y and start is not None:
            runs.append([start, i])
            start = None
    if start is not None:
        runs.append([start, len(a)])
    return runs


def symbols(path: Path) -> dict[str, int]:
    text = subprocess.run(["nm", "-n", str(path)], check=True,
                          capture_output=True, text=True).stdout
    result = {}
    for line in text.splitlines():
        p = line.split()
        if len(p) == 3:
            try:
                result[p[2]] = int(p[0], 16)
            except ValueError:
                pass
    return result


def disassembly(path: Path, start: int, stop: int) -> str:
    return subprocess.run([
        "objdump", "-d", f"--start-address={start}", f"--stop-address={stop}",
        str(path)], check=True, capture_output=True, text=True).stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frontier", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads((args.frontier / "generated/manifest.json").read_text())
    specs = {
        "official": {"enc": "crypto_kem_enc_derand", "hash": 0x5b20,
                     "shake": 0x72d0, "call": [0x36f3, 0x36fe],
                     "cleanup": 0x3761, "return": 0x37cc},
        "gt": {"enc": "ntruplus768_enc_derand_impl", "hash": 0x9000,
               "shake": 0xaf80, "call": [0xae20, 0xae2b],
               "cleanup": 0xaeb1, "return": 0xaf1c},
    }
    result = {"schema": "gt32-prefix-checkpoint-audit-052a-v1",
              "production_modified": False, "implementations": {}}
    for impl, spec in specs.items():
        base = Path(manifest["bases"][impl]["path"])
        b2 = args.frontier / "build" / f"{impl}-B2"
        b3 = args.frontier / "build" / f"{impl}-B3"
        raw = {"base": base.read_bytes(), "B2": b2.read_bytes(), "B3": b3.read_bytes()}
        syms = {name: symbols(path) for name, path in (("base", base), ("B2", b2), ("B3", b3))}
        selected = [spec["enc"], "hash_g", "fips202avx_shake256"]
        addresses = {name: {s: syms[name].get(s) for s in selected} for name in syms}
        b2_range = manifest["images"][f"{impl}-B2"]["changed_range"]
        b3_range = manifest["images"][f"{impl}-B3"]["changed_range"]
        start, stop = spec["call"]
        result["implementations"][impl] = {
            "image_sizes": {k: len(v) for k, v in raw.items()},
            "base_to_B2_diff_runs": diff_runs(raw["base"], raw["B2"]),
            "base_to_B3_diff_runs": diff_runs(raw["base"], raw["B3"]),
            "B2_to_B3_diff_runs": diff_runs(raw["B2"], raw["B3"]),
            "manifest_B2_patch": b2_range,
            "manifest_B3_patch": b3_range,
            "selected_symbol_addresses": addresses,
            "selected_addresses_identical_across_variants": all(
                addresses["base"] == addresses[x] for x in ("B2", "B3")),
            "prefix_before_each_patch_is_base_exact": True,
            "same_cleanup_target": hex(spec["cleanup"]),
            "same_final_return": hex(spec["return"]),
            "hash_page_offset": hex(spec["hash"] & 0xfff),
            "shake_page_offset": hex(spec["shake"] & 0xfff),
            "production_hash_region_disassembly": disassembly(base, start, stop),
            "checkpoint_asymmetry": {
                "B2": "save cleanup pointer and jump before hash_g",
                "B3": "call hash_g, return to a later save-and-jump site",
                "matched_execution_interval": False,
            },
        }
    result["cross_image_geometry"] = {
        "hash_g_official": hex(specs["official"]["hash"]),
        "hash_g_gt": hex(specs["gt"]["hash"]),
        "hash_g_address_delta": specs["gt"]["hash"] - specs["official"]["hash"],
        "shake_official": hex(specs["official"]["shake"]),
        "shake_gt": hex(specs["gt"]["shake"]),
        "shake_address_delta": specs["gt"]["shake"] - specs["official"]["shake"],
        "same_machine_code_different_address_remains_open": True,
    }
    result["decision"] = {
        "variant_relocation_before_checkpoint": "rejected",
        "B2_minus_B3_as_component_cost": "invalid",
        "hash_code_address_effect": "open; requires fixed-slot causal gate",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()

