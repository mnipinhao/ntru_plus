# GT32-PLANE-N16-RADIX4-ROUTE-ELIM-008

This is the bounded continuation of plane-major experiment 007.  It asks
whether two consecutive N16 radix-2 stages can share one physical formation,
or whether an exact radix-4 DIT/DIF factorization can remove a complete route
or Montgomery layer.

GT Clean is not modified.  This experiment is generator-only because every
radix-4 family fails the static assembly gate.

## Exact families

The generator checks three distinct cases:

1. `R2x2_exact`: retain the two qualified radix-2 matrices but replace two
   stage-local unpack formations with one 16-shuffle 4x4-qword transpose;
2. true DIT: prove each four-point block is exactly
   `DFT4(omega32^8) * diag(1,g,g^2,g^3)`;
3. pure DIF: test whether the same local operator closes as a post-diagonal
   radix-4 transform under input/output permutations.

All executable R2/R2x2 paths pass 128 exact basis-vector checks.  Every true
DIT block passes exact matrix equality.  Pure local DIF closes for only 4/8
S2/S3 blocks and 1/8 S4/S5 blocks; the other blocks would carry a new
twist/scale debt across the two-stage boundary, so they are not route-only
candidates.

## Physical-search result

The complete coefficient-plane terminal cost is:

| segmentation | instructions | shuffles | loads | peak YMM | depth |
|---|---:|---:|---:|---:|---:|
| R2+R2+R2+R2 | **144** | **48** | 32 | 13 | 22 |
| R2+R2+R2x2 | 152 | 56 | **32** | 13 | 24 |
| R2+R2x2+R2 | 153 | 56 | 33 | 13 | 24 |
| R2x2+R2+R2 | 153 | 56 | 33 | 13 | 24 |
| R2x2+R2x2 | 168 | 72 | **32** | 13 | 26 |

The joint formation does remove the intermediate radix-2 layout, but it also
moves one or two coefficient axes into word lanes.  Returning to persistent
coefficient-plane SoA needs an 8- or 16-shuffle terminal repair.  Consequently
every joint path has more total routing than the 007 radix-2 control.

## True radix-4 arithmetic and range

S2/S3 initially appears promising: after quotienting identity constants, its
DIT factorization has five non-identity full-vector Montgomery chains instead
of eight.  That count alone is not range-safe.

Starting from the qualified post-S1 bound 3456, the q4=0 raw radix-4 outputs
reach 13824 and 8674.  An exhaustive search over all 2^8 whole-register
center10 sets proves that at least six output registers must be centered for
S4/S5 to finish within the existing BaseMul input bound.  The minimum legal
terminal bound is 10719.

Thus the effective S2/S3 arithmetic is:

```text
5 Montgomery chains × 4 instructions = 20
6 center10 repairs × 3 instructions   = 18
radix-4 add/sub                         = 16
total                                  = 54
```

The exact two-radix-2 control is 48 instructions.  True S2/S3 radix-4 is six
arithmetic instructions worse before physical terminal repair.

For S4/S5, prefix twiddles are mixed within live vectors.  Three pre-twiddles
plus the internal square-root-of-minus-one multiply give the same lower bound
of eight full-vector chains and 48 arithmetic instructions as radix-2x2.

Putting both radix bits into each four-word qword makes `vpshuflw/vpshufhw`
available, but it does not compact the multiplication operands.  The direct
form needs 16 vector chains; reaching the eight-chain scalar-slot lower bound
requires another packing route.  It therefore provides no new acceleration
mechanism.

## Decision

Do not emit assembly and do not modify GT Clean.

This closes persistent full-plane radix-4 as a route-elimination mechanism
under the current N16 arithmetic, 10788 BaseMul range contract, and
coefficient-plane terminal.  It does not close a consumer-selected hybrid
terminal, or a broader twist/scale ABI that intentionally carries a different
domain into the consumer.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/plane_n16_radix4_gate.json`: exact matrices, range search,
  complete segmentation costs, and the hard-stop decision.
