# Checkpoint F0-PROD2-MA2-CONSUMER

## Outcome

P2-B remains faster after appending the unchanged MA2 arithmetic, inverse-four,
and serializer, but the credit does not materially amplify. This is the
predeclared insufficient-credit branch: consumer-native materialization remains
a selected representation optimization, while the current P1-H producer core
is not advanced to native encapsulation.

The serious SUPERCOP-derived comparison uses one pinned P-core, one
SUPERCOP-selected O3 measure ELF, balanced order, 9 fresh processes, and 96
observations per named operation per launch. It is not a native KEM result.

## Frozen island

```text
control:
  P1-H(r) -> generic F0 -> MA2 planes
  P1-H(m) -> generic F0 -> MA2 planes
  -> shared native MA2(h) -> shared inv4/serializer -> ciphertext

candidate:
  P2-B(r) -> MA2 planes
  P2-B(m) -> MA2 planes
  -> shared native MA2(h) -> shared inv4/serializer -> ciphertext
```

The linked ELF audit proves both wrappers tail-transfer into the exact same
`ntruplus1152_exp001_f0_ma2_native_full` symbol. That one symbol owns resident
`h` projection, all MA2 arithmetic and reductions, inverse-four, packing, and
serialization. The control has exactly two P1-H and two projection transfers;
the candidate has exactly two P2-B transfers. No generic MA2 symbol is called.

The exact correctness test additionally runs projected P1-H planes through the
same native MA2 symbol and compares all 1,728 ciphertext bytes against both the
generic-MA2 and direct-P2-B paths over 257 producer-real cases.

## Serious result

| complete two-producer consumer island | pooled StQ2 |
| --- | ---: |
| P1-H plus projection control | 5318.4097 |
| P2-B direct planes candidate | 5191.8750 |
| candidate minus control | -126.5347 |

The paired per-launch median delta is `-126.5000` cycles, with P2-B faster in
9/9 launches. All linked benchmark and producer/consumer symbols are aligned
to 32-byte boundaries.

The previous exact-boundary paired median was `-115.1458` cycles. These are
different benchmark campaigns and are not formally subtracted, but their
similar magnitude is a strong classification signal: unchanged MA2 execution
preserves the boundary credit without amplifying it into the several-hundred-
cycle range.

## Decision

The architecture conclusion is now frozen:

```text
Semantic F0 remains useful; generic F0 physical ABI is not an Encap asset.
Consumer-native MA2 materialization is experimentally validated.
```

P2-B remains selected evidence, but its approximately 126-cycle island credit
is insufficient against the previously measured approximately 1,312-cycle
native encapsulation deficit. Native KEM integration is therefore not
authorized, and the 72 producer-local `vperm2i128` operations are not a
micro-optimization target: their linked net delta was already proved zero.

The next authorized checkpoint is only `F0-PROD3-MA2-MAP`: map a faster
Official-like producer geometry to a scale-four MA2-native late-stage/store
epilogue. It must first prove component ownership, roots, scale, range,
reduction requirements, and exact movement against the pinned Official
producer. No PROD3 assembly or KEM timing is authorized by this checkpoint.
