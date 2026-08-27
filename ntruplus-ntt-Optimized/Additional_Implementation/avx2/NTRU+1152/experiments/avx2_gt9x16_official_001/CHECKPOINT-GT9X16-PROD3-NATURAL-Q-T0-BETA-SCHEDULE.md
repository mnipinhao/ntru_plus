# GT9X16-PROD3-NATURAL-Q-T0-BETA-SCHEDULE

## Scope

This checkpoint lowers the selected `T0-BETA-TO-RADIX2` map to an exact
machine schedule and a 32-byte-aligned constant include. It does not implement
or time ASM. Natural-Q, top split, paper-R2, D8/D4/D2/D1 order, transform scale
4, and Montgomery exponent 0 remain frozen.

The candidate performs a raw load for the `h=0` row and one `alpha_h`
Montgomery chain for each of the other eight rows in every Q-block. The
existing 144 radix-2 chain positions remain unchanged. Each position instead
uses the branch-specific constant

```text
combined = w * g^(offset * distance) mod q.
```

There is no runtime branch, table lookup, index, packing change, or new
register temporary. The two branches are straight-line code regions that
reference separate RIP-relative labels.

## Montgomery representation

Every alpha and combined semantic constant is lowered as

```text
zeta = centered(constant * 2^16 mod q)
qinv = signed16(zeta * 12929).
```

The generator exhaustively replays all 65,536 signed-i16 inputs for all 16
nontrivial alpha occurrences and all 270 branch/row/stage combined-twiddle
occurrences: 18,743,296 exact checks. Every machine chain remains congruent to
the intended semantic multiplication, with no R-exponent or scale drift.

## Chain ledger

| per forward | current | candidate | delta |
| --- | ---: | ---: | ---: |
| T0 / alpha normalization | 72 | 64 | -8 |
| NTT9 | 80 | 80 | 0 |
| NTT16 | 144 | 144 | 0 |
| **total** | **296** | **288** | **-8** |

The two Encap forwards therefore remove 16 Montgomery chains. Each deleted
chain consists of one `vpmullw`, two `vpmulhw`, and one `vpsubw`, giving the
exact schedule delta of 32 instructions per forward.

## Constant-memory operand ledger

| per forward | current | candidate | delta |
| --- | ---: | ---: | ---: |
| T0 / alpha memory-form operands | 144 | 128 | -16 |
| NTT16 memory-form operands | 288 | 288 | 0 |
| other unchanged operands | 234 | 234 | 0 |
| **total** | **666** | **650** | **-16** |

No explicit constant load or table-selection instruction is added. The
radix-2 operands stay in the same memory-form instruction positions. This
closes the main hidden-movement concern: the chain reduction is not repaid by
runtime constant traffic.

The static constant table does grow. Current T0 plus shared radix-2 tables use
270 YMM vectors (8,640 bytes). The candidate uses 32 alpha vectors plus 252
branch-specific radix-2 vectors, or 284 vectors (9,088 bytes). The exact
penalty is 14 vectors / 448 read-only bytes. All 284 vector labels use
`.p2align 5`; no padding is inserted into code.

## Predicted linked machine shape

Relative to the frozen linked Natural-Q producer, the exact schedule predicts:

| item | current | candidate | delta |
| --- | ---: | ---: | ---: |
| instructions | 2819 | 2787 | -32 |
| `vpmullw` | 368 | 360 | -8 |
| `vpmulhw` | 592 | 576 | -16 |
| routing | 432 | 432 | 0 |
| Barrett vectors | 72 | 72 | 0 |
| data loads/stores | 144 / 144 | 144 / 144 | 0 / 0 |
| peak live YMM upper bound | 16 | 16 | 0 |

These are schedule predictions, not linked-candidate audit results. Exact text
size remains unknown until ASM exists.

## Range gate

The schedule rechecks all 296 interval nodes recorded across alpha input,
both paper-R2 layers, and every radix-2 stage. Every pre-operation remains in
signed i16. The final candidate envelope is `[-21333, 21333]`, versus
`[-20751, 20753]` for the control. No range repair or extra reduction is
introduced.

## Decision

The schedule gate passes: all eight chains per forward really disappear,
runtime constant operands decrease by 16, and routing, data movement,
reductions, scratch, and peak register pressure do not increase. The 448-byte
rodata growth is the only identified debt.

A namespaced ASM correctness and linked-audit checkpoint is authorized next.
That checkpoint must confirm the predicted instruction/operand ledger, zero
spill, alignment, representative behavior, and actual text/rodata size before
any timing is authorized. Benchmark and native KEM remain forbidden.

## Evidence

- `generated/gt9x16-prod3-natural-q-t0-beta-schedule.json`
- `generated/gt9x16-prod3-natural-q-t0-beta-constants.inc`
- `tools/generate_gt9x16_prod3_t0_beta_schedule.py`
- `tests/test_gt9x16_prod3_t0_beta_schedule.py`
