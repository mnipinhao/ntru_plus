# ENCAP MA2 ciphertext egress H4-M2

> **Post-ASM correction (H4-M3):** the exact linked ciphertext differential
> rejected M2's same-lane cross-plane pair-locality model.  In the frozen
> Natural-Q ABI, MA2 vector 20 lane 15 is Official coefficient 0, vector 21
> lane 15 is coefficient 16, while coefficient 1 is vector 20 lane 14.
> Therefore the four-instruction `vpunpckwd(A,B)` primitive below does not
> form Official 12-bit serializer pairs.  The 1502-instruction selection is
> retained as historical schedule evidence, not as an authorized benchmark
> candidate.  See `CHECKPOINT-ENCAP-MA2-CT-EGRESS-H4-M3.md`.

## Scope

This checkpoint starts at each live scale-1 `H3_TERMINAL_C` value and lowers
the complete path to the exact 1728 ciphertext bytes.  It compares the four
H4-M1 presentation profiles under two egress families:

- direct-wire, with the `0x1c7` tile order and a required overlap-safe final
  copy; and
- scratch-native, with packed-wire-ish (S0), pair32 (S1), and canonical-i16
  (S2) internal ABIs.

MA2 arithmetic, Natural-Q input ownership, scale, Barrett range, validation,
and ciphertext semantics remain frozen.  This is generated schedule evidence;
no H4 assembly or benchmark exists yet.

## Direct two-input pair pack

M1 proves every serializer pair is in the same lane of two adjacent terminal
vectors.  M2 therefore does not create a pair-vector intermediate.  After the
two vectors have been Barrett-reduced and sign-canonicalized, sixteen exact
24-bit values are formed in two dword vectors:

```text
vpunpcklwd pair_lo, A, B
vpunpckhwd pair_hi, A, B
vpmaddwd   pair_lo, pair_lo, [1,4096]
vpmaddwd   pair_hi, pair_hi, [1,4096]
```

For `0 <= A,B <= 3456`, `A + 4096*B` is an exact signed-dword operation and
equals `A | (B << 12)`.  There is no pre-pair route.  The two unpacks are part
of the arithmetic pack primitive, not a recovery of Official coefficient
presentation.

## Linked H3 liveness correction

The semantic M1 lower bound is one pending YMM, but the linked H3 instruction
stream must decide whether that YMM can actually remain live.  Exact def/use
replay gives:

| adjacent terminal pairs | realization |
| ---: | --- |
| 27 | retain the first canonical endpoint in a free YMM |
| 9 | one localized 32-byte store and reload |

The nine seams are the first plane pair of each H3 decode block.  The existing
arithmetic reaches 16/16 live YMM between those two hooks, so no physical
register is free across the interval.  This does not create a compiler spill
or frame scratch; it is an explicit endpoint materialization.  All lowered
terminal schedules stay at or below 16 YMM.

This is the main correction to M1: `Y_buffer_min = 1` is a semantic lower
bound, not proof that the current linked H3 schedule can retain that buffer at
all 36 intervals.

## Exact final egress network

For each 64-coefficient tile, four pair32 vectors are sorted into their
four-pair parity chunks.  Two parity companions use:

```text
vpunpckldq
vpunpckhdq
vperm2i128 0x20
vperm2i128 0x31
```

twice per tile, producing four consecutive eight-pair wire groups.  Dense
24-bit compaction then uses an exact 27-route construction per tile:

```text
4 vpshufb
4 vextracti128
16 byte shifts / ORs
3 vinserti128
```

It emits three 32-byte vectors, or 96 exact wire bytes, per tile.  The emitted
masks and operation sequence are recorded in
`generated/encap-h4-joint-packed-egress-schedule.json`.  Its independent final
egress register plan peaks at ten YMM.

## Family result

The decisive result is that moving pair packing earlier provides no intrinsic
instruction or traffic credit.  S1 and S2 both store and reload 72 vectors and
both execute the same 144 pair-pack instructions.  S1 performs them at the H3
terminal and must additionally pay the nine zero-slack endpoint seams.  S2
performs them after the alias-required boundary and avoids those seams.

For Natural-Q:

| family | scratch | scheduled instructions | result |
| --- | ---: | ---: | --- |
| S2 canonical i16 | 2304 B | **1502** | selected |
| S1 pair32 | 2304 B | 1520 | +18 from nine store/reload seams |
| D direct-wire | 1728 B | 1556 | +54 vs S2; final overlap-safe copy remains |
| S0 terminal-packed | 1732 B | 1700 | exact 12-byte-chunk realization rejected |

The 2304-byte S2 object reuses the existing caller allocation, so its
incremental frame cost is zero.  It is no longer treated as a generic MA2
result: its contract is the intentional Natural-Q scale-1 packed-egress
scratch ABI.

## Presentation result

The abstract M1 run count is not used for selection.  Exact lowering produces:

| presentation | S2 scheduled instructions | delta vs Natural-Q |
| --- | ---: | ---: |
| Natural-Q identity | **1502** | 0 |
| bitperm-3210-xor-6 | 1574 | +72 |
| tile-specific sorted | 1620 | +118 |
| bitperm-0321-xor-e | 1634 | +132 |

Tile-sorted eliminates 72 final `vpermd` instructions and 26 index-constant
loads relative to Natural-Q, but first pays 216 terminal routes.  It therefore
loses by 118 instructions.  The other paid presentations are also dominated.

`0x1c7` is frozen only inside the rejected direct-wire realization.  It is not
a whole-H4 ordering requirement and is not used by S2.

## Decision

H4-M2 selects:

```text
Natural-Q scale-1 H3 terminal
-> per-vector Barrett and canonicalization
-> canonical-i16 packed-egress scratch
-> direct same-lane pair32 formation
-> exact 24-bit compaction
-> ciphertext bytes
```

This outcome is deliberately less visually fused than S1.  The required alias
boundary is useful: it separates the 16-YMM H3 schedule from a ten-YMM egress
schedule while carrying exactly the representation the final pack consumes.

H4-M3 is authorized to build one namespaced ASM prototype of this selected
path.  It must keep H3 arithmetic unchanged, preserve the 2304-byte
caller-owned scratch, use `.p2align 5`, and prove exact ciphertext bytes,
alias/canary behavior, no spill/frame, and the linked ledger before timing.
No benchmark or native KEM measurement is authorized by M2 itself.

r-hash remains deferred.  It may reuse the two-input pack primitive later, but
its exact-hash-byte consumer does not inherit the ciphertext scratch freedom.
