"""Timing-only schedule of the already allocated pair+merge kernels."""

import hashlib
import json
import logging
import pathlib
import re
import sys

from slothy.core.heuristics import Heuristics
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

from tbl3_a76_model import MEASURED, install


P = pathlib.Path(__file__).resolve().parent
assert pathlib.Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy")
install(timing=True)

for mode in sys.argv[1:] or ["small", "full"]:
    work = P / ("bytes-" + mode)
    kernel = "pair_merge_" + mode
    logger = logging.getLogger("schedule-" + mode)
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(work / "slothy-timing.log", mode="w"))

    source = (work / "candidate.alloc.S").read_text()
    body = [
        line.strip()
        for line in source.splitlines()
        if line.startswith("    ") and line.strip() != "ret" and not line.strip().startswith("//")
    ]
    allocation = json.loads((work / "allocation.json").read_text())
    lengths = [region["instructions"] for region in allocation["regions"]]
    assert sum(lengths) == len(body)
    scheduled = []
    regions = []
    offset = 0
    for region, length in zip(allocation["regions"], lengths):
        part = body[offset : offset + length]
        offset += length
        held = set(region["held"])
        vector_outputs = sorted(
            {physical for symbolic, physical in region["live_out_mapping"].items() if symbolic not in held}
        )
        # Fixed physical allocation; optimize instruction order only.  The
        # allocation gate's natural frontend/row boundaries define live-outs.
        from slothy import Config

        region_logger = logger.getChild(f"region{region['block']}")
        config = Config(Arch, Target, region_logger)
        config.selftest = False
        # Keep all region live-ins available at the boundary.  With physical
        # registers fixed this is conservative and avoids inventing typed
        # virtual-output names for architectural registers.
        config.inputs_are_outputs = True
        config.outputs = vector_outputs
        config.constraints.allow_spills = False
        config.constraints.functional_only = False
        config.constraints.allow_reordering = True
        config.constraints.allow_renaming = False
        config.variable_size = True
        config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
        config.timeout = 30
        result = Heuristics.linear(
            SourceLine.read_multiline("\n".join(part)),
            region_logger,
            config,
        )
        assert result.success
        scheduled.extend(line.text for line in result.code_raw)
        regions.append(
            {
                "block": region["block"],
                "instructions": length,
                "vector_outputs": vector_outputs,
                "cycles": result.cycles,
            }
        )

    output = []
    in_region = False
    inserted = False
    for line in source.splitlines():
        if line.strip() == kernel + "_slothy_start:":
            output.append(line)
            output.extend("    " + instruction.strip() for instruction in scheduled)
            in_region = True
            inserted = True
            continue
        if line.strip() == kernel + "_slothy_end:":
            in_region = False
            output.append(line)
            continue
        if not in_region:
            output.append(line)
    assert inserted
    (work / "candidate.opt.S").write_text("\n".join(output) + "\n")

    report = {
        "mode": mode,
        "source": "candidate.alloc.S",
        "output": "candidate.opt.S",
        "allow_spills": False,
        "allow_renaming": False,
        "schedule_boundaries": "existing frontend plus nine row allocation regions",
        "regions": regions,
        "target_evidence": MEASURED,
        "source_sha256": hashlib.sha256((work / "candidate.alloc.S").read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256((work / "candidate.opt.S").read_bytes()).hexdigest(),
    }
    (work / "timing.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)
