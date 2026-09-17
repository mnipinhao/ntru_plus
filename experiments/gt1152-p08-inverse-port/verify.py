"""Differential gate for the NTRU+1152 fused inverse-to-ternary path.

The whole decapsulation arithmetic chain is checked end to end:

    forward -> basemul_rinv -> invntt_ternary  ==  crepmod3(schoolbook product)

in Z_q[x]/(x^1152 - x^576 + 1).  This exercises G3b's forward, G5's R^-1
boundary, the two remapped Slothy kernels and the C tail together, against a
model that shares no code with any of them.

Correctness only; this host is not Cortex-A76.
"""
import json, random, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
Q, N = 3457, 1152

def schoolbook(a, b):
    c = [0] * (2 * N)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                c[i + j] += ai * bj
    for i in range(2 * N - 1, N - 1, -1):
        if c[i]:
            c[i - N // 2] += c[i]; c[i - N] -= c[i]; c[i] = 0
    return [x % Q for x in c[:N]]

def crep3(x):
    x %= Q
    if x > (Q - 1) // 2:
        x -= Q
    r = x % 3
    return r - 3 if r == 2 else r

def run(a, b):
    o = subprocess.run([str(HERE / "harness"), ",".join(map(str, a + b))],
                       capture_output=True, text=True, check=True).stdout
    return [int(x) for x in o.strip().split(",")]

random.seed(20260917)
cases = [("zero", [0] * N, [0] * N),
         ("ones", [1] * N, [1] * N),
         ("neg", [-1] * N, [1] * N)]
for i in (0, 1, 575, 576, 1151):
    d = [0] * N; d[i] = 1
    cases.append((f"delta@{i}", d, [random.randint(-1, 1) for _ in range(N)]))
for k in range(8):
    cases.append((f"ternary{k}",
                  [random.randint(-1, 1) for _ in range(N)],
                  [random.randint(-1, 1) for _ in range(N)]))

failures = []
for name, a, b in cases:
    got = run(a, b)
    want = [crep3(x) for x in schoolbook(a, b)]
    bad = sum(1 for i in range(N) if got[i] != want[i])
    if bad:
        failures.append({"case": name, "mismatches": bad})
    print(f"  {name:12s} {'ok' if not bad else f'FAIL ({bad})'}", flush=True)
    if any(v not in (-1, 0, 1) for v in got):
        failures.append({"case": name, "error": "output not ternary"})

report = {"cases": len(cases), "coefficients_per_case": N,
          "chain": "forward -> basemul_rinv -> invntt_ternary",
          "model": "crepmod3(schoolbook in Z_q[x]/(x^1152-x^576+1))",
          "failures": failures, "pass": not failures}
(HERE / "verify-report.json").write_text(json.dumps(report, indent=2) + "\n")
if failures:
    print(f"\nFAIL: {failures[:3]}", file=sys.stderr); raise SystemExit(1)
print(f"\nPASS: {len(cases)} cases x {N} coefficients -> verify-report.json")
