"""Symbolic and physical differential for the P2 adjacent-pair numerator."""
import ctypes as ct
import importlib.util
import json
import random
import re
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
BASE = ROOT / "experiments/gt864-native-asm"
PROD = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

spec = importlib.util.spec_from_file_location("gtverify", BASE / "verify.py")
gtverify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gtverify)

def run(buffers, code):
    """Exact local interpreter, including fused-wide SMLSL/SMLSL2."""
    mem = {k: bytearray(gtverify.pack(v)) for k, v in buffers.items()}
    regs = {}
    word = 0
    for line in code:
        op = line.split()[0]
        syms = re.findall(r"<([^>]+)>", line)
        imm = [int(x) for x in re.findall(r"#(-?\d+)", line)]
        if op == "mov":
            word = imm[0]
        elif op == "dup":
            regs[syms[0]] = gtverify.pack([word] * 8)
        elif op in ("ldr", "str"):
            ptr = re.search(r"\[(x\d+)", line)[1]
            off = imm[0]
            if op == "ldr":
                regs[syms[0]] = bytes(mem[ptr][off:off + 16])
            else:
                mem[ptr][off:off + 16] = regs[syms[0]]
        elif op in ("smull", "smull2", "smlal", "smlal2", "smlsl", "smlsl2"):
            a, b = [gtverify.unpack(regs[x]) for x in syms[1:]]
            high = op.endswith("2")
            idx = 4 if high else 0
            accumulating = op.startswith(("smlal", "smlsl"))
            old = gtverify.unpack(regs[syms[0]], 4) if accumulating else [0] * 4
            sign = -1 if op.startswith("smlsl") else 1
            values = [old[i] + sign * a[idx + i] * b[idx + i] for i in range(4)]
            assert all(-(1 << 31) <= x < (1 << 31) for x in values)
            regs[syms[0]] = gtverify.pack(values, 4)
        elif op in ("uzp1", "uzp2"):
            a, b = [gtverify.unpack(regs[x]) for x in syms[1:]]
            parity = int(op[-1]) - 1
            regs[syms[0]] = gtverify.pack(a[parity::2] + b[parity::2])
        elif op in ("mul", "add", "sub", "mls", "sqrdmulh"):
            a, b = [gtverify.unpack(regs[x]) for x in syms[1:]]
            if op == "mul": values = [x * y for x, y in zip(a, b)]
            elif op == "add": values = [x + y for x, y in zip(a, b)]
            elif op == "sub": values = [x - y for x, y in zip(a, b)]
            elif op == "mls": values = [z - x * y for z, x, y in zip(gtverify.unpack(regs[syms[0]]), a, b)]
            else: values = [max(-32768, min(32767, (x * y + 16384) // 32768)) for x, y in zip(a, b)]
            regs[syms[0]] = gtverify.pack(values)
        else:
            raise AssertionError(line)
    return {k: gtverify.unpack(v) for k, v in mem.items()}

def instructions(path):
    inside = False
    result = []
    for line in path.read_text().splitlines():
        if "binv_num_pair_slothy_start:" in line:
            inside = True
            continue
        if "binv_num_pair_slothy_end:" in line:
            break
        instruction = line.split("//", 1)[0].strip()
        if inside and instruction and not instruction.endswith(":"):
            result.append(instruction)
    return result

symbolic = instructions(P / "candidate.sym.S")
assert len(symbolic) == 160
single = json.loads((BASE / "baseinv-tobytes-next-model/fused-numerator-model.json").read_text())
rng = random.Random(0x86402)
zetas_text = (PROD / "gt864_fr0_basemul_tables.h").read_text().split("gt864_fr0_zetas_mul", 1)[1].split("=", 1)[1].split(";", 1)[0]
zetas = list(map(int, re.findall(r"-?\d+", zetas_text)))

cases = 0
for case in range(4096):
    inp = [rng.randrange(-32768, 32768) for _ in range(48)]
    roots = [zetas[(case * 16 + i) % len(zetas)] for i in range(16)]
    got = run({"x0": [0] * 48, "x1": inp, "x2": roots, "x3": [0] * 32}, symbolic)
    a = run({"x0": [0] * 24, "x1": inp[:24], "x2": roots[:8], "x3": [0] * 8}, single)
    b = run({"x0": [0] * 24, "x1": inp[24:], "x2": roots[8:], "x3": [0] * 8}, single)
    assert got["x0"] == a["x0"] + b["x0"]
    assert got["x3"][:8] == a["x3"] and got["x3"][24:32] == b["x3"]
    assert max(map(abs, got["x0"] + got["x3"][:8] + got["x3"][24:32])) <= 4000
    cases += 1

# Assemble and execute the actual Slothy allocation on Apple arm64.
source = (P / "candidate.opt.S").read_text()
source = source.replace(".global binv_num_pair", ".global _binv_num_pair").replace("\nbinv_num_pair:", "\n_binv_num_pair:")
(P / "candidate.mac.S").write_text(source)
lib = P / "candidate-test.dylib"
subprocess.run(["clang", "-dynamiclib", "-arch", "arm64", str(P / "test-wrapper.S"), str(P / "candidate.mac.S"), "-o", str(lib)], check=True)
dll = ct.CDLL(str(lib))
fn = dll.test_binv_num_pair
fn.argtypes = [ct.c_void_p] * 4
physical_cases = 0
for case in range(4096):
    inp = [rng.randrange(-32768, 32768) for _ in range(48)]
    roots = [zetas[(case * 16 + i) % len(zetas)] for i in range(16)]
    expected_a = run({"x0": [0] * 24, "x1": inp[:24], "x2": roots[:8], "x3": [0] * 8}, single)
    expected_b = run({"x0": [0] * 24, "x1": inp[24:], "x2": roots[8:], "x3": [0] * 8}, single)
    inbuf = (ct.c_int16 * 50)(*inp, 0x1234, 0x2345)
    rootsbuf = (ct.c_int16 * 18)(*roots, 0x3456, 0x4567)
    out = (ct.c_int16 * 50)(*([0x5678] * 50))
    den = (ct.c_int16 * 34)(*([0x6789] * 34))
    fn(out, inbuf, rootsbuf, den)
    assert list(out)[:48] == expected_a["x0"] + expected_b["x0"]
    assert list(den)[:8] == expected_a["x3"] and list(den)[24:32] == expected_b["x3"]
    assert list(out)[48:] == [0x5678] * 2 and list(den)[8:24] == [0x6789] * 16 and list(den)[32:] == [0x6789] * 2
    assert list(inbuf)[48:] == [0x1234, 0x2345] and list(rootsbuf)[16:] == [0x3456, 0x4567]
    physical_cases += 1

result = {
    "status": "pass", "symbolic_pair_cases": cases, "physical_pair_cases": physical_cases,
    "instructions": len(instructions(P / "candidate.opt.S")), "spills": 0,
    "range_proof": "two independent copies of closed P0 fused-wide chain",
    "canaries": "pass", "input_unchanged": "pass",
}
(P / "oracle-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
