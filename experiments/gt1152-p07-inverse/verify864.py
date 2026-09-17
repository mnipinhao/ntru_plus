"""Validate the NTRU+864 decapsulation arithmetic chain on this host.

forward -> basemul_rinv -> invntt_ternary must equal crepmod3 of the schoolbook
product in Z_q[x]/(x^864 - x^432 + 1).  This establishes the reference the 1152
port is checked against, and confirms the chain's I/O contract before anything
is remapped.
"""
import json, random, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
Q, N = 3457, 864

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

random.seed(5)
cases = [([random.randint(-1, 1) for _ in range(N)],
          [random.randint(-1, 1) for _ in range(N)]) for _ in range(6)]
fails = 0
for i, (a, b) in enumerate(cases):
    out = subprocess.run([str(HERE / "probe864"), ",".join(map(str, a + b))],
                         capture_output=True, text=True, check=True).stdout
    got = [int(x) for x in out.strip().split(",")]
    want = [crep3(x) for x in schoolbook(a, b)]
    ok = got == want
    fails += not ok
    print(f"  case {i}: {'ok' if ok else 'FAIL'}")
report = {"cases": len(cases), "failures": fails, "pass": fails == 0}
(HERE / "verify864-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"\n{'PASS' if not fails else 'FAIL'}: NTRU+864 chain equals "
      f"crepmod3(schoolbook) -> verify864-report.json")
raise SystemExit(0 if not fails else 1)
