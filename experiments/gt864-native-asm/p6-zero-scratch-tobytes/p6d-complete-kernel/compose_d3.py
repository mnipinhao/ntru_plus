#!/usr/bin/env python3
"""Compose allocated P6-D3 slices into one zero-coefficient-scratch full kernel."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORDER = [0, 3, 6, 1, 4, 7, 2, 5, 8]


def region(path: Path, start: str, end: str) -> list[str]:
    lines = path.read_text().splitlines()
    lo = next(i for i, x in enumerate(lines) if x.strip() == start + ":") + 1
    hi = next(i for i, x in enumerate(lines) if x.strip() == end + ":")
    out = []
    for raw in lines[lo:hi]:
        line = raw.split("//", 1)[0].strip()
        if line and not line.startswith("."): out.append(line)
    return out


def q_load_map(lines: list[str], base: str) -> dict[int, int]:
    out = {}
    pat = re.compile(r"ldr q(\d+), \[" + base + r"(?:, #(\d+))?\]", re.I)
    for line in lines:
        m = pat.fullmatch(line)
        if m: out[int(m.group(2) or 0)//16] = int(m.group(1))
    return out


def q_store_map(lines: list[str], base: str) -> dict[int, int]:
    out = {}
    pat = re.compile(r"str q(\d+), \[" + base + r"(?:, #(\d+))?\]", re.I)
    for line in lines:
        m = pat.fullmatch(line)
        if m: out[int(m.group(2) or 0)//16] = int(m.group(1))
    return out


def x_map(lines: list[str], op: str, base: str, first: int, count: int) -> dict[int, int]:
    out = {}
    pat = re.compile(op + r" x(\d+), \[" + base + r"(?:, #(\d+))?\]", re.I)
    for line in lines:
        m = pat.fullmatch(line)
        if m:
            off = int(m.group(2) or 0)
            if first <= off < first + 8*count: out[(off-first)//8] = int(m.group(1))
    return out


def parallel_moves(current: dict[str, int], target: dict[str, int], kind: str) -> list[str]:
    cur = dict(current)
    out = []
    all_regs = set(range(32)) if kind == "v" else ({*range(18), *range(19, 29)} - {18})
    while any(cur[k] != target[k] for k in target):
        occupied = set(cur.values())
        progress = False
        for key in target:
            if cur[key] == target[key]: continue
            if target[key] not in occupied:
                src, dst = cur[key], target[key]
                out.append(f"orr v{dst}.16b, v{src}.16b, v{src}.16b" if kind == "v" else f"mov x{dst}, x{src}")
                cur[key] = dst; progress = True; break
        if progress: continue
        free = sorted(all_regs - occupied - set(target.values()))
        if not free: free = sorted(all_regs - occupied)
        assert free, (kind, cur, target)
        key = next(k for k in target if cur[k] != target[k])
        src, tmp = cur[key], free[0]
        out.append(f"orr v{tmp}.16b, v{src}.16b, v{src}.16b" if kind == "v" else f"mov x{tmp}, x{src}")
        cur[key] = tmp
    return out


def clean_stage(lines: list[str]) -> list[str]:
    return [x for x in lines if not re.fullmatch(r"ldr q\d+, \[x3(?:, #\d+)?\]", x, re.I)
            and not re.fullmatch(r"str q\d+, \[x4(?:, #\d+)?\]", x, re.I)]


def stage(label: str, input_keys: list[str], output_keys: list[str], current: dict[str, int]) -> tuple[list[str], dict[str, int]]:
    path = HERE / f"d3.{label}.alloc.S"
    lines = region(path, label + "_slothy_start", label + "_slothy_end")
    imap_raw, omap_raw = q_load_map(lines, "x3"), q_store_map(lines, "x4")
    assert sorted(imap_raw) == list(range(len(input_keys))), (label, imap_raw)
    assert sorted(omap_raw) == list(range(len(output_keys))), (label, omap_raw)
    imap = {key: imap_raw[i] for i, key in enumerate(input_keys)}
    omap = {key: omap_raw[i] for i, key in enumerate(output_keys)}
    return parallel_moves(current, imap, "v") + clean_stage(lines), omap


def next_row_state(state: list[str], physical: int) -> list[str]:
    logical = ORDER[physical]
    consumed_q = {f"s{d//2}" for d in range(6*physical, 6*physical+6) if d < 26}
    result = [x for x in state if x not in consumed_q and x != f"b{logical}"]
    if physical % 2 == 1 and "carry" in result: result.remove("carry")
    future = set(ORDER[physical+1:])
    for key in list(result):
        if key.startswith("L"):
            idx = int(key[1:]); users = {2*idx, 2*idx+1} if idx < 4 else {8}
            if not users & future: result.remove(key)
        elif key == "H0" and not ({0,1,2,3} & future): result.remove(key)
        elif key == "H1" and not ({4,5,6,7} & future): result.remove(key)
    if physical < 8 and physical % 2 == 0: result.append("carry")
    return result


def d1_top() -> tuple[list[str], dict[str, int]]:
    p0 = region(HERE / "producer.pair0.alloc.S", "gt864_p6d_pair0_start", "gt864_p6d_pair0_end")
    p1 = region(HERE / "producer.pair1.alloc.S", "gt864_p6d_pair1_start", "gt864_p6d_pair1_end")
    p0map = x_map(p0, "str", "sp", 0, 27)
    p1in = x_map(p1, "ldr", "sp", 0, 27)
    assert sorted(p0map) == list(range(27)) and sorted(p1in) == list(range(27))
    keys = [f"d{i}" for i in range(27)]
    moves = parallel_moves({k:p0map[i] for i,k in enumerate(keys)}, {k:p1in[i] for i,k in enumerate(keys)}, "x")
    p0 = [x for x in p0 if not re.fullmatch(r"str x\d+, \[sp(?:, #\d+)?\]", x, re.I)]
    p1 = [x for x in p1 if not re.fullmatch(r"ldr x\d+, \[sp(?:, #\d+)?\]", x, re.I)
          and not re.fullmatch(r"str (?:q\d+|x\d+), \[sp(?:, #\d+)?\]", x, re.I)]
    qout = q_store_map(region(HERE / "producer.pair1.alloc.S", "gt864_p6d_pair1_start", "gt864_p6d_pair1_end"), "sp")
    assert sorted(qout) == list(range(13))
    return p0 + moves + p1, {f"s{i}": qout[i] for i in range(13)}


def top_body() -> list[str]:
    body, current = d1_top()
    saved = [f"s{i}" for i in range(13)]
    route_a = saved + [f"a{i}" for i in range(9)]
    part, current = stage("gt864_p6d3_route_a", saved, route_a, current); body += part
    packed = saved + [f"L{i}" for i in range(5)] + ["H0", "H1"]
    part, current = stage("gt864_p6d3_pack_a", route_a, packed, current); body += part
    routed_b = packed + [f"b{i}" for i in range(9)]
    part, current = stage("gt864_p6d3_route_b", packed, routed_b, current); body += part
    body += ["ldr x29, [sp, #160]"]
    state = routed_b
    for physical in range(9):
        nxt = next_row_state(state, physical)
        label = f"gt864_p6d3_row{physical}"
        part, current = stage(label, state, nxt, current); body += part
        if physical != 8: body += [f"add x29, x29, #{64 if physical % 2 == 0 else 80}"]
        state = nxt
    assert not state
    return body


def parse_array(path: Path, name: str, count: int) -> list[int]:
    text = path.read_text()
    m = re.search(name + r"[^=]*=\s*\{(.*?)\};", text, re.S); assert m
    values = [int(x) for x in re.findall(r"\b\d+\b", m.group(1))]
    assert len(values) == count, (name, len(values))
    return values


def table_bytes() -> list[int]:
    base = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
    prefix16 = parse_array(base / "p3b1_tables.h", "p3b1_prefix", 56)
    prefix = b"".join(int(x).to_bytes(2, "little") for x in prefix16)
    route = bytes(parse_array(base / "p3b1_tables.h", "p3b1_a_fwd", 144))
    idx0 = bytes([0,16,32,1,17,33,2,18,34,3,19,35,4,20,36,5])
    idx1 = bytes([21,37,6,22,38,7,23,39]+[255]*8)
    q = b"".join((3457).to_bytes(2,"little") for _ in range(8))
    recip = b"".join((9).to_bytes(2,"little") for _ in range(8))
    merge = parse_array(base / "byte_merge_tables.h", "gt864_byte_merge_indices", 240)
    for chunk in range(5):
        for i in range(16):
            pos = 48*chunk+16+i
            if merge[pos] != 255: merge[pos] += 8
    return list(prefix + bytes(48) + route + idx0 + idx1 + q + recip + bytes(merge) + bytes([15]*16))


def main() -> None:
    top = top_body()
    out = [".text", ".p2align 2", ".global gt864_p6d3_full_asm", ".global gt864_p6d3_small_asm",
           "gt864_p6d3_small_asm:", "gt864_p6d3_full_asm:",
           "    sub sp, sp, #176", "    stp x19, x20, [sp, #0]", "    stp x21, x22, [sp, #16]",
           "    stp x23, x24, [sp, #32]", "    stp x25, x26, [sp, #48]", "    stp x27, x28, [sp, #64]",
           "    stp x29, x30, [sp, #80]", "    stp d8, d9, [sp, #96]", "    stp d10, d11, [sp, #112]",
           "    stp d12, d13, [sp, #128]", "    stp d14, d15, [sp, #144]", "    str x0, [sp, #160]",
           "    str x1, [sp, #168]", "    adr x30, .Lp6d3_tables", "    ldr x29, [sp, #168]"]
    out += ["    "+x for x in top]
    out += ["    ldr x29, [sp, #168]", "    add x29, x29, #864"]
    top2 = [x.replace("[sp, #160]", "[sp, #160]") for x in top]
    # The consumer pointer reload needs the second 648-byte output base.
    split = top2.index("ldr x29, [sp, #160]")
    top2[split:split+1] = ["ldr x29, [sp, #160]", "add x29, x29, #648"]
    out += ["    "+x for x in top2]
    out += ["    ldr x0, [sp, #160]"]
    # Match the production public-wrapper cleanup boundary exactly: volatile
    # SIMD state is cleared before the low halves of callee-saved v8-v15 are
    # restored.  This is part of the KEM cleanup contract and must be included
    # in timing rather than treated as optional benchmark overhead.
    out += [f"    movi v{i}.16b, #0" for i in range(32)]
    out += ["    ldp d8, d9, [sp, #96]", "    ldp d10, d11, [sp, #112]",
            "    ldp d12, d13, [sp, #128]", "    ldp d14, d15, [sp, #144]", "    ldp x19, x20, [sp, #0]",
            "    ldp x21, x22, [sp, #16]", "    ldp x23, x24, [sp, #32]", "    ldp x25, x26, [sp, #48]",
            "    ldp x27, x28, [sp, #64]", "    ldp x29, x30, [sp, #80]", "    add sp, sp, #176", "    ret",
            ".p2align 4", ".Lp6d3_tables:"]
    table = table_bytes(); assert len(table) == 624
    for i in range(0, len(table), 16): out.append("    .byte " + ", ".join(map(str, table[i:i+16])))
    (HERE / "p6d3-full.alloc.S").write_text("\n".join(out) + "\n")
    (HERE / "d3-compose-results.json").write_text(json.dumps({"top_semantic_instructions":len(top), "table_bytes":len(table),
        "coefficient_scratch_bytes":0, "public_stack_bytes":176, "final_store_shape_per_top":{"str_q":40,"str_d":1},
        "volatile_simd_clears":32,
        "small_entry":"shares full-normalization DAG in D3 correctness baseline"}, indent=2)+"\n")


if __name__ == "__main__": main()
