#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from analyze_supercop_matrix import decode_measurement, stabilized_quartiles


PAIRS = {
    "local_c5": ("c5_control_cycles", "c5_candidate_cycles"),
    "decap": ("dec_control_cycles", "dec_candidate_cycles"),
    "encap_control": ("enc_control_cycles", "enc_candidate_cycles"),
    "keypair_control": ("keypair_control_cycles", "keypair_cycles"),
}


def q2(path: Path, label: str) -> float:
    values: list[int] = []
    for line in (path / "data").read_text().splitlines():
        if f" {label} " in line:
            values.extend(decode_measurement(line))
    return stabilized_quartiles(values)[1]


def main() -> None:
    manifest = Path(sys.argv[1])
    output = Path(sys.argv[2])
    paths = [Path(line) for line in manifest.read_text().splitlines() if line]
    launches = []
    for path in paths:
        operations = {}
        for name, (control_label, candidate_label) in PAIRS.items():
            control = q2(path, control_label)
            candidate = q2(path, candidate_label)
            operations[name] = {"control_q2_cycles": control,
                                "candidate_q2_cycles": candidate,
                                "candidate_minus_control": candidate-control}
        launches.append({"result_dir": str(path), "operations": operations})
    summary = {}
    for name in PAIRS:
        deltas = [item["operations"][name]["candidate_minus_control"]
                  for item in launches]
        summary[name] = {"launches": len(deltas),
                         "median_delta_cycles": statistics.median(deltas),
                         "favorable_launches": sum(value < 0 for value in deltas),
                         "deltas_cycles": deltas}
    result = {"schema": "ntruplus768-native-rcheck-same-elf-supercop-v1",
              "cycle_backend": "default-perfevent",
              "statistics_unit": "fresh-process launch stabilized Q2",
              "launches": launches, "summary": summary}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
