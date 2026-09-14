# P27 result — a consumer-oriented I16 basis survives the machine gate

P27 exhausts the 15 perfect matchings of the six existing main P8 records.  It
finds one unique matching that preserves inverse9's producer layout, turns the
main I16 output into full eight-channel banks, densely packs the tail, and lets
one bounded `TBL4` consumer produce natural ternary vectors.  Production is not
changed in this gate.

## Selected physical basis

Let `G(c,h)` contain component `c` and rows `4h..4h+3`.  Its four logical
channels are `j=3*row+c`.  The unique best matching is:

| Bank | First four lanes | Second four lanes | Reused P8 blocks |
|---|---|---|---|
| B0 | `G(0,0)`: 0,3,6,9 | `G(1,0)`: 1,4,7,10 | 0,2 |
| B1 | `G(0,1)`: 12,15,18,21 | `G(2,0)`: 2,5,8,11 | 1,4 |
| B2 | `G(1,1)`: 13,16,19,22 | `G(2,1)`: 14,17,20,23 | 3,5 |

Each paired main region consumes two current 16-Q blocks.  Once all 32 states
have been loaded, those same two blocks are dead and can be overwritten: one
holds the 16 top-0 output records and one holds the 16 top-1 records.  There is
no new P8 write/read pass and no larger scratch.

The tail still performs the same arithmetic on channels 24,25,26.  Its 96
useful values are compacted from 16 padded Q states into twelve dense Q records:
six for each top.  Four of the existing 112 scratch records become unused.

## Exact consumer route

The dense scratch contains exactly 108 Q records and all 864 `(top,t,row,
component)` coordinates once.  For each natural output Q, the selected basis
needs:

| Source records per output | Output Q records |
|---:|---:|
| 2 | 48 |
| 3 | 44 |
| 4 | 16 |

A natural-order walk needs at most four live source records.  Interval coloring
assigns them to consecutive `v0-v3`; each source Q is loaded and normalized
exactly once.  One output-specific byte mask then makes every output a legal
`tbl out.16b,{v0.16b-v3.16b},idx.16b`.  The generated 108 masks are checked
with unique coefficient tags, including every cross-`t` and tail boundary.

Normalization commutes with this pure permutation.  Exhaustive inputs
`[-4577,4577]` confirm that the existing raw-to-ternary arithmetic returns only
`{-1,0,1}` and preserves the residue modulo 3.  Final delivery is exactly 108
full-Q stores; there is no lane `ST3`, terminal `UMOV/STRH`, or P11 D-record
post-store route.

## Why top recombination stays after I16

The top-0 and top-1 terminal geometric steps are respectively
`theta^-9` and `theta^-45`.  Their ratio is `theta^-36`, which is not any power
of the order-16 root `omega16=theta^54`.  Therefore the differing terminal
phases cannot be moved through I16 as a cyclic column/lane rotation.  P27 keeps
both top inputs in the paired region and performs the existing exact terminal
scale and top CRT after I16.

Pairing independent channels changes no arithmetic node, root or scale.  The
closed chain remains:

```text
BaseMul R^-1 <=2497 -> inverse9 <=2617 -> I16 <=21397
                    -> raw R0 <=4577 -> ternary <=1
```

## Register and static-cost gates

The paired region has 32 coefficient Q states.  During stages it reserves three
vector auxiliaries, and during terminal reconstruction four.  Parking at most
four Q states in eight caller-saved GPRs keeps the vector peak at 32 without a
memory spill; `x5-x17` provides thirteen registers.  This is a machine budget,
not yet a physical allocation proof.

Current terminal materialization costs 1,728 instructions: one `UMOV` and one
`STRH` for each coefficient.  The candidate budget is:

| Work | Instructions |
|---|---:|
| Join two four-lane main results | 96 |
| Main full-Q stores | 96 |
| Dense-tail `TBL` | 12 |
| Tail full-Q stores | 12 |
| Total | **216** |

This removes 1,512 instructions.  Sharing stage/composite loads across the two
paired states saves another 210 loads.  After conservatively charging 192 GPR
parking instructions and 216 consumer `TBL4`/mask-load instructions, the model
still predicts **at least 1,314 fewer instructions**.  This is not a cycle
claim; cross-class moves and `TBL4` latency must be tested physically.

## Decision and P28

P27 passes as a machine-only candidate.  P28 will author the paired main I16,
dense tail, and consumer as symbolic regions, then require:

1. real `v0-v31`/GPR allocation with no stack spill;
2. exact tagged-layout, arithmetic, range and complete inverse oracle;
3. public wrapper, scratch wipe, alias, KAT and malformed-ciphertext checks;
4. same-boundary Inverse and Decaps PMU on Pi 5;
5. promotion only if complete Inverse and Decaps both improve.

The main risk is the cost and schedulability of GPR parking.  No production
kernel changes until P28 clears it.

