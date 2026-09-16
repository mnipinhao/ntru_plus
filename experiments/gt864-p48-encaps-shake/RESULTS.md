# P48 — Encaps Full-ToBytes-to-SHAKE

P48 passes every declared gate and is selected for production promotion.  It is
an Encaps-private consumer; generic P46 Full ToBytes and generic `hash_g` remain
available and unchanged for their other callers.

## Boundary change

The P47 production baseline performs:

```text
FR0 r -> P46 Full ToBytes -> ct[1296]
      -> hash_g memcpy -> data = 0x01 || ct
      -> SHAKE256 -> ct[216]
```

P48 performs:

```text
FR0 r -> P46 Full ToBytes -> data+1
      -> data[0] = 0x01 -> SHAKE256 -> ct[216]
```

The exact promoted P46 assembly and SHAKE256 implementation are reused.  The
only removed work is the full 1,296-byte copy from temporary ciphertext storage
to the prefixed SHAKE input.  The transcript is still exactly `0x01` followed by
the canonical 1,296-byte serialization.

## Correctness and binding

- Python transcript oracle: 1,000 arbitrary signed-int16 FR0 inputs.
- Native target differential: 1,024 arbitrary signed-int16 FR0 inputs, input
  immutability and output canaries.
- KAT digest and malformed-ciphertext transcript are unchanged.
- Baseline and candidate each pass 64 KEM cases.
- Object audit proves Encaps changes from `Full + hash_g` to `hash_g_fr0`, while
  `hash_g_fr0` calls the exact P46 assembly.
- No Slothy run is required: no assembly instruction, allocation or schedule is
  changed.
- The promoted production directory was uploaded separately and again passed
  its manifest, 64 KEM cases, native differential and expected KAT digest.

## Pi 5 paired PMU

Source root: `/home/pi/supercop-20260831`; 252 paired observations; Cortex-A76,
ondemand governor, unthrottled, final temperature 62.0 C.

| Operation | P47 baseline cycles | P48 cycles | Paired delta | Instructions delta | Branch delta |
|---|---:|---:|---:|---:|---:|
| Keygen control | 43121.750 | 43112.125 | -7.000 | 0 | 0 |
| **Encaps** | **44996.375** | **44877.825** | **-121.225** | **-175** | **-24** |
| Decaps control | 39778.175 | 39767.125 | -7.825 | 0 | 0 |

Control cycle movement is not attributed to P48.  Their identical retired
instruction and branch counts confirm that only Encaps executes the candidate.

## Decision

Promote the Encaps-private `hash_g_fr0` boundary.  Keep P46 as the reusable Full
serializer and retain generic `hash_g`.  P49 Keygen producer-range
specialization is the next recorded KEM serializer gate.
