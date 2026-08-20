# Checkpoint C2: packed-Montgomery utilization

C2 tests whether pairing terminal coefficients `(0,1)` or `(2,3)` can fill all
16 i16 lanes of each constant Montgomery multiply. Generated-oracle inspection
confirms that NTT16 twiddles are independent of terminal coefficient. The two
coefficient halves therefore share one constant vector without changing the
selected terminal ABI or NTT9 row meaning.

## Implemented A/B

- Distance-8-only consumes the already verified skewed `Z` representation.
  C0 executes two independent islands; C2 packs the two eight-value operands
  into one YMM.
- Full NTT16 compares two straight-line C0 bodies against a C2 pair kernel.
  The correctness-first C2 first shears each coefficient, materializes those
  18 skewed rows once, then performs all four pair-packed stages row-by-row.
  That boundary is included in the timing.

All four functions are call-free leaves with no stack, spills, frame, or
`vzeroupper`. C0 and C2 match bit-for-bit for 10,003 full-i16/boundary/random
pairs plus in-place alias cases.

## Result

Nine fresh pinned launches on CPU 1 of the Intel Core Ultra 7 155H, 201 samples
per launch, GCC 15.2 `-O3 -mavx2`:

| Two-island operation | C0 cycles | C2 cycles | Direction |
| --- | ---: | ---: | --- |
| distance-8 only | 38.539 | 37.186 | C2 −3.5% |
| complete NTT16 | 181.199 | 266.010 | C2 +46.8% |

| Static item | distance-8 C0 | distance-8 C2 | full C0 | full C2 |
| --- | ---: | ---: | ---: | ---: |
| Montgomery vector chains | 18 | 9 | 72 | 36 |
| pack/unpack/routing instructions | 38 | 57 | 146 | 399 |
| instructions | 283 | 216 | 1,027 | 962 |
| data loads / stores | 18 / 18 | 20 / 18 | 18 / 18 | 38 / 36 |
| designed peak-live YMM | 13 | 11 | 15 | 16 |
| calls / `vzeroupper` / frame / spills | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |

Halving the distance-8 chains barely clears its extra packing cost. At smaller
distances, compressing eight unique operands and reconstructing two canonical
rows drives routing from 146 to 399 instructions; the initial shear boundary
adds 20 loads and 18 stores relative to full C0. The complete result decisively
reverses direction.

C2 is rejected and Checkpoint D remains paused. The next checkpoint must
reassess physical SIMD orientation or find a producer/consumer schedule that
keeps pair-packed states natively; it must not proceed directly to radix-3
NTT9 on the current row-per-YMM representation.

Evidence: `results/c2-intel155h-20260820-001/c2-diagnostic.json`. This is a
repository-local diagnostic, not SUPERCOP or promotion evidence.
