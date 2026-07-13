# Forward NTT S2 Closeout

Date: 2026-07-09

## Decision

`s2_b2a_umov_str` is the selected serious experiment candidate for the
current rowspec Stage345 line.

Production default remains unchanged.  To build the GT production KEM with S2
as an opt-in forward NTT replacement:

```sh
GT_PRODUCTION_USE_ROWSPEC_S2_NTT=1
```

This flag replaces only the public `poly_ntt` wrapper path with:

```text
asm/gt/experiment/poly_ntt_rowspec_s2_b2a_umov_str_dropin.s
asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S
asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/s2_b2a_umov_str/row0_stage345_s2_b2a_umov_str.opt.s
asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/s2_b2a_umov_str/row1_stage345_s2_b2a_umov_str.opt.s
asm/slothy/experiments/ntt32_forward_ntt_aggressive_wave/s2_b2a_umov_str/row2_stage345_s2_b2a_umov_str.opt.s
```

The production `_gt_ntt32_batch8_to_blockmajor` object is still linked because other wrappers,
including keygen sample triple paths, still call the generic row kernel.

Pi 5 correctness confirmation for this flag:

```text
make test_gt_ntt32_batch8_ct_stage345_rowspec_s2_b2a_umov_str
  s2_b2a_umov_str_mismatches=0

make test_kem_gt_production_default GT_PRODUCTION_USE_ROWSPEC_S2_NTT=1
./build/test_kem_gt_production_default
  count: 0
  keygen=900 ticks, encap=880 ticks, decap=741 ticks
```

## Why S2

S2 is:

```text
B2a rowspec direct-offset Slothy base
  + high-half ext+str replacement
```

The important instruction change is:

```asm
ext  vTmp.16B, vSrc.16B, vSrc.16B, #8
str  dTmp, [addr]
```

to:

```asm
umov x17, vSrc.d[1]
str  x17, [addr]
```

This keeps the store address and store size unchanged, but avoids the vector
`ext` temporary and uses a scalar 64-bit store for the high half.

Current direct paired Pi 5 PMU:

```text
A production: 2707 cycles, 4010 instr
C B2a:        2697 cycles, 3434 instr
S2:           2654 cycles, 3434 instr
S2R:          2654 cycles, 3434 instr
S4:           2652 cycles, 3434 instr
```

S2 vs A:

```text
-53 cycles median direct poly_ntt
-576 retired instructions
```

S2 vs C:

```text
-43 cycles median direct poly_ntt
same retired instructions
```

The instruction count win comes from rowspec direct offsets versus production.
The extra cycle win over C comes from the high-half `umov+str` store shape.

## S2R Rejected As Replacement

`s2_b2a_umov_str_reslothy` reruns Slothy over the S2 tail windows.  It passes
correctness and can be built with:

```sh
GT_PRODUCTION_USE_ROWSPEC_S2_RESLOTHY_NTT=1
```

but it is not selected.

Direct paired PMU:

```text
S2R median cycles = 2654
S2  median cycles = 2654
S2R-S2 median delta = 0
```

KEM-context one-NTT PMU shows S2R is slower at the four measured NTT sites:

```text
encap_ntt_r:  S2R = S2 + 5.644 cycles
encap_ntt_m:  S2R = S2 + 6.428 cycles
decap_ntt_m1: S2R = S2 + 5.605 cycles
decap_ntt_r1: S2R = S2 + 5.590 cycles
```

Full KEM totals are noisy and mixed:

```text
keypair: S2R = S2 - 9.803 cycles
encap:   S2R = S2 + 1.956 cycles
decap:   S2R = S2 - 17.590 cycles
```

Conclusion: S2R is safe as an appendix candidate, but rerunning Slothy over
the S2 tail did not create a stable replacement.

## S4 Audited Reference

`s4_d1_umov_str` is audited and safe, but remains a reference candidate.

It combines the D1 precise-liveout scheduling base with the same high-half
`umov+str` transform.  Direct `poly_ntt` PMU is essentially tied with S2, and
some one-NTT component sites are slightly faster.  Full KEM is flat enough
that this does not justify replacing S2 as the selected base.

Keep S4 for comparison when testing future scheduling or store-shape changes.

## st1 Lane Rejected

The `st1 {vSrc.d}[1]` high-half variants are:

```text
S1 = B2a + st1 lane
S3 = D1 + st1 lane
```

They pass correctness, but direct PMU does not show the same win as `umov+str`:

```text
S1: 2697-2698 cycles range, approximately C-level
S3: 2694-2697 cycles range, far slower than S2/S4
S2: 2654 cycles
```

Conclusion: keep `st1 lane` as evidence, not as a production candidate.

## Twiddle1 Lazy Reduction Rejected

The twiddle=1 deletion idea is rejected under the current row-kernel input
contract.  The range model found:

```text
safe_to_delete: 0
unsafe_counterexample: 15
unknown: 0
```

The broad Phase123 input contract allows operands large enough that deleting
the identity-twiddle reduction changes the signed 16-bit lane value and the
final residue.  No ASM candidate should be emitted unless a future proof
establishes a narrower caller contract for specific sites.

Reference:

```text
experiments/ntt32_twiddle1_lazy_reduction/range_proof.md
```

## Kept Tests And PMU Targets

Keep these targets available:

```sh
make test_gt_ntt32_batch8_ct_stage345_rowspec_s2_b2a_umov_str
make test_s2_abi_sentinel
make -C ../../../aarch64-bench bench_gt_ntt_wave_pmu
python3 ../../../aarch64-bench/scripts/run_s2_selected_kem_context_pmu.py
```

Use `GT_PRODUCTION_USE_ROWSPEC_S2_NTT=1` for full KEM opt-in builds.  Do not
use S2R as the selected production candidate.
