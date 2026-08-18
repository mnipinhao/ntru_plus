#!/usr/bin/env python3
"""Classify linked CleanGT functions by production KEM-root reachability."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict, deque
from pathlib import Path


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def functions(elf: Path) -> dict[str, tuple[int, int]]:
    answer: dict[str, tuple[int, int]] = {}
    for line in command("readelf", "-Ws", str(elf)).splitlines():
        fields = line.split()
        if len(fields) < 8 or fields[3] != "FUNC" or fields[6] == "UND":
            continue
        try:
            address, size = int(fields[1], 16), int(fields[2])
        except ValueError:
            continue
        if size:
            answer[fields[7].split("@", 1)[0]] = (address, size)
    return answer


def call_graph(elf: Path, known: set[str]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = defaultdict(set)
    current: str | None = None
    for line in command("objdump", "-d", "--no-show-raw-insn", str(elf)).splitlines():
        header = re.match(r"[0-9a-f]+ <([^>]+)>:", line)
        if header:
            current = header.group(1).split("+", 1)[0]
            continue
        if current is None:
            continue
        edge = re.search(r"\b(?:call|jmp)\s+[0-9a-f]+\s+<([^>]+)>", line)
        if edge:
            target = edge.group(1).split("+", 1)[0].split("@", 1)[0]
            if target in known and target != current:
                graph[current].add(target)
    return graph


def closure(root: str, graph: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(graph.get(node, ()))
    return seen


def unique_bytes(names: set[str], funcs: dict[str, tuple[int, int]]) -> int:
    ranges = sorted({funcs[name] for name in names if name in funcs})
    merged: list[list[int]] = []
    for address, size in ranges:
        end = address + size
        if merged and address <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([address, end])
    return sum(end - start for start, end in merged)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("elf", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    funcs = functions(args.elf)
    graph = call_graph(args.elf, set(funcs))
    roots = {}
    for op in ("keypair", "enc", "dec"):
        matches = [name for name in funcs if name.startswith("crypto_kem_ntruplus768_") and name.endswith(f"_{op}")]
        if len(matches) != 1:
            raise ValueError(f"could not identify unique {op} root: {matches}")
        roots[op] = matches[0]
    reachable = {op: closure(root, graph) for op, root in roots.items()}
    all_reachable = set().union(*reachable.values())
    category: dict[str, set[str]] = {"shared": set(), "keypair_only": set(), "encap_only": set(), "decap_only": set(), "other_reachable": set(), "cold_unreachable": set()}
    for name in funcs:
        membership = {op for op in reachable if name in reachable[op]}
        if len(membership) >= 2:
            category["shared"].add(name)
        elif membership == {"keypair"}:
            category["keypair_only"].add(name)
        elif membership == {"enc"}:
            category["encap_only"].add(name)
        elif membership == {"dec"}:
            category["decap_only"].add(name)
        elif name in all_reachable:
            category["other_reachable"].add(name)
        else:
            category["cold_unreachable"].add(name)
    report = {
        "schema": "gt32-production-function-reachability-v1",
        "elf": str(args.elf),
        "roots": roots,
        "operations": {
            op: {"function_count": len(names), "unique_named_function_bytes": unique_bytes(names, funcs), "functions": sorted(names)}
            for op, names in reachable.items()
        },
        "categories": {
            name: {"function_count": len(names), "unique_named_function_bytes": unique_bytes(names, funcs), "functions": sorted(names)}
            for name, names in category.items()
        },
        "limitations": [
            "direct-call-and-tail-jump closure only",
            "PLT/shared-library bodies are outside the linked ELF",
            "unnamed padding and non-FUNC text are not assigned to a category",
        ],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
