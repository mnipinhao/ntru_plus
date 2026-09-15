#!/usr/bin/env python3
"""Schedule four terminal shapes, then instantiate all 96 public-offset blocks."""
import re
from pathlib import Path

import optimize

HERE = Path(__file__).resolve().parent
SHAPES = {"both": 0, "none": 1, "high": 2, "low": 12}


def block(text, t, g=0):
    start = f"p32_terminal_{t}_g{g}_start:"
    end = f"p32_terminal_{t}_g{g}_end:"
    head, rest = text.split(start, 1)
    body, tail = rest.split(end, 1)
    return start + body + end


def offsets(t, g):
    component, half = divmod(g, 2)
    base = 2 * component + 24 * half + 54 * t
    result = {"input": 256 * g + 16 * t}
    result["low"] = [base + 6 * lane for lane in range(4)]
    result["high"] = [base + 864 + 6 * lane for lane in range(4)]
    return result


def instantiate(template, source_t, target_t, target_g):
    out = template.replace(
        f"p32_terminal_{source_t}_g0_start", f"p32_terminal_{target_t}_g{target_g}_start"
    ).replace(
        f"p32_terminal_{source_t}_g0_end", f"p32_terminal_{target_t}_g{target_g}_end"
    )
    old, new = offsets(source_t, 0), offsets(target_t, target_g)
    out = out.replace(f"[x1, #{old['input']}]", f"[x1, #{new['input']}]")
    replacements = dict(zip(old["low"], new["low"]))
    replacements.update(zip(old["high"], new["high"]))
    for before, after in sorted(replacements.items(), reverse=True):
        out = out.replace(f"[x0, #{before}]", f"[x0, #{after}]")
    return out


source = HERE / "candidate-terminal.sym.S"
templates = {}
for name, t in SHAPES.items():
    output = HERE / f"terminal-template-{name}.S"
    optimize.run(source, output,
                 f"p32_terminal_{t}_g0_start", f"p32_terminal_{t}_g0_end",
                 f"template-{name}", timing=True,
                 reserved=optimize.ALL_GPRS + [f"v{i}" for i in range(26, 32)], timeout=60)
    templates[name] = block(output.read_text(), t)

text = source.read_text()
for t in range(16):
    shape = "both" if t == 0 else "low" if t == 12 else "high" if t in {2, 8, 10} else "none"
    for g in range(6):
        old = block(text, t, g)
        text = text.replace(old, instantiate(templates[shape], SHAPES[shape], t, g))
(HERE / "candidate-terminal.timing.S").write_text(text)
print({"templates": SHAPES, "instantiated_blocks": 96})
