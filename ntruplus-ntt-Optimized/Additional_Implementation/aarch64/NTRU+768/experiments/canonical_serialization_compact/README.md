# Canonical pack compact shared-core experiment

This experiment is default-off and targets code size and L1I behavior.

The selected P1 implementation expands the same normalize/transpose/pack DAG
twelve times.  The compact candidate keeps each chunk's fixed-offset gather in
the caller and invokes one shared vector core:

```text
16 x ldr d + 8 x mov lane
    -> shared normalize/transpose/pack core
    -> 96 canonical output bytes
```

The arithmetic, range, permutation, and output-byte contracts are unchanged.
The expected tradeoff is substantially smaller text in exchange for twelve
`bl`/`ret` boundaries and less scheduling freedom between gather loads and the
vector arithmetic.

Promotion is not implied.  Correctness, ABI preservation, cycle PMU, symbol
size, and L1I refill behavior must all be measured against P1.
