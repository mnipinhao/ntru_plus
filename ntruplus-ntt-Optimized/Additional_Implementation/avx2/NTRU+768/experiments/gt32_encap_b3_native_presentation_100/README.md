# GT32 Encap B3-native presentation generator (100)

This generator reopens only the Encap `Decode(h) / Forward(r) -> B3` input
presentation around production baseline `b2a4bea`.  It does not emit assembly
and does not modify GT Clean.

## Frozen production contract

- current Encap order and E0V two-source final Q24;
- four-slot, 6592-byte frame;
- `e=0`, current Good--Thomas/NTT32 and quartic B3 mathematics;
- current B3 output M representation and Q24 implementation;
- Keypair and Decap code and placement.

The generator accounts for both consumers of transformed `r`:

```text
Forward(r) -> Er -> WIRE12(r) -> hash_g
                  \
Decode(h)  -> Eh --+-> general B3 -> M product
```

## Source-level correction

Production `general B3_M` already loads four coefficient planes from each
operand directly.  Its M input edge contains eight loads and **zero routing
instructions** per block.  There is no hidden `M -> B3-native` transpose to
delete.

For decoded `h`, the decoder's four packet registers are transposed to M with
the same twelve-operation 4x16 network that an alternative packet-form B3
would have to perform later.  Moving that network from Decode to B3 deletes no
operation class.  Therefore the selected asymmetric left operand remains:

```text
Eh = M
```

## Selected generator candidate: persistent terminal `T` for `r`

`T` is the exact post-S5 state after `FR_MONT_QWORD_PACKED` and before
`FR_PACKED_TO_PLANES`.  Experiment 083 proved symbolically that:

```text
Q24_TRANSPOSE(FR_PACKED_TO_PLANES(T))
  == four qword unpacks(T)
```

The current `Er=M` path executes, over twelve four-vector groups:

```text
Forward T -> M       12 routes/group = 144
M -> WIRE12          12 routes/group = 144
B3 M input            0 routes/group =   0
                                      -----
                                        288
```

The candidate materializes only `T` in the existing 1536-byte `r` slot:

```text
Forward T store       0 routes/group =   0
T -> WIRE12            4 routes/group =  48
T -> M at B3          12 routes/group = 144
                                      -----
                                        192
```

Thus it deletes exactly 96 executed routing instructions without adding a
representation, a vector load/store family, or a reduction.  Scale, bound and
logical leaf mapping are unchanged because `T <-> M` is a permutation only.

This is not the rejected 083 immediate-terminal schedule.  083 formed M and
serialized while the Forward terminal values were live, coupling Q24 to every
Forward tile and losing about 62--64 TSC to the same tile-order control.  The
100 candidate restores a full materialized boundary:

```text
Forward -> store T -> return
pack_T(T) -> return -> hash/SOTP/Forward(m)
B3_M_T(h_M, r_T)
```

The 96-route deletion is the same composite-map credit, but the execution
windows are decoupled.

## Feasibility

`B3_M_T` can convert one four-vector T block before loading the M operand.  A
constructive allocation uses four T source registers, four routing temporaries
and one shuffle mask; the mask and temporaries die before the existing
16-register-saturated arithmetic body begins.  Peak is at most 15 YMM during
the conversion and the unchanged arithmetic peak remains 16, with no spill
required.

## Decision

```text
Eh=M, Er=M control:                 production baseline
Eh=T or partial cuts:              no operation-class deletion
Eh=M, Er=T persistent terminal:    PASS_TO_EXECUTABLE_101
static structural credit:          -96 routing instructions / Encap
GT Clean production:               unchanged
```

The static result selects an executable experiment; it is not a cycle claim.
The next gate must implement experiment-private `ntt_r_T`, `pack_r_T`, and
`B3_M_T`, then benchmark the complete caller-shaped region using the native
SUPERcop method.  It must not integrate into KEM production before that gate.

Run:

```sh
make check
```

Generated evidence:

- `generated/presentation-search.json`
- `generated/candidates.csv`

