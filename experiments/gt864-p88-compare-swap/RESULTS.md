# P88 — re-encrypt into a buffer and verify, at NTRU+864 only

Roadmap item 4.  Decapsulation's FO check re-encrypts and compares against the
received ciphertext.  Both trees fused that: `poly_tobytes_compare` produced each
block of the re-encryption and folded it straight against the expected bytes,
never materialising the result and saving a POLYBYTES buffer.

P86 and P87 made the packers much faster.  The fused compare did not ride that
down, because its cost is not the encoding -- it is the scattered narrow loads
of the expected bytes, which neither rewrite touched.  Packing into a buffer and
running the constant-time `verify` both trees already carry does ride it down.

## Where the two machines disagree

Kernels measured directly, ns per call:

| | M2 864 | M2 1152 | A76 864 | A76 1152 |
|---|---:|---:|---:|---:|
| `tobytes_full` | 97.2 | 98.0 | 481.6 | 564.8 |
| `verify` | ~17 | ~21 | 69.3 | 92.4 |
| **pack + verify** | **114.0** | **119.3** | **542.1** | 647.9 |
| **fused compare** | 133.0 | 159.3 | 605.7 | **568.9** |

On M2 the swap wins at both sizes, by 19 and 40 ns.  On A76 it wins at 864 by
64 ns and **loses at 1152 by 79**.

The reason is visible in the table: at 1152 on A76 the fused compare costs
568.9 against 564.8 for the packing alone -- **the scattered lane loads of the
expected bytes are almost free there**, where on M2 they cost 61 ns on top.  A76
has load slots to spare in this kernel; M2 does not.

So the swap goes in at 864 and not at 1152.  The promotion criterion is that
neither machine may regress, and at 1152 one does.

## At the KEM level

| | M2 decaps | A76 decaps |
|---|---:|---:|
| **NTRU+864** | **-20 ns** | **-47 ns** |
| NTRU+1152 (not adopted) | -50 ns | **+86 ns** |

Key generation and encapsulation are untouched; the compare is decapsulation
only.

## The buffer

The re-encryption goes into `buf3 + NTRUPLUS_SSBYTES`.  `buf3` is
`NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES` and `SYMBYTES == SSBYTES`, so that tail
is exactly `NTRUPLUS_POLYBYTES`; `poly_cbd1` has just consumed the seed that
lived there, and the leading `SSBYTES` that `ss` is read from are untouched.  No
new stack, no new clear -- `buf3` was already cleared on the way out.

## What this retires

`pack_compare.S` was the last user of the fused path at 864, so it goes: 244 KB
of assembly on top of the 564 KB P87 already retired.  `poly_tobytes_compare`,
its `pack_asm` declaration, its ABI sentinel and its ABI-test row go with it.

## Verification

- 200 key pairs, each with one valid and three single-bit-corrupted
  ciphertexts -- 800 decapsulations, 600 of them rejections -- produce output
  identical to the previous implementation, shared secret for shared secret.
  This is the path the KAT does not reach, since KAT vectors are all valid.
- `make check`: 10,368 canonical-boundary cases, ABI masks all zero, 21 clears /
  24,028 bytes / nothing left, KAT matching `kat/expected`, deterministic export.
- SUPERCOP leaf regenerated.
