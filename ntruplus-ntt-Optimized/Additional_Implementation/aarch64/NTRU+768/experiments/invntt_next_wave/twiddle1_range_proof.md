# InvNTT twiddle=1 range proof

Input contract: centered coefficients in `[-1728, 1728]`.

| candidate | max abs | int16 safe | decision |
|---|---:|---|---|
| `stage123_only` | 17280 | yes | proof-only |
| `through_len16` | 29376 | yes | selected |
| `all_identity_sites` | 55296 | no | rejected |

The selected candidate removes 30 identity modular multiplies per row,
or 270 dynamic vector instructions across three rows. The len32 stage
and row-end Barrett reductions remain unchanged.

Deleting every identity multiply is unsafe under this contract: the
DC path reaches 55296 before the final row reduction.
