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
map modulo q in handwritten Neon. M5E-r1 uses paired Algorithm-10 fixed Barrett
constants and grouped independent operations. Its arithmetic blocks have no
stack, coefficient spill, callee-saved vector use, or branches; code size is
7,292 bytes and the local combined diagnostic is 545.354 ns versus 1065.938 ns
for M5D intrinsics. Target attribution remains mandatory. Handwritten
M5F `experiments/gt_forward_composition_barrett` now proves the forward
NTT16-to-NTT9 schedule can consume every meaningful P8 coefficient once and
write every FR-0 coefficient once without an intermediate NTT16 boundary. Its
M5F-r2 `experiments/gt_forward_barrett_reduction_search` records the historical
four-product reduction search. M5G `experiments/gt_forward_symbolic_dag`
changes B3 to two products and supplies the current correlation-aware proof:
NTT16 reaches 9342 and the exact full-Forward DAG reaches 28568 with zero
unsafe halfword nodes. Its 15-instruction B3 is written entirely with Slothy
symbolic registers. The remote Slothy gate is OPTIMAL at 24 N1-proxy cycles
and allocates exactly `v0,v24-v31`, with no spill, stack, memory, GPR, or
forbidden-vector instruction. The whole schedule still peaks at 24
caller-saved vector registers. Surrounding NTT9 realization, handwritten
forward integration, full KEM, and SUPERCOP remain future gates.

Run only the authoritative GT C reference gate:

```sh
make check-reference
```
