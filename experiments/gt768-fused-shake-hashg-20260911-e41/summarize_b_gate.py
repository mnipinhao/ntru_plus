#!/usr/bin/env python3
"""Create the persistent summary from ephemeral Pi output and disassembly."""
import hashlib
import json
from pathlib import Path
import re
import statistics

exp = Path(__file__).resolve().parent
build = exp / ".build/pi-b-gate-v1"
data = json.loads((build / "summary.json").read_text())

def function_words(label, mode, name):
    text = (build / (label + "-" + mode + ".dis")).read_text()
    match = re.search(r"^[0-9a-f]+ <" + re.escape(name) + r">:\n(.*)",
                      text, re.M | re.S)
    assert match, name
    # nm gives 1152 bytes. Internal Lmlk labels split the function into several
    # objdump paragraphs, so collect its complete 288-word extent.
    return re.findall(r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})\s", match[1], re.M)[:288]

perm = "ntruplus_keccak_f1600_x1_aarch64"
a = function_words("A", "hash_g", perm)
b = function_words("B", "hash_g", perm)
assert a == b and len(a) == 288
pmu = {}
for label in ("A", "B"):
    rows = data["pmu_per_operation"][label]
    pmu[label] = {key: statistics.median([row[key] for row in rows])
                  for key in rows[0]}
environment = {k: v for k, v in data["environment"].items() if k != "jobs"}
samples = json.loads((build / "samples.json").read_text())
summary = {
    k: data[k] for k in ("experiment_id", "gate", "baseline_revision", "host",
                         "compiler", "flags", "core", "pairs",
                         "operations_per_sample", "warmups", "order", "results",
                         "source_sha256")
}
summary.update({
    "candidate_code_revision": None,
    "decision": "accept B as experimental control; no production promotion",
    "correctness": {
        "mac_package_check": "pass",
        "mac_asan_ubsan": "2080 cases pass",
        "pi_packages_A_B": "make check pass",
        "prefix_differential": data["test"],
        "kat_rsp_sha256": "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8",
        "permutation_linked_opcodes_identical": True,
        "permutation_bytes": len(a) * 4,
    },
    "winning_pairs": {mode: sum(x > y for x, y in zip(v["A"], v["B"]))
                      for mode, v in samples.items()},
    "pmu_per_operation_medians": pmu,
    "pmu_notes": "4 AB/BA long runs, 200000 hash_g operations, user events, 100% scheduled; process startup included and amortized; ld_spec/st_spec are speculative",
    "linked_kem_sizes_bytes": {
        "A": {"size_text_category": 83143, "text_section": 73328},
        "B": {"size_text_category": 87207, "text_section": 77296},
    },
    "hash_path_own_stack_at_permutation_bytes": {
        "A": {"hash_g": 1200, "shake256": 416, "keccak_absorb": 368, "permutation": 128, "sum": 2112},
        "B": {"hash_g": 0, "prefix_helper": 560, "permutation": 128, "sum": 688},
        "notes": "Static disassembly accounting; excludes libc and higher callers, not a whole-process stack high-water measurement",
    },
    "environment": environment,
    "binary_sha256": {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(build.glob("[AB]-*")) if path.suffix == ""
    },
    "raw_results": "/home/pi/gt768-fused-shake-hashg-20260911-e41/.build/b-gate-v1",
})
(exp / "B-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({"pmu": pmu, "wins": summary["winning_pairs"],
                  "permutation_identity": True}, indent=2))
