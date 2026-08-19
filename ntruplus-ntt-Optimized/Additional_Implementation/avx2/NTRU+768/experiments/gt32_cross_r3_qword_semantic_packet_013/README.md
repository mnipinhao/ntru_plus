# GT32-CROSS-R3-QWORD-SEMANTIC-PACKET-013

This generator-only gate asks whether a qword is the common semantic unit of
the selected Forward `GT_BLEND3` and the first NTT32 stage.  It does not modify
GT Clean and emits no assembly.

## Result

The qword hypothesis is algebraically real; it is not the 128-bit packet from
012 with a smaller name.

For qword semantic coordinate `q mod 3`, let `Cq` be the row permutation
implemented by `GT_BLEND3`, `D` the length-3 DFT, and `T` the diagonal twist.
The generator proves, for all three qword classes and an arbitrary diagonal
twist:

```text
D T Cq = Phiq Swap12 D T'q
```

Therefore the Forward can in principle:

1. delete `GT_BLEND3`;
2. relabel the three twist rows;
3. store DFT rows as current `k3 = [0,2,1]`;
4. carry `Phiq` as typed per-qword scale through NTT32.

Because the selected NTT32 is DIF, the frontend phase is indexed by its input
column `q`.  The exact `physical Q -> column_j` mapping from
`gt32_3x32_mapping.json` applies at the bit-reversed terminal, not before S1.
The executable 016 differential exposed and fixed this coordinate distinction.

## Full R2 closure

For a CT butterfly with stored input scales `dL,dH`, the existing high-arm
Montgomery chain uses the regenerated factor

```text
twiddle * dL / dH
```

and both outputs acquire scale `dL`.  Exact basis tests cover all 32 NTT32
basis vectors for each of the three packet rows.  After five stages every
scale is 1, so the terminal is exactly the current BM ABI.  No 128-bit L/H
join and no canonical R3 materialization is created.

Only S1 changes operation class:

```text
packet row 0: raw S1 remains raw
packet rows 1/2: weighted S1
two Top branches * two rows * four vector chains = 16 added Mont chains
```

Static Forward accounting is:

```text
-96 vpblendd
+64 weighted-S1 instructions
--------------------------------
-32 instructions / Forward
```

This is a real routing-class deletion, but it trades shuffles for 48 vector
multiply uops.  Static count is not performance evidence.

## Register gate

The weighted four-chain S1 is generated as SSA IR.  Exact interval-graph
coloring reports:

```text
peak/minimum: 14 YMM
spills:       0
```

This removes the 18-YMM blocker from 012.

## Representative range

The producer range is enumerated from the real `[-3,4]` input, raw Top split,
permuted twist and DFT3.  All five R2 stages use exhaustive fixed-factor
Montgomery image bounds plus triangle inequality.

```text
candidate producer maximum:       5220
candidate terminal maximum:      14358
current wide-raw control bound:   17724
frozen uniform B3 contract:       10788
```

The candidate is signed-int16 safe and is tighter than the current wide-raw
control, but it does not satisfy the older uniform `10788` consumer contract.
Consequently the semantic/routing gate passes while assembly eligibility does
not.  A joint B3 range proof is required; silently treating `14358` as
`10788` would be incorrect.

## Inverse

The inverse modular dual exists exactly by reversing the conjugated Forward
trajectory.  It would delete 96 `BLEND3_OUT` instructions and add the symmetric
16 weighted chains.  The selected inverse has a different representative
schedule, however, so modular equality alone is insufficient: its signed-i16
range must be generated before assembly.

If both open range contracts close, optimistic whole `2F+I` accounting is:

```text
-288 qword-routing instructions
+192 weighted-stage instructions
--------------------------------
 -96 static instructions
+48 Montgomery chains / +144 vector-multiply uops
```

## Decision

```text
semantic qword ownership:       pass
complete Forward R2 closure:    pass
zero-spill register coloring:   pass
frozen 10788 B3 range:          open/fail
inverse representative range:  open
assembly:                       not emitted
GT Clean:                       unchanged
```

Next gate: `GT32-CROSS-R3-QWORD-B3-INVERSE-RANGE-014`.

## Reproduction

```sh
make check
```

Primary artifact:

- `generated/qword_semantic_packet_gate.json`
