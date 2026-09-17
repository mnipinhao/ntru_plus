"""Measure the NTRU+864 GT forward output layout by running it.

The GT forward's output order is defined by .Lntt_one_bank's internals, which
are 617 instructions of Slothy output.  Rather than reverse-engineer them, this
probe builds the real kernel on the local arm64 host and derives the layout
empirically, then checks the derived rule against further random inputs.

Everything here is correctness/layout only.  This host is Apple silicon, not
Cortex-A76; nothing measured here is a performance fact.
"""

import random
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REF864 = REPO / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864"

Q = 3457
N = 864
DEG = 3
QINV = 12929
OMEGA = -886


def s16(x):
    x &= 0xFFFF
    return x - 0x10000 if x >= 0x8000 else x


def mont(a):
    t = s16(s16(a) * QINV)
    return s16((a - t * Q) >> 16)


_BV = ((1 << 26) + Q // 2) // Q


def barrett(a):
    t = s16((_BV * a + (1 << 25)) >> 26)
    return s16(a - s16(t * Q))


def load_zetas():
    text = (REF864 / "ntt.c").read_text()
    m = re.search(r"const int16_t zetas\[288\]\s*=\s*\{(.*?)\};", text, re.S)
    return [int(t) for t in re.findall(r"-?\d+", m.group(1))]


ZETAS = load_zetas()


def ref_ntt(a):
    """Reference NTRU+864 forward NTT, transcribed from Reference_Implementation."""
    r = [0] * N
    k = 1
    z = ZETAS[k]; k += 1
    for i in range(N // 2):
        t1 = mont(z * a[i + N // 2])
        r[i + N // 2] = s16(a[i] + a[i + N // 2] - t1)
        r[i] = s16(a[i] + t1)

    step = N // 6                       # radix-3: 144, 48
    while step >= 48:
        for start in range(0, N, 3 * step):
            z1 = ZETAS[k]; k += 1
            z2 = ZETAS[k]; k += 1
            for i in range(start, start + step):
                t1 = mont(z1 * r[i + step])
                t2 = mont(z2 * r[i + 2 * step])
                t3 = mont(OMEGA * s16(t1 - t2))
                r[i + 2 * step] = s16(r[i] - t1 - t3)
                r[i + step] = s16(r[i] - t2 + t3)
                r[i] = s16(r[i] + t1 + t2)
        step //= 3

    step = 24                           # radix-2: 24, 12, 6, 3
    while step >= 3:
        for start in range(0, N, step << 1):
            z1 = ZETAS[k]; k += 1
            for i in range(start, start + step):
                t1 = mont(z1 * r[i + step])
                r[i + step] = barrett(s16(r[i] - t1))
                r[i] = barrett(s16(r[i] + t1))
        step >>= 1
    return r


def gt_forward(a):
    out = subprocess.run([str(HERE / "dump864"), ",".join(map(str, a))],
                         capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.strip().split(",")]


def gt_leaf_bases():
    """Derived layout: index = top*432 + row*48 + halfcol*24 + component*8 + lane.

    Read off ntt9.S: each bank issues 18 stores at byte offsets
    {0,96,...,768} and {48,144,...,816}, i.e. 9 rows x 2 half-columns with a
    48-byte stride; component selects a 16-byte slot inside that stride and the
    two tops are 864 bytes apart.
    """
    bases = []
    for top in range(2):
        for row in range(9):
            for halfcol in range(2):
                for lane in range(8):
                    bases.append(top * 432 + row * 48 + halfcol * 24 + lane)
    return bases


def main():
    random.seed(20260917)
    rng_inputs = [[random.randint(-3, 4) for _ in range(N)] for _ in range(6)]

    bases = gt_leaf_bases()
    assert len(bases) == 288, len(bases)

    # Reference leaves are contiguous triples; GT leaves are branch-major with
    # a stride of 8 int16.
    def ref_leaves(r):
        return [tuple(r[DEG * k + b] % Q for b in range(DEG)) for k in range(288)]

    def gt_leaves(r):
        return [tuple(r[base + 8 * b] % Q for b in range(DEG)) for base in bases]

    # Derive the permutation from the first input, then confirm on the rest.
    a0 = rng_inputs[0]
    ref0, gt0 = ref_leaves(ref_ntt(a0)), gt_leaves(gt_forward(a0))

    index = {}
    for k, t in enumerate(ref0):
        index.setdefault(t, []).append(k)
    collisions = sum(1 for v in index.values() if len(v) > 1)

    perm = []
    unmatched = 0
    for g in gt0:
        cand = index.get(g)
        if not cand:
            unmatched += 1
            perm.append(None)
        else:
            perm.append(cand[0])

    print(f"reference leaf triples: {len(ref0)}, colliding triples: {collisions}")
    print(f"GT leaves matched to a reference leaf: {288 - unmatched}/288")

    if unmatched:
        print("\nno direct match; checking for a constant scale factor")
        g = gt0[0]
        for k, t in enumerate(ref0):
            if t[0] == 0:
                continue
            f = g[0] * pow(t[0], Q - 2, Q) % Q
            if all(g[b] == t[b] * f % Q for b in range(DEG)):
                print(f"  GT leaf 0 == reference leaf {k} scaled by {f} "
                      f"(={s16(f) if f < Q else f})")
                break
        else:
            print("  no single-leaf scale relation found on leaf 0")
        return 1

    ok = sorted(x for x in perm if x is not None) == list(range(288))
    print(f"permutation is a bijection over 288 leaves: {ok}")

    stable = True
    for a in rng_inputs[1:]:
        ref, gt = ref_leaves(ref_ntt(a)), gt_leaves(gt_forward(a))
        if any(gt[i] != ref[perm[i]] for i in range(288)):
            stable = False
            break
    print(f"permutation reproduces {len(rng_inputs) - 1} further random inputs: {stable}")

    if ok and stable:
        print("\nfirst 16 GT->reference leaf indices:", perm[:16])
        (HERE / "perm864.txt").write_text(
            "\n".join(str(p) for p in perm) + "\n")
        print("wrote perm864.txt")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
