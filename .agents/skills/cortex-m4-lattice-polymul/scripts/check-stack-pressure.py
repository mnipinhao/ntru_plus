#!/usr/bin/env python3
"""Emit heuristic stack-pressure warnings for Cortex-M4 function bodies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterator


SOURCE_SUFFIXES = {".c", ".h", ".cc", ".cpp"}
INPUT_ERROR = 2
STRICT_WARNINGS = 1

TYPE_SIZES = {
    "int8_t": 1,
    "uint8_t": 1,
    "int16_t": 2,
    "uint16_t": 2,
    "int32_t": 4,
    "uint32_t": 4,
    "int64_t": 8,
    "uint64_t": 8,
    "int": 4,
    "unsigned": 4,
    "long": 4,
    "long long": 8,
}

ARRAY_RE = re.compile(
    r"\b(?P<type>u?int(?:8|16|32|64)_t|int|unsigned|long long|long)"
    r"\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\[(?P<size>[^\]]+)\]"
)
FUNC_SIGNATURE_RE = re.compile(
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\([^;{}]*\)\s*"
    r"(?:__attribute__\s*\(\([^{}]*\)\)\s*)?$",
    re.DOTALL,
)
CONTROL_NAMES = {"if", "for", "while", "switch", "sizeof"}
STRUCT_BLOCK_RE = re.compile(r"\b(?:struct|union|class)\b[^;{}]*\{")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def collect_files(items: list[str]) -> tuple[list[Path], bool]:
    files: list[Path] = []
    seen: set[Path] = set()
    had_error = False
    for item in items:
        path = Path(item)
        if not path.exists():
            print(f"check-stack-pressure: error: input does not exist: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.is_dir():
            try:
                candidates = [child for child in sorted(path.rglob("*")) if child.is_file() and child.suffix in SOURCE_SUFFIXES]
            except OSError as exc:
                print(f"check-stack-pressure: error: cannot walk {path}: {exc}", file=sys.stderr)
                had_error = True
                continue
            if not candidates:
                print(f"check-stack-pressure: error: no supported C/C++ files under: {path}", file=sys.stderr)
                had_error = True
            for candidate in candidates:
                key = candidate.resolve()
                if key not in seen:
                    seen.add(key)
                    files.append(candidate)
            continue
        if not path.is_file():
            print(f"check-stack-pressure: error: input is not a regular file or directory: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.suffix not in SOURCE_SUFFIXES:
            print(f"check-stack-pressure: error: unsupported C/C++ source file: {path}", file=sys.stderr)
            had_error = True
            continue
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            files.append(path)
    if not files:
        print("check-stack-pressure: error: zero supported files selected", file=sys.stderr)
        had_error = True
    return files, had_error


def strip_comments_and_literals(text: str) -> str:
    """Replace comments and string/character contents while preserving lines."""
    out: list[str] = []
    index = 0
    state = "normal"
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "block":
            if char == "*" and nxt == "/":
                out.extend((" ", " "))
                index += 2
                state = "normal"
            else:
                out.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if state == "line":
            if char == "\n":
                out.append("\n")
                state = "normal"
            else:
                out.append(" ")
            index += 1
            continue
        if state in {"string", "char"}:
            quote = '"' if state == "string" else "'"
            if char == "\\" and nxt:
                out.extend((" ", "\n" if nxt == "\n" else " "))
                index += 2
            elif char == quote:
                out.append(" ")
                index += 1
                state = "normal"
            else:
                out.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if char == "/" and nxt == "*":
            out.extend((" ", " "))
            index += 2
            state = "block"
        elif char == "/" and nxt == "/":
            out.extend((" ", " "))
            index += 2
            state = "line"
        elif char == '"':
            out.append(" ")
            index += 1
            state = "string"
        elif char == "'":
            out.append(" ")
            index += 1
            state = "char"
        else:
            out.append(char)
            index += 1
    return "".join(out)


def function_body_lines(text: str) -> Iterator[tuple[int, str, str]]:
    """Yield only text inside function definitions, excluding signatures."""
    pending = ""
    depth = 0
    block_kind: str | None = None
    function_name = ""

    for lineno, line in enumerate(text.splitlines(), 1):
        if depth == 0 and line.lstrip().startswith("#"):
            pending = ""
            continue
        body: list[str] = []
        for char in line:
            if depth == 0:
                if char == ";" or char == "}":
                    pending = ""
                elif char == "{":
                    signature = pending.strip()
                    match = FUNC_SIGNATURE_RE.search(signature)
                    name = match.group("name") if match else ""
                    is_function = bool(
                        match
                        and name not in CONTROL_NAMES
                        and "=" not in signature
                        and not re.match(r"^(?:typedef\s+)?(?:struct|union|enum|class)\b", signature)
                    )
                    block_kind = "function" if is_function else "other"
                    function_name = name if is_function else ""
                    depth = 1
                    pending = ""
                else:
                    pending += char
                continue

            if block_kind == "function":
                body.append(char)
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    block_kind = None
                    function_name = ""
                    pending = ""
        if body and function_name:
            yield lineno, "".join(body), function_name
        if depth == 0 and pending:
            pending += "\n"


def parse_size(expr: str) -> int | None:
    expr = expr.strip()
    if re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|[0-9]+)", expr):
        return int(expr, 0)
    return None


def strip_nested_type_fields(line: str, depth: int) -> tuple[str, int]:
    """Blank struct/union/class bodies declared inside a function."""
    out: list[str] = []
    position = 0
    while position < len(line):
        if depth:
            char = line[position]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            out.append(" ")
            position += 1
            continue
        match = STRUCT_BLOCK_RE.search(line, position)
        if not match:
            out.append(line[position:])
            break
        out.append(line[position : match.start()])
        out.append(" " * (match.end() - match.start()))
        depth = 1
        position = match.end()
    return "".join(out), depth


def analyze_file(path: Path, text: str, threshold: int) -> int:
    warnings = 0
    stripped = strip_comments_and_literals(text)
    current_function = ""
    nested_type_depth = 0
    for lineno, line, function_name in function_body_lines(stripped):
        if function_name != current_function:
            current_function = function_name
            nested_type_depth = 0
        line, nested_type_depth = strip_nested_type_fields(line, nested_type_depth)
        for match in ARRAY_RE.finditer(line):
            declaration_prefix = line[: match.start()]
            if re.search(r"\b(?:static|extern)\b", declaration_prefix):
                continue
            type_name = match.group("type")
            size_expr = match.group("size").strip()
            count_expr = parse_size(size_expr)
            if count_expr is None:
                print(
                    f"{path}:{lineno}: warning[STACK001]: symbolic or variable-length local array "
                    f"'{match.group('name')}[{size_expr}]' in '{function_name}'; confirm with compiler -fstack-usage."
                )
                warnings += 1
                continue
            bytes_used = TYPE_SIZES.get(type_name, 4) * count_expr
            if bytes_used >= threshold:
                print(
                    f"{path}:{lineno}: warning[STACK002]: local array '{match.group('name')}' in "
                    f"'{function_name}' is about {bytes_used} bytes; consider caller scratch or a smaller stack budget."
                )
                warnings += 1
        if re.search(rf"\b{re.escape(function_name)}\s*\(", line):
            print(
                f"{path}:{lineno}: warning[STACK003]: possible recursive call to '{function_name}'; "
                "bound recursion depth and stack use."
            )
            warnings += 1
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit heuristic Cortex-M4 stack-pressure warnings for function bodies.",
        epilog="Compiler -fstack-usage output is authoritative; this checker is a review aid.",
    )
    parser.add_argument("--threshold", type=positive_int, default=512, help="Warn on numeric local arrays at or above this many bytes. Default: 512.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when warnings are found.")
    parser.add_argument("paths", nargs="+", help="C/C++ source files or directories to scan.")
    args = parser.parse_args()

    files, had_error = collect_files(args.paths)
    total = 0
    scanned = 0
    for path in files:
        try:
            text = path.read_text(errors="replace")
        except OSError as exc:
            print(f"check-stack-pressure: error: could not read {path}: {exc}", file=sys.stderr)
            had_error = True
            continue
        scanned += 1
        total += analyze_file(path, text, args.threshold)

    print(f"check-stack-pressure: files scanned: {scanned}; warnings: {total}")
    print("check-stack-pressure: note: compiler -fstack-usage output is authoritative")
    if had_error or scanned == 0:
        return INPUT_ERROR
    if args.strict and total:
        return STRICT_WARNINGS
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
