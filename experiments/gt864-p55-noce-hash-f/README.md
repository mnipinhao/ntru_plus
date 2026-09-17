# P55 — fixed-size NO_CE hash_f

P55 specializes the exact NTRU+864 transcript
`SHAKE256(0x00 || pk[1296]) -> 32 bytes` on baseline AArch64.  Nine full
136-byte absorb blocks and the 73-byte tail are consumed with the Keccak state
resident in GPRs; the tenth permutation produces exactly four output lanes.

The P53 `hash_g` entry and instruction stream remain unchanged.  P55 has an
independent assembly entry so a Keygen/Encaps improvement cannot hide a
`hash_g` regression in Decaps.

Release gates are differential and exact-alias testing, package KEM/KAT,
malformed-ciphertext equivalence, AAPCS64/zeroization/object audits, and paired
Pi 5 measurements of `hash_f`, Keygen, Encaps, and the unchanged Decaps
control.

The experiment compares commit `003a204f` against only the P55 hash change.
It does not alter `hash_g`, transform arithmetic, serialization, or the Decaps
call graph. The authoritative Pi 5 run is under
`/home/pi/supercop-20260831/bench/pinhao/gt864-p55-noce-hash-f-20260916`.
