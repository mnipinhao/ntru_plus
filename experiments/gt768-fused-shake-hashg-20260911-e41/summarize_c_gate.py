#!/usr/bin/env python3
"""Summarize the C run and audit the measured ELF files."""
import hashlib
import json
from pathlib import Path
import re
import statistics
import struct

exp = Path(__file__).resolve().parent
build = exp / ".build/pi-c-gate-v1"
data = json.loads((build / "summary.json").read_text())
samples = json.loads((build / "samples.json").read_text())

def section_sizes(path):
    b = path.read_bytes()
    assert b[:6] == b"\x7fELF\x02\x01"
    off = struct.unpack_from("<Q", b, 40)[0]
    size, count, string_index = struct.unpack_from("<HHH", b, 58)
    headers = [struct.unpack_from("<IIQQQQIIQQ", b, off + i*size) for i in range(count)]
    strings = headers[string_index]
    names = b[strings[4]:strings[4] + strings[5]]
    return {names[h[0]:].split(b"\0", 1)[0].decode(): h[5] for h in headers}

def words(label, name, count):
    text = (build / (label + "-encap.dis")).read_text()
    body = text.split("<" + name + ">:\n", 1)[1]
    return re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", body, re.M)[:count]

permutations = [words(label, "ntruplus_keccak_f1600_x1_aarch64", 288) for label in "ABC"]
assert permutations[0] == permutations[1] == permutations[2]
pmu = {}
for label in "ABC":
    rows = data["pmu_per_operation"][label]
    pmu[label] = {key: statistics.median(row[key] for row in rows) for key in rows[0]}
text = (build / "C-encap.dis").read_text()
body = text.split("<ntruplus_hash_g_fixed>:\n", 1)[1].split("\n\n", 1)[0]
assert not re.search(r"\b(uzp[12]|zip[12]|trn[12]|tbl|tbx)\b", body)
summary = {k: data[k] for k in (
    "experiment_id", "gate", "baseline_revision", "B_revision", "host",
    "compiler", "flags", "core", "pairs", "operations_per_sample",
    "warmups", "order", "results", "source_sha256")}
summary.update({
    "candidate_code_revision": "1493b298e790990038d15c146288280db943d79e",
    "decision": "accept C as next experimental champion; production not promoted",
    "correctness": {
        "mac_package": "make check pass, KAT byte-identical",
        "mac_ASan_UBSan": "3841 cases pass",
        "mac_portable_endian_path": "3841 cases pass (fallback selected on little-endian host)",
        "pi_package_A_B_C": "make check pass, KAT byte-identical",
        "pi_targeted": data["test"],
        "kat_rsp_sha256": "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8",
        "permutation_opcodes_identical": True,
        "permutation_bytes": 1152,
        "wrapper_shuffle_instructions": 0,
    },
    "C_winning_groups": {
        mode: {base: sum(x > y for x, y in zip(rows[base], rows["C"])) for base in "AB"}
        for mode, rows in samples.items()
    },
    "pmu_per_operation_medians": pmu,
    "pmu_notes": "6 permutations of ABC, 200000 operations/run, user events with amortized process-start overhead; ld_spec/st_spec are speculative, all events 100% scheduled",
    "linked_encap_sections": {label: section_sizes(build / (label+"-encap")) for label in "ABC"},
    "wrapper_bytes": {"B_generic_prefix": 4016, "C_fixed": 464},
    "hash_path_own_stack_at_permutation_bytes": {
        "A": 2112, "B": 688, "C": 400,
        "C_detail": "272-byte wrapper + 128-byte permutation; excludes libc/higher callers"
    },
    "cleanup_bytes_per_hash_g": {"A": 1689, "B": 536, "C": 200},
    "environment": {k:v for k,v in data["environment"].items() if k != "jobs"},
    "binary_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(build.glob("[ABC]-*")) if not p.suffix},
    "raw_results": "/home/pi/gt768-fused-shake-hashg-20260911-e41/.build/c-gate-v1",
})
(exp / "C-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"pmu": pmu, "wins": summary["C_winning_groups"],
                  "text": {k: v[".text"] for k,v in summary["linked_encap_sections"].items()},
                  "environment": summary["environment"]}, indent=2))
