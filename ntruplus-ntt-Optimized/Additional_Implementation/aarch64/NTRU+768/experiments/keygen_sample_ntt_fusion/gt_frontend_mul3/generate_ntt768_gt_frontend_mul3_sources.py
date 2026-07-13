#!/usr/bin/env python3
"""Generate SAMPLE-DAG GT frontend mul3 symbolic sources from the flat source.

The transformation is intentionally mechanical:
  - after every input load from x1, scale the loaded vector by 3 using two adds;
  - for the add1 variant, add e0 to v4 in iter0 after its scale-by-3.

The add1 source loads an experiment-only e0 mask from x7 instead of using
`ins v?.h[0], w?`, because the Slothy AArch64 parser used by this project does
not support half-lane scalar insertion.

The production scheduled include is not used as input.  This keeps Slothy in
control of scheduling the new DAG.
"""

from __future__ import annotations

from pathlib import Path
import argparse


HIGH_LOADS = {
    "ldp q10, q11, [x1, #768]": ["v10", "v11"],
    "ldr q12, [x1, #1024]": ["v12"],
    "ldr q13, [x1, #1040]": ["v13"],
    "ldr q14, [x1, #1280]": ["v14"],
    "ldr q15, [x1, #1296]": ["v15"],
}

LOW_LOADS = {
    "ldp q4, q5, [x1, #0]": ["v4", "v5"],
    "ldp q6, q7, [x1, #256]": ["v6", "v7"],
    "ldp q8, q9, [x1, #512]": ["v8", "v9"],
}


def scale_lines(reg: str, tmp: str, side: str) -> list[str]:
    return [
        f"    add {tmp}.8h, {reg}.8h, {reg}.8h    // SAMPLE-DAG: {side} input *= 2\n",
        f"    add {reg}.8h, {tmp}.8h, {reg}.8h    // SAMPLE-DAG: {side} input *= 3\n",
    ]


def generate(base: Path, out: Path, add1: bool) -> None:
    lines = base.read_text().splitlines(keepends=True)
    output: list[str] = []
    current_iter = None
    add1_done = False

    header = [
        "// Generated SAMPLE-DAG GT frontend symbolic source.\n",
        f"// add1_variant={1 if add1 else 0}\n",
        "// Base: asm/slothy/inputs/ntt768_gt_frontend.sym.S\n",
        "// Do not edit generated file directly; edit generate_ntt768_gt_frontend_mul3_sources.py.\n",
    ]
    output.extend(header)

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("slothy_start_ntt768_gt_frontend_iter"):
            current_iter = stripped.removesuffix(":")
        output.append(line)
        if stripped.startswith("slothy_start_ntt768_gt_frontend_iter"):
            output.extend(
                [
                    "    // live-in: x1 input pointer, x3 twist pointer, x4/x5/x6 row scratch pointers, v0 constants\n",
                    "    // live-out: x1/x3/x4/x5/x6 advanced, row0/row1/row2 scratch stores\n",
                    "    // range: cbd1 small coefficients scaled by 3, then production GT frontend reductions and DFT3 bounds\n",
                    "    // reserved physical registers: x8-x30, sp, v0; v1-v31 are fixed physical vectors for repo Slothy style\n",
                ]
            )

        for needle, regs in HIGH_LOADS.items():
            if needle in stripped:
                for reg in regs:
                    output.extend(scale_lines(reg, "v16", "high"))

        for needle, regs in LOW_LOADS.items():
            if needle in stripped:
                for reg in regs:
                    output.extend(scale_lines(reg, "v1", "low"))
                    if add1 and not add1_done and current_iter == "slothy_start_ntt768_gt_frontend_iter0" and reg == "v4":
                        output.extend(
                            [
                                "    ldr q1, [x7]                      // SAMPLE-DAG: e0 mask [1,0,...,0]\n",
                                "    add v4.8h, v4.8h, v1.8h\n",
                            ]
                        )
                        add1_done = True

    if add1 and not add1_done:
        raise RuntimeError("failed to inject add1 e0 into iter0 low-side v4")
    out.write_text("".join(output))


def main() -> None:
    scheme_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="asm/slothy/inputs/ntt768_gt_frontend.sym.S")
    parser.add_argument("--out-dir", default="experiments/keygen_sample_ntt_fusion/gt_frontend_mul3")
    args = parser.parse_args()

    base = Path(args.base)
    if not base.is_absolute():
        base = scheme_root / base
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = scheme_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    generate(base, out_dir / "ntt768_gt_frontend_mul3.sym.S", add1=False)
    generate(base, out_dir / "ntt768_gt_frontend_mul3_add1.sym.S", add1=True)


if __name__ == "__main__":
    main()
