# D1-P3B24 full-KEM closure

Accepted as an experimental full-caller FromBytes substitution. Production
was not edited. Run `python3 run_pi5.py` to reproduce; `--audit-only` inspects
the existing Pi artifacts without repeating PMU.

All three variants share repository SHAKE256 symmetric.c, NTRU+864, q=3457,
GCC -O3 -march=armv8-a+simd and the frozen P3B12 harness. Both GT variants
retain r9_to ToBytes, the original frozen Forward, D1 arithmetic and Inverse.
Only FromBytes changes from P3B11 to P3B23. Official here is the repository
Neon comparator in this binary, not a new SUPERCOP-native run.

Eight deterministic cases pass exact public/secret key, ciphertext and shared
secret comparisons with Official; valid decapsulation and tampered-ciphertext
rejection/failure output comparisons have zero mismatches. This is differential
full-KEM evidence, not a new published KAT certification.

Pi5 Cortex-A76 core 3, three repetitions, both variant orders, 41 samples per
operation/order; aggregated cycle medians:

| API | Official | GT P3B11 | GT P3B23 | P3B23 minus P3B11 |
| --- | ---: | ---: | ---: | ---: |
| Keypair | 46882.875 | 55672.875 | 55683.000 | +10.125 |
| Encaps | 47016.788 | 47935.138 | 47661.325 | -273.813 |
| Decaps | 43442.950 | 46847.775 | 45999.050 | -848.725 |

Instruction deltas are exactly 0/-332/-996; branch median deltas are zero.
Relocation traversal includes GCC's crypto_kem_enc_derand.isra.0 helper and
proves 0/1/3 FromBytes calls in each GT variant. Wrapper relocations select
P3B11 for base and P3B23 for candidate, while both ToBytes wrappers select r9_to.
The isolated predicted deltas were -281.710/-845.130; measured differences
from these predictions are +7.898/-3.595 cycles. Per-repetition Encaps deltas
are -287.675/-283.800/-282.287; Decaps -841.125/-839.950/-864.200.
Keypair has no changed call or instruction count and its small timing delta
is not attributed to FromBytes.

Candidate still trails Official by 644.537 cycles in Encaps and 2556.100 in
Decaps. Do not infer a whole-KEM Official win from the isolated FromBytes win.
All runs report throttled=0x0. Manifest hashes, binary hashes, call ledger,
disassembly and raw samples are under build/.

Decision: retain P3B23 for the experimental full-KEM candidate. Production
promotion is a separate source/package/KAT/SUPERCOP closure; changing
Production first is unnecessary for this gate.
