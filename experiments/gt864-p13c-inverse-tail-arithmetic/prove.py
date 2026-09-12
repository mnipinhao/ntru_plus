#!/usr/bin/env python3
"""Exact tail-only modular map and conservative interval closure for P13-C."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
audit_path = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"
spec = importlib.util.spec_from_file_location("p7audit", audit_path)
a = importlib.util.module_from_spec(spec)
sys.modules["p7audit"] = a
spec.loader.exec_module(a)

Q = a.Q
C = (-1634) % Q
D = (-722) % Q
RESET_LOW = {0, 12}
RESET_HIGH = {0, 2, 8, 10}

def cen(x):
    x %= Q
    return x - Q if x > Q // 2 else x

def coeff(sa, sb):
    return tuple(map(cen, ((1 + D*C)*sa, -D*C*sb, -C*sa, C*sb)))

_, rows = a.chain(True)
states = []
for top in range(2):
    model = a.Model()
    values = [a.V(rows[top, column][8].lo, rows[top, column][8].hi, (0,))
              for column in range(16)]
    states.append(a.intt16(model, values))

contexts = []
worst_before = 0
worst_after = 0
for column, (xa, xb) in enumerate(zip(*states)):
    sa = a.TAIL[column*16] % Q
    sb = a.TAIL[column*16 + 3] % Q
    # The same constants repeat over all three degree-3 components.
    assert a.TAIL[column*16:column*16+3] == [a.TAIL[column*16]] * 3
    assert a.TAIL[column*16+3:column*16+6] == [a.TAIL[column*16+3]] * 3
    assert a.TAIL[column*16+6:column*16+8] == [0, 0]
    la, lb, ha, hb = coeff(sa, sb)
    li = a.image(xa.lo, xa.hi, la, a.magic(la))
    lj = a.image(xb.lo, xb.hi, lb, a.magic(lb))
    hi = a.image(xa.lo, xa.hi, ha, a.magic(ha))
    hj = a.image(xb.lo, xb.hi, hb, a.magic(hb))
    low = (li[0] + lj[0], li[1] + lj[1])
    high = (hi[0] + hj[0], hi[1] + hj[1])
    before = max(map(abs, low + high))
    worst_before = max(worst_before, before)
    if column in RESET_LOW:
        low = a.image(low[0], low[1], 1, 9)
    if column in RESET_HIGH:
        high = a.image(high[0], high[1], 1, 9)
    after = max(map(abs, low + high))
    worst_after = max(worst_after, after)
    contexts.append({"row": 8, "column": column, "components": 3,
                     "A": [xa.lo, xa.hi], "B": [xb.lo, xb.hi],
                     "coefficients": [la, lb, ha, hb], "before": before,
                     "low": list(low), "high": list(high), "after": after})

assert worst_before == 5028
assert worst_after == 4303
assert worst_after <= 4577
for x in range(-worst_after, worst_after + 1):
    k = (x > 1728) - (x < -1728)
    z = x - k
    t = (10923*z + 16384) // 32768
    y = z - 3*t
    assert y in (-1, 0, 1)
    assert y % 3 == (((x + 1728) % Q - 1728) % 3)

result = {
    "status": "proof-pass", "tail_row": 8, "contexts": len(contexts),
    "component_copies_per_context": 3, "modulus": Q,
    "layout": "top0 components0..2 | top1 components0..2 | zero x2",
    "scale": "unchanged I9 R^-1 to natural R0", "i16_bound": 21397,
    "pre_reset_bound": worst_before, "post_reset_bound": worst_after,
    "baseline_contract_bound": 4577,
    "reset_low_columns": sorted(RESET_LOW),
    "reset_high_columns": sorted(RESET_HIGH),
    "general_mulmods_per_column_before": 3,
    "general_mulmods_per_column_after": 2,
    "static_instruction_delta": -66,
    "p8_inputs_exhausted": 2*worst_after + 1,
    "memory_boundary_delta": 0, "details": contexts,
}
(HERE / "proof.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "details"}, indent=2))
