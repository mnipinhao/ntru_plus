# GT9X16-PROD3-H1-INTEGRATION

## Scope

This checkpoint makes direct H1 serialization the current research
encapsulation baseline without running another native performance campaign.
Only the `r` hash edge changes:

```text
old: r MA2 planes -> generic F0 -> Official -> inv4 -> poly_tobytes
new: r MA2 planes -> direct H1 -> exact 1728 hash bytes
```

PROD3, top split, the two coefficient-domain inputs, `hash_g`, SOTP, resident
`h`, native MA2 arithmetic, ciphertext serialization, allocation, secure
clears, keypair, and decapsulation remain unchanged.

## Integration

The generated experiment `src/kem.c` now includes the H1 ABI and calls
`ntruplus1152_exp001_prod3_ma2_hash_h1(ct, r_f0.coeffs)` immediately after the
first PROD3 forward. It no longer calls or includes the old recovery bridge.
The generator owns this change and `make check` verifies that the generated
source is current.

The candidate was installed non-destructively as:

```text
crypto_kem/ntruplus1152/avx2-gt9x16-prod3-h1-exp001
```

in a disposable pinned-SUPERCOP campaign. The official `avx2` implementation
and pristine snapshot were not modified.

## Correctness

The standalone NIST KAT build uses the candidate's installed flat sources and
the frozen repository KAT harness. All 100 NTRU+1152 vectors are byte-exact:

```text
request  SHA-256 36c27b6089b8910733a01fea1136469769b3ca3c35f2b375cfcc592f2112cfaa
response SHA-256 2ddfc810c44f63f8d24086da7c33faf17d66c393f519a5b9cb76b0b7509464c3
```

The integration evidence also fixes the caller shape: two PROD3 forwards, one
direct H1 call, one native MA2 call, and unchanged `hash_g`/SOTP order. The old
bridge call is forbidden.

## Decision

H1 is now the current research Encap baseline. No native SUPERCOP performance,
fixed-ELF pricing, or promotion claim is produced by this checkpoint.

The next checkpoint is the pure-map
`GT9X16-PROD3-MA2-QORDER-CO-DESIGN`. It may search lane gauges and jointly
price producer final routing, resident-`h` projection, and MA2-to-hash
serialization. It must not write assembly or change the integrated caller.

## Evidence

- `results/gt9x16-prod3-h1-integration-20260827-001/kat.json`
- `src/kem.c`
- `tools/generate_f0_ma2_kem.py`
- `tests/test_gt9x16_prod3_h1_integration_evidence.py`
- `scripts/run_gt9x16_prod3_h1_kat.py`
