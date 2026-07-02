# Contract

## Production Decap Verify Call Graph

The production decap verify path is:

```text
poly_frombytes(&c, ct)
poly_frombytes(&f, sk)
poly_frombytes(&hinv, sk + POLYBYTES)

poly_basemul_rminus1(&m1, &c, &f)
poly_invntt_from_rminus1(&m1, &m1)
poly_crepmod3(&m1, &m1)

poly_ntt(&m2, &m1)
poly_sub(&c, &c, &m2)

poly_basemul(&r2, &c, &hinv)
poly_tobytes(buf1, &r2)
hash_g(buf2, buf1)
poly_sotp_decode(msg, &m1, buf2)

msg[N/8..] = sk stored hash_f(pk)
hash_h(buf3, msg)
poly_cbd1(&r1, buf3 + SSBYTES)
poly_ntt(&r1, &r1)
poly_tobytes(buf2, &r1)

fail |= verify(buf1, buf2, POLYBYTES)
ss[i] = buf3[i] & ~(-fail)
```

`buf1` is reconstructed `r` bytes.  It is not full ciphertext bytes.

## Byte Contract

The helper contract is:

```text
gt_decap_verify_basemul_tobytes_contract(out, c_minus_m2, hinv)
  ==
poly_basemul(&r2, c_minus_m2, hinv);
poly_tobytes(out, &r2);
```

The reference helper is:

```c
void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES],
    const poly *c_minus_m2,
    const poly *hinv);
```

It is implemented in:

```text
poly_gt_decap_verify_tobytes_contract_ref.c
```

The C candidate helper is:

```c
void gt_decap_verify_basemul_tobytes_contract_c_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES],
    const poly *c_minus_m2,
    const poly *hinv);
```

This candidate still materializes an internal `poly r2` from
`poly_basemul()`, then emits bytes through a C mirror of the production
Slothy support `poly_tobytes` lane order.  It is useful as a byte-output API
prototype and oracle; it is not the final direct arithmetic reducer.

The benchmark-only direct ASM prototype is:

```c
void gt_decap_verify_basemul_tobytes_direct_candidate(
    uint8_t out[NTRUPLUS_POLYBYTES],
    const poly *c_minus_m2,
    const poly *hinv);
```

This candidate keeps the current `base_gt_opt_body.inc` product DAG and final
reductions, then replaces the public poly store plus later `poly_tobytes` call
with a direct byte-output finalizer.  The first prototype uses stack staging and
scalar byte stores, so it is a diagnostic correctness artifact, not a production
candidate.

## Non-Goals

This helper is not:

```text
generic poly_basemul replacement
Q31 reuse
encap helper
public poly API
arithmetic-correct poly output
optimized ASM/reducer
```

The output is bytes only.  A future optimized candidate may use non-standard
intermediate representatives only if the final bytes exactly match
`poly_tobytes(poly_basemul(...))`.

## Consumers

After the verify basemul, `r2` has no arithmetic consumer.  The only consumer is
`poly_tobytes(buf1, &r2)`.

The produced `buf1` bytes are consumed by:

```text
hash_g(buf2, buf1)
poly_sotp_decode(msg, &m1, buf2)
verify(buf1, buf2, POLYBYTES)
```

`verify()` is constant-time over all `POLYBYTES` bytes.

## Gate

The default-off gate is:

```text
GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT
```

The default-off C candidate gate is:

```text
GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_C
```

The default-off direct ASM candidate gate is:

```text
GT_EXPERIMENT_USE_DECAP_VERIFY_BASEMUL_TOBYTES_CONTRACT_DIRECT
```

The three gates are mutually exclusive.

When disabled, decap remains:

```c
poly_basemul(&r2, &c, &hinv);
poly_tobytes(buf1, &r2);
```

When enabled for the reference experiment:

```c
gt_decap_verify_basemul_tobytes_contract_ref(buf1, &c, &hinv);
```

When enabled for the C candidate experiment:

```c
gt_decap_verify_basemul_tobytes_contract_c_candidate(buf1, &c, &hinv);
```

When enabled for the direct ASM candidate experiment:

```c
gt_decap_verify_basemul_tobytes_direct_candidate(buf1, &c, &hinv);
```

## Release Guard Plan

Future promotion requires guards for:

```text
generic poly_basemul not overwritten
helper call site only in decap verify block
encap/keygen callers = 0
public header exposure = 0
valid/invalid decap differential pass
direct byte oracle pass
```

No release-promotion guard is added yet because there is no optimized candidate.
