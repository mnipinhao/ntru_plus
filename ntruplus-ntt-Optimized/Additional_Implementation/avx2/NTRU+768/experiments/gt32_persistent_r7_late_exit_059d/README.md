# GT32-PERSISTENT-R7-LATE-EXIT-059D

Executable lowering gate for the 059C persistent-R7 consumer contract:

```text
seven H-domain planes
  -> pair-packed K_lambda vpmaddwd
  -> one REDC32 exit per coefficient
  -> existing Q24 transpose/packet route
  -> wire bytes
```

The block gate compares 16 leaves / 64 coefficients / four real Q24 packets.
The full gate processes all 12 blocks in production wire order
`0,1,9,8,4,5,11,10,6,7,3,2`, scanning the complete 6 KiB constant table.
Correctness constructs quartic and H-domain representations from the same
degree-three polynomial and requires byte-exact output for 1,000 deterministic
trials. This is a serializer/lowering check, not a product-folding check.

This is a research continuation gate.  A slower late exit does not by itself
reject persistent R7 because upstream R7 B3, recombination, materialization,
and add credits are outside this timed region.  GT Clean is unchanged.

## Initial executable result

The signed-low-word REDC32 correction is essential.  The unsigned form can
produce representatives below `-q`, which one Q24 sign correction cannot
canonicalize.  Exhausting all 65,536 low-word residues over the proven
accumulator interval gives an exact signed-REDC output interval recorded in
`generated/signed_redc32_range.json`; it lies strictly inside `(-q,q)`.

Eight launches give:

| region | current quartic | R7 late exit | delta |
| --- | ---: | ---: | ---: |
| one 16-leaf block | 12 TSC | 37 TSC | +25 |
| full 192 leaves | 113 TSC | 442 TSC | +329 |

The full result closely tracks twelve block debts.  The 6 KiB constant sweep
does not introduce another discontinuity, but the late interpolation/REDC
cost is real and distributed across multiply, shuffle, and load ports.  This
does not close 059C: the next semantic gate must include R7 point products,
message addition, and the deleted quartic recombination/materialization.

The final measurements use 128-bit low stores and a safe 8+4-byte final high
store.  Output canaries are preserved; an earlier YMM-width low-store draft
was rejected before these results were recorded.

## 059E correction

The subsequent genuine product gate found that the selected lambda table is
`lambda*R` (e=1), while 059C/059D treated it as algebraic lambda, and that the
late constant halves must follow AVX2 lane-local unpack indices. Degree-three
reconstruction cannot expose either lambda-folding error. The timing and
signed-REDC measurement above remain valid, but the product-path correctness
claim is superseded by `gt32_r7_consumer_island_059e`, which uses corrected
logical lambdas and passes 1,000 complete product-plus-message cases.

## Run

```sh
make clean all
python3 tools/prove_signed_redc.py
make run
```
