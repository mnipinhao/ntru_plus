#!/usr/bin/env python3
import json
import random
import statistics
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
rows = []
for placement in ("normal", "reversed"):
    for launch in range(16):
        p = subprocess.run([str(EXP / f"build/bench-{placement}"), str(launch & 1)], capture_output=True, text=True, check=True)
        row = json.loads(p.stdout.strip().splitlines()[-1])
        row.update(placement=placement, launch=launch)
        rows.append(row)

def summarize(values, seed):
    rng = random.Random(seed)
    boots = sorted(statistics.median(rng.choices(values, k=len(values))) for _ in range(20000))
    return {
        "natural_em1_minus_e0_median": statistics.median(values),
        "ci95": [boots[499], boots[19499]],
        "natural_em1_faster_launches": sum(v < 0 for v in values),
        "launches": len(values),
    }

result = {
    "protocol": "SUPERcop-libcpucycles CPU1 ASLR-on 16 fresh launches alternating paired order, Normal/Reversed",
    "placements": {
        placement: summarize([r["em1_minus_e0"] for r in rows if r["placement"] == placement], 136 + i)
        for i, placement in enumerate(("normal", "reversed"))
    },
}
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/launches.json").write_text(json.dumps(rows, indent=2) + "\n")
(EXP / "results/scale-finalizer-ceiling.json").write_text(json.dumps(result, indent=2) + "\n")
survey_path = EXP / "generated/reopen-survey.json"
survey = json.loads(survey_path.read_text())
credits = {p: -v["natural_em1_minus_e0_median"] for p, v in result["placements"].items()}
survey["scale_absorption"]["measured_free_absorption_ceiling_cycles"] = credits
survey["scale_absorption"]["fraction_of_218_repayment"] = {p: v / 218.12 for p, v in credits.items()}
survey["scale_absorption"]["result"] = "INSUFFICIENT_AS_STANDALONE_REOPEN"
survey["scale_absorption"]["reason"] = (
    "even granting a zero-cost downstream absorption, deleting the complete "
    "e=-1 to e=0 finalizer recovers only this measured credit; a real mixed-scale "
    "Q24 path must cost more than zero"
)
survey_path.write_text(json.dumps(survey, indent=2) + "\n")
print(json.dumps(result, indent=2))
