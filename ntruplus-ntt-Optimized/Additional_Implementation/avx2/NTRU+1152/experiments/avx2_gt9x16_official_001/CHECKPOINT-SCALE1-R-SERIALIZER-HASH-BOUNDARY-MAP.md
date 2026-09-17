# Scale-1 r serializer/hash boundary map

## Result

The approximately 188-cycle scale-1 `r` dual-output/fanout debt is a
serializer debt, not a `hash_g` input-staging debt.

The next optimization target is therefore a boundary-preserving serializer
V2.  Forward remains complete and materialized before serialization.  The
rejected full serializer-in-terminal fusion is not reopened.

## Measured boundaries

Every boundary starts from resident materialized transformed state.  Official
and wire states are touched symmetrically outside timing.

```text
S0  exact 1728-byte serialization
S1  S0 + domain byte and 1728-byte hash input staging
S2  S1 + SHAKE256 absorb/finalize/squeeze + secure clear
S3  S2 + SOTP polynomial generation
```

S2 uses an explicit aligned staging buffer so the stages remain nested.  Its
288-byte output is checked against the production `hash_g` implementation.
This is SUPERCOP-derived attribution, not Native SUPERCOP KEM output.

Pinned SUPERCOP 20260831, fixed common GCC 15.2 `-O3`, CPU 1, performance
governor, turbo disabled, balanced same-ELF order, nine fresh processes, 1728
pooled observations per implementation and boundary:

| boundary | Official StQ2 | wire StQ2 | wire debt |
|---|---:|---:|---:|
| S0 serializer | 529.4444 | 729.2245 | **+199.7801** |
| S1 serializer + input staging | 586.8773 | 776.9861 | **+190.1088** |
| S2 serializer + complete SHAKE | 18382.1875 | 18600.6181 | +218.4306 |
| S3 complete hash/SOTP fanout | 18604.4560 | 18846.6667 | +242.2106 |

S0 and S1 are especially clean: wire is slower in 9/9 launches at both
boundaries.  Adding input staging changes the pooled representation debt by
only `-9.67` cycles.  It does not create the roughly 200-cycle gap.

S2/S3 retain the same direction in 9/9 launches, but the roughly 18k-cycle
SHAKE work creates much larger process variance.  Differences of independently
estimated StQ2 values are diagnostic and are not claimed as an exactly
additive component decomposition.

## Exact source and machine structure

Production `hash_g` constructs exactly:

```text
0x01 || 1728 serialized bytes
→ SHAKE256
→ 288 output bytes
→ secure_clear(staging)
```

Both serializers produce the exact same 1728 bytes, so everything after the
serializer is representation-independent.

The linked serializer objects explain the S0 result:

| property | Official `poly_tobytes` | wire direct serializer |
|---|---:|---:|
| geometry | 9 loop iterations | 18 straight-line 64-coefficient tiles |
| input per unit | 8 YMM / 128 coefficients | 4 YMM / 64 coefficients |
| output per unit | 6 YMM / 192 bytes | 96 bytes |
| estimated dynamic instructions | 1075 | 1387 |
| difference | | **+312** |
| linked wire `.text` | | 8525 bytes |

Normalization arithmetic is equal at 72 vectors.  The wire implementation
pays additional packet-formation work, including 108 `vpslldq`, 108 `vpor`,
72 `vpsrldq`, 72 `vpshufb`, 72 `vpmaddwd`, 72 `vextracti128`, and 54
`vinserti128`.  It also has 126 `vmovdqa` versus Official's 74 dynamic aligned
loads; this includes a substantially less favorable constant/load geometry.

## Decision and next gate

- Do not fuse the complete serializer into Forward again.
- Do not start serializer-to-SHAKE fusion: the input staging is not the
  wire-specific debt.
- Open `SCALE1-R-SERIALIZER-V2-PACKET-MAP`.

Serializer V2 will pair two existing 4-YMM wire tiles into one 8-YMM,
128-coefficient packet—the same granularity as one Official loop iteration.
It will search for an ownership-correct lowering to the frozen 192-byte wire
block while preserving the materialized producer boundary.  The first gate is
mapping and instruction budget only; no Forward, hash, SOTP, or Native caller
change is authorized yet.

Machine-readable evidence is in
`generated/scale1-r-serializer-hash-boundary-map.json` and the raw serious
campaign directory.

