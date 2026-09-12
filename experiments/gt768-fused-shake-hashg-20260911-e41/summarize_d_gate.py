#!/usr/bin/env python3
"""Audit D's actual ELF instructions, footprint and measured C/D results."""
import hashlib
import json
from pathlib import Path
import statistics
import struct

exp = Path(__file__).resolve().parent
root = exp.parents[1]
build = exp / ".build/pi-d-gate-v1"
data = json.loads((build / "summary.json").read_text())
samples = json.loads((build / "samples.json").read_text())

class Elf:
    def __init__(self, path):
        self.data = path.read_bytes()
        b = self.data
        assert b[:6] == b"\x7fELF\x02\x01"
        off = struct.unpack_from("<Q", b, 40)[0]
        size, count, si = struct.unpack_from("<HHH", b, 58)
        self.sections = [struct.unpack_from("<IIQQQQIIQQ", b, off+i*size)
                         for i in range(count)]
        sh = self.sections[si]
        names = b[sh[4]:sh[4]+sh[5]]
        self.sizes = {names[s[0]:].split(b"\0", 1)[0].decode(): s[5]
                      for s in self.sections}
        self.symbols = {}
        for s in self.sections:
            if s[1] != 2:
                continue
            t = self.sections[s[6]]
            strings = b[t[4]:t[4]+t[5]]
            for pos in range(s[4], s[4]+s[5], s[9]):
                name, info, other, index, value, length = struct.unpack_from("<IBBHQQ", b, pos)
                self.symbols[strings[name:].split(b"\0", 1)[0].decode()] = (index, value, length)

    def code(self, name, count=None):
        index, value, size = self.symbols[name]
        s = self.sections[index]
        off = s[4] + value - s[3]
        return self.data[off:off + (count if count is not None else size)]

elf = {k: Elf(build / (k+"-encap")) for k in "ACD"}
perm = "ntruplus_keccak_f1600_x1_aarch64"
p = elf["C"].code(perm)
assert len(p) == 1152 and p == elf["D"].code(perm) == elf["A"].code(perm)
source = (root / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/keccakf1600.S").read_text()
macro = source.split(".macro KECCAK_LIVE_PERMUTE\n",1)[1].split(".endm",1)[0]
instructions = [s.split("//",1)[0].strip() for s in macro.splitlines()]
instructions = [s for s in instructions if s and not s.endswith(":")]
round_code = elf["D"].code("Lhash_g_live_round", 4*len(instructions))
assert round_code in p, "D round/normalization instructions differ from standalone C"
pmu = {k: {event: statistics.median(row[event] for row in data["pmu_per_operation"][k])
           for event in data["pmu_per_operation"][k][0]} for k in "ACD"}
summary = {k: data[k] for k in (
    "experiment_id", "gate", "baseline_revision", "C_revision", "host",
    "compiler", "flags", "core", "pairs", "operations_per_sample",
    "warmups", "order", "results", "source_sha256")}
summary.update({
    "candidate_code_revision": "317a52f400fd84ee9b41d313548cc0dcbe81ba52",
    "decision": "accept D as next experimental champion; no production promotion",
    "correctness": {
        "mac_package": "make check pass; KAT byte-identical",
        "mac_sanitizers": "3841 cases pass; 256 frame/register capture cases pass",
        "pi_packages_A_C_D": "make check pass; KAT byte-identical",
        "pi_targeted": data["test"],
        "new_hash_g_ABI_sentinel_mask": 0,
        "kat_rsp_sha256": "22c72039845361ff142273150a59785bada5146c04018ce0a8b67b99a647eaa8",
        "standalone_Keccak_exact_opcode_identity": True,
        "fused_round_normalization_exact_opcode_identity": True,
        "shared_macro_instruction_words": len(instructions),
        "x0_through_x17_and_144_byte_frame_clear": "captured zero on return",
    },
    "D_winning_groups": {mode: {base: sum(x>y for x,y in zip(rows[base],rows["D"]))
                                for base in "AC"} for mode,rows in samples.items()},
    "pmu_per_operation_medians": pmu,
    "pmu_notes": "six balanced ACD orders, 200000 operations/run, user events, 100% scheduled; speculative load/store events, amortized process overhead",
    "linked_encap_sections": {k:e.sizes for k,e in elf.items()},
    "fused_function_bytes": len(elf["D"].code("ntruplus_hash_g_fused_aarch64")),
    "hash_path_own_stack_at_permutation_bytes": {"C": 400, "D": 144},
    "cleanup": "D clears its full 144-byte frame and caller-saved GPRs; C clears its 200-byte state but does not clear its permutation spill. C hook counts exclude D assembly clears.",
    "environment": {k:v for k,v in data["environment"].items() if k != "jobs"},
    "binary_sha256": {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(build.glob("[ACD]-*")) if not p.suffix},
    "raw_results": "/home/pi/gt768-fused-shake-hashg-20260911-e41/.build/d-gate-v1",
})
(exp / "D-summary.json").write_text(json.dumps(summary, indent=2)+"\n")
print(json.dumps({"pmu":pmu,"text":{k:e.sizes[".text"] for k,e in elf.items()},
                  "fused_bytes":summary["fused_function_bytes"],
                  "shared_instruction_words":len(instructions),
                  "wins":summary["D_winning_groups"],
                  "environment":summary["environment"]}, indent=2))
