# P47 — Decaps Full-ToBytes-to-compare

P47 passes every declared gate and is ready for production promotion.  It is a
Decaps-private consumer; generic P46 remains the Full serializer used by Keygen
and Encaps.

## Boundary change

The baseline performs:

```text
FR0 f -> P46 Full ToBytes -> 1296-byte buf2 -> verify(buf1,buf2) -> clear buf2
```

P47 performs:

```text
FR0 f -> P46 route/normalize/pack -> immediate D/W compare with buf1
      -> one constant-time mismatch bit
```

`buf2` remains only for the earlier 216-byte `hash_g` output, so the Decaps
frame drops from 11088 to 10016 bytes and cleanup no longer clears a dead
1296-byte serialization.

The kernel performs exact 8-byte plus 4-byte loads for every 12-byte record.
It does not overread the last record, write candidate bytes, allocate
coefficient scratch, or add a secret-dependent branch/address.  `x8` is the
mismatch accumulator; dead `x0` handles low-D comparison so an early scheduled
high-D value in `x9` is not destroyed.

## Correctness and scheduling

- Python model: 1,000 arbitrary signed-int16 polynomials and 10,000 byte
  mismatches.
- Native differential: 256 arbitrary inputs; equality plus every one of 1,296
  byte positions independently corrupted for every input.
- Exact input immutability and output canaries pass.
- KAT digest and malformed-ciphertext transcript are unchanged.
- Both packages pass 64 KEM round trips/tampered rejection.
- Candidate object has 1,336 static instructions, no Q-register stack traffic
  and no candidate-byte stores.
- Slothy: 18/18 three-record windows optimal, instruction multiset preserved,
  1,257 instructions inside timed regions, 1,661 modeled cycles.

The local A76 model lacks scalar `LDUR X/W`.  Each timing-only load is mapped
bijectively to a unique encodable `LDR X` offset, then restored to its exact
width/address before assembly and native testing.  Therefore the Slothy number
is a scheduling proxy; promotion is decided at complete Decaps.

## Pi 5 paired PMU

Source root: `/home/pi/supercop-20260831`; 252 paired observations; Cortex-A76,
ondemand governor, unthrottled, final temperature 59.8 C.

| Operation | P46 baseline cycles | P47 cycles | Paired delta | Instructions delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen control | 43112.000 | 43101.750 | -8.500 | 0 | 0 |
| Encaps control | 44995.650 | 45003.575 | +30.450 | 0 | 0 |
| **Decaps** | **39907.300** | **39763.225** | **-143.650** | **-19** | **-97.5** |

Keygen and Encaps do not call the new symbol; their identical retired
instruction and branch counts confirm they are controls.  Their cycle movement
is not attributed to P47.  The declared promotion metric is complete Decaps,
which wins materially.

## Decision

Promote the exact scheduled compare kernel and the Decaps-only C integration.
Keep P46 generic Full ToBytes unchanged for Keygen and Encaps.  This result does
not claim that generic ToBytes became faster; it removes an avoidable private
materialization boundary from Decaps.
