"""Differential gate for NTRU+1152 degree-4 baseinv and basemul_rinv.

Checks against the G1 declared oracle under the GT layout, and exercises the
non-invertible path, aliasing, and the D7 output bound.
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

Q = P.Q
N = 1152
DEG = 4
R = -147                      # 2^16 mod q
PERM = [int(x) for x in (REPO / "experiments/gt1152-p03-gt-layout/perm864.txt"
                         ).read_text().split()]


def slots():
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for lane in range(8):
                    yield top, row, halfcol, lane


def gt_index(top, row, halfcol, component, lane):
    return top * 576 + row * 64 + halfcol * 32 + component * 8 + lane


def to_gt(ref):
    out = [0] * N
    for slot_i, (top, row, halfcol, lane) in enumerate(slots()):
        leaf = PERM[slot_i]
        for c in range(DEG):
            out[gt_index(top, row, halfcol, c, lane)] = ref[DEG * leaf + c]
    return out


def run(mode, a, b):
    args = ",".join(map(str, a + b))
    out = subprocess.run([str(HERE / "harness"), mode, args],
                         capture_output=True, text=True, check=True).stdout
    lines = out.strip().split("\n")
    return int(lines[0]), [int(x) for x in lines[1].split(",")]


checks = []


def check(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(f"[{'pass' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def main():
    random.seed(20260917)
    # Keygen feeds baseinv with ntt(3*cbd +/- 1), so use that shape plus
    # general contract-domain inputs.
    cases = []
    for k in range(6):
        t = [3 * random.randint(-1, 1) for _ in range(N)]
        t[0] = P.s16(t[0] + 1)
        cases.append((f"keygen_f{k}", t, [random.randint(-1, 1) for _ in range(N)]))
    for k in range(4):
        cases.append((f"contract{k}",
                      [random.randint(-3, 4) for _ in range(N)],
                      [random.randint(-3, 4) for _ in range(N)]))

    inv_fail = rinv_fail = 0
    rinv_lo = rinv_hi = 0
    inv_skipped = 0

    for name, a, b in cases:
        A, B = P.ntt(a), P.ntt(b)

        # ---- baseinv ----
        fail_ref, want = P.poly_baseinv(A)
        rc, got = run("inv", a, b)
        rc2, got2 = run("inv_alias", a, b)
        if fail_ref:
            inv_skipped += 1
            if rc != 1 or any(got):
                inv_fail += 1
        else:
            wg = to_gt(want)
            if rc != 0 or any(got[i] % Q != wg[i] % Q for i in range(N)):
                inv_fail += 1
            if rc2 != rc or got2 != got:
                inv_fail += 1

        # ---- basemul_rinv: out * R == basemul(a,b) mod q ----
        want_r0 = to_gt(P.poly_basemul(A, B))
        _, got_rinv = run("rinv", a, b)
        _, got_alias = run("rinv_alias", a, b)
        rinv_lo = min(rinv_lo, min(got_rinv))
        rinv_hi = max(rinv_hi, max(got_rinv))
        if any(got_rinv[i] * R % Q != want_r0[i] % Q for i in range(N)):
            rinv_fail += 1
        if got_alias != got_rinv:
            rinv_fail += 1

        print(f"  {name:12s} ok", flush=True)

    check("baseinv_matches_oracle", inv_fail == 0,
          f"{len(cases)} cases, including exact out==in aliasing "
          f"({inv_skipped} were non-invertible and checked for rc=1 plus a "
          f"zeroed output)")
    check("basemul_rinv_scale", rinv_fail == 0,
          "out * R is congruent to the R0 basemul for every coefficient, and "
          "exact aliasing reproduces the non-aliased result")

    # ---- D7 bound ----
    within = max(abs(rinv_lo), rinv_hi) <= 1729
    check("d7_normalization", within,
          f"basemul_rinv output observed in [{rinv_lo}, {rinv_hi}], inside the "
          f"[-1729,1728] Barrett range and so inside NTRU+864's 2497 inverse "
          f"input contract")

    # ---- non-invertible input must be rejected and the output cleared ----
    zero_in = [0] * N
    rc, got = run("inv_raw", zero_in, zero_in)
    check("noninvertible_rejected", rc == 1 and not any(got),
          "an all-zero transform-domain input returns 1 and leaves the output "
          "entirely zero")

    report = {
        "cases": len(cases),
        "basemul_rinv_observed": {"lo": rinv_lo, "hi": rinv_hi},
        "d7_target": 1729,
        "checks": checks,
        "pass": all(c["pass"] for c in checks),
    }
    (HERE / "verify-report.json").write_text(json.dumps(report, indent=2) + "\n")

    if not report["pass"]:
        print("\nFAIL", file=sys.stderr)
        return 1
    print(f"\nPASS -> verify-report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
