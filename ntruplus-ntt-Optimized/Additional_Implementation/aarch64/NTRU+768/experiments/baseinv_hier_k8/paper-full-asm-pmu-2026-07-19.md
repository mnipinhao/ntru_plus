# Paper HIER_K8 Full ASM Candidate

This report records the benchmark-only complete paper-HIER_K8 candidate. The
production default is unchanged.

## Candidate

Entrypoint:

```text
asm/gt/experiment/poly_baseinv_scaled_r_hier_k8_paper_full_asm.S
poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate
```

The data flow is:

```text
prepare2 Slothy
  -> den[24], c01[8], group[8]
  -> balanced group tree 8 -> 4 -> 2 -> 1
  -> one gt_fqinv15_asm call
  -> balanced inverse tree 1 -> 2 -> 4 -> 8
  -> two-group-interleaved group3 recovery
  -> baseinv_batch_finish24_n1_asm
```

The group inverses are consumed directly by group3 recovery. They are not
stored to and reloaded from group scratch after the scalar inverse. The
forward tree uses four-way and two-way independent Montgomery-product groups;
the outer recovery processes two independent three-denominator groups per
window.

Only the prepare2 kernel has been scheduled by Slothy. The new balanced tree
and recovery body are hand-interleaved ASM and have not been scheduled by
Slothy.

The linked candidate symbol is 1848 bytes. The older serial-prefix complete
ASM symbol is 1032 bytes. This candidate deliberately spends text size to
expose independent product branches.

## Correctness

Pi5, core 3:

```text
baseinv and downstream exact cases: 4096
finv/ginv exact mismatches:         0
h/hinv exact mismatches:            0
h/hinv serialized mismatches:       0
zero failure/clear mismatches:       0

deterministic KEM seeds:             256
pk/sk byte mismatches:               0
decapsulation failures:              0
shared-secret mismatches:            0
```

## Pi5 PMU

Same-binary baseinv benchmark, two `poly_baseinv_scaled_r` calls per row,
31 medians and 3000 iterations:

| variant | cycles | instructions | delta vs paper full ASM |
| --- | ---: | ---: | ---: |
| GT production current | 9089 | 8400 | +857 cycles |
| prepare2 Slothy + old serial tree | 8580 | 7970 | +348 cycles |
| old complete serial-tree ASM | 8604 | 7970 | +372 cycles |
| prepare2 Slothy + C/Neon paper tree | 8308 | 7948 | +76 cycles |
| paper full ASM | 8232 | 7860 | baseline |
| KPQC Final native baseinv | 8058 | 8544 | -174 cycles |

Same-binary full-keygen benchmark, 31 medians and 100 iterations:

| variant | cycles | instructions | delta vs paper full ASM |
| --- | ---: | ---: | ---: |
| GT production current | 38490 | 83134 | +856 cycles |
| prepare2 Slothy + C/Neon paper tree | 37694 | 82682 | +60 cycles |
| paper full ASM | 37634 | 82592 | baseline |

The paper full ASM improves the current GT production keypair by 856 cycles,
or 2.22%, in this same-binary harness. It improves the C/Neon paper candidate
by 60 cycles in full keygen.

## Why Native KPQC Baseinv Is Still Faster

Fresh stage measurements on the same Pi5:

| two-operand stage | cycles | instructions | IPC |
| --- | ---: | ---: | ---: |
| GT original quartic prepare (`ld4/st4`) | 5678 | 5435 | 0.957 |
| GT prepare2 Slothy | 4966 | 5036 | 1.014 |
| KPQC contiguous-Q prepare | 4169 | 5025 | 1.205 |
| GT C/Neon paper denominator tree | 1869 | 1869 | 1.000 |
| KPQC flat denominator batch | 2749 | 2285 | 0.831 |

The decisive subtraction is diagnostic but clear:

```text
GT paper full post-prepare: 8232 - 4966 = 3266 cycles
KPQC post-prepare:          8058 - 4169 = 3889 cycles

GT post-prepare advantage: 623 cycles
KPQC prepare advantage:    797 cycles
net KPQC baseinv advantage: 174 cycles
```

Therefore KPQC does not have a better denominator inversion tree. Its native
contiguous-Q NTT-domain contract lets `poly_baseinv_1` use regular Q loads and
stores and sustain higher IPC. GT's block-major quartic contract requires
`ld4/st4` and deinterleaving work in prepare. The two prepare paths retire
almost the same instruction count, but KPQC completes them 797 cycles sooner.

The KPQC native layout is not a valid drop-in GT adapter. The prior local
transpose round trip produced 97241 inverse mod-q mismatches and 72922 product
mod-q mismatches because branch order and lambda correspondence also differ.

## Decision

Keep the paper full ASM as a positive benchmark-only candidate. It is the
fastest semantically valid GT baseinv measured in this experiment, but the
remaining isolated-baseinv gap is now a prepare/layout problem. Scheduling the
balanced tree may recover tens of cycles; it cannot explain or remove the
measured 797-cycle prepare gap.

The next high-value experiment is a baseinv-specific forward-NTT endpoint or
explicit bridge that emits the exact contiguous-Q branch/lambda contract
needed by baseinv while preserving the matching GT basemul path. Any such
contract change must be evaluated as `NTT -> baseinv -> basemul`, not by the
isolated baseinv row.
