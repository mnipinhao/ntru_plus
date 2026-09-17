# 143 — geometry-preserving r pack-to-hash production integration

This gate promotes only the mechanism qualified by Experiment 142 into a
production-shaped image.  Both profiles contain the same noinline helper in a
page-aligned RX-only `.rhash_tail`.  Both Encap input sections reserve exactly
611 bytes.  Existing E0V/QL2 tails and all shared hot symbols must retain the
same addresses, sizes, and bytes; only the Encap caller bytes differ.

The candidate replaces `pack(ct,r_M); hash_g(ct,ct)` with one call that packs
directly into the domain-separated SHAKE input.  Forward, B3, QL2, frame size,
and serializer assembly are frozen.

## Reproduce

```sh
make audit
make correctness
make benchmark
```

`benchmark` performs 16 fresh-process, paired SUPERcop-style launches for
Keypair, Encap, and Decap with ASLR both enabled and disabled.  See
`RESULTS.md` and `generated/benchmark-summary.json`.
