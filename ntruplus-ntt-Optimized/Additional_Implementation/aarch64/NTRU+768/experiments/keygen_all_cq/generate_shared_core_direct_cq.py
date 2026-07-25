#!/usr/bin/env python3
"""Generate a dual-endpoint NTT with one shared Phase123 prefix.

The generic block-major and keygen CQ entrypoints share the exact production
prologue, Phase123 body, table image, and epilogue.  Stage12 and Stage345 are
row-interleaved in the active source, so the endpoint-specific suffix begins at
row0 Stage12 rather than at Stage345 alone.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRODUCTION = ROOT / "asm/gt/ntt/poly_ntt.n1.opt.S"
DIRECT_CQ = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_to_cq_endpoint.S"
DIRECT_CQ_MAP = HERE / "direct_cq_endpoint_map.json"
OUTPUT = ROOT / "asm/gt/experiment/forward_ntt/poly_ntt_shared_core_direct_cq.S"
OUTPUT_MAP = HERE / "shared_core_direct_cq_contract.json"
OUTPUT_MD = HERE / "shared_core_direct_cq_design.md"

BODY_START = "    sub sp, sp, #1696"
SUFFIX_START = "    // ---- row0: Stage12 one-pass block0+block1+block2 live-out ----"
EPILOGUE_START = "    ldp d14, d15, [sp, #112]"
TABLE_INCLUDE = '.include "asm/gt/ntt/poly_ntt_tables.inc"'
MODE_OFFSET = 8

INSTRUCTION_RE = re.compile(r"^\s*[a-zA-Z][a-zA-Z0-9.]*\s")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_index(lines: list[str], marker: str, name: str) -> int:
    matches = [index for index, line in enumerate(lines) if line == marker]
    if len(matches) != 1:
        raise ValueError(f"{name}: expected one marker, got {len(matches)}")
    return matches[0]


def count_instructions(lines: list[str]) -> int:
    count = 0
    for line in lines:
        code = line.split("//", 1)[0].strip()
        if not code or code.endswith(":") or code.startswith("."):
            continue
        if INSTRUCTION_RE.match(code + " "):
            count += 1
    return count


def render_markdown(result: dict[str, object]) -> str:
    counts = result["instruction_model"]
    assert isinstance(counts, dict)
    return f"""# Shared-Core Direct-CQ Design

Date: 2026-07-23

Status: default-off candidate; differential, ABI, full-KEM correctness, PMU,
and code-size gates pass. Production default remains unchanged.

## Real source boundary

The active forward NTT is not organized as all Stage12 followed by all
Stage345. It executes:

```text
shared prologue + Phase123 for all rows
  -> row0 Stage12 + Stage345
  -> row1 Stage12 + Stage345
  -> row2 Stage12 + Stage345
  -> shared epilogue
```

Therefore the safe shared boundary is immediately before row0 Stage12. The
generic and CQ suffixes each retain their exact arithmetic, reduction, and
store contracts.

## Internal dispatch contract

```text
poly_ntt:
  w2 = 0
  branch shared body

gt_experiment_poly_ntt_to_cq:
  w2 = 1
  fall through shared body

shared body:
  allocate existing 1696-byte frame
  save public selector at [sp, #8]
  run exact production Phase123
  load selector and branch to generic or CQ row suffix
```

`[sp, #8]` is unused by the production source. `[sp, #0]` remains the existing
Slothy GPR spill slot. The selector is public and fixed by the called symbol;
it is not derived from polynomial data.

## Static instruction model

| Region | Instructions |
|---|---:|
| shared prefix including prologue | {counts['shared_prefix']} |
| generic row suffix | {counts['generic_suffix']} |
| CQ row suffix | {counts['cq_suffix']} |
| shared epilogue | {counts['shared_epilogue']} |
| dispatch overhead | {counts['dispatch_overhead']} |
| two separate full bodies | {counts['separate_total']} |
| generated dual body | {counts['dual_total']} |
| estimated instructions removed | {counts['estimated_removed']} |

The object also includes the NTT tables only once instead of once per complete
function body. Actual linked text size remains the deciding measurement.

## Measured outcome

The full measurements and build conditions are recorded in
`phase4-shared-core-results.md`. In summary, the shared object removes 8,432
bytes of linked text relative to the separate generic plus direct-CQ bodies.
Its CQ entry retires four extra instructions and costs about five cycles per
forward NTT in the endpoint harness. The generic entry retires six extra
instructions; no stable cycle regression was visible in the full-KEM runs.

## Hard invariants

- Generic suffix is copied exactly from production.
- CQ suffix is copied exactly from the audited direct-CQ candidate.
- Shared prefix and epilogue must be byte-identical between both sources.
- No `bl`, new scratch handoff, arithmetic change, reduction change, or
  secret-dependent branch is introduced.
- Production default does not link this object.
"""


def main() -> None:
    production_lines = PRODUCTION.read_text().splitlines()
    cq_lines = DIRECT_CQ.read_text().splitlines()
    cq_map = json.loads(DIRECT_CQ_MAP.read_text())
    if sha256(DIRECT_CQ) != cq_map["output_sha256"]:
        raise ValueError("direct-CQ source does not match its audited map")

    p_body = unique_index(production_lines, BODY_START, "production body")
    p_suffix = unique_index(production_lines, SUFFIX_START, "production suffix")
    p_epilogue = unique_index(production_lines, EPILOGUE_START, "production epilogue")
    p_table = unique_index(production_lines, TABLE_INCLUDE, "production table")
    c_body = unique_index(cq_lines, BODY_START, "CQ body")
    c_suffix = unique_index(cq_lines, SUFFIX_START, "CQ suffix")
    c_epilogue = unique_index(cq_lines, EPILOGUE_START, "CQ epilogue")
    c_table = unique_index(cq_lines, TABLE_INCLUDE, "CQ table")

    shared_prefix = production_lines[p_body:p_suffix]
    cq_prefix = cq_lines[c_body:c_suffix]
    generic_suffix = production_lines[p_suffix:p_epilogue]
    cq_suffix = cq_lines[c_suffix:c_epilogue]
    shared_epilogue = production_lines[p_epilogue:p_epilogue + 9]
    cq_epilogue = cq_lines[c_epilogue:c_epilogue + 9]
    if shared_prefix != cq_prefix:
        raise ValueError("production and direct-CQ prefixes are not identical")
    if shared_epilogue != cq_epilogue:
        raise ValueError("production and direct-CQ epilogues are not identical")
    if production_lines[p_table] != cq_lines[c_table]:
        raise ValueError("production and direct-CQ table includes differ")
    if any(f"[sp, #{MODE_OFFSET}]" in line for line in production_lines):
        raise ValueError(f"mode stack slot [sp, #{MODE_OFFSET}] is no longer free")

    prefix_with_mode = list(shared_prefix)
    if prefix_with_mode[0] != BODY_START:
        raise ValueError("unexpected shared-prefix first instruction")
    prefix_with_mode.insert(1, f"    str w2, [sp, #{MODE_OFFSET}]  // public endpoint selector")

    preamble = [
        "/* Experiment-only dual endpoint with a shared production prefix. */",
        f"/* production_sha256={sha256(PRODUCTION)} */",
        f"/* direct_cq_sha256={sha256(DIRECT_CQ)} */",
        "/* Production default is unchanged. */",
        "",
        ".text",
        ".align 4",
        ".equ STACK_LOC_0, 0",
        "",
        ".global poly_ntt",
        ".global _poly_ntt",
        ".global gt_block_major_poly_ntt",
        ".global _gt_block_major_poly_ntt",
        ".type poly_ntt, %function",
        "poly_ntt:",
        "_poly_ntt:",
        "gt_block_major_poly_ntt:",
        "_gt_block_major_poly_ntt:",
        "    mov w2, #0",
        "    b .Lgt_shared_core_entry",
        "",
        ".global gt_experiment_poly_ntt_to_cq",
        ".type gt_experiment_poly_ntt_to_cq, %function",
        "gt_experiment_poly_ntt_to_cq:",
        "    mov w2, #1",
        ".Lgt_shared_core_entry:",
    ]
    dispatch = [
        f"    ldr w2, [sp, #{MODE_OFFSET}]",
        "    cbnz w2, .Lgt_shared_core_cq_suffix",
        ".Lgt_shared_core_generic_suffix:",
    ]
    between_suffixes = [
        "    b .Lgt_shared_core_epilogue",
        ".Lgt_shared_core_cq_suffix:",
    ]
    ending = [
        ".Lgt_shared_core_epilogue:",
        *shared_epilogue,
        ".Lgt_shared_core_end:",
        ".size poly_ntt, .Lgt_shared_core_end-poly_ntt",
        ".size gt_experiment_poly_ntt_to_cq, .Lgt_shared_core_end-gt_experiment_poly_ntt_to_cq",
        ".global poly_ntt_end",
        "poly_ntt_end:",
        "",
        TABLE_INCLUDE,
    ]
    output_lines = [
        *preamble,
        *prefix_with_mode,
        *dispatch,
        *generic_suffix,
        *between_suffixes,
        *cq_suffix,
        *ending,
    ]
    output_text = "\n".join(output_lines) + "\n"
    OUTPUT.write_text(output_text)

    instruction_model = {
        "shared_prefix": count_instructions(shared_prefix),
        "generic_suffix": count_instructions(generic_suffix),
        "cq_suffix": count_instructions(cq_suffix),
        "shared_epilogue": count_instructions(shared_epilogue),
        "dispatch_overhead": 7,
    }
    instruction_model["separate_total"] = (
        2 * instruction_model["shared_prefix"]
        + instruction_model["generic_suffix"]
        + instruction_model["cq_suffix"]
        + 2 * instruction_model["shared_epilogue"]
    )
    instruction_model["dual_total"] = (
        instruction_model["shared_prefix"]
        + instruction_model["generic_suffix"]
        + instruction_model["cq_suffix"]
        + instruction_model["shared_epilogue"]
        + instruction_model["dispatch_overhead"]
    )
    instruction_model["estimated_removed"] = (
        instruction_model["separate_total"] - instruction_model["dual_total"]
    )

    result = {
        "candidate": "poly_ntt_shared_core_direct_cq",
        "production_source": str(PRODUCTION.relative_to(ROOT)),
        "production_sha256": sha256(PRODUCTION),
        "direct_cq_source": str(DIRECT_CQ.relative_to(ROOT)),
        "direct_cq_sha256": sha256(DIRECT_CQ),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(output_text.encode()).hexdigest(),
        "boundary": SUFFIX_START.strip(),
        "mode_stack_offset": MODE_OFFSET,
        "selector_public": True,
        "bl_introduced": False,
        "arithmetic_changed": False,
        "reduction_changed": False,
        "production_default_changed": False,
        "instruction_model": instruction_model,
    }
    OUTPUT_MAP.write_text(json.dumps(result, indent=2) + "\n")
    OUTPUT_MD.write_text(render_markdown(result))
    print(
        f"generated {OUTPUT.relative_to(ROOT)}; "
        f"estimated_removed={instruction_model['estimated_removed']} instructions"
    )


if __name__ == "__main__":
    main()
