#!/usr/bin/env python3
"""Gate 11 decision report for rowpack promotion vs Forward v4 rewrite.

This target does not run benchmarks and does not generate assembly.  It
consolidates the already-recorded Pi5 evidence from Gates 1-10 into a single
promotion/rewrite decision point.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


OUTDIR = Path("docs/gt_soa_layout_experiment/forward_topology_decision")


def yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def yaml_dump(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{pad}{key}:")
                lines.append(yaml_dump(value, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}-")
                lines.append(yaml_dump(item, indent + 2))
            else:
                lines.append(f"{pad}- {yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{pad}{yaml_scalar(data)}"


def build_report() -> dict[str, Any]:
    return {
        "gate": "Gate 11: rowpack promotion / Forward topology decision",
        "status": "decision_report_no_benchmark_no_asm",
        "selected_option": "C_keep_rowpack_research_path_not_production",
        "decision": {
            "promote_rowpack_to_production": False,
            "start_forward_v4_asm_now": False,
            "keep_rowpack_as_experimental_backend": True,
            "next_allowed_work": (
                "Forward v4 topology model only; do not write ASM until the "
                "model predicts at least 150 cycles/NTT recoverable, preferably "
                "near 200 cycles/NTT."
            ),
        },
        "three_way_baseline_cycles": [
            {
                "path": "product_pipeline",
                "kpqc_final": 13473.203,
                "production_gt": 12254.750,
                "lazy_asm_rowpack": 12363.188,
                "rowpack_vs_kpqc": -1110.015,
                "rowpack_vs_gt": 108.438,
            },
            {
                "path": "product_add_pipeline",
                "kpqc_final": 16843.469,
                "production_gt": 14996.453,
                "lazy_asm_rowpack": 15556.625,
                "rowpack_vs_kpqc": -1286.844,
                "rowpack_vs_gt": 560.172,
            },
        ],
        "fullchain_stage_accounting_cycles": {
            "product": {
                "pipeline_delta": 94.015,
                "accounted_component_delta": 245.921,
                "unaccounted_glue_delta": -151.906,
                "component_deltas": {
                    "forward_ntt_x2": 640.718,
                    "basemul": -418.750,
                    "invntt": 23.953,
                },
            },
            "product_add": {
                "pipeline_delta": 623.812,
                "accounted_component_delta": 722.109,
                "unaccounted_glue_delta": -98.297,
                "component_deltas": {
                    "forward_ntt_x3": 1040.250,
                    "basemul_add": -337.141,
                    "invntt": 19.000,
                },
            },
        },
        "backend_status": {
            "basemul": "rowpack faster than production GT in fullchain stage accounting",
            "basemul_add": "rowpack faster than production GT in fullchain stage accounting",
            "invntt": "lazy ASM rowpack is production-near",
            "glue": "not the blocker; rowpack unaccounted glue is cheaper in the latest accounting",
            "forward_ntt": "remaining blocker; rowpack output ABI costs about 315-347 cycles/NTT",
        },
        "forward_no_go_evidence": [
            {
                "gate": "Gate 6",
                "path": "v3 structured-store / st4",
                "result": "rejected",
                "reason": "correctness passes but Forward NTT regresses to about 3152 cycles; st4/lane-store style is the wrong primitive",
            },
            {
                "gate": "Gate 8",
                "path": "v3a final-only permutation",
                "result": "rejected",
                "reason": "current v2 tail already matches the 24-permute/block lower bound under the allowed two-input Neon interleave model",
            },
            {
                "gate": "Gate 9",
                "path": "v3b stage345-only live-out rewrite",
                "result": "rejected",
                "reason": "current stage12 scratch is k32-major and stage345 arithmetic is lane-preserving, so rowpack plane live-out still needs a 24-permute/block network",
            },
            {
                "gate": "Gate 10",
                "path": "v3c stage12 scratch-layout-only rewrite",
                "result": "rejected",
                "reason": "partial scratch grouping is worse; fully rowpack-friendly scratch layout-only only moves the same 24-permute/block network earlier",
            },
        ],
        "forward_v4_conditions": {
            "name": "Forward v4 rowpack-native arithmetic topology",
            "scope": "earlier than the stage12 scratch boundary; arithmetic topology, not only store/scratch layout",
            "minimum_continue_gate_cycles_per_ntt": 150,
            "preferred_continue_gate_cycles_per_ntt": 200,
            "forbidden_next_steps": [
                "do not write v4 ASM before a topology model",
                "do not rerun Slothy on rejected v3 DAGs",
                "do not use st4, lane stores, scalar scatter, or scalar GT-to-rowpack conversion as the fix",
            ],
        },
        "options": {
            "A_continue_to_forward_topology_rewrite": {
                "decision": "not_now",
                "reason": "no v4 topology model currently predicts >=150 cycles/NTT recoverable under a valid arithmetic/live-layout plan",
            },
            "B_archive_rowpack_as_experimental_backend": {
                "decision": "too_strong",
                "reason": "rowpack clearly beats KPQC final and remains valuable as a research baseline",
            },
            "C_keep_rowpack_research_path_not_production": {
                "decision": "selected",
                "reason": "rowpack backend is strong, but production GT remains faster and simple Forward layout fixes are closed",
            },
        },
    }


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Gate 11 Rowpack Promotion / Forward Topology Decision",
        "",
        "Status: `decision_report_no_benchmark_no_asm`",
        "",
        "Decision: `C_keep_rowpack_research_path_not_production`",
        "",
        "Do not promote lazy ASM rowpack to production, and do not start Forward",
        "v4 assembly now.  Keep rowpack as an opt-in experimental backend and",
        "only continue toward Forward v4 after a topology model predicts at least",
        "`150 cycles/NTT` recoverable, preferably near `200 cycles/NTT`.",
        "",
        "## Three-Way Baseline",
        "",
        "| path | KPQC final | production GT | lazy ASM rowpack | rowpack vs KPQC | rowpack vs GT |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["three_way_baseline_cycles"]:
        lines.append(
            "| {path} | {kpqc:.3f} | {gt:.3f} | {rowpack:.3f} | {vs_kpqc:+.3f} | {vs_gt:+.3f} |".format(
                path=row["path"],
                kpqc=row["kpqc_final"],
                gt=row["production_gt"],
                rowpack=row["lazy_asm_rowpack"],
                vs_kpqc=row["rowpack_vs_kpqc"],
                vs_gt=row["rowpack_vs_gt"],
            )
        )
    lines.extend(
        [
            "",
            "## Component Blocker",
            "",
            "| path | pipeline delta | accounted component delta | unaccounted glue delta | main visible blocker |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    accounting = report["fullchain_stage_accounting_cycles"]
    lines.append(
        "| product | {pipeline:+.3f} | {accounted:+.3f} | {glue:+.3f} | Forward NTT x2 `{fwd:+.3f}`, basemul `{basemul:+.3f}`, InvNTT `{inv:+.3f}` |".format(
            pipeline=accounting["product"]["pipeline_delta"],
            accounted=accounting["product"]["accounted_component_delta"],
            glue=accounting["product"]["unaccounted_glue_delta"],
            fwd=accounting["product"]["component_deltas"]["forward_ntt_x2"],
            basemul=accounting["product"]["component_deltas"]["basemul"],
            inv=accounting["product"]["component_deltas"]["invntt"],
        )
    )
    lines.append(
        "| product-add | {pipeline:+.3f} | {accounted:+.3f} | {glue:+.3f} | Forward NTT x3 `{fwd:+.3f}`, basemul_add `{basemul:+.3f}`, InvNTT `{inv:+.3f}` |".format(
            pipeline=accounting["product_add"]["pipeline_delta"],
            accounted=accounting["product_add"]["accounted_component_delta"],
            glue=accounting["product_add"]["unaccounted_glue_delta"],
            fwd=accounting["product_add"]["component_deltas"]["forward_ntt_x3"],
            basemul=accounting["product_add"]["component_deltas"]["basemul_add"],
            inv=accounting["product_add"]["component_deltas"]["invntt"],
        )
    )
    lines.extend(
        [
            "",
            "Backend status:",
            "",
        ]
    )
    for key, value in report["backend_status"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Forward No-Go Evidence",
            "",
            "| gate | closed path | result | reason |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in report["forward_no_go_evidence"]:
        lines.append(
            f"| {item['gate']} | {item['path']} | `{item['result']}` | {item['reason']} |"
        )
    v4 = report["forward_v4_conditions"]
    lines.extend(
        [
            "",
            "## Forward v4 Conditions",
            "",
            f"- scope: {v4['scope']}",
            f"- minimum continue gate: `{v4['minimum_continue_gate_cycles_per_ntt']} cycles/NTT`",
            f"- preferred continue gate: `{v4['preferred_continue_gate_cycles_per_ntt']} cycles/NTT`",
            "",
            "Forbidden next steps:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in v4["forbidden_next_steps"])
    lines.extend(
        [
            "",
            "## Option Decision",
            "",
            "| option | decision | reason |",
            "| --- | --- | --- |",
        ]
    )
    for key, value in report["options"].items():
        lines.append(f"| `{key}` | `{value['decision']}` | {value['reason']} |")
    lines.extend(
        [
            "",
            "One-line conclusion: Gate 10 closes the small Forward-output-layout",
            "patch route.  Rowpack is a strong experimental backend, but promotion",
            "requires a larger Forward v4 arithmetic topology model before any new",
            "ASM or Slothy work.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    (OUTDIR / "decision.yml").write_text(yaml_dump(report) + "\n")
    (OUTDIR / "decision-report.md").write_text(report_markdown(report))
    print(f"wrote {OUTDIR / 'decision.yml'}")
    print(f"wrote {OUTDIR / 'decision-report.md'}")
    print("decision: keep rowpack experimental; do not start Forward v4 ASM without a topology model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
