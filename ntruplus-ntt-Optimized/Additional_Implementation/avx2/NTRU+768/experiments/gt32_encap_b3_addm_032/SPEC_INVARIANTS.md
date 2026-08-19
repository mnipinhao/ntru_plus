# 032 specification invariants

- Canonical serialized public-key interpretation is unchanged.
- Every serialized coefficient greater than or equal to `q` is rejected with
  the same fixed-flow behavior as 031.
- `h_hat`, `r_hat`, and `m_hat` use the same private M SoA lane mapping.
- B3 general output, Forward output, and their sum all have Montgomery
  exponent `e=0`.
- The candidate changes only when `m_hat` is added; the quartic product and
  B3 reduction DAG are unchanged.
- The current selected executable has a generated conservative terminal bound
  of 18424, not the obsolete 10788 bound.
- The four fused sum planes are conservatively bounded by 20215, 20250,
  20285, and 20296, so signed `vpaddw` cannot wrap.
- Q24 output must remain byte-exact with the baseline canonical serializer.
- Ciphertext, shared secret, failure return, and zero-on-rejection behavior
  must remain exact.
- GT Clean production sources are outside this experiment and remain
  untouched.
