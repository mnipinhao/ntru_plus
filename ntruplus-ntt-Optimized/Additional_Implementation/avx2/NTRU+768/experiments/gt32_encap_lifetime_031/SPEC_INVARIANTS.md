# Encap 031/032 spec invariants

The optimization boundary is NTRU+ Encap Algorithm 12.  Internal storage,
aliasing and final-store scheduling may change; the following semantic edges
may not.

## Immutable algorithm edges

```text
r = CBD1(randomness)
r_hat = NTT(r)
r_bytes = Encodeq(r_hat)
mask = G(r_bytes)
m = SOTP.Encode(message, mask)
m_hat = NTT(m)
h_hat = Decodeq(pk), rejecting every noncanonical coefficient
c_hat = h_hat o r_hat + m_hat
ciphertext = Encodeq(c_hat)
```

`F`, `G`, and `H` retain their existing domain separation, input bytes and
ordering.  In particular, hashing a private M representation is not equivalent
to `G(Encodeq(r_hat))`.

## 031 lifetime reduction

031 changes only the storage schedule:

```text
frontend(c, work); NTT_M(r, c)
    ->
frontend(r, work); NTT_M(r, r)
```

and the corresponding `m` path.  Its executable gate requires:

- exact `r_hat` and `m_hat` words, not only congruence modulo q;
- byte-exact `Encodeq(r_hat)` before `G`;
- byte-exact final ciphertext and shared secret;
- identical rejection for every serialized public-key slot containing q;
- no change to CBD1, SOTP, hash calls, Decodeq, B3, add or Q24;
- an independently tested `out == in` NTT_M contract.

## 032 B3 final-store add-m

032 is not implemented by 031.  It may proceed only after separately proving:

1. B3 output lane and `m_hat` lane denote the same `(index, degree)` under the
   exact M bijection.
2. The four degree bounds after addition are at most
   `[12580,12626,12676,12699]`, hence signed `vpaddw` cannot wrap.
3. The output remains exponent `e=0` and represents
   `h_hat o r_hat + m_hat` modulo 3457.
4. `pack_m_highrange12699` emits the same canonical bytes as spec Encodeq.
5. Decodeq canonical rejection and all hash boundaries remain untouched.

Internal raw-word equality with `B3 + poly_add` is a debugging invariant.  The
spec-visible acceptance criterion is byte-exact final Encodeq output.
