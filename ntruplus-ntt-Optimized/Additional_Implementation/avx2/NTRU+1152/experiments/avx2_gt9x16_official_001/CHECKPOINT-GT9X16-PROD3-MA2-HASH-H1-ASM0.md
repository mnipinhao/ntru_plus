# GT9X16-PROD3-MA2-HASH-H1-ASM0

## Result

H1 is now a complete straight-line AVX2 serializer:

```text
2304-byte materialized scale-4 MA2 planes
  -> exact Official physical-vector reconstruction
  -> inv4 Montgomery
  -> sign-add-q canonicalization
  -> pinned pack.s bit/transpose network
  -> exact 1728 hash bytes
```

It creates no generic-F0 array, Official coefficient temporary, stack frame,
spill, call, branch, or `vzeroupper`. The input and output pointer contracts
remain naturally aligned (`int16_t` input, byte output), with no YMM-alignment
requirement; only generated read-only constants require 32-byte alignment.

## Correctness and range gates

The raw 1,728-byte differential passes:

- all 2,304 signed MA2-plane impulses;
- zero and alternating proved bounds;
- 1,003 random full-range plane states;
- every uniform value in the complete 41,505-value `[-20751,20753]` envelope;
- 2,304 signed coefficient-domain caller impulses;
- zero, alternating, and 1,003 random-small caller-realistic inputs;
- unaligned source/output cases, source immutability, and prefix/suffix canaries.

The independent scalar oracle follows the probed pinned-pack bit ownership.
The actual caller differential separately compares against
`poly_ntt -> poly_tobytes`. The linked arithmetic is exactly
`[-20751,20753] -> [-1998,1998] -> [0,3456]`; it contains no saturating pack
instruction and no Barrett stage.

## Linked structural ledger

| Category | Scheduled | Linked |
| --- | ---: | ---: |
| data loads | 272 | 272 |
| constant vector loads | 27 | 27 |
| shuffle-mask memory operands | 136 | 136 |
| coefficient routing | 336 | 336 |
| inv4 Montgomery instructions | 288 | 288 |
| sign canonicalization | 216 | 216 |
| pack-bit instructions | 144 | 144 |
| pack-transpose routes | 324 | 324 |
| byte stores | 54 | 54 |
| vector spill/reload | 0 | 0 |

The leaf contains 1,662 instructions and uses exactly `ymm0..ymm15`. Its
symbol text is 10,133 bytes; its private object `.rodata` is 640 bytes. The
object entry is `mod32=0, mod64=0`; in the correctness ELF it is
`mod32=0, mod64=32`. Object `.text/.rodata` alignment is 32 bytes and linked
ELF `.text/.rodata` alignment is at least 32 bytes.

## Pack-layout correction

ASM0 raw-byte testing exposed and repaired a circular assumption in the prior
H2 map. `official_coefficient` names a physical Official NTT cell, while
`pack.s` transposes each eight-vector block before emitting logical serialized
pairs. A checked-in basis probe now records the exact 1,152-element
physical-to-serialized permutation.

With that permutation applied, zero of the 576 true serialized pairs stays
within one MA2 vector. The previous H2 claim that all 576 pairs were local,
and therefore its 72-load H2-96 schedule, is withdrawn. H1 is unaffected: it
always reconstructs the exact eight physical vectors consumed by pinned
`pack.s`.

## Decision

H1 ASM0 passes correctness, range, ABI, alignment, and linked-ledger gates.
H2 remains unauthorized and now requires a new map rather than lowering the
withdrawn schedule. No performance measurement or KEM integration was run.
The next authorized checkpoint is H0-versus-H1 fanout-edge pricing with the
existing SUPERCOP-derived serious methodology.
