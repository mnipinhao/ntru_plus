# P52 selected-Official profiler results

P52 is a measurement checkpoint of exact P51 commit `f786a587` against the
selected SHAKE256 AArch64 tree in `/home/pi/supercop-20260831`. The selected
tree is the benchmark contract for this campaign; its status as the newest
upstream NTRU+ revision remains unverified.

All manifest/build/KEM/KAT, six-process exact/tampered compatibility, and
instrumentation-equivalence gates passed. The Pi 5 reported no throttling.

| operation | Official cycles | P51 GT cycles | GT delta | GT delta % |
|---|---:|---:|---:|---:|
| Keygen | 44310.000 | 43128.000 | -1182.000 | -2.668% |
| Encaps | 46439.975 | 44914.025 | -1525.950 | -3.286% |
| Decaps | 40756.225 | 38768.800 | -1987.425 | -4.876% |

The caller-level profile identifies these useful boundaries:

- GT `hash_g`: 14459.800 net cycles in Decaps; Official: 14551.825.
- GT `Full_to_hash_g`: 15755.775 net cycles in Encaps. This remains a large
  absolute boundary even though P48 already removed the immediate copy.
- P51 FR0 equality: 462.000 net cycles. Comparable Official work is its
  182-cycle verifier plus one approximately 1104-cycle Full serialization.
- GT fused inverse-to-ternary: 4760.000 net cycles; Official Inverse plus
  `Crepmod3` totals approximately 4602.550 cycles.

P51 therefore remains a valid, faster experimental candidate. It is not
production: the user explicitly requested that promotion be withdrawn before
the hash campaign. Production is restored to the P47 serializer/compare
boundary, while all P51 source, proof, and measurements remain archived.

P53 is selected because fixed-size NO_CE `hash_g` can reuse the proven NTRU+768
production sponge organization without transferring any 768 transform,
layout, scale, or range assumption.
