# P34 result — select consumer-closed terminal reset pruning

## Decision

P34 completes the decision gate without changing production.  It rejects a
third materialized or batched I16 design and selects **P35: KEM-only terminal
reset pruning** for physical assembly, Slothy and Pi 5 validation.

The selected DAG preserves the P8 scratch layout, every natural scalar store,
the 1792-byte scratch allocation and wipe, and the existing P8 raw-to-ternary
consumer.  It only removes terminal `SQRDMULH; MLS` representative-reset
chains proven unnecessary at that consumer boundary.

## Fresh production stage profile

P34 reused the exact current production library already present on the Pi 5
(SHA-256 `7e71af80...aff0`) and the hash-bound P21 stage profiler.  The current
main and tail assembly hashes are byte-identical to the sources from which its
diagnostic controls were built.  Six balanced processes produced 258 samples
per boundary on Cortex-A76 core 3; the machine stayed unthrottled.

| Production boundary | Net cycles | Instructions | IPC | Reads | Writes |
|---|---:|---:|---:|---:|---:|
| inverse9 ×12 | 1682.172 | 2381 | 1.415 | 344.000 | 296.985 |
| main I16 ×6 | **2117.821** | **4070** | 1.922 | 520.000 | 770.000 |
| tail I16 | 341.453 | 611 | 1.789 | 88.000 | 95.985 |
| raw-to-ternary | 430.156 | 951 | 2.211 | 109.016 | 107.969 |
| complete Inverse-to-ternary | **4888.141** | **8336** | 1.705 | 1045.016 | 1398.016 |

This reproduces the current bottleneck ordering.  Main I16 remains the largest
individual stage, while raw-to-ternary has high IPC and is not selected for a
new routing/materialization design.

## Exact consumer acceptance domain

P8 does not canonicalize modulo 3457.  It only needs the residue modulo 3.  For
an input outside the centered interval it conditionally subtracts or adds one
because `3457 = 1 (mod 3)`, then performs the fixed division-by-three step.
Exhausting all signed-int16 inputs proves that its largest contiguous symmetric
correct interval is exactly:

```text
[-5185, 5185] = [-(q + floor(q/2)), q + floor(q/2)].
```

Both endpoints pass.  `-5186` and `5186` are explicit first-failure witnesses,
so the limit is not merely conservative.

## Reset search

The exact P7-C0/P13 interval DAG was re-evaluated for every row, column and
low/high terminal output before the six historical `b=1` resets.

| Producer | Old reset chains | Required by P8 | Largest selected input |
|---|---:|---:|---:|
| each main I16 call | 6 | only high column 8 | 5143; retained column becomes 1821 |
| tail I16 call | 6 | none | 5028 |

Main high column 8 reaches 5278, so that one reset cannot be removed under the
current producer contract.  The other main outputs peak at 5143 and the tail
at 5028, both within P8's exact 5185 interval.

Across six main calls and one tail call, the selected successor deletes:

```text
6 calls × 5 chains × 2 instructions = 60
1 tail  × 6 chains × 2 instructions = 12
                                             ----
                                               72 instructions / Decaps
```

It adds zero loads, stores, routes or scratch bytes.  Each deletion also removes
a quotient temporary and a serial dependency immediately before output
extraction.  This is the required qualitative difference from P32/P33, which
reduced table loads but introduced a preterminal memory boundary and lost IPC.

## Scope and next gate

The wider raw representatives are valid only for the production KEM
Inverse-to-ternary consumer.  The centered general Inverse keeps the existing
reset-complete helpers.  P35 must therefore use distinct KEM-only main/tail
symbols or an equivalently explicit wrapper selection; it must not silently
widen the centered API.

P35 promotion gates are exact range/oracle, physical no-spill allocation,
fixed-allocation timing, inverse alias/AAPCS/scratch wipe, KAT and malformed
ciphertext behavior, followed by paired complete-Inverse and Decaps PMU.  A
72-instruction reduction alone is not a performance claim.
