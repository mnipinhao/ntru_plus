# Checkpoint C: register-resident GT9x16 NTT16 island

Checkpoint C fixes one branch and one terminal coefficient. Its input and
output are nine YMM registers containing rows `R0..R8`; lane order remains the
selected physical bit-reversed order. The diagnostic ABI loads and stores nine
rows, while `GT9X16_NTT16_C{0,1}_BODY` in `asm/gt9x16_ntt16.inc` is the
register-only form intended for direct expansion into a future `poly_ntt_gt`.

## C0 selected structural port

C0 preserves the verified arithmetic and routing: the exact 27-`vpblendw`
shear; streaming distance-8 overwrite; distances 4/2/1 in registers; and
Official's `vpmullw`/`vpmulhw`/`vpmulhw(q)` Montgomery idiom with generated
constants. No stage data is materialized in memory.

The leaf has no calls, frame, stack reference, spill, or `vzeroupper`. It is
bit-exact with the retained C reference for 10,003 full-i16/boundary/random
inputs, in-place aliasing, canaries, and repeated-body checks.

## C1 split-representation experiment

C1 keeps the distance-4 plus/minus states and distance-2 PP/PM/MP/MM states
separate until the distance-1 boundary. This removes two intermediate routing
blends, but computes unused lanes on every split path. It passes the complete
C0 correctness gate but is rejected for selection: vector Montgomery
multiplies double from 36 to 72 and median leaf cost rises from 105.076 to
196.453 cycles. C1 remains a reproducible negative experiment.

## Diagnostic evidence

`results/ntt16-intel155h-20260820-002/ntt16-diagnostic.json` contains nine
fresh pinned launches, 201 samples per launch, GCC 15.2 `-O3 -mavx2`, on CPU 1
of an Intel Core Ultra 7 155H. These are repository-local diagnostics, not
SUPERCOP or promotion evidence.

| Variant | Median cycles/island |
| --- | ---: |
| retained C reference | 289.533 |
| C0 leaf, nine loads + nine stores | 105.076 |
| C0 arithmetic body replay | 101.647 |
| C1 split leaf, nine loads + nine stores | 196.453 |

| Static item | C0 | C1 |
| --- | ---: | ---: |
| instructions | 510 | 996 |
| `.text` bytes | 2,364 | 4,578 |
| `vpblendw` | 36 (27 shear) | 63 (27 shear) |
| `vpblendd` | 18 | 27 |
| vector Montgomery multiplies | 36 | 72 |
| input row loads / output row stores | 9 / 9 | 9 / 9 |
| designed peak-live YMM | 15 | 16 |
| calls / `vzeroupper` / frame / spills | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |

There is no 40–50-cycle hard gate. C0 is selected for direct expansion into a
two-layer radix-3 NTT9 baseline; only the later full pipeline is decisive.
