#!/usr/bin/env python3
"""Normalize and summarize the G1R123+S2 same-binary paired PMU run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PRIMARY_SCOPES = (
    "encap_total",
    "decap_total",
    "encap_ntt_r",
    "encap_ntt_m",
    "decap_ntt_m1",
    "decap_ntt_r1",
)
DIAGNOSTIC_EVENTS = (
    "branch_misses",
    "l1i_refill",
    "l1i_miss",
    "stall_frontend",
    "stall_backend",
)


def parse_fields(line: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field in line.rstrip().split(",")[1:]:
        key, value = field.split("=", 1)
        fields[key] = value
    return fields


def normalized_row(fields: dict[str, str]) -> dict[str, Any]:
    iterations = int(fields["iterations"])
    result: dict[str, Any] = {
        "scope": fields["scope"],
        "event": fields["event"],
        "samples": int(fields["samples"]),
        "iterations": iterations,
        "wins": int(fields["wins"]),
        "ties": int(fields["ties"]),
        "candidate_win_rate_percent": int(fields["candidate_win_rate_milli_percent"]) / 1000.0,
        "tie_rate_percent": int(fields["tie_rate_milli_percent"]) / 1000.0,
    }
    for key in ("a_p10", "a_p50", "a_p90", "b_p10", "b_p50", "b_p90"):
        result[key] = int(fields[key]) / iterations
    for key in ("delta_p10", "delta_p50", "delta_p90"):
        result[key] = int(fields[key]) / iterations
    result["mad"] = int(fields["mad"]) / iterations
    result["delta_percent_vs_a_p50"] = 100.0 * result["delta_p50"] / result["a_p50"]
    return result


def parse_pmu(path: Path) -> dict[str, Any]:
    benchmark: dict[str, str] = {}
    correctness: dict[str, dict[str, int]] = {}
    event_support: dict[str, dict[str, Any]] = {}
    rows: dict[str, dict[str, dict[str, Any]]] = {}
    cpi: dict[str, dict[str, float]] = {}

    for line in path.read_text().splitlines():
        if line.startswith("benchmark,"):
            benchmark = parse_fields(line)
        elif line.startswith("correctness,"):
            fields = parse_fields(line)
            phase = fields.pop("phase")
            correctness[phase] = {key: int(value) for key, value in fields.items()}
        elif line.startswith("event_support,"):
            fields = parse_fields(line)
            event = fields.pop("event")
            event_support[event] = {
                "available": bool(int(fields["available"])),
                "type": int(fields["type"]),
                "config": fields["config"],
            }
        elif line.startswith("paired_raw,"):
            row = normalized_row(parse_fields(line))
            rows.setdefault(row["event"], {})[row["scope"]] = row
        elif line.startswith("cpi_summary,"):
            fields = parse_fields(line)
            scope = fields.pop("scope")
            cpi[scope] = {key: float(value) for key, value in fields.items()}

    return {
        "benchmark": benchmark,
        "correctness": correctness,
        "event_support": event_support,
        "measurements": rows,
        "cpi": cpi,
    }


def promotion_gate(report: dict[str, Any], layout: dict[str, Any]) -> dict[str, Any]:
    correctness = report["correctness"]
    cycles = report["measurements"]["cycles"]
    checks = {
        "prepare_correctness": correctness.get("prepare", {}).get("mismatches") == 0
        and correctness.get("prepare", {}).get("capture_error") == 0,
        "paired_correctness": correctness.get("paired", {}).get("mismatches") == 0,
        "same_binary_linkage": layout.get("status") == "pass"
        and layout.get("same_binary") is True
        and layout.get("measured_poly_ntt_dispatch_branch") is False,
        "encap_no_regression": cycles["encap_total"]["delta_p90"] < 0
        and cycles["encap_total"]["candidate_win_rate_percent"] == 100.0,
        "decap_no_regression": cycles["decap_total"]["delta_p90"] < 0
        and cycles["decap_total"]["candidate_win_rate_percent"] == 100.0,
        "forward_ntt_stable": all(
            cycles[scope]["delta_p90"] < 0
            and cycles[scope]["candidate_win_rate_percent"] == 100.0
            for scope in PRIMARY_SCOPES[2:]
        ),
    }
    return {
        "checks": checks,
        "same_binary_measurement_gate": "pass" if all(checks.values()) else "fail",
        "external_gates_required": [
            "full poly_ntt differential",
            "ABI sentinel",
            "Slothy self-check and instruction multiset",
            "drop-in KEM correctness",
        ],
    }


def fmt(value: float) -> str:
    return f"{value:.3f}"


def render_markdown(report: dict[str, Any], layout: dict[str, Any]) -> str:
    rows = report["measurements"]
    cpi = report["cpi"]
    gate = report["promotion_gate"]
    lines = [
        "# G1R123+S2 Same-Binary Paired KEM PMU",
        "",
        "Pi 5 Cortex-A76, core 3 pinned, 61 paired samples, 2000 calls per sample.",
        "A is production; B is G1R123+S2. Negative delta means B is faster or uses fewer events.",
        "",
        "## Cycles",
        "",
        "| Scope | A p50 | B p50 | delta p10 | delta p50 | delta p90 | MAD | win rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for scope in PRIMARY_SCOPES:
        row = rows["cycles"][scope]
        lines.append(
            f"| {scope} | {fmt(row['a_p50'])} | {fmt(row['b_p50'])} | "
            f"{fmt(row['delta_p10'])} | {fmt(row['delta_p50'])} | "
            f"{fmt(row['delta_p90'])} | {fmt(row['mad'])} | "
            f"{fmt(row['candidate_win_rate_percent'])}% |"
        )

    lines.extend(
        [
            "",
            "## Instructions And CPI",
            "",
            "| Scope | A instructions | B instructions | delta | A CPI | B CPI |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for scope in PRIMARY_SCOPES:
        row = rows["instructions"][scope]
        cpi_row = cpi[scope]
        lines.append(
            f"| {scope} | {fmt(row['a_p50'])} | {fmt(row['b_p50'])} | "
            f"{fmt(row['delta_p50'])} | {cpi_row['a_cpi']:.6f} | "
            f"{cpi_row['b_cpi']:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Frontend And Backend Diagnostics",
            "",
            "Values are median paired deltas per KEM call.",
            "",
            "| Event | encap delta | encap win rate | decap delta | decap win rate |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for event in DIAGNOSTIC_EVENTS:
        enc = rows[event]["encap_total"]
        dec = rows[event]["decap_total"]
        lines.append(
            f"| {event} | {fmt(enc['delta_p50'])} | "
            f"{fmt(enc['candidate_win_rate_percent'])}% | {fmt(dec['delta_p50'])} | "
            f"{fmt(dec['candidate_win_rate_percent'])}% |"
        )

    symbols = layout["symbols"]
    lines.extend(
        [
            "",
            "## Layout And Gates",
            "",
            f"- Binary text size: {layout['binary_text_size']} bytes.",
            f"- Production poly_ntt: {symbols['poly_ntt']['span_to_next_text_symbol']} bytes, "
            f"address mod32/mod64 = {symbols['poly_ntt']['addr_mod32']}/{symbols['poly_ntt']['addr_mod64']}.",
            f"- Candidate poly_ntt: {symbols['poly_ntt_u01v3_g1_r123_s2']['size']} bytes, "
            f"address mod32/mod64 = {symbols['poly_ntt_u01v3_g1_r123_s2']['addr_mod32']}/"
            f"{symbols['poly_ntt_u01v3_g1_r123_s2']['addr_mod64']}.",
            f"- Paired correctness: {report['correctness']['paired']['mismatches']} mismatches "
            f"across {report['correctness']['paired']['checks']} checks.",
            f"- Same-binary measurement gate: **{gate['same_binary_measurement_gate']}**.",
            "- Keypair is intentionally not measured or claimed: the optimized triple path does not use generic poly_ntt.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pmu", type=Path)
    parser.add_argument("layout", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    report = parse_pmu(args.pmu)
    layout = json.loads(args.layout.read_text())
    report["layout"] = layout
    report["promotion_gate"] = promotion_gate(report, layout)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output_dir / "summary.md").write_text(render_markdown(report, layout))
    print(args.output_dir / "summary.json")
    print(args.output_dir / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
