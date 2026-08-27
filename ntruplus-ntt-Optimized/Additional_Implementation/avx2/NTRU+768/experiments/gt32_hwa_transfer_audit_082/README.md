# NTRU+768 Hwa/1152 transfer audit (082)

This is a source-backed architecture audit of the current GT Clean NTRU+768
implementation.  It does not copy 1152 assembly, emit new assembly, modify GT
Clean, or make a benchmark claim.

The question is narrower:

> For each architecture principle learned from the 1152/Hwa work, does current
> 768 have the same producer/representation/consumer problem, has it already
> been tested, and what genuinely new gate remains?

Run the audit with:

```sh
make check
```

The generator fails if the selected GT Clean call graph or the relevant
NTT/Q24 macro shapes no longer match the audited source.

## Corrections to the proposed transfer model

Four corrections are required before transferring any conclusion:

1. Production `M` is **coefficient-plane SoA**, not persistent TILE4 AoS.
   TILE4 is the transform-friendly NTT32 register state.  `ntt_m` performs its
   S4/S5 work and retires each tile through `FR_PACKED_TO_PLANES` into M.
2. `ENC-R` currently materializes exactly one 1536-byte transform-domain
   polynomial, M.  Q24 and general B3 both read that same value.  There are not
   separate full M and P copies to delete.
3. `P` is the Keygen-specific placement.  It is not the name of every
   pack-friendly transient packet state.
4. Current GT Clean `DEC-R1` compares two M/e=0 values with native modular
   equality; it no longer serializes the derived value.  Older consumer maps
   that list a second Decap Q24 boundary are stale.

These corrections matter because they change the optimization budget.  A new
ENC-R terminal cannot delete the M stores: B3 still needs M.  Its direct credit
can only come from producing the required wire bytes before a later Q24 pass
reloads and transposes M.

## Current six-Forward graph

| Site | Selected output | Consumers | Transfer status |
|---|---|---|---|
| KG-F | P/F0/e0 | BaseInv J1, F0xJ1 BM, P Q24 into SK | Already caller-specialized |
| KG-G | P/F0/e0 | BaseInv J1, F0xJ1 BM | Already caller-specialized |
| ENC-R | M/e0 | M Q24 bytes for `hash_g`; later general B3 RHS | **Open dual-consumer seam** |
| ENC-M | M/e0 | lane-wise add to B3 result; final M Q24 | 032 and 068--071 already cover this seam deeply |
| DEC-M2 | M/e0 | subtract from decoded `c`; then general B3 | No wire consumer |
| DEC-R1 | M/e0 | native M-domain modular equality | Second serialization already deleted |

The machine-readable graph is
[`generated/forward_callsite_graph.json`](generated/forward_callsite_graph.json).

## What 768 has already absorbed

The persistent-representation lesson is already present, but in a more
caller-specific form than the proposal implied:

```text
shared frontend
  -> transform-friendly TILE4 NTT32 state
  -> M terminal for Encap/Decap
  -> P terminal for Keygen
```

The implementation also already has:

- direct M/P-to-WIRE12 Q24 codecs without Official-layout materialization;
- M-native general/scale B3 and inverse;
- P-native BaseInv J1, F0xJ1 multiplication, and SP1 serializer;
- typed Montgomery exponents;
- native-domain final Decap verification;
- Late-SoA evidence that moving a representation boundary can improve a
  complete producer/consumer region even when its producer gets slower.

Therefore a new “768 persistent AoS” campaign, another standalone
TILE4-to-wire serializer, or a universal P/M layout search would repeat work.

## What ENC-M experiments already closed

The final Encap seam has already been explored much more deeply than a simple
transfer checklist suggests:

- 032 fused message addition into B3 retirement and is the local executable
  champion for this seam.
- 068 removed the complete ordinary M sum materialization.  Both the shared
  core and 12-KiB inline forms lost because of transition/frontend delivery.
- 069 tried bounded clusters; total unique executed text remained about 12 KiB
  and still lost to 032.
- 070 found a uniform-Q24 M-prime with B3 table relabeling only, but current
  Forward could not land it without additional routing.
- 071 granted an affine output gauge independently to every block; eight
  blocks remained non-affine, closing the current terminal topology.

Thus the Hwa lesson does not reopen `B3 -> add(m) -> Q24` by itself.  That
family needs a genuinely smaller uniform executable body or a non-affine DAG
that replaces current S4/S5 movement.

## The distinct open gate: ENC-R dual terminal

Immediately before `FR_PACKED_TO_PLANES`, the selected M Forward still owns
TILE4-like packet registers.  Current execution then does:

```text
terminal TILE4 registers
  -> 12 x FR_PACKED_TO_PLANES
  -> 48 M stores

later M Q24
  -> 48 M loads
  -> 12 x four-plane transpose
  -> canonical reduction / 12-bit pack / wire stores
```

A real dual terminal would instead do:

```text
terminal TILE4 registers
  |-> unchanged M formation/stores for later B3
  `-> direct canonical WIRE12 fragments for hash_g
```

Source-level accounting gives the maximum direct deletion before charging any
new work:

| Item | Ceiling |
|---|---:|
| later M loads | 48 vector loads / 1536 bytes |
| later four-plane transpose | 12 x 12 = 144 instructions |
| total instruction deletion before new costs | 192 |
| M stores deletable | 0 |
| Q24 reduction or wire stores deletable | 0 |

This is a ceiling, not a speed prediction.  The hard problem is executable
shape.  Folding a roughly 5-KiB Q24 body into each Forward tile would repeat
the exact failure mechanism seen in 068/069.  A candidate must preserve a
compact shared packet body or otherwise prove that its unique executed text
does not explode.

This gate is distinct from 068--071: those experiments start at the final
general-B3/add/Q24 seam or search an M-prime terminal.  None executes a
Forward-r terminal that simultaneously retains M and emits the first wire
polynomial.

## Decision

The transfer audit selects one next experiment:

```text
ENC-R-DUAL-TERMINAL

control:
  frontend -> ntt_m -> M
  M -> current lazy Q24 -> WIRE12

candidate:
  same frontend and NTT32 arithmetic
  terminal -> identical M/e0
           -> byte-exact WIRE12
```

The first timing region must be the complete Forward plus wire output, not a
terminal microkernel.  It should use one fixed ELF, paired order, matched code
geometry, and report TSC, core cycles, instructions, loads/stores, port 5/11,
DSB/MITE, IDQ not-delivered, and active code bytes.  B3 and full Encap remain
outside the first gate.

Stop immediately if the candidate:

- creates a second full 1536-byte representation;
- duplicates the Q24 body per tile or otherwise produces giant unique text;
- fails to beat complete `Forward + current Q24`, even if its isolated
  terminal looks cheaper.

Only after an executable dual terminal exists should the old `e=1` scale gate
be recomputed.  CBD/SOTP direct deposit remains a secondary structural gate.
`d=6`/`d=8` remain unproved macroarchitecture wildcards and require a complete
ring/root/BaseMul/BaseInv/inverse proof before performance costing.

See [`generated/transfer_audit.json`](generated/transfer_audit.json) for the
machine-readable decision and exact static accounting.
