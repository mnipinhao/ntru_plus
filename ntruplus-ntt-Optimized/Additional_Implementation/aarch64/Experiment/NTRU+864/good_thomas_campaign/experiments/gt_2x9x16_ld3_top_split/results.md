# Results

Status: passed locally on 2026-08-28 on an Apple arm64 host.

The exact assembly differential test reported:

```text
gt864_top_split_ld3,total_mismatches=0
differential_cases=106
fixed_mul_checks=5185
output_coefficients=896
```

The cases include low-only and high-only index tags, the centered and canonical
range boundaries `-1728`, `1728`, `0`, and `3456`, and 100 deterministic
centered-random inputs.  The fixed-multiply gate exhausts `-1728..3456` and
checks congruence with `-722 * input mod 3457`.

`objdump -d` confirms two `ld3.8h` instructions in the main loop followed by
three `mul/sqrdmulh/mls` fixed-constant sequences.  The tail reads exactly six
bytes from each half, including at `t=15`; it does not over-read the input.

Static checks reported zero optional-feature warnings and zero
secret-dependent-flow warnings.  The pattern checker reported the expected
manual-review prompts for `dup`/`ins` lane operations and `sqrdmulh`.  Their
indices are public, and the signed rounding and range are covered by the exact
model and exhaustive fixed-multiply gate.

The complete campaign `make check` passed all five registered experiments.

No cycle or Production claim is made by this experiment.
