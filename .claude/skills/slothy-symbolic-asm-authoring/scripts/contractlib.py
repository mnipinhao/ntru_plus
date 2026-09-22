"""Small YAML-like helpers for Slothy skill gate scripts.

The templates in this skill intentionally use a simple subset of YAML. These
helpers avoid a PyYAML dependency while still supporting nested scalar keys,
indented scalar lists, and inline scalar lists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PLACEHOLDER_MARKERS = (
    "TODO",
    "TBD",
    "FIXME",
    "KERNEL_",
    "CANDIDATE_",
    "BASELINE_",
    "FUNCTION_NAME",
    "SCHEME_NAME",
    "OPERATION_NAME",
    "path/to/",
    "YYYY-MM-DD",
)


def strip_yaml_comment(value: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for idx, char in enumerate(value):
        if char == "\\" and in_double and not escaped:
            escaped = True
            continue
        if char == "'" and not in_double and not escaped:
            in_single = not in_single
        elif char == '"' and not in_single and not escaped:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return value[:idx].rstrip()
        escaped = False
    return value.rstrip()


def parse_scalar(value: str) -> Any:
    value = strip_yaml_comment(value).strip()
    if value == "":
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def load_flat_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    data: dict[str, Any] = {}
    stack: list[str] = []
    for raw in path.read_text(errors="replace").splitlines():
        line = strip_yaml_comment(raw.rstrip())
        if not line.strip():
            continue
        stripped = line.lstrip(" ")
        if stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)
        level = indent // 2

        if stripped.startswith("- "):
            parent = ".".join(stack[:level])
            if not parent:
                parent = "items"
            data.setdefault(parent, [])
            if not isinstance(data[parent], list):
                data[parent] = [data[parent]]
            data[parent].append(parse_scalar(stripped[2:].strip()))
            continue

        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        stack = stack[:level]
        stack.append(key)
        full_key = ".".join(stack)
        value = value.strip()
        if value == "":
            data.setdefault(full_key, [])
        else:
            data[full_key] = parse_scalar(value)
    return data


def is_missing(value: Any) -> bool:
    return value is None or value == "" or value == []


def contains_placeholder(value: Any) -> bool:
    if isinstance(value, list):
        return any(contains_placeholder(item) for item in value)
    if value is None:
        return False
    text = str(value)
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def value_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "pass", "passed"}


def value_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def value_list(value: Any) -> list[Any]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [value]


def status_value(value: Any) -> str:
    if value is None:
        return "unknown"
    return str(value).strip().lower()
