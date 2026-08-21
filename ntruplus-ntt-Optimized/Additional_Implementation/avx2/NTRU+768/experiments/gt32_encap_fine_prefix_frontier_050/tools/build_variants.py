#!/usr/bin/env python3
"""Patch the frozen 043 images into fine Encap prefix-frontier variants."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


CHECKPOINTS = ("A1", "A2", "A3", "B1", "B2", "B3", "D", "T0", "T1", "E")

# Entry format: address, complete-instruction byte count, expected bytes,
# exit kind. Normal exits run the production cleanup. Minimal exits are used
# only for the matched T0/T1 tail pair.
SPECS = {
    "official": {
        "cleanup": 0x3761, "return": 0x37cc,
        "saved_pointer": bytes.fromhex("4c89742418"),
        "patches": {
            "A1": (0x365b, 38,
                   "c4c17e6f0424894424044c89ee488dbc2490180000"
                   "4c8db42430180000c5fe7f842430180000", "a1"),
            "A2": (0x36c1, 16, "488db424d0180000488dbc24200c0000", "normal"),
            "A3": (0x36d6, 21,
                   "488dbc24200c0000e89d080000488db424200c0000", "normal"),
            "B1": (0x36e3, 11, "488db424200c00004889df", "normal"),
            "B2": (0x36f3, 11, "4889de4889dfe822240000", "normal"),
            "B3": (0x36fe, 11, "4889da4c89f64c89742418", "normal"),
            "D":  (0x3754, 8, "488d7424204889df", "cleanup"),
            "T0": (0x3754, 8, "488d7424204889df", "minimal"),
            "T1": (0x3761, 5, "488b442410", "minimal"),
        },
    },
    "gt": {
        "cleanup": 0xaeb1, "return": 0xaf1c,
        "saved_pointer": bytes.fromhex("4c89742438"),
        "patches": {
            "A1": (0xad6c, 41,
                   "c5fe6f03894424244c89ee488dbc24b01e0000"
                   "4c8db424501e0000c5fe7f8424501e0000c5fe6f4320", "a1"),
            "A2": (0xadd1, 16, "488db424f01e0000488dbc2440180000", "normal"),
            "A3": (0xade6, 16, "488db42440180000488dbc2440120000", "normal"),
            "B1": (0xae10, 16, "488db424400600004c89e7e8e0bbffff", "normal"),
            "B2": (0xae20, 11, "4c89e64c89e7e8d5e1ffff", "normal"),
            "B3": (0xae2b, 16, "488b7424384c89e2488dbc2440180000", "normal"),
            "D":  (0xaea1, 8, "488db42440120000", "cleanup"),
            "T0": (0xaea1, 8, "488db42440120000", "minimal"),
            "T1": (0xaeb1, 5, "488b442430", "minimal"),
        },
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jump(source: int, target: int) -> bytes:
    return b"\xe9" + struct.pack("<i", target - source - 5)


def a1_shim(implementation: str, source: int, target: int) -> bytes:
    if implementation == "official":
        # eax=0; save return code; initialize the two pointer slots consumed
        # by the original cleanup; r14 points at the clearable hash buffer.
        prefix = bytes.fromhex(
            "31c089442404488d8424b01800004889442408"
            "4c8db424301800004c89742418")
    else:
        prefix = bytes.fromhex(
            "31c089442424488d8424d01e00004889442428"
            "4c8db424501e00004c89742438")
    return prefix + jump(source + len(prefix), target)


def make(base: bytes, implementation: str, checkpoint: str):
    image = bytearray(base)
    if checkpoint == "E":
        return image, None
    start, length, expected_hex, kind = SPECS[implementation]["patches"][checkpoint]
    expected = bytes.fromhex(expected_hex)
    if len(expected) != length or bytes(image[start:start + length]) != expected:
        raise SystemExit(f"{implementation}-{checkpoint}: anchor mismatch")
    if kind == "a1":
        replacement = a1_shim(implementation, start, SPECS[implementation]["cleanup"])
    elif kind == "normal":
        prefix = SPECS[implementation]["saved_pointer"]
        replacement = prefix + jump(start + len(prefix), SPECS[implementation]["cleanup"])
    elif kind == "cleanup":
        replacement = jump(start, SPECS[implementation]["cleanup"])
    elif kind == "minimal":
        replacement = jump(start, SPECS[implementation]["return"])
    else:
        raise AssertionError(kind)
    if len(replacement) > length:
        raise SystemExit(f"{implementation}-{checkpoint}: replacement overflow")
    replacement += b"\x90" * (length - len(replacement))
    image[start:start + length] = replacement
    return image, {"start": hex(start), "end": hex(start + length),
                   "bytes": length, "expected": expected.hex(),
                   "replacement": replacement.hex(), "exit": kind}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    sources = {"official": args.official, "gt": args.gt}
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"schema": "gt32-encap-fine-prefix-frontier-050-v1",
                "method": "byte patch of frozen 043 exact-production PIE",
                "bases": {}, "images": {}}
    for implementation, source in sources.items():
        base = source.read_bytes()
        manifest["bases"][implementation] = {
            "path": str(source.resolve()), "bytes": len(base), "sha256": digest(base)}
        for checkpoint in CHECKPOINTS:
            image, changed = make(base, implementation, checkpoint)
            path = args.output / f"{implementation}-{checkpoint}"
            path.write_bytes(image)
            path.chmod(0o755)
            manifest["images"][f"{implementation}-{checkpoint}"] = {
                "path": str(path.resolve()), "bytes": len(image),
                "sha256": digest(image), "changed_range": changed,
                "prefix_before_patch_byte_exact": True,
                "full_image_byte_exact": checkpoint == "E"}
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
