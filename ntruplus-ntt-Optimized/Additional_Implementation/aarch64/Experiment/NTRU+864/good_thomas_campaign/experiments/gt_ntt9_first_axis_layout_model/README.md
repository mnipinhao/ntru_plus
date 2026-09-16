# M5A-E2E-AUDIT1: exact NTT9-first axis/layout model

This default-off design audit asks whether the current `top split -> NTT16 ->
NTT9` Forward should be replaced by `top split -> NTT9 -> NTT16` before CF5-B
assembly is written.  It changes no Production source.

The audit separates two often-confused questions:

1. can the current row-major P8 layout physically expose NTT9 rows and then
   feed NTT16 without a new coefficient-memory pass;
2. can the column-dependent mathematical phase cross NTT16 for free.

The answer is **yes** to the first and **no** to the second.  The axis candidate
is therefore rejected.  `REGISTER_FLOW.md` gives the full register and
coordinate interpretation; `audit-results.json` contains every LD3 register
lane for all sixteen `t` values and the complete CRT gather map.

Run:

```sh
make report
make check
```

The checked model proves all 864 P8 and FR-ISO2 maps are bijective, simulates
both 8x8 transposes, computes the exact nine-point DFT conjugations over
`q=3457`, and evaluates the canonical Good-Thomas CRT packing escape route.
