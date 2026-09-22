#!/usr/bin/env python3
"""Hard/static checks for Slothy symbolic assembly candidates."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from contractlib import load_flat_yaml, value_list


SOURCE_SUFFIXES = {".s", ".S", ".asm", ".inc"}
SYMBOLIC_RE = re.compile(r"\b(?:Q|V|D|S|H|B|X|W)?<([A-Za-z_][A-Za-z0-9_]*)>")
ANGLE_RE = re.compile(r"<[^>]*>")
ANGLE_TOKEN_RE = re.compile(r"^<[A-Za-z_][A-Za-z0-9_]*>$")
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][A-Za-z0-9_.$]*):")
INSTR_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_.]*)\b")
BRANCH_RE = re.compile(r"^\s*(b(?:\.[a-z]+)?|br|blr|ret|cbz|cbnz|tbz|tbnz)\b", re.IGNORECASE)
LOAD_RE = re.compile(r"^\s*ld[0-9a-z]*\b", re.IGNORECASE)
STORE_RE = re.compile(r"^\s*st[0-9a-z]*\b", re.IGNORECASE)
REGISTER_OFFSET_RE = re.compile(r"\[[^\]]*,\s*[wx](?:[0-9]|[12][0-9]|30)\b[^\]]*\]")
SECRET_WORD_RE = re.compile(r"\b(secret|priv|private|sk|key|coeff|coef|poly|challenge|nonce)\b", re.IGNORECASE)

DEST_DEFINES = {
    "add", "sub", "mul", "mla", "mls", "smull", "smull2", "umull", "umull2",
    "smlal", "smlal2", "umlal", "umlal2", "sqrdmulh", "sqdmulh", "sqrshrn",
    "sqrshrn2", "shrn", "shrn2", "xtn", "xtn2", "sqxtn", "sqxtn2", "and",
    "orr", "eor", "bic", "movi", "dup", "ext", "zip1", "zip2", "uzp1",
    "uzp2", "trn1", "trn2", "sshr", "ushr", "sli", "sri", "rev64",
}

DEST_READWRITE = {"mla", "mls", "smlal", "smlal2", "umlal", "umlal2", "sqxtn2", "xtn2", "shrn2", "sqrshrn2"}


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


def comment_text(line: str) -> str:
    if "//" in line:
        return line.split("//", 1)[1]
    if "@" in line:
        return line.split("@", 1)[1]
    return ""


def is_instruction(line: str) -> bool:
    stripped = strip_comment(line).strip()
    if not stripped or stripped.startswith(".") or stripped.endswith(":"):
        return False
    return bool(INSTR_RE.match(stripped))


def symbols_from_contract(path: Path | None) -> set[str]:
    if path is None or not path.is_file():
        return set()
    data = load_flat_yaml(path)
    symbols: set[str] = set()
    for key in ("region.live_in", "region.live_out"):
        for item in value_list(data.get(key)):
            symbols.update(SYMBOLIC_RE.findall(str(item)))
            for token in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", str(item)):
                if token not in {"x", "w", "sp"}:
                    symbols.add(token)
    return symbols


def is_asset_fragment(path: Path) -> bool:
    parts = set(path.parts)
    return "assets" in parts and ("patterns" in parts or path.name.endswith("template.S"))


def emit_missing(path: Path, line: int | None, code: str, message: str, candidate: bool) -> tuple[int, int]:
    location = f"{path}:{line}" if line else str(path)
    severity = "error" if candidate else "warning"
    print(f"{location}: {severity}[{code}]: {message}")
    return (1, 0) if candidate else (0, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Assembly files or directories to scan.")
    parser.add_argument("--candidate", action="store_true", help="Treat scanned .S as candidate output and enforce contract gates.")
    parser.add_argument("--kernel-contract", help="Required kernel-contract.yml for candidate scans.")
    parser.add_argument("--baseline-contract", help="Required for existing_region_replacement scans.")
    parser.add_argument("--mode", choices=[
        "new_symbolic_kernel",
        "existing_region_replacement",
        "new_kernel_baseline_then_iterate",
        "oracle_scaffold_only",
        "post_slothy_review",
    ])
    parser.add_argument("--warnings-only", action="store_true", help="Return zero even when hard findings are emitted.")
    args = parser.parse_args()

    kernel_contract = Path(args.kernel_contract) if args.kernel_contract else None
    baseline_contract = Path(args.baseline_contract) if args.baseline_contract else None
    errors = 0
    warnings = 0

    if args.candidate:
        if kernel_contract is None or not kernel_contract.is_file():
            print("error[SYM100]: candidate .S generation/checking requires kernel-contract.yml", file=sys.stderr)
            errors += 1
        if args.mode == "existing_region_replacement" and (baseline_contract is None or not baseline_contract.is_file()):
            print("error[SYM101]: existing_region_replacement requires baseline-contract.yml before candidate .S", file=sys.stderr)
            errors += 1

    contract_live = symbols_from_contract(kernel_contract)

    for path in iter_files(args.paths):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError as exc:
            print(f"{path}: error[SYM000]: could not read file: {exc}", file=sys.stderr)
            errors += 1
            continue

        if not args.candidate and not is_asset_fragment(path) and path.suffix in {".S", ".s"}:
            print(f"{path}: warning[SYM099]: scanned as advisory fragment; pass --candidate to enforce contract gates.")
            warnings += 1

        start_count = sum(1 for line in lines if "slothy_start" in line and LABEL_RE.match(line))
        end_count = sum(1 for line in lines if "slothy_end" in line and LABEL_RE.match(line))
        if start_count == 0 or end_count == 0:
            print(f"{path}: error[SYM001]: no Slothy start/end label pair found.")
            errors += 1
        elif start_count != end_count:
            print(f"{path}: error[SYM002]: Slothy start/end label count mismatch: {start_count} start, {end_count} end.")
            errors += 1

        defined: set[str] = set(contract_live)
        in_region = False
        region_start_line = None
        region_has_live_in = False
        region_has_live_out = False
        region_has_range = False
        region_has_reserved = False
        for lineno, line in enumerate(lines, 1):
            label = LABEL_RE.match(line)
            if label and "slothy_start" in label.group(1):
                in_region = True
                region_start_line = lineno
                preamble = "\n".join(lines[max(0, lineno - 12):lineno]).lower()
                region_has_live_in = "live-in" in preamble or "live in" in preamble
                region_has_live_out = "live-out" in preamble or "live out" in preamble
                region_has_range = "range" in preamble or "coefficient bounds" in preamble or "bounds before" in preamble
                region_has_reserved = "reserved" in preamble and ("reg" in preamble or "physical" in preamble)
                defined.update(SYMBOLIC_RE.findall("\n".join(lines[max(0, lineno - 12):lineno])))
                defined.update(contract_live)
                continue
            if label and "slothy_end" in label.group(1):
                if in_region:
                    if not region_has_live_in:
                        error_delta, warning_delta = emit_missing(path, region_start_line, "SYM006", "Slothy region has no live-in comment.", args.candidate)
                        errors += error_delta
                        warnings += warning_delta
                    if not region_has_live_out:
                        error_delta, warning_delta = emit_missing(path, region_start_line, "SYM007", "Slothy region has no live-out comment.", args.candidate)
                        errors += error_delta
                        warnings += warning_delta
                    if not region_has_range:
                        error_delta, warning_delta = emit_missing(path, region_start_line, "SYM008", "Slothy region has no coefficient range comment.", args.candidate)
                        errors += error_delta
                        warnings += warning_delta
                    if not region_has_reserved:
                        error_delta, warning_delta = emit_missing(path, region_start_line, "SYM009", "Slothy region has no reserved physical register comment.", args.candidate)
                        errors += error_delta
                        warnings += warning_delta
                in_region = False
                region_start_line = None
                continue

            lower_line = line.lower()
            if in_region:
                ctext = comment_text(line)
                if "live-in" in lower_line or "live in" in lower_line:
                    region_has_live_in = True
                    defined.update(SYMBOLIC_RE.findall(ctext))
                    defined.update(token for token in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", ctext) if token not in {"live", "in"})
                if "live-out" in lower_line or "live out" in lower_line:
                    region_has_live_out = True
                if "range" in lower_line or "coefficient bounds" in lower_line or "bounds before" in lower_line:
                    region_has_range = True
                if "reserved" in lower_line and ("reg" in lower_line or "physical" in lower_line):
                    region_has_reserved = True

            code = strip_comment(line)
            if in_region and BRANCH_RE.search(code):
                mnemonic = BRANCH_RE.search(code).group(1).lower()
                if mnemonic != "ret":
                    print(f"{path}:{lineno}: warning[SYM010]: branch-like instruction inside Slothy region; verify it is public and supported.")
                    warnings += 1
                else:
                    print(f"{path}:{lineno}: error[SYM011]: ret inside Slothy region; keep ABI scaffolding outside the optimized region unless intentional.")
                    errors += 1
            if in_region and LOAD_RE.search(code):
                if REGISTER_OFFSET_RE.search(code):
                    print(f"{path}:{lineno}: warning[SYM012]: register-indexed load inside Slothy region; verify address is public and memory contract allows it.")
                    warnings += 1
                if SECRET_WORD_RE.search(line) and "[" in code and "]" in code:
                    print(f"{path}:{lineno}: warning[SYM013]: secret/coefficient-looking memory access; verify no secret-dependent address.")
                    warnings += 1

            for angle in ANGLE_RE.findall(code):
                if not ANGLE_TOKEN_RE.fullmatch(angle):
                    print(f"{path}:{lineno}: error[SYM003]: unusual symbolic token '{angle}'. Use names like Q<a0> or V<a0>.8h.")
                    errors += 1

            symbols = SYMBOLIC_RE.findall(code)
            if not symbols or not is_instruction(code):
                continue

            instr = INSTR_RE.match(code.strip())
            mnemonic = instr.group(1).lower() if instr else ""

            if LOAD_RE.search(mnemonic):
                defined.add(symbols[0])
                continue
            if STORE_RE.search(mnemonic):
                uses = symbols
            elif mnemonic in DEST_DEFINES:
                uses = symbols if mnemonic in DEST_READWRITE else symbols[1:]
                defined.add(symbols[0])
            else:
                uses = symbols
                print(f"{path}:{lineno}: warning[SYM005]: checker cannot classify instruction '{mnemonic}'; verify symbolic defs/uses manually.")
                warnings += 1

            for sym in uses:
                if sym not in defined:
                    print(f"{path}:{lineno}: error[SYM004]: symbolic value '{sym}' may be used before a visible definition or live-in declaration.")
                    errors += 1

    if errors == 0 and warnings == 0:
        print("check-symbolic-asm: passed")
    else:
        print(f"check-symbolic-asm: {errors} error(s), {warnings} warning(s)")
    return 0 if errors == 0 or args.warnings_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
