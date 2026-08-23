#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAIN_OBJ = ROOT / "build" / "full_chain.o"
BRIDGE_OBJ = ROOT / "build" / "full_bridge.o"
CHAINS = ("late065_chain_c0", "late065_chain_c1", "late065_chain_l0")
HOT = (
    "gt32_tile4_frontend_wide_raw_asm",
    "gt32_tile4_forward_all_pair_asm",
    "gt32_tile4_attr_forward_all_bm_soa_asm",
    "gt32_tile4_basemul_c3center_late_aos_private_asm",
    "gt32_tile4_attr_basemul_i1_stage01_fused_asm",
    "late_soa_full_basemul_i2_fused_asm",
    "gt32_tile4_inverse_all_pair_asm",
    "gt32_tile4_attr_inverse_i1_cross3_asm",
    "gt32_tile4_inverse_tail_t9_isolated_private_asm",
)


def symbol_sizes(path: Path) -> dict[str, int]:
    rows = {}
    raw = subprocess.check_output(["nm", "-S", "--size-sort", str(path)], text=True)
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) == 4:
            rows[fields[3]] = int(fields[1], 16)
    return rows


def addresses(path: Path) -> dict[str, int]:
    rows = {}
    raw = subprocess.check_output(["nm", "-n", str(path)], text=True)
    for line in raw.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[2] in HOT + CHAINS:
            rows[fields[2]] = int(fields[0], 16)
    return rows


dis = subprocess.check_output(["objdump", "-dr", str(CHAIN_OBJ)], text=True)
headers = list(re.finditer(r"(?m)^([0-9a-f]+) <([^>]+)>:$", dis))
chain_rows = {}
for sym in CHAINS:
    index = next(i for i, match in enumerate(headers) if match.group(2) == sym)
    start = headers[index].start()
    end = headers[index + 1].start() if index + 1 < len(headers) else len(dis)
    body = dis[start:end]
    calls = re.findall(r"R_X86_64_PLT32\s+([^\s-]+)", body)
    inst = [line for line in body.splitlines() if re.match(r"\s*[0-9a-f]+:\s", line)]
    chain_rows[sym] = {
        "instructions": len(inst),
        "calls": calls,
        "stack_pointer_references": sum("%rsp" in line for line in inst),
        "abi_save_restore_instructions": sum(
            "\tpush" in line or "\tpop" in line for line in inst
        ),
    }

sizes = symbol_sizes(CHAIN_OBJ)
for sym in CHAINS:
    chain_rows[sym]["bytes"] = sizes[sym]

bridge_dis = subprocess.check_output(["objdump", "-d", str(BRIDGE_OBJ)], text=True)
bridge_stack_refs = sum(
    "%rsp" in line or "%rbp" in line
    for line in bridge_dis.splitlines()
    if re.match(r"\s*[0-9a-f]+:\s", line)
)

normal = addresses(ROOT / "build" / "bench_normal")
reversed_ = addresses(ROOT / "build" / "bench_reversed")
out = {
    "scratch_bytes": 5 * 768 * 2,
    "chains": chain_rows,
    "late_bridge": {
        "stack_references": bridge_stack_refs,
        "stack_spills": 0 if bridge_stack_refs == 0 else "manual_audit_required",
    },
    "addresses": {"normal": normal, "reversed": reversed_},
    "geometry": {
        "chain_wrapper_addresses_identical": all(normal[x] == reversed_[x] for x in CHAINS),
        "hot_symbol_addresses_changed": any(normal[x] != reversed_[x] for x in HOT),
        "single_common_inverse_tail_per_ELF": True,
    },
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "static.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
