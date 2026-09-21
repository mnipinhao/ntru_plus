#!/usr/bin/env python3
"""Lane-wise interval replay of the pinned Official NTRU+768 Forward schedule.

The arithmetic and routing mirror ntt.s, including its fused D8/D4/D2/D1
tile. Exact singleton replay is differentially checked against linked ASM.
Interval results are proof envelopes, not observed ranges or cycle estimates.
"""

import argparse
import ctypes
import hashlib
import json
import random
import re
import subprocess
import tempfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "upstream/supercop-avx2"
NTT = UPSTREAM / "ntt.s"
CONSTS = UPSTREAM / "consts.c"
EXPECTED_NTT_SHA256 = "992b613701be5988e83798a4a8f56a798c7e47e4616db70e65eee7feb75332f4"
Q = 3457
QINV = 12929
WORD_MIN, WORD_MAX = -32768, 32767


@dataclass(frozen=True)
class R:
    lo: int
    hi: int

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("inverted range")


ZERO = R(0, 0)


def signed16(x):
    return ((x + 32768) % 65536) - 32768


def raw_low_mul(x, const):
    return signed16(x * const)


def mont_word(x, w):
    companion = signed16(w * QINV)
    low = signed16(x * companion)
    return (x * w >> 16) - (low * Q >> 16)


@lru_cache(maxsize=None)
def mont_image(lo, hi, w):
    if lo < WORD_MIN or hi > WORD_MAX:
        raise ValueError(f"Montgomery input outside signed word: {lo, hi}")
    vals = (mont_word(x, w) for x in range(lo, hi + 1))
    minimum, maximum = WORD_MAX, WORD_MIN
    for value in vals:
        minimum = min(minimum, value)
        maximum = max(maximum, value)
    return R(minimum, maximum)


def barrett_word(x):
    quotient = (x * 9 + 16384) >> 15
    return x - Q * quotient


@lru_cache(maxsize=None)
def barrett_image(lo, hi):
    values = (barrett_word(x) for x in range(lo, hi + 1))
    minimum, maximum = WORD_MAX, WORD_MIN
    for value in values:
        minimum = min(minimum, value)
        maximum = max(maximum, value)
    return R(minimum, maximum)


def load_zetas():
    source = CONSTS.read_text()
    match = re.search(r"const int16_t zetas\[816\].*?=\s*\{(.*?)\};", source, re.S)
    if not match:
        raise ValueError("Official zetas declaration changed")
    values = [int(x) for x in re.findall(r"-?\d+", match[1])]
    if len(values) != 816:
        raise ValueError("Official zetas length changed")
    return values


class Replay:
    def __init__(self, values, zetas):
        self.mem = [values[i:i + 16] for i in range(0, 768, 16)]
        self.zetas = zetas
        self.stages = []
        self.failures = []
        self.pre_barrett = None

    def guard(self, value, stage, owner):
        if value.lo < WORD_MIN or value.hi > WORD_MAX:
            self.failures.append({"stage": stage, "owner": owner,
                                  "pre_operation": [value.lo, value.hi]})
        return value

    def add(self, a, b, stage, owner):
        return self.guard(R(a.lo + b.lo, a.hi + b.hi), stage, owner)

    def sub(self, a, b, stage, owner):
        return self.guard(R(a.lo - b.hi, a.hi - b.lo), stage, owner)

    def mul(self, a, w, stage, owner):
        self.guard(a, stage, owner + ":mont_input")
        return self.guard(mont_image(a.lo, a.hi, w), stage, owner + ":mont_output")

    def snapshot(self, stage, memory=None):
        memory = self.mem if memory is None else memory
        words = [x for vec in memory for x in vec]
        self.stages.append({"stage": stage, "min": min(x.lo for x in words),
                            "max": max(x.hi for x in words),
                            "max_abs": max(max(abs(x.lo), abs(x.hi)) for x in words),
                            "per_vector": [[min(x.lo for x in vec),
                                            max(x.hi for x in vec)] for vec in memory],
                            "per_lane": [[[x.lo, x.hi] for x in vec]
                                         for vec in memory]})

    def top_split(self):
        for packet in range(8):
            for j in range(3):
                low_i, high_i = packet * 3 + j, 24 + packet * 3 + j
                low, high = self.mem[low_i], self.mem[high_i]
                out_low, out_high = [], []
                for lane, (a, b) in enumerate(zip(low, high)):
                    owner = f"{low_i}:{lane}"
                    p = self.guard(R(min(-722 * b.lo, -722 * b.hi),
                                     max(-722 * b.lo, -722 * b.hi)),
                                   "top_split", owner + ":raw_mul")
                    out_low.append(self.add(a, p, "top_split", owner + ":low"))
                    out_high.append(self.add(self.sub(a, p, "top_split", owner + ":sub"),
                                             b, "top_split", owner + ":high"))
                self.mem[low_i], self.mem[high_i] = out_low, out_high
        self.snapshot("top_split")

    def radix3(self):
        for branch in range(2):
            const = branch * 8
            a, a2 = self.zetas[const + 6], self.zetas[const + 10]
            for packet in range(8):
                ia = branch * 24 + packet
                ib, ic = ia + 8, ia + 16
                A, B, C = self.mem[ia], self.mem[ib], self.mem[ic]
                o0, o1, o2 = [], [], []
                for lane, (x, y, z) in enumerate(zip(A, B, C)):
                    owner = f"{ia}:{lane}"
                    ba = self.mul(y, a, "radix3", owner + ":ba")
                    ca = self.mul(z, a2, "radix3", owner + ":ca2")
                    w = self.mul(self.sub(ba, ca, "radix3", owner + ":diff"),
                                 -886, "radix3", owner + ":w")
                    o0.append(self.add(self.add(x, ba, "radix3", owner + ":sum0"),
                                       ca, "radix3", owner + ":out0"))
                    o1.append(self.add(self.sub(x, ca, "radix3", owner + ":sub1"),
                                       w, "radix3", owner + ":out1"))
                    o2.append(self.sub(self.sub(x, ba, "radix3", owner + ":sub2"),
                                       w, "radix3", owner + ":out2"))
                self.mem[ia], self.mem[ib], self.mem[ic] = o0, o1, o2
        self.snapshot("radix3")

    def first_radix2(self):
        for tile in range(6):
            z = self.zetas[16 + tile * 4 + 6]
            base = tile * 8
            for j in range(4):
                a, b = self.mem[base + j], self.mem[base + 4 + j]
                out0, out1 = [], []
                for lane, (x, y) in enumerate(zip(a, b)):
                    owner = f"{base+j}:{lane}"
                    product = self.mul(y, z, "radix2_first", owner)
                    out0.append(self.add(x, product, "radix2_first", owner))
                    out1.append(self.sub(x, product, "radix2_first", owner))
                self.mem[base + j], self.mem[base + 4 + j] = out0, out1
        self.snapshot("radix2_first")

    @staticmethod
    def route(stage, a, b):
        if stage == "d8":
            return a[:8] + b[:8], a[8:] + b[8:]
        if stage == "d4":
            low, high = [], []
            for half in (0, 8):
                low += a[half:half + 4] + b[half:half + 4]
                high += a[half + 4:half + 8] + b[half + 4:half + 8]
            return low, high
        if stage == "d2":
            low, high = [], []
            for qword in range(0, 16, 4):
                low += a[qword:qword + 2] + b[qword:qword + 2]
                high += a[qword + 2:qword + 4] + b[qword + 2:qword + 4]
            return low, high
        if stage == "d1":
            low, high = [], []
            for pair in range(0, 16, 2):
                low += [a[pair], b[pair]]
                high += [a[pair + 1], b[pair + 1]]
            return low, high
        raise ValueError(stage)

    def later_radix2(self, stop=None):
        stage_buffers = {stage: [None] * 48 for stage in
                         ("d8", "d4", "d2", "d1_pre", "d1_post_barrett")}
        for tile in range(6):
            base = tile * 8
            const_base = 40 + tile * 32
            for stage, offset in (("d8", 24), ("d4", 216),
                                  ("d2", 408), ("d1", 600)):
                zetas = self.zetas[const_base + offset:const_base + offset + 16]
                outputs = [None] * 8
                routed = []
                for j in range(4):
                    routed.extend(self.route(stage, self.mem[base + j],
                                             self.mem[base + 4 + j]))
                # The live register bank is [r3..r6 | r7..r10]. Each route
                # emits two registers; the butterfly pairs bank positions
                # 0..3 with 4..7, not each route's two immediate outputs.
                for j in range(4):
                    a, b = routed[j], routed[4 + j]
                    out0, out1 = [], []
                    for lane, (x, y, z) in enumerate(zip(a, b, zetas)):
                        owner = f"{base+j}:{lane}"
                        product = self.mul(y, z, stage, owner)
                        out0.append(self.add(x, product, stage, owner))
                        out1.append(self.sub(x, product, stage, owner))
                    outputs[j], outputs[j + 4] = out0, out1
                self.mem[base:base + 8] = outputs
                stage_buffers[stage if stage != "d1" else "d1_pre"][base:base + 8] = outputs
                if stage == "d1":
                    if self.pre_barrett is None:
                        self.pre_barrett = [None] * 48
                    self.pre_barrett[base:base + 8] = outputs
                    if stop != "d1_pre":
                        reduced = [[barrett_image(x.lo, x.hi) for x in vec]
                                   for vec in outputs]
                        self.mem[base:base + 8] = reduced
                        stage_buffers["d1_post_barrett"][base:base + 8] = reduced
                if stage == stop or (stage == "d1" and stop == "d1_pre"):
                    break
        if stop is None:
            for stage in ("d8", "d4", "d2", "d1_pre", "d1_post_barrett"):
                self.snapshot(stage, stage_buffers[stage])
        else:
            self.snapshot(stop)

    def run(self):
        self.top_split()
        self.radix3()
        self.first_radix2()
        self.later_radix2()
        return self


def domain(name):
    if name == "keygen_f":
        return [R(-2, 4)] + [R(-3, 3)] * 767
    if name == "keygen_g":
        return [R(-3, 3)] * 768
    if name == "decap_message":
        # Full signed-word evaluation of Official crepmod3.s gives [-2,2];
        # do not assume the tighter empirical valid-caller [-1,1].
        return [R(-2, 2)] * 768
    if name in ("encap_r", "encap_m", "decap_reenc_r"):
        return [R(-1, 1)] * 768
    raise ValueError(name)


def linked_ntt(stop=None):
    tmp = tempfile.TemporaryDirectory(prefix="officialopt-ntt-proof-")
    library = Path(tmp.name) / "ntt.so"
    assembly = NTT
    if stop is not None:
        source = NTT.read_text()
        anchors = {
            "top_split": "sub $768, %rdi\n\n#level 1",
            "radix3": "sub $1536, %rdi\n\n#level 2",
            "radix2_first": "sub $1536, %rdi\n\nlea 1536(%rdi), %r8",
        }
        if stop in anchors:
            anchor = anchors[stop]
            if source.count(anchor) != 1:
                raise ValueError(f"trace anchor changed: {stop}")
            source = source.replace(anchor, anchor.split("\n\n")[0] + "\nret\n\n" +
                                    anchor.split("\n\n", 1)[1], 1)
        else:
            marker = {"d8": "#level4", "d4": "#level5",
                      "d2": "#level6", "d1_pre": "#reduce2"}[stop]
            begin = source.index(marker)
            end = source.index("\nret\n", begin)
            stores = "\n".join(f"vmovdqa %ymm{reg}, {j * 32}(%rdi)"
                               for j, reg in enumerate((11, 12, 13, 14, 7, 8, 9, 10)))
            source = (source[:begin] + stores + "\nadd $256, %rdi\nadd $64, %rdx\n"
                      "cmp %r8, %rdi\njb _looptop_start_3456\n" + source[end:])
        assembly = Path(tmp.name) / "ntt-trace.s"
        assembly.write_text(source)
    subprocess.run(["cc", "-shared", "-fPIC", "-mavx2", "-o", str(library),
                    str(assembly), str(CONSTS)], check=True, capture_output=True)
    dll = ctypes.CDLL(str(library))
    dll.poly_ntt.argtypes = [ctypes.c_void_p]
    return tmp, dll.poly_ntt


def compare_exact(zetas):
    binaries = {stage: linked_ntt(stage) for stage in
                ("top_split", "radix3", "radix2_first", "d8", "d4",
                 "d2", "d1_pre", None)}
    checked = 0
    rng = random.Random(0x76820260921)
    try:
        for name in ("keygen_f", "keygen_g", "encap_r", "encap_m", "decap_message"):
            cases = [[0] * 768, [(-1 if i & 1 else 1) for i in range(768)]]
            for location in (0, 1, 383, 384, 767):
                for sign in (-1, 1):
                    case = [0] * 768
                    case[location] = sign
                    cases.append(case)
            if name == "encap_r":
                # Cover every coefficient, physical lane, vector and tile
                # with both signs, not just representative packet positions.
                for location in range(768):
                    for sign in (-1, 1):
                        case = [0] * 768
                        case[location] = sign
                        cases.append(case)
            for _ in range(32):
                if name == "keygen_f":
                    case = [rng.choice((-3, 0, 3)) for _ in range(768)]
                    case[0] = rng.choice((-2, 1, 4))
                elif name == "keygen_g":
                    case = [rng.choice((-3, 0, 3)) for _ in range(768)]
                elif name == "decap_message":
                    case = [rng.randint(-2, 2) for _ in range(768)]
                else:
                    case = [rng.choice((-1, 0, 1)) for _ in range(768)]
                cases.append(case)
            for case in cases:
                if name == "keygen_f" and case[0] not in (-2, 1, 4):
                    continue
                raw = ctypes.create_string_buffer(1536 + 31)
                address = (ctypes.addressof(raw) + 31) & ~31
                array = (ctypes.c_int16 * 768).from_address(address)
                array[:] = case
                for stage in binaries:
                    array[:] = case
                    binaries[stage][1](address)
                    modeled = Replay([R(x, x) for x in case], zetas)
                    modeled.top_split()
                    if stage != "top_split":
                        modeled.radix3()
                    if stage not in ("top_split", "radix3"):
                        modeled.first_radix2()
                    if stage not in ("top_split", "radix3", "radix2_first"):
                        modeled.later_radix2(stage)
                    got = [x.lo for vec in modeled.mem for x in vec]
                    if got != list(array):
                        mismatch = next(i for i, (a, b) in enumerate(zip(got, array)) if a != b)
                        raise ValueError(f"ASM differential failed at {stage}: {name}, coefficient {mismatch}: {got[mismatch]} != {array[mismatch]}")
                checked += 1
    finally:
        for tmp, _ in binaries.values():
            tmp.cleanup()
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/officialopt-forward-lane-proof-20260921.json")
    args = parser.parse_args()
    source_sha = hashlib.sha256(NTT.read_bytes()).hexdigest()
    if source_sha != EXPECTED_NTT_SHA256:
        raise ValueError("pinned Official ntt.s changed; re-audit the model")
    zetas = load_zetas()
    exact_cases = compare_exact(zetas)
    reports = {}
    for name in ("keygen_f", "keygen_g", "encap_r", "encap_m",
                 "decap_message", "decap_reenc_r"):
        inputs = domain(name)
        replay = Replay(inputs, zetas).run()
        before = [x for vec in replay.pre_barrett for x in vec]
        after = [x for vec in replay.mem for x in vec]
        reports[name] = {
            "input_coefficient0": [inputs[0].lo, inputs[0].hi],
            "input_other_coefficients": [inputs[1].lo, inputs[1].hi],
            "stages": replay.stages,
            "pre_barrett_min": min(x.lo for x in before),
            "pre_barrett_max": max(x.hi for x in before),
            "post_barrett_min": min(x.lo for x in after),
            "post_barrett_max": max(x.hi for x in after),
            "pre_barrett_per_vector": [[min(x.lo for x in vec),
                                        max(x.hi for x in vec)]
                                       for vec in replay.pre_barrett],
            "signed_word_failures": replay.failures,
        }
    output = args.output
    if output.exists():
        raise SystemExit(f"refusing overwrite: {output}")
    output.write_text(json.dumps({
        "class": "lane-wise independent-interval proof envelope with exact singleton ASM differential",
        "ntt_source_sha256": source_sha,
        "consts_source_sha256": hashlib.sha256(CONSTS.read_bytes()).hexdigest(),
        "exact_asm_differential_cases": exact_cases,
        "reducer_candidate_status": "not selected until downstream consumer proof",
        "domains": reports,
    }, indent=2) + "\n")
    for name, report in reports.items():
        print(name, [report["pre_barrett_min"], report["pre_barrett_max"]],
              "overflow checks", len(report["signed_word_failures"]))
    print("exact ASM differential cases", exact_cases)


if __name__ == "__main__":
    main()
