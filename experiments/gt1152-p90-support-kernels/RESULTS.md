# P90 — NTRU+1152's support kernels, without writing assembly

Roadmap item 3's other half.  P86 replaced the serializer; `poly_cbd1`,
`poly_sub` and `poly_triple` were still the plain C the tree shipped, and the
re-profile after P86/P87 left them as the largest single deficit on the board:
`sotp/cbd/add` at +191 ns in key generation, +102 in encapsulation, +28 in
decapsulation.

## Per kernel, M2, gated harness

|  | before | after | official |
|---|---:|---:|---:|
| `poly_cbd1` | 78.1 | **48.5** | 51.0 |
| `poly_sub` | 55.0 | **32.4** | 32.0 |
| `poly_triple` | 49.8 | **27.5** | 26.2 |
| `poly_sotp_encode` | 86.1 | (rides `cbd1`) | 55.7 |
| `poly_sotp_decode` | 55.6 | unchanged | 59.1 |

`poly_sotp_encode` is an xor and a copy in front of `poly_cbd1`, so it collects
the same 30 ns.  `poly_sotp_decode` was already ahead.

## What was wrong, and what replaced it

**`poly_cbd1` expanded one byte at a time.**  `vdupq_n_u16(buf[i])` takes a
scalar byte through a general-purpose register and broadcasts it, twice per
eight coefficients -- 144 iterations of that at 1152.

NTRU+864's `cbd.S` does not, and neither does the official kernel: they are
bit-sliced.  Sixteen bytes of each half arrive at once; a shift and an 0x55 mask
separate the even and odd bit positions; adding 0x55 biases each two-bit field
by one so the difference cannot borrow; the subtraction then leaves four fields
per byte holding `a - b + 1` in {0,1,2}.  Two more mask-and-unbias stages peel
those out into eight byte streams, a three-level `trn` network interleaves them
back into coefficient order, and the widening finishes it.  Nothing leaves the
vector unit.

1152 is the easy case for this: N/8 is 144 bytes a half, exactly nine sixteen-
byte blocks, where 864's 108 forced the prologue that makes its `cbd.S` 532
instructions long.  Transcribed into intrinsics it matched the old
implementation on the first run, and it is **2.5 ns faster than the official
assembly**.

**`poly_sub` and `poly_triple` were straightforward `i += 8` loops.**  864's
`add.S` takes twelve vectors a turn with the loads hoisted above the arithmetic.
Written that way in C both land at parity, 55.0 to 32.4 and 49.8 to 27.5.  A
plain `#pragma GCC unroll 4` gets most of it too (28.9 for the tripling), so the
old code was simply not unrolled enough.

**No assembly was written.**  That is now three rounds -- P86, P87, P90 -- where
C intrinsics matched or beat hand-written kernels, and one, P87, where they
replaced 564 KB of it.

## At the KEM level

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| **M2 Pro** | **-115** | **-60** | **-53** |
| **Cortex-A76**, `taskset -c 3` | -5 | -15 | **-46** |

Neither machine regresses.  A76 gains much less, which is consistent with the
kernels having been unroll-limited rather than algorithm-limited there -- gcc
had already done most of what the twelve-way form does by hand, and only the
bit-sliced `cbd1` is a genuine algorithmic change it could not have found.

## Verification

- 500 random buffers through `poly_cbd1`, bit-identical to the previous
  implementation.
- `make check`: ABI masks all zero, 33 clears / 34,000 bytes / nothing left,
  10,368-case canonical boundary, KAT matching `kat/expected`, deterministic
  export.
- SUPERCOP leaf regenerated.
