# Results

Status: local scalar correctness gate passed on 2026-08-26.

Command:

```sh
make check
```

Compiler command:

```text
cc -O2 -std=c99 -Wall -Wextra -Wpedantic -Werror \
  -o build/test_gt864_reference \
  gt864_reference.c test_gt864_reference.c
```

Observed result:

```text
gt864_scalar_reference,total_mismatches=0
forward_direct_cases=36
roundtrip_cases=36
multiplication_schoolbook_cases=21
alias_cases=93
```

The forward cases include structured boundaries, selected impulses, and
deterministic random polynomials. Multiplication compares the complete
forward/cubic-basemul/inverse path with independent schoolbook convolution and
trinomial reduction.

No benchmark is authorized for this reference experiment.
