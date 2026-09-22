#!/usr/bin/env python3
"""Hard gate for physical registers inside Slothy symbolic regions."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from contractlib import load_flat_yaml, value_list


SOURCE_SUFFIXES = {".s", ".S", ".asm", ".inc"}
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][A-Za-z0-9_.$]*):")
VECTOR_RE = re.compile(r"\b[vq](?:[0-9]|[12][0-9]|3[01])(?:\.[0-9]+[bhsdq])?\b", re.IGNORECASE)
GPR_RE = re.compile(r"\b[wx](?:[0-9]|[12][0-9]|30)\b")
SYMBOLIC_TOKEN_RE = re.compile(r"\b(?:Q|V|D|S|H|B|X|W)?<[A-Za-z_][A-Za-z0-9_]*>(?:\.[0-9]+[bhsdq])?", re.IGNORECASE)


def iter_files(paths: list[str]):
    for item in paths:
        path = Path(item)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in SOURCE_SUFFIXES:
                    yield child
        elif path.is_file():
            yield path


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].split("@", 1)[0]


def allowed_from_contract(path: Path | None) -> tuple[set[str], set[str]]:
    gprs = {"x0", "w0", "x1", "w1", "x2", "w2", "x3", "w3", "x4", "w4", "x5", "w5", "x6", "w6", "x7", "w7", "sp"}
    vectors: set[str] = set()
    if path is None or not path.is_file():
        return gprs, vectors
    data = load_flat_yaml(path)
    for item in value_list(data.get("abi.concrete_gprs_allowed")):
        reg = str(item).lower()
        gprs.add(reg)
        if reg.startswith("x"):
            gprs.add("w" + reg[1:])
        if reg.startswith("w"):
            gprs.add("x" + reg[1:])
    for item in value_list(data.get("abi.fixed_vector_registers")):
        reg = str(item).split(".", 1)[0].lower()
        vectors.add(reg)
        if reg.startswith("v"):
            vectors.add("q" + reg[1:])
        if reg.startswith("q"):
            vectors.add("v" + reg[1:])
    return gprs, vectors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Assembly files or directories to scan.")
    parser.add_argument("--contract", help="kernel-contract.yml or candidate-contract.yml.")
    parser.add_argument("--allow-reg", action="append", default=[], help="Physical register allowed inside regions. May be repeated.")
    parser.add_argument("--allow-frame-regs", action="store_true", help="Allow x29/w29 and x30/w30.")
    parser.add_argument("--warnings-only", action="store_true", help="Return zero even for disallowed physical registers.")
    args = parser.parse_args()

    allowed_gprs, allowed_vectors = allowed_from_contract(Path(args.contract) if args.contract else None)
    for reg in args.allow_reg:
        lowered = reg.lower()
        if lowered.startswith(("x", "w")) or lowered == "sp":
            allowed_gprs.add(lowered)
        if lowered.startswith(("v", "q")):
            allowed_vectors.add(lowered.split(".", 1)[0])
    if args.allow_frame_regs:
        allowed_gprs.update({"x29", "w29", "x30", "w30"})

    errors = 0
    for path in iter_files(args.paths):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError as exc:
            print(f"{path}: error[PHYS000]: could not read file: {exc}")
            errors += 1
            continue

        in_region = False
        for lineno, line in enumerate(lines, 1):
            label = LABEL_RE.match(line)
            if label and "slothy_start" in label.group(1):
                in_region = True
                continue
            if label and "slothy_end" in label.group(1):
                in_region = False
                continue
            if not in_region:
                continue

            code = SYMBOLIC_TOKEN_RE.sub("", strip_comment(line))
            for match in VECTOR_RE.finditer(code):
                reg = match.group(0).split(".", 1)[0].lower()
                if reg not in allowed_vectors:
                    print(f"{path}:{lineno}: error[PHYS001]: physical vector register '{match.group(0)}' inside Slothy region; use symbolic Q<name>/V<name> unless contract fixes it.")
                    errors += 1
            for match in GPR_RE.finditer(code):
                reg = match.group(0).lower()
                if reg not in allowed_gprs:
                    print(f"{path}:{lineno}: error[PHYS002]: physical GPR '{match.group(0)}' inside region; add to contract only if ABI/memory policy requires it.")
                    errors += 1

    if errors == 0:
        print("check-physical-reg-leaks: passed")
    else:
        print(f"check-physical-reg-leaks: {errors} error(s)")
    return 0 if errors == 0 or args.warnings_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
