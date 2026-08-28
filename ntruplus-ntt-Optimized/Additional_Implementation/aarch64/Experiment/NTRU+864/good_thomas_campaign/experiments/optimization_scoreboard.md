# NTRU+864 Good-Thomas optimization scoreboard

This is the campaign decision ledger. A row is not a performance claim unless
the named correctness and benchmark evidence exists.

| Experiment | Gate | Evidence | Decision | Next action |
| --- | --- | --- | --- | --- |
| `gt_9x32_root_gate` | root-set equality, 9-by-32 grid bijection, legacy leaf-label bijection | pass; mapping SHA-256 `a15f659eb13bf6ee173d04135e02a774ef0e90c2b153797dcecb39644eaecae5` | keep as algebra oracle | Start a separate direct scalar evaluation/interpolation experiment; do not start Neon. |
| `gt_9x32_scalar_reference` | factorized forward vs direct evaluation; round trip; GT product vs schoolbook; aliases | pass: 36 forward, 36 round-trip, 21 product, 93 alias cases; zero mismatches | freeze as readable canonical algebra oracle | Open a new experiment for legacy leaf order and Montgomery boundaries. Do not add that work to this closed directory. |
| `gt_9x32_montgomery_reference` | exact current forward and basemul representatives; inverse/full-product modulo q; alias; Montgomery scale | pass: 32 exact forward, 17 exact basemul, 32 inverse-mod-q, 32 centered round trip, 17 full product, 81 alias; zero mismatches | freeze as Montgomery/legacy-boundary oracle | Start a new range-proof and staged 32-point algorithm experiment; do not add Neon here. |
| `gt_9x32_radix3_orientation_reference` | oriented radix-3 vs frozen Horner/current scalar forward; full product vs frozen GT/schoolbook; alias; sanitizer | pass: 39 exact Horner forward, 39 exact current forward, 21 frozen-reference product, 21 schoolbook product, 60 alias; zero mismatches | freeze as reduced-constant NTT9 algebra reference; no performance claim | Open a separate `(P,D)` representation experiment spanning Forward, BaseMul, and InvNTT before Neon instruction selection. |
| `gt_2x9x16_ld3_top_split` | exact LD3 map; exact Neon representatives; fixed-multiply congruence; range boundaries; padding; ISA and secret-independent flow | pass: 106 differential cases and 5,185 exhaustive fixed-multiply checks; zero mismatches | freeze as the P8-plus-tail top-split layout candidate; no performance claim | Open a separate NTT16 experiment comparing the 896-value padded contract with a compact 864-value alternative. |

## Global promotion rule

No experiment changes the NTRU+864 Production default. Promotion requires a
separate audit covering exact representation boundaries, range, constant time,
ABI, KAT, full KEM, source closure, Pi 5 PMU, and SUPERCOP-native evidence.
