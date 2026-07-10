# InvNTT next-wave experiments: tracks 2-5

Date: 2026-07-10

Track 2 has been promoted to the production rminus1 InvNTT path. Tracks 3-5
remain default-off experiments. The historical pre-promotion implementation is
still available through
`GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16=0` for differential and PMU
comparison.

## Measurement

Pi 5 Cortex-A76, core 3, Linux `perf_event_open`, paired rotating order:

- 61 samples.
- 20,000 calls per full InvNTT sample.
- 50,000 calls per boundary-kernel sample.
- cycles and retired instructions measured as one PMU group.

## Result summary

| Track | Baseline cycles | Candidate cycles | Paired delta | Decision |
|---|---:|---:|---:|---|
| 2. Twiddle=1 lazy through len16, production | 4002.60 | 3558.62 | -443.95 | promoted; production default |
| 3. Three-output post Slothy, core-to-core | 4002.72 | 4003.94 | +1.26 | reject as flat |
| 4. Stage45 -> post one-vector handoff | 122.25 | 116.00 | -6.25 | keep isolated evidence |
| 5. Stage123 -> Stage45 stripe0 handoff | 354.00 | 352.75 | -1.25 | pause |

The paired delta is the median of per-sample candidate-minus-baseline values;
it can differ slightly from subtracting the two independent medians.

## Track 2: proof-gated twiddle=1 deletion

The inverse NTT32 Stage123 transform sizes are 2, 4, and 8. The selected
candidate also covers the two multiplier-1 butterflies in transform size 16.
Production executes:

```text
sqrdmulh + mul + mls
```

for these identity products. The candidate replaces them with the direct
butterfly and defers reduction:

```text
lo' = lo + hi
hi' = lo - hi
```

There are 16 + 8 + 4 + 2 = 30 identity sites per row and three rows. This
removes 270 dynamic vector instructions. The conservative bound is:

```text
input centered bound          1728
after transform size 2        3456
after transform size 4        6912
after transform size 8       13824
after transform size 16      27648
after retained size 32       29376
```

The selected candidate leaves the transform-size-32 multiply and row-end
Barrett reduction unchanged. Deleting the transform-size-32 identity multiply
is not safe under this model: the DC path can reach 55296 before reduction.
See `twiddle1_range_proof.md` and `twiddle1_range_proof.json`.

Direct same-binary PMU after promotion:

| Variant | cycles | instructions | CPI |
|---|---:|---:|---:|
| historical production baseline | 4002.60 | 5074 | 0.7888 |
| promoted production | 3558.62 | 4814 | 0.7392 |
| Stage123-only ABI-safe | 3593.28 | 4834 | 0.7433 |
| through-len16 core | 3555.04 | 4804 | 0.7400 |
| through-len16 ABI-safe | 3559.16 | 4816 | 0.7390 |

The promoted in-core production path retires 260 fewer instructions: 270
arithmetic instructions are deleted and 10 in-frame instructions preserve and
restore `d8-d15`. The older standalone experiment used an outer call wrapper,
so its net reduction was 258 instructions instead.

Validation:

- 516 actual `poly_ntt -> poly_basemul_rminus1 -> InvNTT` differential cases.
- exact output, in-place output, and ABI sentinel all pass.
- current G1R123+S2 full KEM: 100,000 iterations, `count: 0`.
- historical baseline and promoted production NIST KAT responses are
  byte-identical; SHA-256 is
  `dca76b32748655990289002a05f7b1d648334d7ded05845c7fe3f1449d26690f`.
- production ABI sentinel preserves `x19-x28` and the AAPCS64-required low
  halves `d8-d15`; mask is `0x0`.

Same-binary paired full-KEM PMU (`61 x 2000`, alternating AB/BA):

| Scope | historical baseline | promoted production | promoted-minus-baseline paired p50 | promoted win rate |
|---|---:|---:|---:|---:|
| encapsulation control | 37615.06 | 37613.13 | -0.80 | noise/flat |
| decapsulation | 33223.02 | 32771.96 | -451.16 | 61/61 |

Decapsulation retires 260 fewer instructions. Its promoted-minus-baseline
paired delta range is -455.67 cycles at p10 to -448.13 cycles at p90, with
MAD 2.23 cycles. All 732 paired correctness checks pass.

The promoted implementation is the default. The historical baseline remains
available as an explicit fallback:

```sh
make test_kem_gt_production_default \
  GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16=0
```

The production implementation preserves the AAPCS64 callee-saved low halves
`d8-d15` inside its existing frame. The historical baseline is retained only
as a reproducible pre-promotion reference and does not provide that fix.

## Track 3: branchfold/post scheduling

The symbolic window contains the three independent branchfold outputs after
one inverse DFT3: 69 instructions, six exact 8-byte stores, no spills. Slothy
uses the Neoverse N1 model and a driver-local parser extension for the missing
general-address `str d, [xN,#imm]` variant. Pi assembly and differential tests
are the acceptance gate.

The scheduled core is flat:

| Variant | cycles | instructions | paired delta |
|---|---:|---:|---:|
| production core | 4002.72 | 5074 | 0.00 |
| post Slothy core | 4003.94 | 5074 | +1.26 |
| post Slothy ABI-safe | 4010.39 | 5086 | +7.72 |

Therefore the N1 schedule is rejected. It should not be combined with Track 2.
The symbolic source, driver, generated output, and integration script remain as
reproducible negative evidence.

## Track 4: Stage45 to inverse DFT3 handoff

The isolated correctness kernel replaces:

```text
Stage45 q17 -> str row2[k=0] -> ldr q3 -> inverse DFT3
```

with:

```text
Stage45 q17 -> mov q3, q17 -> inverse DFT3
```

It removes one store and one load, inserts one vector move, and preserves all
arithmetic, reductions, branchfold constants, and final stores.

PMU is positive: 122.25 -> 116.00 cycles, with 155 -> 154 instructions. This
is worth a later full-path integration attempt, but it is not yet a full
InvNTT candidate. The main integration problem is arranging the final row2
Stage45 consumption order without regressing the existing all-stripe schedule.

## Track 5: Stage123 to Stage45 stripe0 handoff

Four Stage123 group outputs for stripe0 are kept in registers and used by one
Stage45 stripe. The experiment removes four q stores and four q loads. It must
also add three parking moves while later Stage123 groups are computed and four
moves into the Stage45 consumer register contract.

The net instruction change is therefore only one instruction:

```text
-4 stores -4 loads +3 parking moves +4 consumer moves = -1 instruction
```

PMU is correspondingly small: 354.00 -> 352.75 cycles. This does not justify
replacing the production all-stripe Stage45 schedule or expanding the fusion
before a consumer-shaped Stage123 allocation eliminates most of the moves.

## Commands

```sh
make -B test_invntt_lazy_twiddle1_stage123
make -B test_invntt_boundary_experiments
make -B test_kem_invntt_lazy_twiddle1_stage123
make -B test_kem_invntt_lazy_twiddle1_stage123_len16
make -B test_invntt_production_abi
make -B test_kem_gt_production_default
make -B test_kem_gt_production_default \
  GT_PRODUCTION_USE_INVNTT_LAZY_TWIDDLE1_LEN16=0
make -B bench_invntt_next_wave_pmu
taskset -c 3 ./build/bench_invntt_next_wave_pmu

cd ../../../aarch64-bench
make -B bench_invntt_lazy_len16_paired_kem_pmu
make -B bench_invntt_promoted_paired_kem_pmu
```
