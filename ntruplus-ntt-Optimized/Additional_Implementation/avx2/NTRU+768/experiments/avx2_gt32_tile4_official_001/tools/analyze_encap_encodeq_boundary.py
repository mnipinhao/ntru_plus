#!/usr/bin/env python3
"""Close the current Encap private-SoA Encodeq bridge accounting."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    encap = json.loads(
        (ROOT / "results/tile4-encap-mixed-general-short.json").read_text()
    )
    attribution = json.loads(
        (ROOT / "results/tile4-basemul-attribution-short.json").read_text()
    )
    transpose = float(attribution["derived"]["output_materialization_TO_tsc"])
    runs = encap["corroboration"]
    arithmetic_savings = {
        name: float(run["paired_saving_tsc"]) for name, run in runs.items()
    }
    control_net = {
        name: saving - transpose for name, saving in arithmetic_savings.items()
    }
    result = {
        "schema": "ntruplus768-encap-encodeq-boundary-v1",
        "spec_edge": "NTT(r)->Encodeq(rhat)->G before basemul(hhat,rhat)",
        "baseline": "N5 AoS rhat -> AoS Encodeq",
        "candidate_control": (
            "N5 private-SoA rhat -> SoA-to-AoS transpose -> identical AoS Encodeq"
        ),
        "correctness_basis": (
            "existing private-SoA-to-AoS forward differential is exact; the "
            "subsequent Encodeq and G suffix is therefore byte-identical"
        ),
        "arithmetic_side_saving_tsc": arithmetic_savings,
        "soa_to_aos_control_penalty_tsc": transpose,
        "net_saving_after_encodeq_control_tsc": control_net,
        "control_wins_end_to_end": all(value > 0.0 for value in control_net.values()),
        "direct_private_soa_encodeq": {
            "implemented": False,
            "maximum_extra_cost_for_directional_parity_tsc": min(
                arithmetic_savings.values()
            ),
            "required_properties": [
                "Official byte-exact Encodeq output",
                "non-destructive rhat retained for mixed BM",
                "fixed public control flow and addresses",
                "no intermediate AoS materialization",
            ],
            "existing_network_warning": (
                "the analogous natural direct-SoA decoder network costs 1056 "
                "instructions versus its 480-instruction AoS control; this is "
                "not a proof for the reverse encoder but rejects assuming symmetry is free"
            ),
        },
        "decision": "stop-AoS-bridge-path; direct-private-SoA-Encodeq-unproven",
        "serious_benchmark_run": False,
        "production_integration": False,
    }
    output = ROOT / "results/tile4-encap-encodeq-boundary.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
