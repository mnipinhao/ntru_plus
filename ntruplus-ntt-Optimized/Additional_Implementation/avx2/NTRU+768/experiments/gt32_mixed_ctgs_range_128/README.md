# GT32 complete NTT32 mixed CT/GS range gate (128)

This experiment searches the complete five-stage production NTT32 rather than
only its S4/S5 suffix.  The algebra, input/output ordering, `q=3457`, root
convention, TILE4 layout, and current BaseMul input contract remain fixed.

The executable search unit is one AVX2 butterfly packet.  Each NTT32 stage has
four packets, and each packet contains four logical-Q butterflies (with all
four quartic coefficients carried in SIMD lanes), for 20 independently chosen
CT/GS modes in total.  A packet must use one mode uniformly; scalar lane masks
that would require extra blend/repair work are intentionally outside this
zero-spill lowering class.

For every mode assignment the generator solves the intermediate diagonal
gauges implied by

```text
CT: (a,b) -> (a + w b, a - w b)
GS: (a,b) -> (a + b, f(a - b))
```

while pinning both the public input and output gauges to one.  It then derives
the actual per-lane factors, propagates exact fixed-Montgomery interval bounds,
and requires:

- no signed-16-bit add/sub overflow;
- the same NTT32 value and output order modulo q;
- final `|word| <= 10788`, the existing B3 input contract;
- no standalone S2 identity-centering checkpoint.

The search also tags selective-GS schedules as split-radix-inspired.  This is
a range/scheduling analogy on the existing radix-2 graph, not a claim that a
new split-radix arithmetic factorization has already been implemented.

## Result

`make check` exhausts all `2^20 = 1,048,576` packet-mode assignments.  Only
5,504 assignments admit diagonal gauges with the current input and output
contracts.  The generator performs a 32-way coordinate search over every free
gauge component and uses 16 deterministic restarts for the requested
split-radix-inspired selective-GS class.

No searched realization preserves both signed-int16 safety and the current B3
input bound:

| class | exact topologies | B3-safe without checkpoint | best terminal bound |
|---|---:|---:|---:|
| no free gauge (gauge search exhaustive) | 36 | 0 | 17608 |
| selective-GS / split-radix-inspired | 120 | 0 | 17388 |
| all exact packet-mode topologies | 5504 | 0 | 17388 |

The closest schedule is CT everywhere except packet 0 of S3, which is GS.  Its
conservative stage maxima are:

```text
S1  3456
S2  6912
S3 13824
S4 15579
S5 17388
```

It uses 14 Montgomery-factor packets and is signed-int16 safe, but its terminal
bound exceeds the B3 contract by 6,600.  Adding a terminal center would merely
move the deleted S2 checkpoint to the NTT32 output.  The scalar oracle verifies
the closest eight synthesized networks on 549 impulse, structured, centered,
and modulo-q cases; all produce the same logical NTT32 result and order modulo
q.

For comparison, the generator independently reproduces the selected production
range schedule:

```text
               S1    S2    S3    S4     S5
current max  3456  5274  7029  8866  10788
```

That schedule uses two S2 identity-center packets plus fourteen ordinary
Montgomery-factor packets.  The center layer is therefore doing real range
work, not merely repairing a historical representation choice.

## Decision

`NO_ASM_CANDIDATE`: the explicit continuation condition was not met, so this
experiment intentionally emits no assembly and runs no same-ELF benchmark.
Benchmarking a candidate with a hidden terminal reduction would not answer the
requested question.

This closes only the tested class: current radix-2 graph, current TILE4 packet
uniformity, omega32 diagonal gauges, unchanged `e=0` output, and unchanged B3
bound.  The free-gauge search above is deterministic coordinate optimization,
not an exhaustive `32^k` proof for topologies with free components.  A genuine
split-radix graph, a B3 consumer that natively accepts `|x|>10788`, or an exact
solver finding a materially better nonzero gauge is a valid reopen premise.

The generated [`search.json`](generated/search.json) is the detailed evidence
artifact.
