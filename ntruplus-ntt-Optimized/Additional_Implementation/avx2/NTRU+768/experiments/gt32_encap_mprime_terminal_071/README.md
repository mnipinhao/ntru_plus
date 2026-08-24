# GT32 Encap M-prime terminal synthesis gate (071)

This generator-only experiment fixes the M-prime consumer ABI found by 070
and asks whether the selected pair-packed Forward terminal can naturally emit
it. GT Clean is not modified and no assembly candidate is generated.

## Fixed target

070 already closed the consumer side:

```text
M-prime block order = [0,1,9,8,4,5,11,10,6,7,3,2]
B3                  = current arithmetic + lambda table relabel
Q24                 = one uniform four-packet body, repeated 12 times
```

071 therefore does not search another Q24 template or B3 representation. It
searches only the producer question:

```text
fixed post-S3 state
  -> equivalent S4/S5 physical output gauge
  -> M-prime-aware current plane deposit
  -> fixed M-prime
```

## Exact bounded search

The selected source topology is audited directly from `ntt_m.s`:

- four `FR_MONT_HALF_PAIR` calls per tile;
- four `FR_MONT_QWORD_PACKED` calls per tile;
- two `FR_PACKED_TO_PLANES` calls per tile;
- four S4 `vperm2i128` instructions per pair;
- one low and one high S5 qword unpack per pair;
- four `vpshufb`, four dword unpacks and four qword unpacks per deposit.

Lane-wise Montgomery and butterfly arithmetic cannot permute lanes. Source
reversal, sum/difference destination exchange, pair ordering, unpack/rejoin
ordering, qword/half ownership and store relabeling all induce
degree-independent affine permutations of the four leaf-lane bits.

The generator deliberately grants **every** member of `AGL(4,2)` independently
to every block:

```text
|GL(4,2)| * 16 = 20,160 * 16 = 322,560 gauges/block
```

This is more permissive than the actual shared six-iteration Forward loop.
For each gauge, the four existing deposit `vpshufb` masks are also allowed to
change freely while the current dword/qword deposit topology remains fixed.
Thus failure in this family is not caused by choosing too few sum/diff or
pair-order variants.

## Permutation classification

The twelve target blocks contain five raw lane permutations:

| class | blocks | algebraic degrees of four output bits | zero-extra? |
|---:|---:|---|---|
| 0 | 4 | `[1,1,1,1]` | yes |
| 1 | 2 | `[1,1,3,2]` | no |
| 2 | 2 | `[1,1,2,1]` | no |
| 3 | 3 | `[1,1,3,2]` | no |
| 4 | 1 | `[1,1,2,1]` | no |

Only class 0 is affine. It is exactly the four blocks that 070 could already
absorb through deposit-mask relabeling. The other eight remain nonzero under
all 322,560 independently granted affine gauges.

The exact block/cycle classification is stored in
`generated/permutation_classes.csv` and `generated/terminal_search.json`.

## Movement lower bound

Every nonzero block has four independent coefficient-plane YMM outputs. An
AVX2 movement or blend instruction has one YMM destination, so even granting
an unrealistically cheap one-instruction route to every affected plane gives:

```text
8 nonzero blocks * 4 degree planes = at least 32 extra vector ops/Forward
```

This is intentionally optimistic. A secondary route score is 52 per Forward,
where every unresolved "more than one" route is assigned a cost of exactly
two. That is only a selection score: it is neither an emitted 52-operation
network nor a universal lower bound over arbitrary non-affine AVX2 DAGs.

The predeclared eligibility tiers were:

```text
T0 FREE       delta <= 0
T1 NEAR_FREE  0 < delta <= 16 vector ops/Forward
T2 EXPENSIVE  delta > 16
```

071 is therefore `T2_EXPENSIVE` even at its optimistic lower bound. No 072 ASM
gate is opened.

## Interpretation and scope

This closes the proposed current-topology reopen premise:

```text
current pair-packed S4/S5 output gauges
  + current plane-deposit topology/mask relabel
  -> fixed 070 M-prime
```

It does not prove that every non-affine terminal DAG is impossible. A future
reopen needs a concrete network in which a non-affine blend/route **replaces**
mode-critical current movement at no extra cost. Adding a post-terminal
permutation, enumerating another affine gauge, changing Q24 again, or changing
B3 does not meet that condition.

## Reproduce

```sh
make check
```

This regenerates the complete 322,560-gauge search, validates the source
topology and checks the committed JSON/CSV evidence byte-for-byte.
