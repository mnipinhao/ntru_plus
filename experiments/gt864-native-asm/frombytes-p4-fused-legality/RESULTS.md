# P4 — fuse FromBytes legality into decode/routing

P4 removes the separate 1,728-byte legality scan from
`gt864_fr0_frombytes_checked`.  The cluster decoder already creates exactly 108
vectors of eight unsigned 12-bit coefficients.  The promoted implementation
updates an unsigned vector maximum immediately after every `unpack8`, before
the temporary enters the unchanged TRN/ZIP/lane-routing network.

Each 432-coefficient half returns one scalar maximum.  Both halves are always
executed; the wrapper combines their public fixed-path comparisons without a
secret-dependent branch.  Returning a scalar is deliberate: the first draft
returned a vector and compiler audit found a `STR Q0,[SP]` across the second
half call.  The final form has no vector stack access in
`transpose_top_checked`.

## Exact memory and ABI change

| Item | P3-A | P4 |
|---|---:|---:|
| Packed input bytes loaded | 1,296 | 1,296 |
| Decode vectors | 108 | 108 |
| FR0 routing stores | 108 vectors | 108 vectors |
| Output legality reread | 108 vectors | 0 |
| Extra coefficient scratch | 0 | 0 |
| Vector spill in transpose core | 0 | 0 |
| Return value | any coefficient >=3457 | unchanged |

The observable output bytes, FR0 ordering, canonical predicate, caller failure
handling, and constant-time address/branch policy are unchanged.

## Correctness gates

- Local differential oracle: 5,828 cases, including `q-1/q` at every one of
  864 positions, uniform 0/3456/3457/4095, 4,096 random packed polynomials, and
  output canaries.
- Pi 5 production-shaped packages: manifest, `test_kem`, and 100-case KAT
  passed.  The KAT SHA-256 is unchanged:
  `0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c`.
- KEM rejection: 13,824 cases across both implementations, all 864 positions,
  invalid values 3457 and 4095, and four paths: Encaps `pk`, Decaps `ct`, first
  secret-key polynomial, and second secret-key polynomial.
- Six paired PMU processes each passed 24 valid KEM and exact checked-FromBytes
  comparisons.
- The promoted production package rebuilt on Pi 5 with library SHA-256
  `576ce2b76bf81a7198c1dea3ffb245b88e82715dc0f3c12c219609a7a2c82bea`
  and repeated the same KAT and 13,824-case rejection gates.

## Paired Pi 5 PMU versus production P3-A

| Boundary | P3-A cycles | P4 cycles | Delta | Instructions | Branches |
|---|---:|---:|---:|---:|---:|
| checked FromBytes | 870.856 | 715.062 | **-155.794 (-17.89%)** | -322 | -108 |
| Encaps | 45991.700 | 45865.600 | **-126.100 (-0.27%)** | -322 | -108 |
| Decaps | 44001.950 | 43558.200 | **-443.750 (-1.01%)** | -966 | -324 |
| Keygen | 46489.000 | 46493.750 | +4.750 noise | 0 | 0 |

The exact instruction and branch deltas propagate once into Encaps and three
times into Decaps, proving that the full-KEM improvement comes from the fused
legality scan rather than unrelated code.

This is a compiler-emitted C/Neon kernel, not a symbolic assembly replacement.
No Slothy scheduling claim is made; GCC 14.2 object audit plus real Pi 5 PMU is
the relevant scheduling evidence.  P4 is promoted and P5 becomes active.
