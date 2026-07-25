# R-minus-one basemul pair pipeline

Status: promoted to GT production; the reproducible experiment remains here.

This experiment replaces two dynamic iterations of the production
`poly_basemul` loop with one two-group scheduling region. It does not change:

- quartic multiplication modulo `X^4 - lambda`;
- Montgomery reduction arithmetic;
- the row-bit-reversed block-major input/output layout;
- the raw output factor, which remains `R^-1`;
- the public 24-group loop trip count.

The production physical allocation keeps the second iteration's `ld4` and
lambda load late because its input registers overlap the first iteration's
output registers. The candidate gives the two iterations distinct symbolic
values, then asks Slothy to allocate and schedule the complete pair without
spills.

The exact baseline is generated from
`asm/gt/basemul/poly_basemul_body.inc`; generated candidate assembly remains
reproducible from the symbolic source and remote Slothy log. The compact
production artifact is
`asm/gt/basemul/poly_basemul_rminus1.n1.opt.S`.

## State

```text
mode: existing_region_replacement
target model: Neoverse N1 scheduling candidate
hardware decision target: Raspberry Pi 5 Cortex-A76
allow_spills: false
production default: unchanged
```
