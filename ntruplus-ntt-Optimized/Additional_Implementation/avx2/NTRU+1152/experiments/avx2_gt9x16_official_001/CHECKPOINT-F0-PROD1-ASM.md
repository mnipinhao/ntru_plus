# Checkpoint F0-PROD1-ASM P1-H

## Outcome

P1-H replaces PROD0's scalar GT adapters and coefficient/pair staging with one
direct AVX2 pair helper. It preserves the exact pipeline authorized by
F0-PROD1-SCHED:

```text
coefficient input
-> unchanged existing top split
-> 2,304-byte materialized split state
-> direct AVX2 coefficient-stream formation
-> frozen paper R2
-> frozen F-R3D1
-> scale-four F0 ABI
```

Top-split arithmetic, P/Q physical order, scale, reductions, MA2, the caller,
and the zero-copy boundary are unchanged. This checkpoint contains no timing
or KEM claim.

## P1-H geometry

The C wrapper owns only the aligned split array and invokes the same helper for
four public `(branch,terminal-pair)` combinations. The helper selects branch
constants and one of the mechanically proved `vpshufd 0x88/0xdd` paths once at
entry. It then:

1. forms three GT rows at a time from aligned split loads;
2. pre-twists both streams in AVX2 registers;
3. executes the unchanged R2 first-layer arithmetic and reductions;
4. writes those results directly to strided eventual-F0 slots;
5. executes R2 second layer and D1 in place in those slots; and
6. returns without a frame or `vzeroupper`.

The third R2 first-layer group keeps the existing `(8,2,5)->(2,5,8)` address
rotation. There is no temporary coefficient, pair-input, or pair-output array.

## Correctness and range

P1-H passes:

- 1,152 positive and 1,152 negative impulses;
- zero, alternating-bound, and 1,003 deterministic random `[-1,1]` inputs;
- raw representative equality against PROD0 for all 1,152 cells;
- canonicalized Official-times-four equality;
- generated per-cell signed-i16 bounds;
- in-place alias, input immutability, and output canaries; and
- ASan/UBSan with strict warnings.

Raw equality to PROD0 confirms that the arithmetic and lazy representative
policy did not change. No cosmetic reduction was inserted.

## Structural gate

The O3 linked-shape audit records:

| item | P1-H |
| --- | ---: |
| wrapper stack reservation | 2,336 bytes |
| retained split materialization | 2,304 bytes |
| dynamic top-split calls | 1 |
| dynamic pair-helper calls | 4 |
| scalar GT adapter calls | 0 |
| coefficient/pair staging bytes | 0 |
| helper calls / frame / vector stack accesses | 0 / 0 / 0 |
| wrapper/helper internal `vzeroupper` | 0 |
| Official transform/adapter calls | 0 |
| helper `.text` / `.rodata` alignment | 32 / 32 bytes |
| helper text | 7,635 bytes |

The wrapper's fixed public loops cause two static helper call sites and four
dynamic calls. The helper's only conditional selects the public terminal-pair
formation path. Both formation paths have identical opcode ledgers.

## Exact instruction attribution

Per complete forward producer, direct formation contains exactly 36 maps:

| formation class | dynamic count |
| --- | ---: |
| aligned split YMM loads | 144 |
| `vpshufd` | 144 |
| `vpermq` | 216 |
| `vperm2i128` | 72 |
| `vpshufb` | 72 |
| `vpunpcklqdq` + `vpunpckhqdq` | 72 |
| total direct routing | 576 |
| pre-twist Montgomery chains | 72 |
| pre-twist Montgomery instructions | 288 |

R2 first layer executes 24 radix-3 bodies, 72 reductions, and 72 transient-F0
stores. The common R2-second region is 148 instructions per helper execution;
the common D1 region is 370. The audit retains the full opcode ledger for all
four regions, so later changes cannot silently move work between categories.

## Decision

P1-H passes correctness, range, sanitizer, helper ABI, stack, alignment,
constant-time-control, and structural attribution gates. It answers the
implementation question: the PROD0 scalar/staging scaffold can be replaced by
a valid production-shaped AVX2 producer while retaining only the explicit
top-split materialization.

The next authorized checkpoint is a producer-only paired comparison against:

```text
Official poly_ntt -> Official-to-scale4-F0 adapter
```

Both sides must end at the same materialized scale-four F0 ABI and use the
same harness, compiler, pinning, input residency, and output consumption. KEM,
MA2 caller integration, top-split fusion, and routing superoptimization remain
unauthorized until that producer price is known.
