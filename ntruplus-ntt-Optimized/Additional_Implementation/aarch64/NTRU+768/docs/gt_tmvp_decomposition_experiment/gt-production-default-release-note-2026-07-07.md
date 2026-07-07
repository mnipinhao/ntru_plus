# GT production default release note, 2026-07-07

Scope: NTRU+768 GT production default on Raspberry Pi 5 / AArch64 Neon.

## Decision

Promote the Wave 4 combination into `gt_production_default`:

```text
GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY=1
GT_BASEINV_USE_HIER_K8_TREE=1
```

The existing production defaults remain enabled:

```text
GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP=1
GT_PRODUCTION_USE_RMINUS1_DECAP=1
GT_PRODUCTION_USE_SCALED_KEYPAIR=1
GT_BASEINV_USE_FQINV15_ASM=1
GT_BASEINV_BATCH_USE_ASM_FINISH=1
GT_BASEINV_USE_HIER_K8=1
```

## Kill switches

Both promoted keygen changes have explicit build fallback switches:

```text
GT_PRODUCTION_DISABLE_KEYGEN_SAMPLE_NTT_TRIPLE_SLOTHY=1
GT_PRODUCTION_DISABLE_HIERK8_TREE=1
```

## Guard results

The release guard confirms:

```text
sample_hierk8 default release_guard_pass=1
sample_hierk8 sample-off release_guard_pass=1
sample_hierk8 hier-off release_guard_pass=1
generic_poly_ntt_symbols=1
generic_poly_baseinv_scaled_r_symbols=1
sample_dag_call_sites=2
experiment_tree_symbol_present=0
public_headers_with_internal_symbols=0
```

The Q31 guard was re-run after this promotion:

```text
q31 enabled release_guard_pass=1
direct32_q31_call_sites=1
direct32_q31_call_site=gt_encap_basemul_add_tobytes_contract
generic_poly_basemul_add_overwritten=0
decap_or_arithmetic_q31_callers=0
public_headers_with_q31_symbol=0
q31 disabled release_guard_pass=1
```

## Production PMU

Latest production default KEM PERF medians:

| mode | cycles |
| --- | ---: |
| keygen | 37978 |
| encap | 37749 |
| decap | 33075 |

Latest component-profile totals:

| row | cycles/call | instr/call |
| --- | ---: | ---: |
| keypair_total | 38251.234 | 81708 |
| encap_total | 37632.930 | 105879 |
| decap_total | 33305.420 | 75190 |

Correctness:

```text
component profile: correctness,total_mismatches=0,valid_cases=64
scheme test: count: 0
```

## KPQC final comparison

Same harness, `aarch64-bench`, Pi5 `CORE=3`:

| mode | GT production | KPQC final | GT reduction |
| --- | ---: | ---: | ---: |
| keygen | 37978 | 39966 | 1988 cycles, 4.97% |
| encap | 37749 | 39095 | 1346 cycles, 3.44% |
| decap | 33075 | 35165 | 2090 cycles, 5.94% |

## Notes

Q31 remains an encap-only byte-contract path and is not a generic
`poly_basemul_add` replacement.  The SAMPLE-DAG path is keygen-only and does
not replace generic `poly_ntt`.  The HIERK8 tree path does not link the
benchmark-only experiment tree symbol into production.
