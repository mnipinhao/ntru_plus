# P101 — P29 landed

Adopted as `ed4d870c`.  The first change to land under the amended promotion
criterion, and the first assembly change of this campaign.

## It still fitted

P29 was built on 15 September against a production inverse that has been
reworked since, so the first question was whether its P8 scratch contract still
holds.  It does, unchanged.  The route reads Q-bases `(0,16,64)` for top0 and
`(32,48,80)` for top1, which are exactly production's six 256-byte P8 blocks,
so the paired calls have to be `(block0,block2)`, `(block1,block3)`,
`(block4,block5)` -- and that first guess reproduced production's output
exactly.

`differential.c`: **9,744 cases** -- random, the stated `abs<=2617` boundary,
zero, all 864 unit vectors, four hash-derived families, each also run in place
the way `kem.c` calls it -- **zero mismatched coefficients**, output always in
`{-1,0,1}`.  Repeated with the scratch pre-filled with garbage, since production
never initialises it: still exact.

## What replaced what

| | before | after |
|---|---|---|
| main | 6 x `invntt16_asm` | 3 x `invntt16_paired_asm` |
| tail | `invntt16_tail_asm` | `invntt_tail_direct_asm` |
| ternary | separate `crepmod3_ternary_asm` pass | folded into `invntt_route_asm` |
| retired instructions | ~5,362 | **4,320** |
| store µops | ~972 | **224** |

## Measured, both machines, before and after built in the same session

| ns per operation | M2 before | M2 after | A76 before | A76 after |
|---|---:|---:|---:|---:|
| keygen | 4,336 | 4,340 | 15,278 | 15,258 |
| encaps | 4,985 | 4,987 | 14,809 | 14,808 |
| **decaps** | **4,093** | **4,055** | **14,149** | **14,268** |

Three runs each, spread under 3 ns on M2 and under 15 on A76; A76 accepted
400/401 batches.  Key generation and encapsulation never call the inverse, so
their movement is code layout.

**Decapsulation: -38 ns on M2 (-0.93%), +118 on A76 (+0.83%).**  Against
Official, 864's decapsulation goes from **-1.1% to -2.1% on M2** and from
**-16.4% to -15.7% on A76**.  The thinnest of the campaign's nine margins
roughly doubles.

Promotion rule 2: a regression of at most 1% on one machine when the other's
gain in percent is strictly larger.  0.83 <= 1 and 0.93 > 0.83.

## A stack bug went with it

The driver's "tail padding" clear wrote 256 bytes at `sp + 1536` -- the
*caller's* frame -- while the scratch has been caller-owned in `x25` since P80.
It was landing inside `poly_invntt_ternary`'s own 1,792-byte array by
coincidence of frame layout.  Both the old and the new consumer were measured
insensitive to the padding's contents, so it is simply gone.

## Gates

manifest, KEM, ABI, canonical boundary 10,368 cases / 0 failures, zeroization
`clear_calls=21 nonzero_after=0`, KAT byte-identical to `kat/expected` with
SHA-256 `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`,
deterministic SUPERCOP export, `test_keccak_v84a` d8-d15 preserved,
`test_shake_prefixed` 765 cases.

## What is still open on this kernel

P29's own next-gate note stands: its IPC on A76 is **1.41 against production's
1.93**, and that is why it costs 300 cycles there while retiring 1,042 fewer
instructions.  Break-even needs **1.56, only 11% more**; at production's issue
width the same 4,320 instructions would take 2,234 cycles and beat the old path
on *both* machines.  That is a producer/consumer dependency question, and both
symbolic sources are on disk in `gt864-p28-paired-i16/candidate-main.sym.S` and
`gt864-p29-direct-st3/candidate-main-route.sym.S`.
