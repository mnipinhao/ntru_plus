#!/usr/bin/env python3
"""Generate P35 KEM-only main/tail symbolic helpers from reviewed P13 DAG."""
import contextlib
import importlib.util
import io
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
source = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/generate.py"
spec = importlib.util.spec_from_file_location("p13gen", source)
g = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(g)

g.RESET_LOW = set()
g.RESET_HIGH = {8}
main = g.kernel("inverse16_lazy", "p35_i16", False)
main = main.replace("output abs<=4454", "P8-consumer output abs<=5143")

g.RESET_LOW = set()
g.RESET_HIGH = set()
tail = g.kernel("inverse_tail_lazy", "p35_itail", True)
tail = tail.replace("output abs<=4454", "P8-consumer output abs<=5028")
tail = tail.replace("    mov w8, #9\n    dup V<nine>.8h, w8\n", "")

(HERE / "candidate-main.sym.S").write_text(main)
(HERE / "candidate-tail.sym.S").write_text(tail)
count = lambda text: sum(line.startswith("    ") for line in text.splitlines()) - 1
assert count(main) == 657
assert count(tail) == 589
print({"main": count(main), "tail": count(tail), "decaps_delta": 6*(657-667)+(589-603)})
