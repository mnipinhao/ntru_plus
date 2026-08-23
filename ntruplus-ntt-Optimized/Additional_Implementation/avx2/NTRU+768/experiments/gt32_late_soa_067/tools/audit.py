#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SYMBOLS = (
    "crypto_kem_keypair", "crypto_kem_enc", "crypto_kem_dec_control",
    "crypto_kem_dec_latesoa", "ntruplus768_dec_control",
    "ntruplus768_dec_latesoa", "ntruplus768_unpack3_m_avx2",
    "ntruplus768_basemul_scale_m_avx2", "ntruplus768_invntt_m_avx2",
    "late_soa_full_basemul_i2_fused_asm",
    "gt32_tile4_attr_inverse_i1_cross3_asm", "poly_crepmod3", "hash_g",
    "hash_h", "ntruplus768_equal_m_modq12699_avx2",
)


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True)


def relocations(path: Path) -> list[str]:
    rows = []
    in_text = False
    for line in command("objdump", "-r", str(path)).splitlines():
        if line.startswith("RELOCATION RECORDS FOR ["):
            in_text = line.startswith("RELOCATION RECORDS FOR [.text")
            continue
        if not in_text or "R_X86_64_" not in line:
            continue
        rows.append(re.sub(r"^[0-9a-f]+\s+", "", line.strip()))
    return rows


def section_bytes(path: Path, section: str) -> bytes:
    encoded = bytearray()
    for line in command("objdump", "-s", "-j", section, str(path)).splitlines():
        fields = line.split()
        if len(fields) < 2 or re.fullmatch(r"[0-9a-f]+", fields[0]) is None:
            continue
        for field in fields[1:5]:
            if re.fullmatch(r"[0-9a-f]{8}", field) is None:
                break
            encoded.extend(bytes.fromhex(field))
    return bytes(encoded)


control_reloc = relocations(BUILD / "decap_control.o")
candidate_reloc = relocations(BUILD / "decap_candidate.o")
normalized_candidate = [
    row.replace("ntruplus768_dec_latesoa", "ntruplus768_dec_control")
       .replace("late_soa_full_basemul_i2_fused_asm",
                "ntruplus768_basemul_scale_m_avx2")
       .replace("gt32_tile4_attr_inverse_i1_cross3_asm",
                "ntruplus768_invntt_m_avx2")
    for row in candidate_reloc
]
if normalized_candidate != control_reloc:
    raise SystemExit("Decap object relocation audit failed")

control_code = section_bytes(
    BUILD / "decap_control.o", ".text.ntruplus768_dec_control")
candidate_code = section_bytes(
    BUILD / "decap_candidate.o", ".text.ntruplus768_dec_latesoa")
if control_code != candidate_code:
    raise SystemExit("Decap caller machine bytes differ before relocation")

placements = {}
for placement in ("normal", "reversed"):
    binary = BUILD / f"bench_{placement}"
    nm_rows = {}
    for line in command("nm", "-n", str(binary)).splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-1] in SYMBOLS:
            nm_rows[fields[-1]] = int(fields[0], 16)
    sections = {}
    for line in command("size", "-A", str(binary)).splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[0] in (".text", ".rodata", ".data",
                                               ".bss"):
            sections[fields[0]] = int(fields[1])
    elf_type = next(line.split(":", 1)[1].strip()
                    for line in command("readelf", "-h", str(binary)).splitlines()
                    if "Type:" in line)
    placements[placement] = {
        "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "elf_type": elf_type,
        "sections": sections,
        "symbols": nm_rows,
    }

output = {
    "schema": "gt32-late-soa-067-static-v1",
    "decap_relocations_control": control_reloc,
    "decap_relocations_candidate": candidate_reloc,
    "normalized_relocations_exact": True,
    "decap_caller_machine_bytes_exact_before_relocation": True,
    "decap_caller_code_bytes": len(control_code),
    "decap_caller_code_sha256": hashlib.sha256(control_code).hexdigest(),
    "allowed_call_target_changes": [
        "scale-B3 -> Late-SoA fused B3/post-I1",
        "current M inverse -> existing post-I1 remainder",
    ],
    "placements": placements,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "static.json").write_text(
    json.dumps(output, indent=2) + "\n")
print(json.dumps(output, indent=2))
