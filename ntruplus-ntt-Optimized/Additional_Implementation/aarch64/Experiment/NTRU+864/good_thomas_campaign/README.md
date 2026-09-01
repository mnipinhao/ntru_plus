# NTRU+864 Good-Thomas campaign

This is the default-off development front door for the NTRU+864 Good-Thomas
campaign. Production remains in `../../NTRU+864/` and does not include this
directory.

Reading order:

1. `PLAN.md` — campaign phases and promotion gates.
2. `LEARNING_PROTOCOL.md` — evidence labels and explanation standard.
3. `ring-profile.yml` — scheme and representation facts.
4. `REFERENCE.md` — authoritative GT C reference and oracle hierarchy.
5. `experiments/README.md` — active experiment registry.
6. `experiments/optimization_scoreboard.md` — decisions and next actions.
7. The selected experiment's contracts, checker, results, and decision.

Run all currently implemented static/correctness gates:

```sh
make check
```

This target does not build or link Production and does not run benchmarks.

Current checkpoint: M5A `experiments/gt_fr0_kernel_realization` is the frozen
first handwritten FR-0 assembly baseline. It passes exact differential,
stack/register, formal-range, and leaf-map gates. Its producer bound is
`|P8+tail| <= 15752`. M5B `experiments/gt_ntt16_producer_range` now proves the
actual twisted radix-2 producer reaches at most 8874 with no extra Barrett
reduction. Its intrinsics spill, so assembly memory scheduling remains open;
M5C `experiments/gt_fr0_basemul_arithmetic` now consumes the generated zetas
in working BaseMul/BaseMulAdd tile arithmetic with proved int32/R0 bounds. M5D
`experiments/gt_fr0_inverse_consumer` closes the matching inverse arithmetic:
inverse NTT9 returns FR-0 to P8+tail, while packed alpha/beta inverse NTT16 and
top recombination finish in the second pass without a top-branch scratch.
M5E `experiments/gt_fr0_inverse_asm_realization` realizes that exact two-pass
map in handwritten Neon. Its arithmetic blocks have no stack, coefficient
spill, callee-saved vector use, or branches, and the local component diagnostic
is faster than the M5D intrinsics. The fully unrolled inverse costs 10,744 code
bytes, so target instruction-cache attribution remains mandatory. Handwritten
forward composition, full KEM, and SUPERCOP remain future gates.

Run only the authoritative GT C reference gate:

```sh
make check-reference
```
