# `hash_g` fixed-size SHAKE256 mapping

Experiment ID: `gt768-fused-shake-hashg-20260911-e41`

Baseline: `aarch64-production` at
`a64e7035cb13410554af1c67870d4132a30037b4`.

This document fixes the byte, lane, padding, output, and register-boundary
contract before any fused assembly is written.  All lane integers are
little-endian, matching `load64()` and `store64()` in `fips202.c`.

## Mathematical operation

`hash_g(out, msg)` computes

```text
SHAKE256(0x01 || msg[0..1151], 192 bytes)
```

SHAKE256 has a 136-byte rate (17 lanes), a `0x1f` delimiter, and the terminal
Keccak padding bit in bit 63 of rate lane 16.  The input length is 1153 bytes:

```text
1153 = 8 * 136 + 65
```

The output length is 192 bytes:

```text
192 = 136 + 56
```

The operation therefore executes ten permutations:

```text
8 full input blocks + 1 padded tail + 1 continuation squeeze = 10
```

## Full-block lane mapping

Let the semantic input stream be `M = 0x01 || msg`.  Full absorb block `b`
contains `M[136*b .. 136*b+135]`, split into rate lanes 0 through 16.

Block 0 is the only block containing the domain byte:

```text
lane 0 = LE64(0x01, msg[0], ..., msg[6])
lane l = LE64(msg[8*l-1 .. 8*l+6])       for l = 1..16
```

For blocks `b = 1..7`:

```text
lane l = LE64(msg[136*b + 8*l - 1 .. 136*b + 8*l + 6])
```

Thus the eight blocks consume these message ranges:

| block | semantic content |
|---:|---|
| 0 | `0x01 || msg[0..134]` |
| 1 | `msg[135..270]` |
| 2 | `msg[271..406]` |
| 3 | `msg[407..542]` |
| 4 | `msg[543..678]` |
| 5 | `msg[679..814]` |
| 6 | `msg[815..950]` |
| 7 | `msg[951..1086]` |

Every block after block 0 begins one byte before an 8-byte `msg` boundary.
A fused implementation can use unaligned 64-bit loads directly for these
words; per-word shifts/extracts are not required. Only the first prefix lane
needs assembly from the domain byte and seven message bytes. It must not
silently treat these as eight naturally aligned 136-byte `msg` blocks.

## Tail and padding

After eight blocks, 65 message bytes remain: `msg[1087..1151]`.

```text
tail lanes 0..7 = LE64(msg[1087..1150])
tail lane 8     = msg[1151] | (0x1f << 8)
tail lanes 9..15 = 0
tail lane 16    = 0x8000000000000000
```

These values are XORed into the current state.  The delimiter occupies tail
byte 65, immediately after the final message byte; the terminal bit occupies
tail byte 135.

## Squeeze mapping

After the padded-tail permutation:

```text
out[0..135] = LE byte serialization of state lanes 0..16
```

The state is permuted once more without absorbing input, then:

```text
out[136..191] = LE byte serialization of state lanes 0..6
```

The final 56 bytes are exactly seven complete lanes, so no partial-lane store
is needed.

## Existing scalar-assembly register boundary

After its final normalization rotates, the current permutation holds canonical
state lanes in this order:

```text
lane:  0  1   2   3   4   5  6   7   8   9  10 11  12  13  14 15 16  17  18  19 20 21  22  23  24
reg:  x1 x6 x11 x16 x21 x2 x7 x12 x17 x22 x3 x8 x13 x28 x23 x4 x9 x14 x19 x24 x5 x10 x15 x20 x25
```

The remaining GPRs are `x0`, `x26`, `x27`, `x29`, and `x30`; `x30` is usable
only after the caller link register has been saved.  This is enough to hold an
input/output pointer, a temporary load, round-constant state, and boundary
control, but only if the continuation reuses the existing round-body allocation
and its bounded stack temporaries.

The current body normalizes 23 rotated lanes before every store.  A fused
implementation may normalize once at each absorb boundary and XOR the next
block directly into the register map above.  It must then enter a live-state
round path; calling the existing public function would reload all 25 lanes and
defeat the experiment.

## Stage gates

1. Mapping oracle: the virtual block construction must equal the contiguous
   `0x01 || msg` stream plus SHAKE padding for every tested message.
2. B control: remove only the 1153-byte `data[]` construction while retaining
   the existing sponge/permutation boundary.
3. C control: fixed-size C path with the exact mapping above, still calling the
   existing permutation for every block.
4. D liveness/static gate: define the live-state round continuation and count
   boundary loads, stores, spills, calls, normalization, and input seam work.
5. D implementation: only after gate 4 demonstrates a net static opportunity.
6. KAT/full callers precede any Pi timing.
