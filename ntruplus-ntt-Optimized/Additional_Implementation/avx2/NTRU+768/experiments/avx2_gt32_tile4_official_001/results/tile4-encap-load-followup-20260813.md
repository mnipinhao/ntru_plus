# CleanGT Encap load-quality and bounded follow-up

## Result

The exact +763-retired-load closure is real, but it is not a cache-miss debt
and it is not directly convertible into cycle savings.  The extra accesses are
warm-L1; measured L1/L2 misses are effectively zero, and store-forward,
address-alias and store-buffer blocking are also effectively zero.

The strongest stable backend signal belongs to general B3 and the two Q24
serializers.  The two Forward calls retire +358 loads, but their load-bound
counter is favorable or neutral: their extra loads overlap with arithmetic and
are not a valid reason to reopen N5.

## B3 finalizer + add(m) bounded probe

The probe leaves the qualified B3 arithmetic unchanged.  It consumes the four
SoA message planes in the existing R-squared output finalizer before the sole
final stores.  It therefore removes, per Encap:

- about 131 retired instructions;
- 49 retired loads;
- 49 retired stores;
- the standalone `poly_add` materialization boundary.

Correctness is byte-exact for cumulative stages 12--18 in both link orders and
the specialized symbol has no stack spill.  Nevertheless, 20 paired PMU runs
do not give a stable cycle win:

| Metric | Normal | Reversed |
|---|---:|---:|
| Direct edge core cycles (default group) | -24.28 (13/20) | +8.46 (10/20) |
| Direct edge core cycles (stall group) | +12.95 (10/20) | -64.96 (12/20) |
| Direct edge TSC (default group) | -14.70 (13/20) | +8.12 (10/20) |

The fixed work reduction is not cycle-stable and does not pass the required
two-placement, >=30-cycle continuation gate.  It remains benchmark-only and is
not connected to the production candidate.

## Q24 register-resident packet constants

Static attribution showed that each serializer has 48 memory-source
`vpmaddwd` pair factors and 48 memory-source `vpshufb` masks.  A benchmark-only
RR body keeps both constants in YMM registers while preserving the exact v=9
reducer, transpose, packet order, and stores.

The implementation removes exactly 94 retired loads per serializer (96
memory-source operands replaced by two entry loads), or 188 loads in full
Encap.  It adds only one or two retired instructions.  Yet the isolated result
is neutral to slightly slower:

| Edge | Normal core cycles | Reversed core cycles |
|---|---:|---:|
| Serialize r-hat | +3.59 | +4.18 |
| Serialize ciphertext | +0.36 | +0.41 |

The stall-event rerun agrees.  The full-prefix result remains noisy and cannot
override the precise isolated result.  Memory-source AVX2 operands are already
cheap and overlap well on this CPU; counting them as retired loads greatly
overstates their executable cost.  The RR variant is therefore a hard stop.

## Updated interpretation and remaining options

1. Do not optimize retired-load count as a proxy objective.  Require a stable
   cycle/critical-path mechanism.
2. Keep N5/B3/I1 arithmetic frozen.  N5 scratch removal and Q24-to-B3 streaming
   already failed because their larger coupled schedules lost reuse and ILP.
3. Do not hoist more Q24 constants.  This experiment directly disproves that
   the serializer's +95-load attribution is recoverable load-port headroom.
4. Do not production-integrate B3+add.  The boundary is another example where
   warm-L1 materialization is mostly hidden by the out-of-order core.
5. A future AVX2 candidate must remove a dependency or arithmetic layer, not
   merely memory-source operands.  Plausible reopen conditions are a changed
   range/scale contract that deletes the full R-squared finalizer, a changed
   decomposition, or a wider register/ISA domain.
6. For the current decomposition, the next useful work is cross-CPU validation
   or a fixed hybrid backend selection, not another Encap load-count rewrite.

Artifacts:

- `results/tile4-encap-load-attribution-pmu.json`
- `results/tile4-encap-load-stall-pmu.json`
- `results/tile4-encap-bm-add-fused-pmu.json`
- `results/tile4-encap-q24-rr-pmu.json`
- `bench/bench_encap_load_attribution.c`
- `tools/run_encap_bm_add_fused_pmu.py`
- `tools/run_encap_q24_rr_pmu.py`
