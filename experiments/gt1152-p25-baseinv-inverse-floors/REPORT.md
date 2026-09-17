# P25 — Where `baseinv` and `inverse` actually stand

Branch `neon-1152`, parent `d1ed5720`.  Analysis gate: no code changed.
Pi 5 core 3, GCC 14.2.0.

Two questions after P22-P24: is `baseinv` the next target, and does `inverse`
still have headroom now that it sits at +18?

## 1. `baseinv` — yes, and it has two separate problems

+2,397, larger than every other remaining loss combined, and **keygen-only**,
which is why keygen (+1.09%) is the one operation still behind.

Phase timing, PMU reads inside the function (about 540 cycles of instrumentation
overhead against the profiler's 6,498 per call):

| phase | cycles | share |
|---|---:|---:|
| numerator loop, 36 groups | 3,783 | 53.8% |
| **prefix + inversion + recover** | **1,928** | **27.4%** |
| finish loop, 36 groups | 1,087 | 15.4% |

**The serial phase is a latency problem, not a throughput one.**  It is a
35-step `fqmul` prefix chain, then `fqinv`'s addition chain for exponent 3455,
then 35 recover steps each carrying `inv = fqmul(inv, di)` — every one of them
strictly serial, with one vector in flight and the multiply pipe idle most of
the time.  This is exactly what "no ILP split" means, and NTRU+864's 12x3
decomposition runs three independent chains so the latency divides by about
three.

**The other two phases are throughput-bound and under-scheduled**, at the same
~78% the campaign has seen elsewhere:

| phase | multiply-class ops per group | V0 floor | x36 | measured | utilisation |
|---|---:|---:|---:|---:|---:|
| numerator | 21 wide pairs + 10 reductions | 82 | 2,952 | 3,783 | 78% |
| finish | 4 `fqmul` | 24 | 864 | 1,087 | 79% |

So `baseinv` has roughly **1,100 cycles available from the ILP split and another
~800 from scheduling**, which would put it near 4,500 against the official's
5,300 per call and flip keygen negative.

## 2. `inverse` — real headroom, but no competitive gap

`poly_invntt_ternary` measures **6,293** against the official's `poly_invntt` +
`poly_crepmod3` at **6,292**.  Dead level.

Its multiply-pipe floor, from the shipped kernels and the driver's confirmed
call counts:

| kernel | calls | multiply-class ops each | total |
|---|---:|---:|---:|
| `packed_i9` (`inverse9.S`) | 16 | 19+19+19 = 57 | 912 |
| `invntt16_asm` (`inverse16.S`) | 8 | 51+51+49 = 151 | 1,208 |
| `invntt16_tail_asm` | 1 | 50+50+49 = 149 | 149 |
| `crepmod3_ternary_asm` | 1 (x36) | 4+4 = 8 | 288 |
| | | **2,557** | |

At the measured 2 cycles per vector multiply on this core that is a **5,114
cycle floor against 6,293 measured — 81%**.

So there is about 1,200 cycles of absolute headroom, but taking it moves the
total without changing the standing: the official is already level.

**One apparent cheap win is not available.**  `inverse16.S` still spends 128
`umov` plus 128 `strh` per call, the same degree-3 extraction P22 replaced with
32 `str d` in the tail.  It does not transfer: the tail's four branches are four
*contiguous* int16, but `invntt16_asm`'s 128 outputs are **8 bytes apart** — one
component across leaves, gaps of 8 (96 times) and 48 (31 times), no aligned run
of four anywhere.  Making them contiguous means one call producing all four
components, which is the four-components-live restructure P14 rejected for
`ntt9.S`.

## 3. Conclusion

| | remaining | nature |
|---|---:|---|
| **`baseinv`** | **+2,397** | serial batch inversion (ILP split) + ~78% scheduling |
| hash | +902 | M2-1, a large absolute win on top |
| `basemul_rinv` | +634 | pure scheduling, 78% of floor, M2-2 |
| `frombytes` | +659 | structural, at its floor (P19) |
| `inverse` | +18 | level; ~1,200 absolute headroom, no gap |

**`baseinv` next**, and the ILP split before the scheduling: it is the larger of
its two levers, it is the one with a known shape from NTRU+864, and it is a
restructure rather than a re-derivation, so it carries no bound risk.

## Reproduce

`baseinv_phase_driver.c` against an `inverse.c` with PMU reads inserted at the
two phase boundaries; kernel instruction counts with `grep -cE '^\s+[a-z]'` and
the mnemonic histogram on the shipped `.S` files.
