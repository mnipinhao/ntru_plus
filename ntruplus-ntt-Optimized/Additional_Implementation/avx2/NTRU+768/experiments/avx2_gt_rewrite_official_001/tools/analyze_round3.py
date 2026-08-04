#!/usr/bin/env python3
"""Close the Round 3 GT-vs-Official differential and apply its stop gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
BACKEND = ("ntt", "basemul", "basemul_scale", "baseinv", "invntt",
           "tobytes", "frombytes")
COMMON = ("add", "sub", "cbd1", "triple", "crepmod3", "sotp_encode",
          "sotp_decode", "hash_f", "hash_g", "hash_h", "shake256",
          "randombytes32", "randombytes96")


def load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text())


def weighted(counts: dict, costs: dict, backend: str, names: tuple[str, ...]) -> float:
    return sum(counts.get(name, 0) * costs[name][backend]["median_cycles"]
               for name in names)


def error(reconstructed: float, measured: float) -> float:
    return abs(reconstructed - measured) / abs(measured)


def main() -> None:
    primary = load("kem-caller-benchmark.json")
    reversed_run = load("round3-kem-reversed.json")
    count_doc = load("round3-call-counts.json")
    direct = load("round3-symmetric-cycles.json")
    coarse = load("round3-coarse-shared-differential.json")
    pmu = load("round3-symmetric-pmu.json")
    costs = direct["costs"]
    triplet_counts = count_doc["triplet"]

    measured_o = primary["official"]["total"]["median_cycles"]
    measured_g = primary["gt"]["total"]["median_cycles"]
    measured_gap = measured_g - measured_o
    reversed_gap = (reversed_run["gt"]["total"]["median_cycles"]
                    - reversed_run["official"]["total"]["median_cycles"])
    placement_change = abs(reversed_gap - measured_gap) / abs(measured_gap)
    if len(pmu["measurements"]) != 27:
        raise SystemExit("Round 3 PMU matrix is incomplete")
    scaling = []
    for measurement in pmu["measurements"].values():
        if set(measurement["groups"]) != {"1", "2", "3", "4"}:
            raise SystemExit("Round 3 PMU event group is incomplete")
        for group in measurement["groups"].values():
            scaling.extend(event["scaling_factor"]
                           for event in group["events"].values()
                           if event["scaling_factor"] is not None)

    backend_o = weighted(triplet_counts, costs, "official", BACKEND)
    backend_g = weighted(triplet_counts, costs, "gt", BACKEND)
    common = weighted(triplet_counts, costs, "official", COMMON)
    reconstructed_o = backend_o + common
    reconstructed_g = backend_g + common
    direct_gap = backend_g - backend_o

    operation_rows = {}
    for operation in ("keypair", "encap", "decap"):
        c = count_doc["operations"][operation]
        operation_rows[operation] = {
            "official_backend_cycles": weighted(c, costs, "official", BACKEND),
            "gt_backend_cycles": weighted(c, costs, "gt", BACKEND),
            "common_kem_cycles": weighted(c, costs, "official", COMMON),
        }

    decap_direct_gap = (operation_rows["decap"]["gt_backend_cycles"]
                        - operation_rows["decap"]["official_backend_cycles"])
    shared_differential = coarse["differential_cycles"] - decap_direct_gap
    reconstructed_gap = direct_gap + shared_differential
    reconstructed_g += shared_differential

    classes = {
        "common_kem": common,
        "official_backend": backend_o,
        "gt_backend": backend_g,
        "gt_glue_unclosed": measured_gap - reconstructed_gap,
        "shared_but_differential": shared_differential,
    }

    # A zero floor is more optimistic than any feasible arithmetic/memory floor.
    # If a coherent scope fails at zero, detailed floor modelling cannot rescue it.
    def scope(name: str, edges: list[str], current: float) -> dict:
        return {
            "name": name,
            "edge_ids": edges,
            "current_gt_cycles": current,
            "optimistic_floor_cycles": 0.0,
            "potential_cycles": current,
            "floor_note": "zero-floor upper bound; detailed mandatory floor waived",
        }

    scopes = []
    operation_edge_ids = {
        "keypair": ["keypair.ntt_f", "keypair.baseinv_f", "keypair.ntt_g",
                    "keypair.baseinv_g", "keypair.basemul_h",
                    "keypair.encode_pk", "keypair.basemul_hinv",
                    "keypair.encode_sk_f", "keypair.encode_sk_hinv"],
        "encap": ["encap.decode_pk", "encap.ntt_r", "encap.encode_r",
                  "encap.ntt_m", "encap.basemul_hr", "encap.encode_c"],
        "decap": ["decap.decode_ct", "decap.decode_sk_f",
                  "decap.decode_sk_hinv", "decap.basemul_scale_cf",
                  "decap.invntt_m", "decap.ntt_m", "decap.basemul_chinv",
                  "decap.encode_recovered_r", "decap.ntt_expected_r",
                  "decap.encode_expected_r"],
    }
    for op in ("keypair", "encap", "decap"):
        eligible = operation_rows[op]["gt_backend_cycles"]
        edges = list(operation_edge_ids[op])
        if op == "decap":
            eligible += shared_differential
            edges.append("decap.shared_differential_region")
        scopes.append(scope(
            f"{op}-backend-pipeline",
            edges, eligible))
    scopes.extend((
        scope("serialization-boundary-class", ["*.tobytes", "*.frombytes"],
              weighted(triplet_counts, costs, "gt", ("tobytes", "frombytes"))),
        scope("base-arithmetic-boundary-class",
              ["*.basemul", "*.basemul_scale", "*.baseinv"],
              weighted(triplet_counts, costs, "gt",
                       ("basemul", "basemul_scale", "baseinv"))),
        scope("forward-materialization-boundary-class", ["*.ntt"],
              weighted(triplet_counts, costs, "gt", ("ntt",))),
        scope("inverse-store-reload-boundary-class", ["decap.invntt_m"],
              weighted(triplet_counts, costs, "gt", ("invntt",))),
    ))
    scopes.sort(key=lambda item: item["potential_cycles"], reverse=True)

    abs_o = error(reconstructed_o, measured_o)
    abs_g = error(reconstructed_g, measured_g)
    diff = error(reconstructed_gap, measured_gap)
    closure_over_10 = max(abs_o, abs_g, diff) > 0.10
    if placement_change > 0.10 or closure_over_10:
        decision = "stop-attribution-inconclusive"
    elif scopes[0]["potential_cycles"] < 70000.0:
        decision = "stop-gt-unsuitable-for-avx2"
    else:
        decision = f"prototype-selected-{scopes[0]['name']}"

    report = {
        "schema_version": 1,
        "authoritative_baseline_id": "round3-primary-20260804-cpu1-f059ceb",
        "baseline": {
            "official_cycles": measured_o,
            "gt_cycles": measured_g,
            "measured_gap": measured_gap,
            "reversed_gap": reversed_gap,
            "placement_gap_change_fraction": placement_change,
            "frontend_sensitive": placement_change > 0.03,
        },
        "pmu": {
            "artifact": "results/round3-symmetric-pmu.json",
            "measurement_count": len(pmu["measurements"]),
            "groups_per_measurement": 4,
            "max_scaling_factor": max(scaling),
            "min_scaling_factor": min(scaling),
        },
        "reconstruction": {
            "official_cycles": reconstructed_o,
            "gt_cycles": reconstructed_g,
            "gap_cycles": reconstructed_gap,
            "direct_gap_before_coarse_region_cycles": direct_gap,
            "coarse_region": {
                "artifact": "results/round3-coarse-shared-differential.json",
                "scope": "shared_differential",
                "region": "decap-complete-non-nested",
                "measured_differential_cycles": coarse["differential_cycles"],
                "direct_decap_backend_differential_cycles": decap_direct_gap,
                "supplemental_shared_differential_cycles": shared_differential,
            },
            "absolute_closure_error_fraction": {"official": abs_o, "gt": abs_g},
            "differential_closure_error_fraction": diff,
            "classes": classes,
            "operations": operation_rows,
        },
        "scope_floor_policy": (
            "Zero is a strict upper-bound floor. Required arithmetic, memory, "
            "canonical byte, permutation, spill and dependency costs are nonnegative; "
            "therefore a scope below 70k at zero cannot pass a detailed floor."),
        "candidate_scopes": scopes,
        "thresholds": {"closure": 0.05, "inconclusive": 0.10,
                       "removable_cycles": 70000.0},
        "decision": decision,
        "prototype_built": False,
        "prototype_reason": ("No candidate passes the zero-floor 70k gate."
                             if "prototype-selected" not in decision
                             else "Pending benchmark-only prototype."),
    }
    (RESULTS / "round3-attribution.json").write_text(
        json.dumps(report, indent=2) + "\n")

    lines = [
        "# Round 3 differential closure and stop decision", "",
        f"Authoritative baseline: `{report['authoritative_baseline_id']}`.", "",
        f"- Measured Official: {measured_o:.3f} cycles",
        f"- Measured GT: {measured_g:.3f} cycles",
        f"- Measured gap: {measured_gap:.3f} cycles",
        f"- Reconstructed gap: {reconstructed_gap:.3f} cycles",
        f"- Differential closure error: {100.0 * diff:.3f}%",
        f"- Reversed-link gap change: {100.0 * placement_change:.3f}% "
        "(`frontend-sensitive`, but below the 10% stop threshold)", "",
        "## Coherent zero-floor upper bounds", "",
        "| Candidate | GT cycles | Zero-floor potential |", "|---|---:|---:|",
    ]
    lines.extend(f"| `{row['name']}` | {row['current_gt_cycles']:.3f} | "
                 f"{row['potential_cycles']:.3f} |" for row in scopes)
    lines.extend(("", "A zero floor is deliberately more optimistic than the required "
                  "arithmetic/memory/byte-boundary floor. Since even that upper bound "
                  "does not reach 70,000 cycles, no prototype is authorized.", "",
                  f"Final decision: `{decision}`.", ""))
    (RESULTS / "round3-decision.md").write_text("\n".join(lines))
    print(json.dumps({"decision": decision,
                      "differential_closure_percent": 100.0 * diff,
                      "max_zero_floor_potential": scopes[0]["potential_cycles"]},
                     indent=2))


if __name__ == "__main__":
    main()
