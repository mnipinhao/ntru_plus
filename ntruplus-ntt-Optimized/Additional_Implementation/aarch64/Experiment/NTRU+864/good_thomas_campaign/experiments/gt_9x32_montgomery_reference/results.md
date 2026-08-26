# Results

Status: local Montgomery representation gate passed on 2026-08-26.

Standard command:

```sh
make check
```

Sanitizer command used the same source and test with:

```text
-O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer
```

Final result under both builds:

```text
gt864_montgomery_reference,total_mismatches=0
exact_current_forward_cases=32
exact_current_basemul_cases=17
current_inverse_modq_cases=32
centered_roundtrip_cases=32
full_product_cases=17
alias_cases=81
```

## Preserved failed observation

The first basemul differential run reported 12 exact-representative mismatches,
for example:

```text
candidate=1724 current=-1733
candidate=1715 current=-1742
```

Every pair differed by exactly `q=3457`, so scale and algebra were correct. The
cause was an invalid extra centered normalization in the grid-to-legacy layout
adapter. The current basemul output is bounded `R^0`, not necessarily centered.

The adapter was corrected to perform a raw int16 permutation only. After that
change exact basemul equality passed. This is now a contract rule: index/layout
conversion must not silently perform representative conversion.

No benchmark is authorized for this representation experiment.
