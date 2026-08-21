#!/usr/bin/env python3
"""Build fixed-ELF Encap prefix-stop variants by patching frozen images."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


CHECKPOINTS = ("A", "B", "C", "D", "E")

# The frozen PIE executable LOAD segment maps file offset == virtual address.
# A-D jump to the implementation's original normal cleanup. E is byte-exact.
SPECS = {
    "official": {
        "cleanup": 0x3761,
        "patches": {
            # A must first initialize the cleanup's saved r14 pointer slot.
            "A": (0x36d6, 13, "488dbc24200c0000e89d080000",
                  bytes.fromhex("4c89742418")),
            # B likewise replaces the original delayed save with an equal
            # semantic save before taking the prefix exit.
            "B": (0x36fe, 11, "4889da4c89f64c89742418",
                  bytes.fromhex("4c89742418")),
            "C": (0x3723, 8, "488d9424200c0000", b""),
            "D": (0x3754, 8, "488d7424204889df", b""),
        },
    },
    "gt": {
        "cleanup": 0xaeb1,
        "patches": {
            "A": (0xade6, 8, "488db42440180000", b""),
            "B": (0xae2b, 5, "488b742438", b""),
            "C": (0xae6a, 8, "488d942440060000", b""),
            "D": (0xaea1, 8, "488db42440120000", b""),
        },
    },
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def near_jump(source: int, target: int) -> bytes:
    return b"\xe9" + struct.pack("<i", target - (source + 5))


def patch_image(base: bytes, implementation: str, checkpoint: str):
    image = bytearray(base)
    if checkpoint == "E":
        return image, None
    start, length, expected_hex, prefix = SPECS[implementation]["patches"][checkpoint]
    expected = bytes.fromhex(expected_hex)
    if len(expected) != length or bytes(image[start:start + length]) != expected:
        raise SystemExit(f"{implementation}-{checkpoint}: frozen patch anchor mismatch")
    jump_address = start + len(prefix)
    replacement = prefix + near_jump(jump_address, SPECS[implementation]["cleanup"])
    if len(replacement) > length:
        raise SystemExit(f"{implementation}-{checkpoint}: replacement overflow")
    replacement += b"\x90" * (length - len(replacement))
    image[start:start + length] = replacement
    return image, {
        "start": hex(start), "end": hex(start + length), "bytes": length,
        "expected": expected.hex(), "replacement": replacement.hex(),
        "cleanup_target": hex(SPECS[implementation]["cleanup"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    bases = {"official": args.official.read_bytes(), "gt": args.gt.read_bytes()}
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "gt32-exact-production-prefix-frontier-049-v1",
        "method": "byte patch of frozen exact-production PIE; no relink",
        "bases": {}, "images": {},
    }
    for implementation, source in (("official", args.official), ("gt", args.gt)):
        base = bases[implementation]
        manifest["bases"][implementation] = {
            "path": str(source.resolve()), "bytes": len(base), "sha256": digest(base)}
        for checkpoint in CHECKPOINTS:
            image, changed = patch_image(base, implementation, checkpoint)
            path = args.output / f"{implementation}-{checkpoint}"
            path.write_bytes(image)
            path.chmod(0o755)
            manifest["images"][f"{implementation}-{checkpoint}"] = {
                "path": str(path.resolve()), "bytes": len(image),
                "sha256": digest(image), "changed_range": changed,
                "prefix_before_patch_byte_exact": True,
                "full_image_byte_exact": checkpoint == "E",
            }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
