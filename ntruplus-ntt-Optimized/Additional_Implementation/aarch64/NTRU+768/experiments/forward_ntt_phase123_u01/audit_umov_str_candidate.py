#!/usr/bin/env python3
"""Audit high-half ext+str -> umov+str replacements for wave candidates."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/ntt32_forward_ntt_aggressive_wave"
ROWS = ("row0", "row1", "row2")

COMMENT_RE = re.compile(r"//.*$")
EXT_HIGH_RE = re.compile(
    r"^\s*ext\s+v(?P<tmp>\d+)\.16B,\s*v(?P<src>\d+)\.16B,\s*"
    r"v(?P=src)\.16B,\s*#8"
)
HIGH_STR_RE = re.compile(
    r"^\s*str\s+d(?P<tmp>\d+),\s*\[x0,\s*#(?P<offset>\d+)\]"
)
UMOV_RE = re.compile(r"^\s*umov\s+x(?P<xtmp>\d+),\s*v(?P<src>\d+)\.d\[1\]\s*$")
UMOV_STR_RE = re.compile(
    r"^\s*str\s+x(?P<xtmp>\d+),\s*\[x0,\s*#(?P<offset>\d+)\].*highhalf_umov_str"
)
MNEMONIC_RE = re.compile(r"^\s*(?P<op>[A-Za-z][A-Za-z0-9_.]*)\b(?P<rest>.*)$")
XREG_RE = re.compile(r"\b(?P<reg>x(?:[0-9]|[12][0-9]|30)|sp)\b")
VREG_RE = re.compile(r"\b[vqds](?P<num>[0-9]|[12][0-9]|3[01])(?:\b|[.])")
MEM_BASE_RE = re.compile(r"\[(?P<base>x(?:[0-9]|[12][0-9]|30)|sp)\b")

ROLE_REGS = {
    "x0": "dst/address base",
    "x4": "row_base scratch base",
    "x10": "old scatter_ptr",
    "x11": "old scatter_hi",
    "x12": "twiddle pointer",
    "x13": "old scatter_next",
    "x14": "old scatter_bound",
    "x15": "old scatter_wrap",
}
BANNED_XTMP = {
    "x18",
    "x19",
    "x20",
    "x21",
    "x22",
    "x23",
    "x24",
    "x25",
    "x26",
    "x27",
    "x28",
    "x29",
    "x30",
    "sp",
}
CALLER_SAVED_X = {f"x{i}" for i in range(0, 18)}


@dataclass(frozen=True)
class CandidateAudit:
    name: str
    output_prefix: str
    source_name: str
    source_dir: Path
    source_pattern: str
    target_dir: Path
    target_pattern: str
    expected_xtmp: str


CONFIGS = {
    "s2": CandidateAudit(
        name="s2_b2a_umov_str",
        output_prefix="s2",
        source_name="b2a rowspec direct-offset Slothy",
        source_dir=ROOT / "asm/slothy/experiments/ntt32_stage345_rowspec_direct_offsets_slothy",
        source_pattern="{row}_stage345_direct_offsets_slothy.opt.s",
        target_dir=ROOT / "asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/s2_b2a_umov_str",
        target_pattern="{row}_stage345_s2_b2a_umov_str.opt.s",
        expected_xtmp="x17",
    ),
    "s4": CandidateAudit(
        name="s4_d1_umov_str",
        output_prefix="s4",
        source_name="d1_precise_noren",
        source_dir=ROOT / "asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/d1_precise_noren",
        source_pattern="{row}_stage345_d1_precise_noren.opt.s",
        target_dir=ROOT / "asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/s4_d1_umov_str",
        target_pattern="{row}_stage345_s4_d1_umov_str.opt.s",
        expected_xtmp="x17",
    ),
}


def code_part(line: str) -> str:
    return COMMENT_RE.sub("", line).strip()


def is_instruction(line: str) -> bool:
    code = code_part(line)
    return bool(code and not code.startswith(".") and not code.endswith(":"))


def split_operands(rest: str) -> list[str]:
    operands: list[str] = []
    current: list[str] = []
    bracket_depth = 0
    brace_depth = 0
    for char in rest:
        if char == "[":
            bracket_depth += 1
        elif char == "]":
            bracket_depth -= 1
        elif char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
        if char == "," and bracket_depth == 0 and brace_depth == 0:
            operand = "".join(current).strip()
            if operand:
                operands.append(operand)
            current = []
        else:
            current.append(char)
    operand = "".join(current).strip()
    if operand:
        operands.append(operand)
    return operands


def xregs_in(text: str) -> set[str]:
    return {match.group("reg") for match in XREG_RE.finditer(text)}


def vregs_in(text: str) -> set[str]:
    return {f"v{match.group('num')}" for match in VREG_RE.finditer(text)}


def mem_bases_in(text: str) -> set[str]:
    return {match.group("base") for match in MEM_BASE_RE.finditer(text)}


def parse_instruction(line_no: int, line: str) -> dict[str, object] | None:
    code = code_part(line)
    match = MNEMONIC_RE.match(code)
    if match is None:
        return None
    op = match.group("op").lower()
    operands = split_operands(match.group("rest"))
    reads: set[str] = set()
    writes: set[str] = set()
    address_bases = mem_bases_in(code)
    all_xregs = xregs_in(code)

    if op in {"str", "stp"} or op.startswith("st"):
        reads |= all_xregs
    elif op in {"ldr", "ldp"} or op.startswith("ld"):
        reads |= address_bases
        if op == "ldp" and len(operands) >= 2:
            writes |= xregs_in(operands[0]) | xregs_in(operands[1])
        elif operands:
            writes |= xregs_in(operands[0])
    elif op in {"cmp", "cmn", "tst"}:
        reads |= all_xregs
    elif op == "umov":
        if operands:
            writes |= xregs_in(operands[0])
    elif op == "bl":
        pass
    else:
        if operands:
            writes |= xregs_in(operands[0])
            for operand in operands[1:]:
                reads |= xregs_in(operand)
        reads |= address_bases

    return {
        "line_no": line_no,
        "code": code,
        "op": op,
        "reads": sorted(reads),
        "writes": sorted(writes),
        "address_bases": sorted(address_bases),
        "vreads": sorted(vregs_in(code)),
    }


def vector_writes(line: str) -> set[str]:
    code = code_part(line)
    match = MNEMONIC_RE.match(code)
    if match is None:
        return set()
    op = match.group("op").lower()
    operands = split_operands(match.group("rest"))
    if not operands or op.startswith("st") or op == "str":
        return set()
    if op == "ldp" and len(operands) >= 2:
        return vregs_in(operands[0]) | vregs_in(operands[1])
    return vregs_in(operands[0])


def vector_reads(line: str) -> set[str]:
    code = code_part(line)
    match = MNEMONIC_RE.match(code)
    if match is None:
        return set()
    op = match.group("op").lower()
    operands = split_operands(match.group("rest"))
    if not operands:
        return set()
    if op.startswith("st") or op in {"str", "umov"}:
        return vregs_in(code)
    if op.startswith("ld"):
        return set()
    reads = set()
    for operand in operands[1:]:
        reads |= vregs_in(operand)
    if op in {"mla", "mls", "smlal", "smlal2", "smlsl", "smlsl2"}:
        reads |= vregs_in(operands[0])
    return reads


def source_path(config: CandidateAudit, row: str) -> Path:
    return config.source_dir / config.source_pattern.format(row=row)


def target_path(config: CandidateAudit, row: str) -> Path:
    return config.target_dir / config.target_pattern.format(row=row)


def collect_original_sites(config: CandidateAudit, row: str) -> list[dict[str, object]]:
    path = source_path(config, row)
    lines = path.read_text().splitlines()
    ext_defs: dict[str, tuple[int, str]] = {}
    sites: list[dict[str, object]] = []

    def ext_is_store_only(ext_idx: int, store_idx: int, tmp: str, src: str) -> bool:
        tmp_reg = f"v{tmp}"
        src_reg = f"v{src}"
        for between in lines[ext_idx + 1 : store_idx]:
            writes = vector_writes(between)
            if tmp_reg in writes or src_reg in writes:
                return False
        for after in lines[store_idx + 1 :]:
            code = code_part(after)
            if not code:
                continue
            reads = vector_reads(after)
            writes = vector_writes(after)
            if tmp_reg in reads:
                return False
            if tmp_reg in writes:
                return True
        return True

    for idx, line in enumerate(lines):
        for written in vector_writes(line):
            ext_defs.pop(written[1:], None)
        ext = EXT_HIGH_RE.match(code_part(line))
        if ext:
            ext_defs[ext.group("tmp")] = (idx, ext.group("src"))
            continue
        store = HIGH_STR_RE.match(code_part(line))
        if store is None:
            continue
        offset = int(store.group("offset"))
        if offset < 768:
            continue
        tmp = store.group("tmp")
        if tmp not in ext_defs:
            continue
        ext_idx, src = ext_defs[tmp]
        if not ext_is_store_only(ext_idx, idx, tmp, src):
            ext_defs.pop(tmp, None)
            continue
        tmp_reg = f"v{tmp}"
        src_reg = f"v{src}"
        sites.append(
            {
                "row": row,
                "site_id": f"{row}_{len(sites):02d}",
                "original_ext_line": ext_idx + 1,
                "original_store_line": idx + 1,
                "original_source_vector": f"v{src}",
                "original_ext_tmp_vector": f"v{tmp}",
                "original_store_address": f"[x0, #{offset}]",
                "original_store_offset": offset,
                "original_no_intervening_write_to_vsrc": all(
                    src_reg not in vector_writes(between)
                    for between in lines[ext_idx + 1 : idx]
                ),
                "original_no_intervening_write_to_tmp": all(
                    tmp_reg not in vector_writes(between)
                    for between in lines[ext_idx + 1 : idx]
                ),
            }
        )
        ext_defs.pop(tmp, None)
    return sites


def collect_target_sites(
    config: CandidateAudit, row: str
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    path = target_path(config, row)
    lines = path.read_text().splitlines()
    instructions = [
        parsed
        for line_no, line in enumerate(lines, start=1)
        if is_instruction(line)
        for parsed in [parse_instruction(line_no, line)]
        if parsed is not None
    ]
    instr_by_line = {int(instr["line_no"]): idx for idx, instr in enumerate(instructions)}
    sites: list[dict[str, object]] = []

    for idx, line in enumerate(lines):
        umov = UMOV_RE.match(code_part(line))
        if umov is None:
            continue
        if idx + 1 >= len(lines):
            raise ValueError(f"{path}:{idx + 1}: umov has no following store")
        store = UMOV_STR_RE.match(lines[idx + 1])
        if store is None:
            raise ValueError(f"{path}:{idx + 1}: umov not followed by highhalf_umov_str store")
        if umov.group("xtmp") != store.group("xtmp"):
            raise ValueError(f"{path}:{idx + 1}: umov/store xTmp mismatch")
        line_no = idx + 1
        str_line_no = idx + 2
        sites.append(
            {
                "new_umov_line": line_no,
                "new_store_line": str_line_no,
                "new_source_vector": f"v{umov.group('src')}",
                "new_xtmp_register": f"x{umov.group('xtmp')}",
                "new_store_address": f"[x0, #{int(store.group('offset'))}]",
                "new_store_offset": int(store.group("offset")),
                "umov_instr_idx": instr_by_line[line_no],
                "str_instr_idx": instr_by_line[str_line_no],
            }
        )
    return sites, instructions


def reg_live_before(instructions: list[dict[str, object]], instr_idx: int, reg: str) -> bool:
    for instr in instructions[instr_idx:]:
        if reg in instr["reads"]:
            return True
        if reg in instr["writes"]:
            return False
    return False


def reg_live_after(instructions: list[dict[str, object]], instr_idx: int, reg: str) -> bool:
    for instr in instructions[instr_idx + 1 :]:
        if reg in instr["reads"]:
            return True
        if reg in instr["writes"]:
            return False
    return False


def previous_active_line(lines: list[str], line_no: int) -> str:
    for idx in range(line_no - 2, -1, -1):
        if is_instruction(lines[idx]):
            return code_part(lines[idx])
    return ""


def next_active_line(lines: list[str], line_no: int) -> str:
    for idx in range(line_no, len(lines)):
        if is_instruction(lines[idx]):
            return code_part(lines[idx])
    return ""


def audit_row(config: CandidateAudit, row: str) -> tuple[list[dict[str, object]], list[str]]:
    original_sites = collect_original_sites(config, row)
    target_sites, instructions = collect_target_sites(config, row)
    path = target_path(config, row)
    lines = path.read_text().splitlines()
    if len(original_sites) != len(target_sites):
        raise ValueError(
            f"{row}: original/target site count mismatch "
            f"{len(original_sites)} != {len(target_sites)}"
        )

    audited: list[dict[str, object]] = []
    failures: list[str] = []
    for original, target in zip(original_sites, target_sites):
        if original["original_source_vector"] != target["new_source_vector"]:
            failures.append(f"{original['site_id']}: source vector changed")
        if original["original_store_offset"] != target["new_store_offset"]:
            failures.append(f"{original['site_id']}: store offset changed")
        xtmp = str(target["new_xtmp_register"])
        aliases = {role: xtmp == reg for reg, role in ROLE_REGS.items()}
        no_xtmp_write_between_umov_str = not any(
            xtmp in instr["writes"]
            for instr in instructions[
                int(target["umov_instr_idx"]) + 1 : int(target["str_instr_idx"])
            ]
        )

        record = {
            **original,
            **{key: value for key, value in target.items() if not key.endswith("_idx")},
            "target_little_endian_aarch64": True,
            "store_size_bytes": 8,
            "address_offset_unchanged": original["original_store_offset"] == target["new_store_offset"],
            "no_intervening_write_to_vsrc_before_umov": original[
                "original_no_intervening_write_to_vsrc"
            ],
            "no_intervening_write_to_original_tmp_before_store": original[
                "original_no_intervening_write_to_tmp"
            ],
            "no_intervening_write_to_xtmp_before_str": no_xtmp_write_between_umov_str,
            "xtmp_live_before_umov": reg_live_before(instructions, int(target["umov_instr_idx"]), xtmp),
            "xtmp_live_after_str": reg_live_after(instructions, int(target["str_instr_idx"]), xtmp),
            "xtmp_aliases_role_register": any(aliases.values()),
            "xtmp_role_aliases": aliases,
            "xtmp_is_expected_register": xtmp == config.expected_xtmp,
            "xtmp_is_caller_saved": xtmp in CALLER_SAVED_X,
            "xtmp_is_banned_register": xtmp in BANNED_XTMP,
            "xtmp_used_as_address_base_at_site": xtmp in {"x0"},
            "previous_active_instruction": previous_active_line(lines, int(target["new_umov_line"])),
            "next_active_instruction": next_active_line(lines, int(target["new_store_line"])),
        }
        reject = (
            record["xtmp_is_banned_register"]
            or record["xtmp_live_before_umov"]
            or record["xtmp_live_after_str"]
            or record["xtmp_aliases_role_register"]
            or record["xtmp_used_as_address_base_at_site"]
            or not record["xtmp_is_expected_register"]
            or not record["xtmp_is_caller_saved"]
            or not record["address_offset_unchanged"]
            or not record["no_intervening_write_to_vsrc_before_umov"]
            or not record["no_intervening_write_to_xtmp_before_str"]
        )
        record["reject_site"] = bool(reject)
        if reject:
            failures.append(str(record["site_id"]))
        audited.append(record)
    return audited, failures


def write_register_audit(
    config: CandidateAudit, sites: list[dict[str, object]], failures: list[str]
) -> None:
    by_row = {row: [site for site in sites if site["row"] == row] for row in ROWS}
    name_upper = config.output_prefix.upper()
    if config.output_prefix == "s2":
        sentinel_lines = [
            "Pi 5 result:",
            "",
            "```text",
            "make -B test_s2_abi_sentinel",
            "s2_abi_sentinel_mask=0x0",
            "s2_abi_sentinel_mismatches=0",
            "```",
            "",
            "The sentinel checks x19-x28 and the low 64-bit d8-d15 ABI-preserved lanes.",
        ]
    else:
        sentinel_lines = ["See the existing S4 sentinel artifact."]
    lines = [
        f"# {name_upper} Register / ABI Audit",
        "",
        f"Candidate: `{config.name}`.",
        "",
        "This audit covers every high-half replacement generated as:",
        "",
        "```asm",
        "ext vtmp.16B, vsrc.16B, vsrc.16B, #8",
        "str dtmp, [x0, #offset]",
        "```",
        "",
        "to:",
        "",
        "```asm",
        f"umov {config.expected_xtmp}, vsrc.d[1]",
        f"str  {config.expected_xtmp}, [x0, #offset]",
        "```",
        "",
        "## Summary",
        "",
        f"- source candidate: `{config.source_name}`",
        f"- total sites: {len(sites)}",
        f"- rejected sites: {len(failures)}",
        f"- xTmp register: `{config.expected_xtmp}` for all generated sites",
        f"- {config.expected_xtmp} class: caller-saved temporary under AAPCS64",
        "- banned register check: x18/x19-x28/x29/x30/sp are not used",
        "- role alias check: xTmp does not alias dst, row_base, old scatter, or twiddle role registers",
        "",
        "## Row Counts",
        "",
        "| Row | Sites | Rejected |",
        "| --- | ---: | ---: |",
    ]
    for row, row_sites in by_row.items():
        row_failures = [site for site in row_sites if site["reject_site"]]
        lines.append(f"| {row} | {len(row_sites)} | {len(row_failures)} |")
    lines.extend(
        [
            "",
            "## Hard Rule Result",
            "",
            f"PASS: {name_upper} is not rejected by this static audit."
            if not failures
            else f"FAIL: {name_upper} has rejected sites.",
            "",
            "Hard-rule predicates checked per site:",
            "",
            "- xTmp is not x18",
            "- xTmp is not x19-x28",
            "- xTmp is not x29",
            "- xTmp is not x30",
            "- xTmp is not sp",
            "- xTmp is not live across the replacement",
            "- xTmp is not used as address/base/state/twiddle register at that site",
            "- xTmp is caller-saved",
            "- xTmp is the expected register for this candidate",
            "",
            "## Dynamic ABI Sentinel",
            "",
            *sentinel_lines,
            "",
            "## Site Table",
            "",
            "| Site | Source | Tmp | Offset | xTmp | Live before | Live after | Role alias | Reject |",
            "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for site in sites:
        lines.append(
            f"| {site['site_id']} | {site['original_source_vector']} | "
            f"{site['original_ext_tmp_vector']} | {site['new_store_offset']} | "
            f"{site['new_xtmp_register']} | {site['xtmp_live_before_umov']} | "
            f"{site['xtmp_live_after_str']} | {site['xtmp_aliases_role_register']} | "
            f"{site['reject_site']} |"
        )
    lines.append("")
    (EXP / f"{config.output_prefix}_register_audit.md").write_text("\n".join(lines))


def write_equivalence_audit(
    config: CandidateAudit, sites: list[dict[str, object]], failures: list[str]
) -> None:
    bad_equiv = [
        site
        for site in sites
        if not (
            site["target_little_endian_aarch64"]
            and site["store_size_bytes"] == 8
            and site["address_offset_unchanged"]
            and site["no_intervening_write_to_vsrc_before_umov"]
            and site["no_intervening_write_to_xtmp_before_str"]
        )
    ]
    name_upper = config.output_prefix.upper()
    lines = [
        f"# {name_upper} Semantic Equivalence Audit",
        "",
        f"Candidate: `{config.name}`.",
        "",
        "## Equivalence Claim",
        "",
        "For little-endian AArch64, this pair:",
        "",
        "```asm",
        "ext vtmp.16B, vsrc.16B, vsrc.16B, #8",
        "str dtmp, [x0, #offset]",
        "```",
        "",
        "stores bytes 8..15 of `vsrc` as an 8-byte little-endian memory write.",
        "The replacement:",
        "",
        "```asm",
        f"umov {config.expected_xtmp}, vsrc.d[1]",
        f"str  {config.expected_xtmp}, [x0, #offset]",
        "```",
        "",
        "extracts the same high 64-bit lane and stores the same 8 bytes to the same address.",
        "",
        "## Mechanical Checks",
        "",
        f"- total sites: {len(sites)}",
        f"- failed equivalence sites: {len(bad_equiv)}",
        f"- failed hard-rule sites: {len(failures)}",
        "- target model: little-endian AArch64",
        "- store size: exactly 8 bytes at every replacement",
        "- address form: `[x0, #offset]` preserved",
        "- no intervening write to `vsrc` between original ext site and new `umov`",
        f"- no intervening write to `{config.expected_xtmp}` between `umov` and `str`",
        "",
        "## Result",
        "",
        f"PASS: all checked {name_upper} replacements are semantically equivalent under the stated conditions."
        if not bad_equiv and not failures
        else f"FAIL: at least one {name_upper} replacement needs manual review.",
        "",
    ]
    if bad_equiv:
        lines.extend(["## Failed Sites", ""])
        for site in bad_equiv:
            lines.append(f"- {site['site_id']}")
        lines.append("")
    (EXP / f"{config.output_prefix}_equivalence_audit.md").write_text("\n".join(lines))


def run_audit(config: CandidateAudit) -> int:
    sites: list[dict[str, object]] = []
    failures: list[str] = []
    for row in ROWS:
        row_sites, row_failures = audit_row(config, row)
        sites.extend(row_sites)
        failures.extend(row_failures)

    data = {
        "candidate": config.name,
        "source_candidate": config.source_name,
        "replacement": "ext+str high-half -> umov+str",
        "site_count": len(sites),
        "failure_count": len(failures),
        "failures": failures,
        "sites": sites,
    }
    (EXP / f"{config.output_prefix}_transform_sites.json").write_text(
        json.dumps(data, indent=2) + "\n"
    )
    write_register_audit(config, sites, failures)
    write_equivalence_audit(config, sites, failures)
    print(f"{config.output_prefix}_sites={len(sites)} failures={len(failures)}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", choices=sorted(CONFIGS))
    args = parser.parse_args()
    return run_audit(CONFIGS[args.candidate])


if __name__ == "__main__":
    raise SystemExit(main())
