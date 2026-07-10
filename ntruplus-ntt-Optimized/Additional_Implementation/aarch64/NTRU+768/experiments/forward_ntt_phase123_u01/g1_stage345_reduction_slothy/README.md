# G1 Stage345 Final-Reduction Slothy Experiment

This experiment schedules only the late Stage345 arithmetic/reduction/scatter
region of each G1 block. The region starts at the first final Barrett
`sqdmulh` and ends at the final block instruction.

It is intentionally not another load-elimination experiment. Physical register
allocation, arithmetic, Barrett reduction, output addresses, store shapes, and
the complete instruction multiset are frozen. Slothy may only reorder
instructions with `allow_renaming=false` and `allow_spills=false`.

Generate inputs:

```sh
python3 experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/generate_g1_stage345_reduction_slothy.py
```

Run on the Slothy host:

```sh
SLOTHY_PATH=$HOME/slothy python3 \
  experiments/forward_ntt_phase123_u01/g1_stage345_reduction_slothy/optimize_g1_stage345_reduction.py
```

Production remains unchanged. A scheduled wrapper is generated only from
outputs that pass the instruction-multiset gate; rejected blocks retain the
original G1 instruction order.

## Result

Block1/2/3 reached optimal N1 schedules and passed Slothy self-check plus the
exact instruction-multiset gate. Block0 remained unchanged because its inherited
`stack_0` spill/restore handoff made the full tail immediately infeasible even
when those existing spills were explicitly modeled.

The resulting `G1R123` and `G1R123+S2` wrappers pass full `poly_ntt`
differential, in-place tests, ABI sentinels, and KEM correctness. Long Pi5 paired
PMU measured G1R123 at -7 cycles versus G1 and G1R123+S2 at -11 cycles versus
G1+S2. The KEM-context one-NTT boundary confirms about -10 cycles for R123;
the extra combination gain over G1+S2 is only about 2 cycles per site.
