# P106 — P29's A76 cost is not the paired kernel's IPC

P29 landed at -38 ns on M2 and +118 on A76, and its own next-gate note blamed
issue width: IPC 1.41 against the old path's 1.93, "a producer/consumer
dependency question".  Measured per component, that is not where it is.

## Per component, Cortex-A76

| | cycles | instructions | IPC |
|---|---:|---:|---:|
| P29 `paired` x3 | **1,984** | 2,532 | 1.28 |
| old `invntt16` x6 | **~2,018** | 3,960 | 1.96 |
| P29 `tail_direct` | **502** | 850 | 1.69 |
| old tail | **322** | 592 | 1.84 |
| P29 `route` | **586** | 938 | 1.60 |
| old `crepmod3` | **438** | 978 | 2.23 |

**The paired kernel is a 34-cycle win.**  The regression is +180 in the tail and
+148 in the route.  Its low IPC is a consequence of doing the same arithmetic in
37% fewer instructions, not a stall problem.

`old invntt16 x6` is the one figure that moves with code layout -- 2,018, 2,352,
2,690, 3,025 across four builds that differ only in which other kernels are
linked beside it, while every other row held to single digits.  The +294 total
matches the KEM-level +300, which fixes its true value near 2,018.

## The GPR parking is not the cause

P28 parks six Q values in twelve GPRs (`umov x5, v21.d[0]` ... restored with
`dup`/`ins`) so that neither kernel spills.  A76 charges heavily for NEON-to-GPR,
so this looked like the answer.  `paired_spill.S` replaces the 24 cross-domain
instructions with six `STR Q` and six `LDR Q` on a 96-byte frame, bit-identical
over 5,000 inputs: **A76 1,990 against 1,986, backend stalls 22.72M against
22.81M.  No change.**  M2 gains 17 cycles.

## The route's cost is `ST3`, and half of it is now gone

Substituting plain stores for the 64 `ST3.4H` (wrong output, right cost) prices
the interleave: **A76 586 -> 450, so 136 cycles; M2 204 -> 171, so 33.**  A76
charges four times what M2 does for the same instruction.

Per group the eight-lane components are `c0 = (A.lo | D.lo)`, `c1 = (A.hi |
D.hi)` and `c2 = C`, so **two `ZIP .2D` replace three `EXT` and one `ST3.8H`
replaces two `ST3.4H`**.  938 instructions become 874, 64 interleaving stores
become 32, output byte-identical over 5,000 inputs across all 1,024 halfwords.

| route | A76 | M2 |
|---|---:|---:|
| 64 `ST3.4H` | 586 | 204 |
| **32 `ST3.8H`** | **530** | **188** |
| plain stores (floor) | 450 | 171 |

Landed as `b9a3c7f5`: decapsulation **-18 ns on A76 and -5 on M2**, both
machines, all gates.

## What is left is the tail, and it is the ternary conversion

| | P29 tail | old tail | delta |
|---|---:|---:|---:|
| `CMGT` | 64 | 0 | +64 |
| `SQRDMULH` / `MLS` | 88 / 88 | 50 / 50 | +38 / +38 |
| `ADD` / `SUB` | 130 / 64 | 64 / 32 | +66 / +32 |
| `UMOV` / `STRH` | 0 / 0 | 96 / 96 | -192 |
| stores | 64 | 96 | -32 |

P29's tail already stores less.  The +258 instructions are the ternary reduction
it performs itself, and it performs it badly: **238 instructions for 96 values,
2.48 each, against `crepmod3`'s 978 for 864, or 1.13.**

The cause is on record: the tail runs on **six of eight lanes**
(`invntt16_tail_constants` has lanes 6 and 7 zero in 64 of 64 rows, and
`invntt16_tail_scale` in 32 of 32), because `j = 8` has exactly six independent
problems -- three components times two halves.  At `crepmod3`'s density the 96
values would cost 109 instructions rather than 238: about **-129 instructions,
-71 cycles on A76**.

## Where P29 stands now

| 864 decapsulation | before P29 | after P29 | after the route fix |
|---|---:|---:|---:|
| M2 Pro | 4,093 | 4,055 | **4,045 (-1.17%)** |
| Cortex-A76 | 14,149 | 14,266 | **14,248 (+0.70%)** |

Rule 2 holds with more margin than at landing.  The tail is the last named item
on this kernel.
