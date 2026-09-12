#!/usr/bin/env python3
"""Generate the P13-C tail symbolic kernel from the reviewed P13-B algebra."""
import contextlib
import importlib.util
import io
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P13B = ROOT / "experiments/gt864-p13b-inverse16-arithmetic"
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

spec = importlib.util.spec_from_file_location("p13b_generate", P13B / "generate.py")
g = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(g)

# P13-B deliberately generated both tables, but promoted only the main kernel.
# Bind P13-C to the exact already-manifested tail constants.
text = (PROD / "gt864_p13b_composite_tables.h").read_text()
tail = text.split("gt864_p13b_tail", 1)[1].split("=", 1)[1].split(";", 1)[0]
production_tail = list(map(int, re.findall(r"-?\d+", tail)))
assert production_tail == g.TAIL_NEW

source = g.kernel("inverse_tail_lazy", "p13c_itail", True)
source = source.replace("output abs<=4454", "output abs<=4303")
(HERE / "candidate.sym.S").write_text(source)
print({"instructions": sum(x.startswith("    ") for x in source.splitlines()) - 1,
       "table_entries_checked": len(production_tail),
       "table": "production gt864_p13b_tail"})
