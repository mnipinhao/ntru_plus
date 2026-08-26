#!/usr/bin/env python3
"""Enforce the NTRU+864 GT campaign experiment lifecycle and size budget."""

from __future__ import annotations

import json
from pathlib import Path


ALLOWED_STATUS = {"active", "passed", "rejected", "blocked", "superseded", "promoted"}
REQUIRED_FILES = {
    "README.md",
    "baseline-contract.yml",
    "candidate-contract.yml",
    "iteration.yml",
    "results.md",
    "DECISION.md",
}


def main() -> None:
    campaign = Path(__file__).resolve().parents[1]
    experiments_root = campaign / "experiments"
    registry_path = experiments_root / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    entries = registry["experiments"]
    ids = [entry["id"] for entry in entries]
    assert len(ids) == len(set(ids)), "duplicate experiment id"

    active = [entry["id"] for entry in entries if entry["status"] == "active"]
    assert len(active) <= registry["active_limit"], (
        f"active experiment limit exceeded: {active}"
    )

    checked_files = 0
    for entry in entries:
        assert entry["status"] in ALLOWED_STATUS, entry
        assert entry["production_linked"] is False, entry
        directory = experiments_root / entry["path"]
        assert directory.is_dir(), f"missing experiment directory: {directory}"
        present = {path.name for path in directory.iterdir() if path.is_file()}
        missing = REQUIRED_FILES - present
        assert not missing, f"{entry['id']} missing {sorted(missing)}"

        files = [
            path for path in directory.rglob("*")
            if path.is_file()
            and "build" not in path.relative_to(directory).parts
            and "__pycache__" not in path.relative_to(directory).parts
        ]
        budget = entry.get("artifact_budget_waiver", registry["default_artifact_budget"])
        assert len(files) <= budget, (
            f"{entry['id']} has {len(files)} artifacts; budget is {budget}"
        )
        checked_files += len(files)

    production_root = campaign.parents[2] / "NTRU+864"
    stock_makefile = campaign.parents[2] / "stock.mk"
    forbidden_tokens = ["good_thomas_campaign", *ids]
    production_files = [path for path in production_root.rglob("*") if path.is_file()]
    production_files.append(stock_makefile)
    for source in production_files:
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden_tokens:
            assert token not in text, f"Production reference {token!r} in {source}"

    print("experiment_registry_gate=pass")
    print(f"registered_experiments={len(entries)}")
    print(f"active_experiments={len(active)}")
    print(f"active_ids={','.join(active)}")
    print(f"checked_experiment_files={checked_files}")
    print("production_campaign_references=0")


if __name__ == "__main__":
    main()
