# P3B31 — Pass-2 static cost and fixed-multiplication audit

Status: PASS for static provenance/classification. Not a stage-cycle benchmark,
not an elimination proof. P3B29 remains the selected small-input Forward.
No kernel arithmetic, allocation, schedule, or production file changed.

## Exact selected source

P3B29 raw/gt864_forward_six_bank.S (original T1 allocation), SHA-256:
`1cf9efd21be0774ee094f4683b7cf7f0db1670d7f1e48ab997098496d16a84d3`.
The analyzer follows constant-register overwrites and x2/x3 table increments
through the actual scheduled helper. It resolves all 90 MUL operands for each
top, rather than reading obsolete symbolic comments. The three components per
top reuse the same constant sequence, giving 540 vector multiplications total.

## Static cost, not independent cycle attribution

| Logical owner | Instructions per bank | Six banks |
|---|---:|---:|
| Tail NTT16 (loads/twist/butterflies/permutation) | 47 | 282 |
| Main NTT16 (loads/twist/butterflies) | 233 | 1398 |
| Two 8x8 transposes | 48 | 288 |
| Two NTT9 blocks including constants | 224 | 1344 |
| Return | 1 | 6 |
| Total helper | 553 | 3318 |

Actual mnemonic histogram per bank: LDP 1, LDR 69, MUL 90, SQRDMULH 90,
MLS 90, SUB 84, ADD 72, TRN1 27, TRN2 27, TBL 2, RET 1.
Six-bank driver adds 153 instructions (including its output stores); Pass-2
totals 3471. T1 tail preparation outside Pass-2 adds another 77 instructions.

Logical groups overlap in scheduled instruction order. Their cycles cannot be
obtained by summing isolated timings or multiplying instruction counts by a
latency. No current stage-cycle fractions are claimed. In particular, main
NTT16 and NTT9 are similarly large static owners; NTT9 is not the sole target.

## Multiplication ledger

| Kind | Per bank | Complete Forward |
|---|---:|---:|
| Tail NTT16 twist + butterfly | 6 | 36 |
| Main NTT16 twist + butterfly | 48 | 288 |
| NTT9 input twists | 16 | 96 |
| One-product B3 | 12 | 72 |
| eta corrections | 8 | 48 |
| Total | 90 | 540 |

Each NTT9 block is 8 input twists + 6 B3 products + 4 eta products.

| Actual vector constant class | Per bank | Complete Forward |
|---|---:|---:|
| All eight lanes b=1 | 17 | 102 |
| Some lanes b=1, others nonidentity | 4 | 24 |
| No b=1 lanes | 69 | 414 |

The 17 all-one cases belong to NTT16: 16 main and one tail. Four mixed cases
belong to tail NTT16. NTT9 has no all-one vector opportunity in these tables.
Full per-top lists, source lines and all eight constants are emitted as
build/multiplications.csv. There are 180 rows; multiply each top's rows by its
three components when forming complete-Forward counts.

## Necessity is not settled by this classification

For b=1, bprime=9, the actual operation is

```
r = a - floor((9*a + 16384)/32768)*3457
```

It is bitwise the identity exactly on [-1820,1820], verified over all 65,536
signed halfwords. At a=2000 it returns -1457. A reachable raw-top example is
low=0, high=3: alpha=-2166; multiplication by one changes it to 1291.

Therefore:

- 102 vector operations are mathematically identity modulo q, but their entire
  three-instruction reduction cannot yet be deleted under the current proof.
- Nonidentity products are not proven globally indispensable: fusion or
  representation changes may absorb them. They are merely not local no-ops.
- Mixed-lane identities cannot erase a whole vector multiplication; exploiting
  them may require masks/routing and can cost more than it saves.
- Replacing MUL-by-one with an alias/move while retaining SQRDMULH/MLS is a
  separate lowering/RA question; no benefit is assumed.

The next proof should first inspect the all-one input-twist and earliest
butterfly nodes. Track incoming intervals and exact representative changes,
then propagate each proposed deletion through all later NTT16 and one-product
NTT9 nodes and the existing M5C/D1/M5E consumers. A successful final-output
congruence check alone does not establish int16 intermediate safety.

## Memory, constants, and producer-consumer follow-up

- Per bank: 21 NTT16 constant q loads + 32 NTT9 constant q loads.
- The same top's tables are reloaded for its three components; this is real
  repeated traffic, not proof that retaining all constants in registers wins.
- Main coefficients already have two load/store passes; s=8 tail has three
  because T1 performs an extra memory transpose.
- Direct bank-major production remains an untested alternative, not an omitted
  winner. Compare producer+consumer together, including changed stores.
- Two main 8x8 transposes cost 48 TRNs per bank, but a replacement must preserve
  NTT9 lane meaning and account for extra constants, live state, and routing.
- Keep original allocation and old schedule-only as controls. Do not schedule
  a new candidate before its arithmetic/layout proof and ledger are closed.

## Decision

Next gate: **NTT16 identity-reduction elimination search**, starting with the
17 all-one vectors per bank, with no ISA or layout change. Require at least one
actual reduction deletion with complete downstream range closure before a new
assembly/PMU candidate. This is prioritization, not a claim that any of the 102
operations can already be deleted or that 306 instructions will be saved.

Reproduce: `python3 audit.py`. Only audit artifacts are written under build/.
No Pi5 or Slothy run is needed for this static gate. Existing total Forward
timing remains P3B29; separate stage cycles remain unmeasured.
