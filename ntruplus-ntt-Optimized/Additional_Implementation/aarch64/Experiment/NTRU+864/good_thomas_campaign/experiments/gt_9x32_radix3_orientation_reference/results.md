# Results

Status: passed locally on 2026-08-26.

The standard and ASan/UBSan builds both reported:

```text
gt864_radix3_orientation,total_mismatches=0
exact_horner_forward_cases=39
exact_current_forward_cases=39
full_product_cases=21
schoolbook_product_cases=21
alias_cases=60
```

The standard build used `-O2 -std=c99 -Wall -Wextra -Wpedantic -Werror`.
The sanitizer build additionally used `-fsanitize=address,undefined` and
`-fno-omit-frame-pointer`.

The cases contain coefficient-range boundaries, ten impulses selected to expose
the branch/residue/degree index split, and deterministic randomized inputs.

This proves the oriented radix-3 NTT9 identity under the NTRU+864 Montgomery and
row-major GT contracts. It does not prove a cycle improvement: the readable C
candidate makes the lambda twist explicit and writes canonical output order.
