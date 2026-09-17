# CBD and r-serializer audit

## Why the profiler reports a CBD delta

The GT and Official builds use the same `poly_cbd1` algorithm and instruction
sequence.  The production profile's `+26.5 core cycles` is an elapsed
call-region difference, not evidence that GT changed CBD arithmetic.

The source files are byte-identical; both SHA-256 values are
`1b1f991128d5f1eed916e6ab5ddd6594cb41ffcc6fe27308b805f6499edae63b`.

The two ELFs place the same CBD body, its constants, caller stack destination,
and surrounding producer/consumer code at different addresses.  LBR-derived
call-region cycles include cache state, outstanding work, front-end delivery,
and out-of-order overlap at the call boundaries.  Consequently an unchanged
leaf can receive a non-zero contextual delta.  Earlier stack-offset permutation
gates did not find a reproducible CBD placement win, so this number is an
attribution clue, not a 26-cycle CBD rewrite budget.

## Current GT r serializer

Encap keeps `r` in private M/SoA because B3 consumes it later.  Before `hash_g`,
`ntruplus768_pack_m_lazy10788_avx2` must also produce the canonical 1152-byte
WIRE12 representation.

For each of twelve four-vector groups it:

1. loads four coefficient-plane YMM vectors from M;
2. executes the 4x16 transpose (`12` routing instructions) to recover packet
   order;
3. applies the `v=9` quotient estimate and `x-kq` reduction;
4. adds `q` to negative representatives;
5. packs coefficient pairs with `vpmaddwd` and `vpshufb`;
6. writes four 24-byte packets using the existing partial/overlapping store
   pattern.

Thus the serializer performs 48 vector loads, 144 transpose routes, 48 vector
reductions, packing, and 48 logical packet stores.

## Official serializer

Official `poly_tobytes` receives its NTT output in its own coefficient-friendly
layout.  It loops six times; each iteration loads eight YMM vectors (128
coefficients), reduces them, forms 12-bit groups using shifts/blends/unpacks,
and writes six contiguous 32-byte vectors (192 bytes).  It does not pay GT's
private-M-to-packet transpose, but its packing network is itself substantial.

The controlled serializer-only gate remains the useful intrinsic comparison:
GT was about `+20 TSC` versus Official.  The fresh production LBR frontier
(`+45.25 core cycles`) is larger because it includes caller context and should
not be treated as 45 cycles of isolated serializer arithmetic.

## Remaining optimization space

- **Not enough:** another loop form, constant-residency variant, or moving the
  same transpose between producer and serializer.  Those search classes have
  already failed to delete work or were delivery-sensitive.
- **Real opportunity:** delete a representation boundary.  Since `r_M` must
  survive for B3 while canonical bytes must cross `hash_g`, a candidate must
  form both outputs from one producer terminal state without duplicating the
  current M stores plus a second full transpose.
- **Most concrete bounded gate:** replace `pack(ct,r); hash_g(ct,ct)` with a
  private `hash_g_from_m(ct,r)` whose 1153-byte domain-separated input buffer
  is the serializer destination.  Current `hash_g` first copies the complete
  1152-byte temporary ciphertext into its local `data[1+]`; packing directly
  to `data+1` deletes that full copy while keeping the exact SHAKE input bytes.
  This is pack/hash glue deletion, not a faster Q24 reducer, and must be tested
  against the current production caller in one ELF.
- **Alternative:** a new B3 input factorization that consumes a serializer-
  friendly `r` presentation without reconstructing M.  Experiment 141 shows
  that merely moving the existing three transpose layers is not sufficient.
- **Bound:** optimizing the current serializer alone has an observed intrinsic
  ceiling near 20 TSC, so it cannot by itself close the complete Encap gap.

The next executable serializer gate should therefore require an explicit
operation-class deletion (for example, eliminate one 48-vector reload or one
complete 144-route network), not just fewer static instructions.
