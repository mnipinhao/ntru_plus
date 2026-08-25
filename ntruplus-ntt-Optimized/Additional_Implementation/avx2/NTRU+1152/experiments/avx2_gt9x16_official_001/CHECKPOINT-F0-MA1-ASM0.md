# Checkpoint F0-MA1-ASM0

## Outcome

The fixed `(branch=0,p=0)` F0-native MA1 correctness island passes. It is an
architecture control, not a benchmark candidate: no timing was run and no
performance conclusion is authorized. The next gate is ASM1 over all nine
serializer chunks, with exactly two semantic tiles scheduled per chunk.

The tested boundary is:

```text
F0(r) B0/P0 tile + F0(m) B0/P0 tile + full resident Official h
-> exact resident-h projection
-> MA1 weighted schoolbook
-> S0 inv4 finalization
-> four canonical semantic coefficient planes
```

There is no standalone canonicalization pass. ASM0 does use its non-aliasing
output as correctness-first scratch for four projected `h` vectors; the four
stores and four reloads are included in the static audit and are not claimed
free.

## Correctness and scale

An independent C quartic schoolbook oracle checks 1,003 zero, boundary, and
random cases coefficient by coefficient. Inputs use the proved wide F0
envelope, resident `h` uses `[0,3456]`, and the test checks output canaries,
input immutability, and the declared 32-byte pointer alignment.

The exact Montgomery ledger for one tile is:

| Region | Chains |
| --- | ---: |
| Lift four R^0 resident-`h` vectors with R2 | 4 |
| Sixteen schoolbook products | 16 |
| Four wrapped-term lambda products | 4 |
| MA1 core | 20 |
| Four S0 `inv4` finalizers | 4 |
| Total | 28 |

Thus the output is R^0 at transform scale 1. The common four-chain `h` lift
was implicit in the earlier schedule and is now explicit. It does not change
MA1 versus MA3's seven-chain core difference.

Exact differential testing also corrected the resident-`h` projection. B0/P0
needs a lane-7 exchange across the two 128-bit halves after the word shuffle;
the generated contract records this physical mapping.

## Machine routing and ABI

The earlier `792` MA1 number counts semantic route slots, not executed AVX2
shuffle instructions. For this fixed tile, the linked object classifies:

| Class | Meaning | Executed instructions |
| --- | --- | ---: |
| R0 | address/load-order choice | 0 |
| R1 | native register reuse | 0 |
| R2 resident-`h` projection | permute/shuffle/blend | 20 |
| R2 bilinear operand formation | broadcasts and pair formation | 24 |
| R2 semantic output formation | final pair extraction | 4 |
| R2 total | actual routing instructions | 48 |

The leaf uses YMM0--YMM12, has no call, conditional branch, frame, stack
reference, spill, or `vzeroupper`, and preserves a strict non-alias contract
for output versus `r`, `m`, and `h`. This one-tile count is diagnostic
structure only; ASM1 must be rescheduled before any whole-caller route total is
reported.

## Alignment audit

The source uses `.p2align 5` for the entry and generated YMM constants in an
aligned read-only section. All declared aligned caller-vector offsets are
multiples of 32. In the checked linked test ELF:

```text
symbol address:                 8672
symbol mod 32 / mod 64:         0 / 32
caller address:                 4288
symbol distance from caller:    4384 bytes
constant-table distance:        3616 bytes
object .text / .rodata align:   32 / 32
linked .text / .rodata align:   64 / 32
symbol size:                    2462 bytes
```

These values describe this correctness ELF only. ASM1, a SUPERCOP-derived
measure ELF, and any later installed KEM ELF must each repeat the placement
audit.

## Artifacts and next gate

- `asm/f0_ma1_asm0.S`
- `tools/generate_f0_ma1_asm0.py`
- `generated/f0-ma1-asm0.json`
- `generated/f0-ma1-asm0-constants.inc`
- `generated/f0-ma1-asm0.h`
- `tests/test_f0_ma1_asm0.c`
- `tools/audit_f0_ma1_asm0.py`
- `generated/f0-ma1-asm0-audit.json`
- `tests/test_f0_ma1_asm0_evidence.py`

Next implement ASM1 as a caller-shaped nine-chunk schedule. Only after its
full correctness, range, ABI, serializer, and alignment gates pass may it be
priced with the SUPERCOP-derived methodology. MA3 remains second; MA2 remains
deferred.
