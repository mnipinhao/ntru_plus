#!/usr/bin/env python3
"""Differential oracle for the Phase123 U01 symbolic prototype.

The oracle interprets the small AArch64 Neon subset used by:

  - asm/slothy/inputs/my_ntt_phase123_flat.sym.s
  - experiments/forward_ntt_phase123_u01/phase123_u01.sym.s

It compares production Phase123 iteration slots0+1 against the matching U01
type A/B/C producer.  This is a source-level oracle; it does not claim anything
about Slothy scheduling or final performance.
"""

from __future__ import annotations

import argparse
import random
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE123 = ROOT / "asm/slothy/inputs/my_ntt_phase123_flat.sym.s"
U01 = ROOT / "experiments/forward_ntt_phase123_u01/phase123_u01.sym.s"
NTT_BODY = ROOT / "asm/gt/ntt_gt_body.inc"


def u16(x: int) -> int:
    return x & 0xFFFF


def s16(x: int) -> int:
    x &= 0xFFFF
    return x - 0x10000 if x & 0x8000 else x


def vec(values: list[int]) -> list[int]:
    if len(values) != 8:
        raise ValueError(f"expected 8 lanes, got {len(values)}")
    return [s16(v) for v in values]


def add_vec(a: list[int], b: list[int]) -> list[int]:
    return [s16(x + y) for x, y in zip(a, b)]


def sub_vec(a: list[int], b: list[int]) -> list[int]:
    return [s16(x - y) for x, y in zip(a, b)]


def mul_vec(a: list[int], b: list[int]) -> list[int]:
    return [s16(x * y) for x, y in zip(a, b)]


def sqrdmulh_lane(a: int, b: int) -> int:
    # Signed saturating rounding doubling high multiply for 16-bit lanes.
    if a == -32768 and b == -32768:
        return 32767
    product = 2 * a * b
    return s16((product + (1 << 15)) >> 16)


def sqrdmulh_vec(a: list[int], b: list[int]) -> list[int]:
    return [sqrdmulh_lane(x, y) for x, y in zip(a, b)]


def zip_d(which: int, a: list[int], b: list[int]) -> list[int]:
    if which == 1:
        return a[:4] + b[:4]
    if which == 2:
        return a[4:] + b[4:]
    raise ValueError(which)


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].strip()


def extract_region(path: Path, start: str, end: str) -> list[str]:
    lines = path.read_text().splitlines()
    inside = False
    out: list[str] = []
    for line in lines:
        if line.strip() == f"{start}:":
            inside = True
            continue
        if line.strip() == f"{end}:":
            return out
        if inside:
            line = strip_comment(line)
            if line:
                out.append(line)
    raise ValueError(f"region {start}..{end} not found in {path}")


def parse_hwords(path: Path) -> tuple[list[int], list[int]]:
    zetas: list[int] = []
    twist: list[int] = []
    section: str | None = None
    for raw in path.read_text().splitlines():
        line = strip_comment(raw)
        if not line:
            continue
        if line == "zetas:":
            section = "zetas"
            continue
        if line == "twist_table:":
            section = "twist"
            continue
        if line.endswith(":") and not line.startswith("."):
            section = None
            continue
        if ".hword" not in line or section is None:
            continue
        nums = [s16(int(x, 0)) for x in re.findall(r"0x[0-9a-fA-F]+|-?\d+", line)]
        if section == "zetas":
            zetas.extend(nums)
        elif section == "twist":
            twist.extend(nums)
    if len(zetas) < 8:
        raise ValueError("failed to parse zetas")
    if len(twist) < 1536:
        raise ValueError(f"twist table too short: {len(twist)} hwords")
    return zetas[:8], twist


class NeonInterp:
    def __init__(
        self,
        input_mem: list[int],
        twist_mem: list[int],
        zetas: list[int],
        extra_mems: dict[str, list[int]] | None = None,
    ):
        self.v: dict[int, list[int]] = {0: vec(zetas)}
        self.ptr = {
            "x1": 0,
            "x3": 0,
            "x4": 0,
            "x5": 0,
            "x6": 0,
            "x7": 0,
            "x12": 0,
            "x13": 0,
        }
        self.input_mem = input_mem
        self.mems = {
            "x1": input_mem,
            "x3": twist_mem,
            "x7": twist_mem,
        }
        if extra_mems:
            self.mems.update(extra_mems)
        self.rows = {"x4": {}, "x5": {}, "x6": {}}

    def set_iteration(self, iteration: int) -> None:
        self.ptr["x1"] = iteration * 32
        self.ptr["x3"] = iteration * 384
        self.ptr["x4"] = iteration * 64
        self.ptr["x5"] = iteration * 64
        self.ptr["x6"] = iteration * 64

    def load_q(self, base: str, offset: int) -> list[int]:
        absolute = self.ptr[base] + offset
        idx = absolute // 2
        mem = self.mems[base]
        return vec(mem[idx : idx + 8])

    def store_q(self, base: str, offset: int, value: list[int]) -> None:
        absolute = self.ptr[base] + offset
        value = vec(value)
        if base in self.mems:
            idx = absolute // 2
            mem = self.mems[base]
            if len(mem) < idx + 8:
                mem.extend([0] * (idx + 8 - len(mem)))
            mem[idx : idx + 8] = value
        self.rows.setdefault(base, {})[absolute] = value

    def operand_vec(self, operand: str) -> list[int]:
        m = re.fullmatch(r"v(\d+)\.8h", operand)
        if m:
            return self.v[int(m.group(1))]
        m = re.fullmatch(r"v(\d+)\.h\[(\d+)\]", operand)
        if m:
            r = int(m.group(1))
            lane = int(m.group(2))
            return [self.v[r][lane]] * 8
        raise ValueError(f"unsupported operand {operand}")

    def run(self, lines: list[str]) -> None:
        for line in lines:
            self.step(line)

    def step(self, line: str) -> None:
        line = re.sub(r"\s+", " ", line.strip()).lower()
        if line.endswith(":") or line.startswith("."):
            return

        m = re.fullmatch(r"ldr q(\d+), \[(x\d+), #(-?\d+)\]", line)
        if m:
            dst, base, off = int(m.group(1)), m.group(2), int(m.group(3))
            self.v[dst] = self.load_q(base, off)
            return

        m = re.fullmatch(r"ldp q(\d+), q(\d+), \[(x\d+), #(-?\d+)\]", line)
        if m:
            d0, d1, base, off = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))
            self.v[d0] = self.load_q(base, off)
            self.v[d1] = self.load_q(base, off + 16)
            return

        m = re.fullmatch(r"ldp q(\d+), q(\d+), \[(x\d+)\], #(\d+)", line)
        if m:
            d0, d1, base, inc = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))
            self.v[d0] = self.load_q(base, 0)
            self.v[d1] = self.load_q(base, 16)
            self.ptr[base] += inc
            return

        m = re.fullmatch(r"str q(\d+), \[(x\d+), #(-?\d+)\]", line)
        if m:
            src, base, off = int(m.group(1)), m.group(2), int(m.group(3))
            self.store_q(base, off, self.v[src])
            return

        m = re.fullmatch(r"add (v\d+\.8h), (v\d+\.8h), (v\d+\.8h)", line)
        if m:
            dst = int(m.group(1)[1:].split(".")[0])
            self.v[dst] = add_vec(self.operand_vec(m.group(2)), self.operand_vec(m.group(3)))
            return

        m = re.fullmatch(r"sub (v\d+\.8h), (v\d+\.8h), (v\d+\.8h)", line)
        if m:
            dst = int(m.group(1)[1:].split(".")[0])
            self.v[dst] = sub_vec(self.operand_vec(m.group(2)), self.operand_vec(m.group(3)))
            return

        m = re.fullmatch(r"mul (v\d+\.8h), (v\d+\.8h), (v\d+\.(?:8h|h\[\d+\]))", line)
        if m:
            dst = int(m.group(1)[1:].split(".")[0])
            self.v[dst] = mul_vec(self.operand_vec(m.group(2)), self.operand_vec(m.group(3)))
            return

        m = re.fullmatch(r"sqrdmulh (v\d+\.8h), (v\d+\.8h), (v\d+\.(?:8h|h\[\d+\]))", line)
        if m:
            dst = int(m.group(1)[1:].split(".")[0])
            self.v[dst] = sqrdmulh_vec(self.operand_vec(m.group(2)), self.operand_vec(m.group(3)))
            return

        m = re.fullmatch(r"mls (v\d+\.8h), (v\d+\.8h), (v\d+\.h\[\d+\])", line)
        if m:
            dst = int(m.group(1)[1:].split(".")[0])
            cur = self.operand_vec(m.group(1))
            prod = mul_vec(self.operand_vec(m.group(2)), self.operand_vec(m.group(3)))
            self.v[dst] = sub_vec(cur, prod)
            return

        m = re.fullmatch(r"zip([12]) (v\d+)\.2d, (v\d+)\.2d, (v\d+)\.2d", line)
        if m:
            which = int(m.group(1))
            dst = int(m.group(2)[1:])
            a = self.v[int(m.group(3)[1:])]
            b = self.v[int(m.group(4)[1:])]
            self.v[dst] = zip_d(which, a, b)
            return

        m = re.fullmatch(r"add (x\d+), (x\d+), #(\d+)", line)
        if m:
            dst, src, imm = m.group(1), m.group(2), int(m.group(3))
            self.ptr[dst] = self.ptr[src] + imm
            return

        raise ValueError(f"unsupported instruction: {line}")


def make_input(seed: int) -> list[int]:
    rnd = random.Random(seed)
    tagged = [s16((i * 257 + seed * 17) ^ (i << 3)) for i in range(768)]
    random_part = [rnd.randrange(-32768, 32768) for _ in range(768)]
    # Mix deterministic tags and random signed values to catch lane swaps and
    # arithmetic differences without depending on symmetric inputs.
    return [s16(tagged[i] + random_part[i]) for i in range(768)]


def compare_one(seed: int, zetas: list[int], twist: list[int]) -> list[str]:
    errors: list[str] = []
    input_mem = make_input(seed)
    type_for_iter = {0: "a", 1: "b", 2: "c", 3: "a", 4: "b", 5: "c", 6: "a", 7: "b"}

    for iteration in range(8):
        prod = NeonInterp(input_mem, twist, zetas)
        prod.set_iteration(iteration)
        prod.run(extract_region(
            PHASE123,
            f"slothy_start_ntt_phase123_iter{iteration}",
            f"slothy_end_ntt_phase123_iter{iteration}",
        ))

        utype = type_for_iter[iteration]
        cand = NeonInterp(input_mem, twist, zetas)
        cand.set_iteration(iteration)
        cand.run(extract_region(
            U01,
            f"slothy_start_ntt_phase123_u01_type_{utype}",
            f"slothy_end_ntt_phase123_u01_type_{utype}",
        ))

        for row_base in ("x4", "x5", "x6"):
            for off in (iteration * 64, iteration * 64 + 16):
                got = cand.rows[row_base].get(off)
                want = prod.rows[row_base].get(off)
                if got != want:
                    errors.append(
                        f"seed={seed} iter={iteration} type={utype} "
                        f"row={row_base} off={off}: want={want} got={got}"
                    )
                    if len(errors) >= 16:
                        return errors
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    args = ap.parse_args()

    zetas, twist = parse_hwords(NTT_BODY)
    total = 0
    for seed in range(args.seeds):
        errors = compare_one(seed, zetas, twist)
        total += 1
        if errors:
            print("phase123_u01_symbolic_mismatches:")
            for err in errors:
                print(err)
            return 1

    print(f"phase123_u01_symbolic_ok seeds={total} iterations=8 rows=3 slots=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
