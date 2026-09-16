# P41 — paired 12-byte record store

P41 is complete and is **not promoted**.  Production remains the P24/P23 Full
and Small ToBytes kernels.

## Why the experiment changed shape

The original two-live-record idea would keep packed A while routing and packing
adjacent record B, then form one Q plus one D store.  Under the exact 26-route-
register cap that schedule costs 423 route instructions and 136 coefficient
loads per top, versus P24's 285 and 61.  The complete call would add 168
instructions and 150 reads, so that candidate was rejected before assembly.

The implemented candidate instead makes only the public A-before-B ordering a
constraint:

1. record A stores a Q containing its twelve final bytes and four temporary
   high bytes;
2. record B overwrites those four bytes with `STUR S`;
3. `EXT #4` plus `STUR D` writes B's remaining eight bytes.

No packed record remains live across another route.  Every pair therefore uses
four terminal instructions instead of P24's six, without scratch or a new
coefficient pass.

## Static and correctness gates

The constrained global schedule uses, per 432-coefficient top:

| | P24 | P41 |
|---|---:|---:|
| route instructions | 285 | 320 |
| coefficient Q loads | 61 | 76 |
| terminal instructions / 27 pairs | 162 | 108 |

The terminal saving is 54 instructions/top, but route reloads add 35/top.  The
complete call therefore changes by:

- instructions: `2154 -> 2116` Full and `1934 -> 1896` Small (`-38`);
- coefficient reads: `+30`;
- stores: `-54`;
- vector-to-GPR moves: `-108`.

The exact model passed 1,028 signed-int16 route/overlapping-store cases.  Both
physical sources assemble for arm64.  The Pi 5 component harness passed 513
cases with canaries, and linked KAT, malformed-ciphertext, exact/tampered KEM,
AAPCS/wipe and object no-spill gates all passed.

## Slothy

Slothy was loaded from `/Users/chenpinhao/slothy` with the approved interpreter.
All eighteen three-output windows preserve their instruction multisets with
renaming and spilling disabled.

- Full Cortex-A76 model: P24 `1495` -> P41 `1489` cycles/top.
- Small control model: P24 `1010` -> P41 `1014` cycles/top.

Only Full was therefore linked into the Pi 5 candidate; Small remained the
byte-identical P24 production object.  Because Slothy has no scalar-S immediate
store model, `STUR S` was conservatively modeled as one same-register/address
D store and restored by its fixed public offset before arm64 assembly.

## Pi 5 decision

Selected tree: `/home/pi/supercop-20260831`; host remained unthrottled.

At the exact Full ToBytes boundary:

| | P24 | P41 | delta |
|---|---:|---:|---:|
| cycles | 1393.356 | 1395.609 | **+2.253** |
| retired instructions | 2168.156 | 2130.156 | -38 |
| reads | 132.023 | 162.023 | +30 |
| writes | 223.023 | 169.031 | -53.992 |

The two process orders disagree (`+2.210` versus `-0.960` median cycles), so the
isolated cycle result is near neutral, but it does not pass the predeclared
same-boundary promotion gate.

The complete KEM signal was favorable: Keygen/Encaps/Decaps paired medians were
`-45.125/-16.775/-31.450` cycles with exactly `-38` instructions each.  This is
retained as evidence that the store shape is useful in caller context, but it
does not override the failed exact-component attribution gate.  P41 is not
promoted.

## Reopen condition

The next candidate must retain the overlapping Q/S/D store idea while removing
the A-before-B schedule's 30 extra coefficient reads.  A useful static target is
at most 61 coefficient loads and at most 300 route instructions/top, which would
leave at least 78 complete-call instructions of net saving before Slothy.  One
concrete avenue is transiently borrowing the normalization scratch register as
a 27th route-cache register between consumers, then evicting only at the pack
boundary.
