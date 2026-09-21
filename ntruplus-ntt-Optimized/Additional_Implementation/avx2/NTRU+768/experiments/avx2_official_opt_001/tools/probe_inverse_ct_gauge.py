#!/usr/bin/env python3
"""Map a twisted CT realization of Official's five radix-2 inverse layers.

At each butterfly, `actual = gauge * stored (mod q)`.  The Official GS map
`(a+b, z(a-b))` is represented by CT `(A+tB, A-tB)` with
`t = gauge_b/gauge_a`; the output gauges are `(gauge_a,z*gauge_a)`.
This is a modular identity, not a signed-i16 range proof or an ASM schedule.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSTS = ROOT / "upstream/supercop-avx2/consts.c"
ASM = ROOT / "upstream/supercop-avx2/invntt.s"
Q = 3457
R = 65536 % Q
RINV = pow(R, -1, Q)


def zetas_inv():
    match = re.search(r"const int16_t zetas_inv\[816\].*?=\s*\{(.*?)\};",
                      CONSTS.read_text(), re.S)
    if not match:
        raise ValueError("missing pinned inverse twiddle table")
    result = [int(x) % Q for x in re.findall(r"-?\d+", match[1])]
    if len(result) != 816:
        raise ValueError("inverse table length changed")
    return result


def route(stage, a, b):
    width = {6: 1, 5: 2, 4: 4, 3: 8}[stage]
    if width == 8:
        return a[:8] + b[:8], a[8:] + b[8:]
    first, second = [], []
    for half in (0, 8):
        for start in range(half, half + 8, 2 * width):
            first += a[start:start + width] + b[start:start + width]
            second += a[start + width:start + 2 * width]
            second += b[start + width:start + 2 * width]
    return first, second


def compute():
    zetas = zetas_inv()
    gauges = [[1] * 16 for _ in range(48)]
    stages = []
    for stage in (6, 5, 4, 3, 2):
        new = [[0] * 16 for _ in range(48)]
        twiddles = []
        for packet in range(6):
            base = packet * 8
            z_index = ({6: 16, 5: 208, 4: 400, 3: 592}[stage] + packet * 32
                       if stage != 2 else 770 + packet * 4)
            stored = zetas[z_index:z_index + 16] if stage != 2 else [zetas[z_index]] * 16
            # Official table words are Montgomery-encoded constants.
            zvec = [(word * RINV) % Q for word in stored]
            upper, lower = [], []
            for pair in range(4):
                ga, gb = gauges[base + pair], gauges[base + pair + 4]
                t = [(b * pow(a, -1, Q)) % Q for a, b in zip(ga, gb)]
                upper.append(ga[:])
                lower.append([(z * a) % Q for z, a in zip(zvec, ga)])
                twiddles.append(t)
                # Coefficient identities prove both outputs for arbitrary a,b.
                for aa, bb, tt in zip(ga, gb, t):
                    assert aa * tt % Q == bb
            if stage == 2:
                new[base:base + 8] = upper + lower
            else:
                inputs = upper + lower
                for pair in range(4):
                    lo, hi = route(stage, inputs[2 * pair], inputs[2 * pair + 1])
                    new[base + pair] = lo
                    new[base + pair + 4] = hi
        identity = sum(all(x == 1 for x in vec) for vec in twiddles)
        stages.append({"stage": stage, "butterfly_vectors": len(twiddles),
                       "identity_twiddle_vectors": identity,
                       "nonidentity_twiddle_vectors": len(twiddles) - identity,
                       "distinct_twiddle_vectors": len(set(map(tuple, twiddles))),
                       "twiddles": twiddles,
                       "twiddles_montgomery": [[(x * R) % Q for x in v] for v in twiddles],
                       "output_gauges": new})
        gauges = new
    result = {"kind": "modular_CT_inverse_radix2_gauge_map_only",
              "source_invntt_sha256": hashlib.sha256(ASM.read_bytes()).hexdigest(),
              "source_consts_sha256": hashlib.sha256(CONSTS.read_bytes()).hexdigest(),
              "q": Q, "stages": stages,
              "pre_radix3_nonidentity_gauge_vectors":
                  sum(not all(x == 1 for x in vec) for vec in gauges),
              "pre_radix3_distinct_gauge_vectors": len(set(map(tuple, gauges)))}
    return result


def main():
    result = compute()
    output = ROOT / "results/officialopt-inverse-ct-gauge-20260921.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"stages": [{k: v for k, v in s.items()
                                  if k not in ("twiddles", "output_gauges")}
                                  for s in result["stages"]],
                      "pre_radix3_nonidentity_gauge_vectors":
                          result["pre_radix3_nonidentity_gauge_vectors"],
                      "pre_radix3_distinct_gauge_vectors":
                          result["pre_radix3_distinct_gauge_vectors"]}, indent=2))


if __name__ == "__main__":
    main()
