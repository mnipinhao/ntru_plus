#!/usr/bin/env python3
"""P34 exact consumer-domain and terminal-reset selection audit."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"
P7 = ROOT / "experiments/gt864-native-asm/inverse-p7c0-range/audit.py"

spec = importlib.util.spec_from_file_location("p7audit", P7)
a = importlib.util.module_from_spec(spec)
sys.modules["p7audit"] = a
assert spec.loader is not None
spec.loader.exec_module(a)

Q = a.Q
C = (-1634) % Q
D = (-722) % Q
OLD_LOW = {0, 12}
OLD_HIGH = {0, 2, 8, 10}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def center(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def coeff(sa: int, sb: int) -> tuple[int, int, int, int]:
    return tuple(map(center, ((1 + D*C)*sa, -D*C*sb, -C*sa, C*sb)))


def raw_ternary(x: int) -> int:
    # Exact scalar interpretation used by the already-validated P8 proof.
    wrap = (x > Q // 2) - (x < -(Q // 2))
    z = x - wrap
    quotient = (10923*z + 16384) // 32768
    return z - 3*quotient


def raw_ok(x: int) -> bool:
    y = raw_ternary(x)
    return y in (-1, 0, 1) and y % 3 == center(x) % 3


def accepted_symmetric_radius() -> int:
    radius = 0
    for value in range(0, 32768):
        if not raw_ok(value) or not raw_ok(-value):
            break
        radius = value
    return radius


def terminal_bounds(row: int, tail: bool) -> dict[int, dict[str, int]]:
    _, rows = a.chain(True)
    states = []
    for top in range(2):
        model = a.Model()
        values = [a.V(rows[top, column][row].lo,
                      rows[top, column][row].hi, (0,))
                  for column in range(16)]
        states.append(a.intt16(model, values))

    table = a.TAIL if tail else a.SCALE
    lane = 3 if tail else 4
    result = {}
    for column, (xa, xb) in enumerate(zip(*states)):
        sa = table[column*16] % Q
        sb = table[column*16 + lane] % Q
        la, lb, ha, hb = coeff(sa, sb)
        li = a.image(xa.lo, xa.hi, la, a.magic(la))
        lj = a.image(xb.lo, xb.hi, lb, a.magic(lb))
        hi = a.image(xa.lo, xa.hi, ha, a.magic(ha))
        hj = a.image(xb.lo, xb.hi, hb, a.magic(hb))
        low = max(abs(li[0] + lj[0]), abs(li[1] + lj[1]))
        high = max(abs(hi[0] + hj[0]), abs(hi[1] + hj[1]))
        result[column] = {"low": low, "high": high}
    return result


radius = accepted_symmetric_radius()
assert radius == Q + Q // 2 == 5185
assert raw_ok(radius) and raw_ok(-radius)
assert not raw_ok(radius + 1) and not raw_ok(-(radius + 1))

main_by_row = [terminal_bounds(row, False) for row in range(8)]
tail = terminal_bounds(8, True)
main = {
    column: {
        side: max(main_by_row[row][column][side] for row in range(8))
        for side in ("low", "high")
    }
    for column in range(16)
}

required_main_low = sorted(c for c in OLD_LOW if main[c]["low"] > radius)
required_main_high = sorted(c for c in OLD_HIGH if main[c]["high"] > radius)
required_tail_low = sorted(c for c in OLD_LOW if tail[c]["low"] > radius)
required_tail_high = sorted(c for c in OLD_HIGH if tail[c]["high"] > radius)
assert required_main_low == []
assert required_main_high == [8]
assert required_tail_low == []
assert required_tail_high == []

# After retaining main high-column 8, every other producer interval goes
# directly to P8.  The retained reset is strictly below q by Algorithm 10.
selected_main_bound = max(
    bound
    for column, sides in main.items()
    for side, bound in sides.items()
    if not (column == 8 and side == "high")
)
selected_tail_bound = max(v for sides in tail.values() for v in sides.values())
retained_main_high_8 = max(map(abs, a.image(
    -main[8]["high"], main[8]["high"], 1, 9)))
assert selected_main_bound == 5143 <= radius
assert selected_tail_bound == 5028 <= radius
assert retained_main_high_8 == 1821

deleted_main_chains = len(OLD_LOW) + len(OLD_HIGH) - 1
deleted_tail_chains = len(OLD_LOW) + len(OLD_HIGH)
result = {
    "status": "select-p35",
    "production_revision": __import__("subprocess").check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": {
        name: sha256(PROD / name)
        for name in (
            "gt864_native_public.S",
            "gt864_native_inverse16_lazy.S",
            "gt864_native_inverse_tail_lazy.S",
            "gt864_crepmod3_raw.S",
            "gt864_p13b_composite_tables.h",
        )
    },
    "consumer": {
        "symmetric_accepted_radius": radius,
        "accepted_endpoints": [-radius, radius],
        "first_rejected_witnesses": [-(radius + 1), radius + 1],
        "reason": "one conditional q-wrap encoded modulo 3; q=3457 is congruent to 1 modulo 3",
    },
    "main_pre_reset_bounds": main,
    "tail_pre_reset_bounds": tail,
    "selected_resets": {
        "main_low": required_main_low,
        "main_high": required_main_high,
        "tail_low": required_tail_low,
        "tail_high": required_tail_high,
    },
    "selected_output_bounds": {
        "main_unreset": selected_main_bound,
        "main_high_column_8_after_reset": retained_main_high_8,
        "tail": selected_tail_bound,
    },
    "static_delta": {
        "deleted_main_reset_chains_per_call": deleted_main_chains,
        "main_calls": 6,
        "deleted_tail_reset_chains": deleted_tail_chains,
        "instructions_per_chain": 2,
        "deleted_instructions_per_decaps":
            2 * (6 * deleted_main_chains + deleted_tail_chains),
        "added_loads": 0,
        "added_stores": 0,
        "added_routes": 0,
        "added_scratch_bytes": 0,
    },
    "decision": {
        "selected": "P35 KEM-only terminal-reset pruning",
        "general_centered_inverse": "retain current reset-complete helpers",
        "why_not_remove_main_high_8": "bound 5278 exceeds exact P8 radius 5185; witnesses at +/-5186 fail",
        "why_not_materialize": "P32/P33 measured lower IPC from the added preterminal boundary",
    },
}
assert result["static_delta"]["deleted_instructions_per_decaps"] == 72
(HERE / "audit-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
