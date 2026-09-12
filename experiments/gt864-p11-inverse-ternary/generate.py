#!/usr/bin/env python3
"""Replace P10 terminal scalar scatters by compressed D stores."""

import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

UMOV = re.compile(r"^\s*umov\s+(w\d+),\s*v(\d+)\.h\[(\d+)\]\s*(?://.*)?$")
STRH = re.compile(r"^\s*strh\s+(w\d+),\s*\[x0,\s*#(\d+)\]\s*(?://.*)?$")
VDEF = re.compile(r"^\s*[a-z0-9]+\s+(?:v|q|d|s)(\d+)(?:\.|,)", re.I)


def transform(source: Path, output: Path, useful: int, tail: bool) -> dict:
    lines = source.read_text().splitlines()
    last_def = {i: -1 for i in range(32)}
    pending = {}
    records = []
    for index, line in enumerate(lines):
        match = UMOV.match(line)
        if match:
            gpr, vector, lane = match.groups()
            key = (int(vector), last_def[int(vector)])
            pending[gpr] = (index, key, int(lane))
            continue
        match = STRH.match(line)
        if match:
            gpr, offset = match.groups()
            if gpr in pending:
                umov_index, key, lane = pending.pop(gpr)
                records.append({
                    "key": key,
                    "lane": lane,
                    "offset": int(offset),
                    "umov": umov_index,
                    "strh": index,
                })
                continue
        match = VDEF.match(line)
        if match and not line.lstrip().startswith(("str ", "st1 ", "st2 ", "st3 ")):
            last_def[int(match.group(1))] = index

    expected = 96 if tail else 128
    assert len(records) == expected, (source, len(records), expected)
    grouped = {}
    for record in records:
        grouped.setdefault(record["key"], []).append(record)
    assert len(grouped) == 32

    remove = set()
    insert = {}
    report = []
    for (vector, definition), group in grouped.items():
        group.sort(key=lambda r: r["lane"])
        assert [r["lane"] for r in group] == list(range(useful))
        starts = [r["offset"] - 2 * r["lane"] if tail else r["offset"] - 6 * r["lane"] for r in group]
        assert len(set(starts)) == 1
        start = starts[0]
        k = (48 + start) // 54 if tail else start // 54
        assert 0 <= k < 32
        first = min(r["umov"] for r in group)
        insert[first] = f"        str d{vector}, [x1, #{8 * k}] // P11 scratch record k={k}"
        for record in group:
            remove.add(record["umov"])
            remove.add(record["strh"])
        report.append({"vector": vector, "definition": definition, "k": k, "offsets": [r["offset"] for r in group]})

    assert sorted(r["k"] for r in report) == list(range(32))
    result = []
    for index, line in enumerate(lines):
        if index in insert:
            result.append(insert[index])
        if index not in remove:
            result.append(line)
    old_name = "lazy_itail" if tail else "lazy_i16"
    new_name = "p11_lazy_itail" if tail else "p11_lazy_i16"
    rewritten = ("\n".join(result) + "\n").replace(old_name, new_name)
    output.write_text(rewritten)
    return {
        "source": str(source.relative_to(ROOT)),
        "output": str(output.relative_to(ROOT)),
        "removed_umov_strh": 2 * expected,
        "added_str_d": len(grouped),
        "net_instructions": len(grouped) - 2 * expected,
        "function": new_name,
        "records": sorted(report, key=lambda r: r["k"]),
    }


report = {
    "main": transform(PROD / "gt864_native_inverse16_lazy.S", P / "candidate-main.S", 4, False),
    "tail": transform(PROD / "gt864_native_inverse_tail_lazy.S", P / "candidate-tail.S", 3, True),
}
(P / "generation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: {x: v[x] for x in ("removed_umov_strh", "added_str_d", "net_instructions")} for k, v in report.items()}, indent=2))
