#!/usr/bin/env python3
"""Bind P7-C0's exact inverse model to the current production tree.

The tables were renamed when the tree was tidied; the layouts are unchanged:
  gt864_inverse9_twist_barrett       -> invntt9_constants        [2][2][9][2][8]
  gt864_inverse16_stage_barrett      -> invntt16_constants       [4][16]
  gt864_inverse16_main_scale_barrett -> invntt16_main_scale      [16][2][8]
  gt864_inverse16_tail_scale_barrett -> invntt16_tail_scale      [16][2][8]
"""
import importlib.util, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
P7   = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"
RENAME = {
    "gt864_inverse9_twist_barrett":       ("inverse_tables.h",   "invntt9_constants"),
    "gt864_inverse16_stage_barrett":      ("inverse_tables.h",   "invntt16_constants"),
    "gt864_inverse16_main_scale_barrett": ("inverse_tables.h",   "invntt16_main_scale"),
    "gt864_inverse16_tail_scale_barrett": ("inverse_tables.h",   "invntt16_tail_scale"),
}

def load():
    src = P7.read_text()
    shim = '''
def table(name, file=None):
    import re as _re
    _f, _n = _RENAME[name]
    _t = (PROD / _f).read_text().split(_n, 1)[1].split("=", 1)[1].split(";", 1)[0]
    return list(map(int, _re.findall(r"-?\\\\d+", _t)))
'''
    src = re.sub(r"def table\(name, file='[^']*'\):\n(?:    .*\n)+", shim.lstrip()+"\n", src, count=1)
    src = src.replace("ROOT = Path(__file__).resolve().parents[3]",
                      f"ROOT = Path({str(ROOT)!r})")
    src = src.replace("if __name__ ==", "if False and __name__ ==")
    mod_src = f"_RENAME = {RENAME!r}\n" + src
    spec = importlib.util.spec_from_loader("p62_p7", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__dict__["__file__"] = str(P7)
    sys.modules["p62_p7"] = mod
    exec(compile(mod_src, str(P7), "exec"), mod.__dict__)
    return mod

if __name__ == "__main__":
    m = load()
    print(f"  model loaded; Q={m.Q} R={m.R}")
    print(f"  TWIST {len(m.TWIST)}  STAGE {len(m.STAGE)}  SCALE {len(m.SCALE)}  TAIL {len(m.TAIL)}")
    print(f"  pair(0,0,0) = {m.pair(0,0,0)}   pair(0,0,1) = {m.pair(0,0,1)}")
    print(f"  API: {[n for n in ('i9','intt16','chain','numeric_i9','numeric_inverse','physical_i9','physical_i16','root_proof') if hasattr(m,n)]}")
