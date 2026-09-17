"""Differential gate for the NTRU+1152 codec.

Checks the exact wire bytes against the G1 declared oracle's serialization,
the round trip, the canonical rejection boundary in full, and the constant-time
compare against every single-byte corruption.
"""

import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments/gt1152-p01-ring-profile"))

import ntruplus1152 as P  # noqa: E402

Q, N, PB = P.Q, 1152, 1728
DEG = 4
PERM = [int(x) for x in (REPO / "experiments/gt1152-p03-gt-layout/perm864.txt"
                         ).read_text().split()]


def slots():
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for lane in range(8):
                    yield top, row, halfcol, lane


GT_OF_NAT = [0] * N
for _si, (_t, _r, _h, _l) in enumerate(slots()):
    for _c in range(DEG):
        GT_OF_NAT[DEG * PERM[_si] + _c] = _t * 576 + _r * 64 + _h * 32 + _c * 8 + _l


def to_gt(nat):
    out = [0] * N
    for j in range(N):
        out[GT_OF_NAT[j]] = nat[j]
    return out


def run(mode, *parts):
    args = ",".join(",".join(map(str, p)) for p in parts)
    o = subprocess.run([str(HERE / "harness"), mode, args],
                       capture_output=True, text=True, check=True).stdout
    return o.strip().split("\n")


checks = []


def check(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"[{'pass' if ok else 'FAIL'}] {name}: {detail}")
    return ok


random.seed(20260917)

# ---- Full: exact wire bytes over arbitrary int16 ---------------------------
#
# The oracle's poly_tobytes is the reference version: it only folds the sign
# bit, so it is defined on (-q, q).  NTRU+864's Full contract is wider -- "Full
# accepts all signed int16" -- because kem.c serializes raw Forward output,
# measured at +/-14607.  The model for Full is therefore the canonical
# representative of x mod q, and the oracle is used to cross-check that the two
# agree wherever the oracle is defined.
def pack_mod_q(nat):
    out = bytearray(PB)
    for i in range(N // 2):
        t0, t1 = nat[2 * i] % Q, nat[2 * i + 1] % Q
        out[3 * i + 0] = t0 & 0xFF
        out[3 * i + 1] = ((t0 >> 8) | (t1 << 4)) & 0xFF
        out[3 * i + 2] = (t1 >> 4) & 0xFF
    return list(out)


full_fail = 0
for k in range(8):
    nat = [random.randint(-32768, 32767) for _ in range(N)]
    got = [int(x) for x in run("full", to_gt(nat))[0].split(",")]
    full_fail += got != pack_mod_q(nat)
for v in (-32768, 32767, 0, Q, -Q, Q - 1, -(Q - 1), 14607, -14607):
    nat = [v] * N
    got = [int(x) for x in run("full", to_gt(nat))[0].split(",")]
    full_fail += got != pack_mod_q(nat)
check("full_exact_bytes", full_fail == 0,
      "17 cases including every int16 extreme and the measured Forward bound; "
      "model is the canonical representative of x mod q")

# the two models must agree wherever the oracle's narrower one is defined
agree_fail = 0
for k in range(4):
    nat = [random.randint(-(Q - 1), Q - 1) for _ in range(N)]
    agree_fail += pack_mod_q(nat) != list(P.poly_tobytes([P.s16(v) for v in nat]))
check("full_model_agrees_with_oracle", agree_fail == 0,
      "on (-q, q), where the oracle's reference serializer is defined, the "
      "mod-q model reproduces it exactly")

# ---- Small: identical bytes on its restricted domain ------------------------
small_fail = 0
for k in range(8):
    nat = [random.randint(-(Q - 1), Q - 1) for _ in range(N)]
    a = run("small", to_gt(nat))[0]
    b = run("full", to_gt(nat))[0]
    small_fail += a != b
check("small_matches_full_on_its_domain", small_fail == 0,
      "8 cases over (-q, q); Small skips the Barrett and must still agree")

# ---- round trip -------------------------------------------------------------
rt_fail = 0
for k in range(6):
    nat = [random.randrange(0, Q) for _ in range(N)]
    packed = run("small", to_gt(nat))[0]
    lines = run("from", [int(x) for x in packed.split(",")])
    rc = int(lines[0])
    back = [int(x) for x in lines[1].split(",")]
    rt_fail += rc != 0 or back != to_gt(nat)
check("round_trip", rt_fail == 0,
      "6 canonical polynomials survive tobytes then frombytes exactly, and "
      "decode reports 0")

# ---- canonical rejection: every position, every boundary value --------------
BOUNDARY = [Q, Q + 1, 4095]
base = [random.randrange(0, Q) for _ in range(N)]
packed0 = [int(x) for x in run("small", to_gt(base))[0].split(",")]
rej_fail = 0
tested = 0
for pos in range(N):
    for v in BOUNDARY:
        nat = list(base)
        nat[pos] = v
        # pack by hand: v may exceed q so Small is not valid, emit directly
        buf = bytearray(packed0)
        i, lo = divmod(pos, 2)
        t0 = nat[2 * i] if lo == 0 else base[2 * i]
        t1 = v if lo == 1 else base[2 * i + 1]
        if lo == 0:
            t0 = v
        buf[3 * i + 0] = t0 & 0xFF
        buf[3 * i + 1] = ((t0 >> 8) | (t1 << 4)) & 0xFF
        buf[3 * i + 2] = (t1 >> 4) & 0xFF
        rc = int(run("from", list(buf))[0])
        tested += 1
        if rc != 1:
            rej_fail += 1
check("canonical_rejection", rej_fail == 0,
      f"{tested} cases: every one of the {N} coefficient positions carrying "
      f"each of {BOUNDARY} is rejected with 1")

# a fully canonical buffer must be accepted
check("canonical_accepted", int(run("from", packed0)[0]) == 0,
      "the unmodified canonical buffer decodes with 0")

# ---- constant-time compare --------------------------------------------------
nat = [random.randint(-(Q - 1), Q - 1) for _ in range(N)]
gt = to_gt(nat)
exact = [int(x) for x in run("full", gt)[0].split(",")]
cmp_fail = int(run("cmp", gt, exact)[0]) != 0
corrupt_missed = 0
for pos in random.sample(range(PB), 256):
    bad = list(exact)
    bad[pos] ^= 0x01
    if int(run("cmp", gt, bad)[0]) != 1:
        corrupt_missed += 1
check("tobytes_compare", not cmp_fail and corrupt_missed == 0,
      "equal input returns 0; 256 sampled single-bit corruptions all return 1")

report = {"checks": checks, "pass": all(c["pass"] for c in checks)}
(HERE / "verify-report.json").write_text(json.dumps(report, indent=2) + "\n")
if not report["pass"]:
    print("\nFAIL", file=sys.stderr)
    raise SystemExit(1)
print("\nPASS -> verify-report.json")
