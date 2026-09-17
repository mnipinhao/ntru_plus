import sys
from pathlib import Path
sys.path.insert(0, "/Users/chenpinhao/slothy")
from slothy.targets.aarch64 import aarch64_neon as A
from slothy.helper import SourceLine

src = Path(sys.argv[1]).read_text().splitlines()
inside = False
bad = []
for i, raw in enumerate(src, 1):
    t = raw.split("//")[0].strip()
    if t.endswith("_slothy_start:"): inside = True; continue
    if t.endswith("_slothy_end:"): inside = False; continue
    if not t or t.endswith(":") or t.startswith("."): continue
    try:
        A.Instruction.parser(SourceLine(t))
    except Exception as e:
        bad.append((i, t, type(e).__name__))
print(f"lines in region checked; unparseable: {len(bad)}")
for i, t, e in bad[:12]:
    print(f"  line {i}: {t}    [{e}]")
