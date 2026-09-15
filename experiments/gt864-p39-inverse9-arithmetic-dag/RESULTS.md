# P39 — Inverse9 arithmetic-DAG gate

Date: 2026-09-16. Baseline: production P35 at `3c6fe3c7` (the inverse9 body is
the promoted P7-C1 body). Decision: **reject before Slothy; production stays
unchanged**.

## Outcome

The exact production region is 184 instructions per block and is called 12
times per Inverse. Its 19 Algorithm-10 products are:

| Class | Products/block | Instructions/block |
|---|---:|---:|
| six one-product B3 nodes | 6 | 18 |
| eta corrections | 4 | 12 |
| terminal twist/scale | 9 | 27 |
| total | 19 | 57 |

P39 required a real reduction of at least one complete `mul; sqrdmulh; mls`
triple per block, hence 36 instructions per complete Inverse. No rewrite under
the frozen P35 I16 and memory ABI reaches that threshold. The best exact lead
would save only one instruction per block (12 per Inverse), so no candidate
assembly, Slothy run, Pi 5 run or production edit was made.

## Machine checks

- The active source hash is bound in `results.json`; its operation histogram is
  19 each of `MUL`, `SQRDMULH`, and `MLS`.
- All 288 physical terminal linear maps (2 tops × 16 columns × 9 rows) equal
  the independent P7-C0 model.
- All 64 choices of the two known one-product B3 orientations retain 19
  products/block. They only move the closed range between the already-known
  2596/2617 I9-output families.
- None of the 36 terminal constant vectors is the identity vector. Four are
  uniform, exactly the four `(top, eight-column-block, s=0)` vectors.
- All 32 scalar terminal contexts satisfy

  ```text
  k(top,column,s) = -384 * lambda(top,column)^s mod 3457
  ```

  Here `-384 = 9^-1 mod 3457`. This proves the terminal table is an inverse-9
  normalization times a geometric phase; it does not by itself make either
  operation free.

## Why the apparent `s=0` deletion fails the gate

For `s=0`, every terminal multiplier is `-384`, independent of top and column.
It commutes algebraically through the following linear NTT16 and can ultimately
be composed with its terminal table. But deleting the inverse9 product exposes
the total of nine inputs:

```text
abs(input) <= 2497
abs(unscaled row-0) <= 9 * 2497 = 22473
first legal I16 pair can reach 44946 > 32767
```

So the unchanged int16 P35 I16 cannot consume that representation. Performing
a `b=1` representative reset first is safe and takes `SQRDMULH; MLS`; composing
`-384` into the later table then changes three instructions to two. The real
saving is only **1 instruction/block**, not the required 3.

The same distinction explains why modular equality is insufficient: moving a
factor preserves roots and scale but may destroy the representative range at
the very next 16-bit add.

## Other rejected narrow rewrites

- The six B3 products are already the one-product form. Removing one changes
  the rank/nontrivial root action of that B3.
- The four eta constants are nonidentity roots and feed add/sub fanout before
  the next product; there is no adjacent product pair to collapse into one
  composite constant.
- The remaining eight terminal vectors are lane-varying. Their geometric phase
  cannot be deleted while retaining both the current inverse9 output coordinates
  and the frozen P35 I16 consumer.
- Reordering the 64 B3 orientations cannot change the product count.

This is a bounded search of the current radix-3 topology and its known
orientations, not a proof that no arbitrary 9-point linear circuit can ever use
fewer multiplications.

## Next gate

P40 should explicitly widen the contract to the **inverse9 → I16 phase ABI**.
It must machine-prove whether `lambda^s` can become row-dependent NTT16 output
rotation/table ordering while maintaining safe representatives, P35's natural
coefficient result, and no new memory pass. Static success must be at least 36
net instructions/Inverse after all resets, routing and wrapper changes. Only
then create symbolic assembly and run `/Users/chenpinhao/slothy`, followed by
paired Pi 5 Inverse-to-ternary and Decaps timing.

Reproduce:

```sh
python3 experiments/gt864-p39-inverse9-arithmetic-dag/audit.py
```
