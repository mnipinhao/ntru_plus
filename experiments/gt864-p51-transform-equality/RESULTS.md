# P51 — transform-domain re-encryption equality

P51 is promoted.  Decapsulation retains the recovered polynomial in FR0/R0,
regenerates the candidate in the dead `c` slot, and compares the two transform
arrays modulo `q=3457`.  It no longer creates and compares a second canonical
1296-byte polynomial encoding.

## Algebra and range gate

- FR0-to-Official is a permutation of all 864 coordinates; both operands have
  the same root order and R0 scale.
- K1 regenerated envelope: `[-24799,24794]`.
- D1 recovered envelope: `[-3023,3023]`.
- Exact per-leaf difference envelope: `[-27822,27817]`, hence signed-int16.
- Exhaustive signed-int16 proof: `SQRDMULH(x,9); MLS(x,qhat,3457)` produces
  `[-3291,3291]`, preserves congruence, and is zero iff `x` is divisible by q.
- The wire map and canonical 12-bit encoding are injective, so transform-domain
  equality is exactly the former byte-equality decision.

## Implementation gate

- Selected object: 86 static instructions, one public loop branch.
- 216 Q loads, no stores, no coefficient scratch, no stack/vector spill.
- Secret-independent address/control flow; secret SIMD temporaries are wiped.
- Mac native differential: 4096 random/equal pairs plus alias, immutability and
  range-edge cases.
- Pi 5: 64 valid/tampered KEM cases, unchanged 100-case KAT digest, unchanged
  malformed-ciphertext transcript, and six 100-case exact/tampered processes.

## Pi 5 paired PMU

Exact baseline is commit `03f8ba29` (P50 production), on the selected
`/home/pi/supercop-20260831` environment.  There are 252 clean observations per
operation and implementation.

| operation | P50 cycles | P51 cycles | paired delta | instructions delta |
|---|---:|---:|---:|---:|
| Keygen | 43106.625 | 43123.500 | +12.250 | 0 |
| Encaps | 44863.575 | 44891.550 | +32.675 | 0 |
| Decaps | 39770.675 | 38788.225 | **-988.525** | **-2014** |

Keygen and Encaps contain no changed instruction path; their small cycle
deltas are control noise, not candidate work.

## Slothy decision

Using `/Users/chenpinhao/slothy` with the established dependency environment,
the 29-register candidate was fixed-allocation scheduled for Cortex-A76.  The
60-instruction loop multiset was preserved, spills and renaming were disabled,
and the model reported 62 cycles rather than 128 for the compact fixed-register
model.  Complete Pi 5 Decaps measured `-989.550` cycles versus P50, effectively
tied with the compact candidate while retiring 20 more wipe instructions.
Production therefore keeps the smaller compact allocation.  The Slothy output
is retained as negative target-silicon evidence, not silently promoted.
