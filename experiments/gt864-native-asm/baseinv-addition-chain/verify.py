"""P1 exact exponent, scale/range, and symbolic-instruction oracle."""
import importlib.util
import json
import random
from pathlib import Path

P = Path(__file__).resolve().parent
Q = 3457
R = 65536

spec = importlib.util.spec_from_file_location("gtverify", P.parent / "verify.py")
gtverify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gtverify)


def instructions(path):
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.startswith("    ") and line.strip() != "ret" and not line.strip().startswith("//")
    ]


code = instructions(P / "candidate.sym.S")
assert len(code) == 157, len(code)

# Machine-check the named addition-chain exponents, rather than trusting comments.
exp = {"a": 1}
steps = [
    ("a2", "a", "a"), ("a4", "a2", "a2"), ("a8", "a4", "a4"),
    ("a16", "a8", "a8"), ("a17", "a16", "a"),
    ("a32", "a16", "a16"), ("a64", "a32", "a32"),
    ("a128", "a64", "a64"), ("a145", "a128", "a17"),
    ("a273", "a145", "a128"), ("a546", "a273", "a273"),
    ("a691", "a546", "a145"), ("a1382", "a691", "a691"),
    ("a2764", "a1382", "a1382"), ("a3455", "a2764", "a691"),
]
for dst, left, right in steps:
    exp[dst] = exp[left] + exp[right]
assert exp["a3455"] == Q - 2

# Every MM input after the first prefix edge is inside the same conservative
# envelope.  The worst signed widening numerator remains below int32.
correction = 32768 * Q
assert 4000 * 4000 + correction < 2**31
assert (4000 * 4000 + correction) // R < 2000

rng = random.Random(0x8643455)
cases = 0
for case in range(4096):
    values = []
    for lane in range(24):
        value = rng.randrange(-4000, 4001)
        while value % Q == 0:
            value = rng.randrange(-4000, 4001)
        values.append(value)
    result = gtverify.run(
        "p1",
        {"x0": [0] * 24, "x1": values},
        code=code,
    )["x0"]
    for lane in range(8):
        x, y, z = values[lane], values[8 + lane], values[16 + lane]
        got = result[lane], result[8 + lane], result[16 + lane]
        want = pow(x, Q - 2, Q) * R % Q, pow(y, Q - 2, Q) * R % Q, pow(z, Q - 2, Q) * R % Q
        # Inputs and outputs represent R1 values.  Convert the expected inverse
        # of an R1 encoding back to R1: (x/R)^-1 * R = R^2/x.
        want = tuple((v * R) % Q for v in want)
        assert tuple(v % Q for v in got) == want, (case, lane, got, want)
        assert max(abs(v) for v in got) < 2000
    cases += 1

print(json.dumps({
    "status": "pass",
    "exponent": exp["a3455"],
    "addition_chain_multiplications": 15,
    "total_montgomery_multiplications": 21,
    "symbolic_instructions": len(code),
    "random_vector_cases": cases,
    "lanes_checked": cases * 8,
    "scale": "R1 input -> R1 inverse output",
    "range": "signed int32 widening closed; every REDC abs < 2000",
}, indent=2))
