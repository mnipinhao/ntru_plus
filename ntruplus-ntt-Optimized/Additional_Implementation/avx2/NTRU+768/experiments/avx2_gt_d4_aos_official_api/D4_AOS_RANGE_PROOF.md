# d4AoS reference range proof

All externally observable reference values are canonical integers in
`[0,3456]`.  Inputs to the coefficient wrapper may be any `int16_t`; they are
reduced before entering the transform.  The proof below is for the scalar C
reference and must not be reused as a lazy-AVX2 range proof.

| Operation | Conservative unreduced bound | Storage before reduction |
| --- | ---: | --- |
| CRT forward term `a + alpha*b` | `< 9,468,000` | `int64_t` |
| one 96-term forward accumulation | `< 3.15e12` | `int64_t` |
| inverse DFT sum | `< 1.15e9` | `int64_t` |
| inverse DFT times `96^-1` | `< 3.93e12` | `int64_t` |
| quartic direct convolution | `< 4.78e7` | `int64_t` |
| quartic zeta fold | `< 1.66e11` | `int64_t` |
| natural 768-term schoolbook test oracle | `< 9.18e9` before ring folds | `int64_t` |

Every bound is far below `INT64_MAX` (approximately `9.22e18`).  Reduction is
performed before every `int16_t` store; `[0,3456]` fits `int16_t`.  The inverse
CRT multiplication is likewise reduced before its stores.  The test covers
`0`, `+/-1`, `+/-2`, `+/-3`, both edge representatives around the modulus, and
the signed `int16_t` extremes, distinguishing exact equality after canonical
reduction from merely congruent values.

The reference does not model Official's undisclosed NTT intermediate range,
Montgomery scale, or any checked-wire failure state.  Those are explicit
unavailable/bridge items in the coverage ledger, not assumptions.
