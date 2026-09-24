# P133 — NTRU+864 frombytes as the inverse of the run-based serializer

Question: do the ideas of the NTRU+864 AVX2 `tobytes`/`frombytes` rewrite
(exp002: pair the coefficients that share a lane, no transpose, one byte
shuffle, overlapping 16-byte stores) have NEON counterparts in GT?

Most were already in GT: no natural-order pass and no stack round trip (P86,
P87), `sli` does in one instruction what `vpmaddwd` does for AVX2, `add` +
`umin` canonicalisation in the small serializer, overlapping 16-byte stores
(P130/P131).  GT's layout, like Official's, keeps six consecutive
coefficients down a lane, but its runs are scattered (Good-Thomas order), so
adjacent lanes are not adjacent wire runs and each run is stored on its own;
`tobytes` needs its one transpose for that.

What was left was `frombytes`, still the generated decoder with 388 lane
inserts.  Its inverse-of-`tobytes` form:

- one 16-byte load per run at its own offset (the run at 1287 loads the 16
  bytes ending at byte 1296, index shifted by seven);
- one `tbl` expanding nine bytes to six halfwords;
- an 8x8 halfword transpose (vector i = halfword i of all runs);
- one `and 0xfff` or `ushr 4` per vector, the same for every lane;
- one running `umax`, one comparison.

## Correctness (`check.c`, M2 clang and A76 gcc)

Against the production decoder: 200,000 inputs (half canonical encodings,
half random bytes) and one out-of-range coefficient at each of the 864
positions -- identical output and return value; the input ends at a guard
page, so any read past byte 1296 would fault.  Integrated, the same check
against HEAD's decoder compiled under another name: identical.  KAT,
`make check` on M2 and Linux, TIMECOP `-O`..`-Os` pass.

## Speed

| | M2 | A76 |
|---|---:|---:|
| `frombytes`, one call (`bench.c`) | 73.8 -> 55.4 ns (-25%) | 640 -> 498 cycles (-22%) |
| decapsulation (3 calls) | 3,818 -> 3,760 ns (-1.5%) | 14,022 -> 13,841 ns (-1.3%) |
| encapsulation (1 call) | -0.36% | -0.34% |

Against SUPERCOP's Official, same sessions (P129 harness): M2 vs Official + CE
-9.6 / -11.7 / -9.1%, Keccak equal -6.0 / -6.7 / -5.6%; A76 Keccak equal
-10.8 / -12.5 / -10.5%, vs Official as shipped -18.0 / -23.8 / -18.4%.
