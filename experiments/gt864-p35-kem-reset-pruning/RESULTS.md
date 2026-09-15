# P35 result — promoted KEM-only terminal-reset pruning

## What changed

The centered `gt864_native_inverse` path still calls `lazy_i16` and
`lazy_itail`.  Only `gt864_inverse_ternary_asm`, the Decaps-oriented P8 path,
calls the new `p35_i16` and `p35_itail` helpers.  Main retains the high-column-8
`SQRDMULH; MLS` reset because its proved pre-reset bound is 5278, above P8's
exact 5185 limit.  Five other main resets and all six tail resets are deleted.
The tail also deletes the now-dead `mov; dup` setup for the value-one Barrett
constant.

This changes no coefficient loads, stores, addresses, routes, scratch size or
public control flow.  The exact dynamic change is `6*(-10) + (-14) = -74`
instructions per Decaps.

## Proof and physical gates

- 1,088 symbolic cases have identical store addresses, residues modulo 3457,
  and exact P8 ternary outputs.
- Main/tail Cortex-A76 Slothy allocation is `OPTIMAL`, selfcheck is `OK`, and
  spills are disabled.  Fixed-allocation estimates improve from 166 to 164
  cycles for main and 150 to 147 for tail.
- Both physical outputs assemble on arm64.  Production source selection and
  the source manifest pass.
- Apple arm64 passes 64 KEM round trips/tampered rejection and the 100-case KAT.
- Pi 5 passes identical KAT and 417,216-byte malformed transcript, exhaustive
  9,155-value raw conversion, and 1,024 complete exact/alias/AAPCS/wipe cases.

## Paired Pi 5 PMU

Six balanced processes on Cortex-A76 core 3, unthrottled, measured:

| Boundary | Baseline cycles | P35 cycles | Delta | Instructions delta |
|---|---:|---:|---:|---:|
| Inverse-to-ternary | 4893.594 | 4754.109 | -139.485 (-2.85%) | -74 |
| Keygen | 43111.125 | 43110.875 | -0.250 | 0 |
| Encaps | 45006.950 | 44976.925 | -30.025 | 0 |
| Decaps | 40072.400 | 39933.575 | -138.825 (-0.346%) | -74 |

The Keygen/Encaps cycle movement is noise: both retire exactly the same number
of instructions.  The Inverse-to-ternary saving reaches Decaps essentially
one-for-one, so P35 is promoted.
