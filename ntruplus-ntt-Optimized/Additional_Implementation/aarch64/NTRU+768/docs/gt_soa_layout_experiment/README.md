# GT Rowpack SoA Experiment Map

This directory tracks the opt-in rowpack/SoA experiment for the NTRU+768
Good-Thomas pipeline.  Production GT symbols remain on the existing promoted
path unless a target explicitly opts into the rowpack files listed here.

## Current State

The current best rowpack candidate is:

```text
Forward NTT rowpack-v2 Slothy output
  + native rowpack basemul/add from the fullpath harness
  + lazy no-entry/no-end InvNTT32 rowkernel
  + hand-written ASM native postmerge
```

It is selected by the `ROWPACK_FORWARD_NTT_ASM`,
`ROWPACK_NATIVE_BASEMUL`, `ROWPACK_NATIVE_POSTMERGE`,
`ROWPACK_NATIVE_POSTMERGE_CHUNKED_GATHER`,
`ROWPACK_NATIVE_POSTMERGE_ASM`, `ROWPACK_PIPELINE_INVNTT_INPLACE`, and
`ROWPACK_CHECK_FINAL_BOUNDED` macros in the opt-in Makefile targets.

Latest Pi5 evidence says this is a strong experimental continue path, not a
production replacement yet:

- product pipeline gap: about `+94` to `+111` cycles versus promoted GT across
  the latest compare/accounting runs;
- product-add pipeline gap: about `+560` to `+624` cycles versus promoted GT
  across the latest compare/accounting runs;
- lazy rowpack InvNTT is about `4.04k` cycles, essentially matching promoted
  GT InvNTT on the latest run;
- the product-add gap is accounted by visible component costs, not hidden glue:
  Forward NTT x3 is about `+1040` cycles versus promoted GT, while native
  basemul_add recovers about `-337` cycles and unaccounted glue is about
  `-98` cycles in rowpack's favor;
- the rowpack Forward NTT overhead is currently explained by output
  scatter/transpose: direct scatter-only probe is about `319` cycles, while
  the rowpack compute-only estimate is within about `2` cycles of production
  GT Forward;
- Forward output store lower bound is about `97-109` cycles, leaving roughly
  `210-223` cycles/NTT recoverable if a register-order candidate can emit
  rowpack plane vectors directly;
- the lane-store scatter candidate is rejected: it is about `1.67k` cycles
  slower than the current transpose-plus-vector-store path;
- production GT Forward plus scalar GT-to-rowpack conversion is not viable:
  the scalar conversion probe is about `3363` cycles;
- production GT path is still the promoted default.

## Read Order

Read these first to understand the implementation:

1. `docs/gt_soa_layout_experiment/component-productionization-dashboard.md`
   - Decision log, Pi5 cycle tables, and stop/continue criteria.
2. `docs/gt_soa_layout_experiment/rowpack-invntt-post-fused-contract.yml`
   - Rowpack InvNTT/postmerge ABI, range contracts, evidence, and validation
     gates.
3. `Makefile`
   - Variables near `ROWPACK_INVNTT32_*`,
     `ROWPACK_INVNTT_POSTMERGE_ASM`, and `ROWPACK_FORWARD_NTT_V2_ASM`.
   - Current best gates:
     `test_gt_rowpack_lazy_postmerge_asm_fullpath`,
     `bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles`, and
     `bench_gt_rowpack_lazy_postmerge_asm_cycles_compare`.
4. `gt_test/test_gt_rowpack_soa_invntt32_fullpath.c`
   - The opt-in fullpath harness, native rowpack basemul/add, postmerge
     dispatch, and final bounded-output checks.
5. `asm/slothy/README.md`
   - Forward/InvNTT Slothy context and production-vs-experimental assembly
     notes.

Then read the active assembly files:

- `asm/slothy/ntt32_v2_symbolic.s`
- `asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s`
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_no_entry_no_end.S`
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S`

For production baseline comparison, read:

- `asm/my_ntt.s`
- `asm/slothy/my_32ntt.opt.s`
- `asm/inv_my_ntt.s`
- `asm/slothy/invntt_opt.s`
- `asm/base_gt.opt.s`
- `gt_test/bench_ntt_pipeline.c`

## Active Rowpack Candidate Graph

```text
Forward NTT:
  asm/my_ntt.s
    includes asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s
    via ROWPACK_FORWARD_NTT_ASM opt-in target

Pointwise multiply/add:
  gt_test/test_gt_rowpack_soa_invntt32_fullpath.c
    native Neon rowpack basemul/add helpers under ROWPACK_NATIVE_BASEMUL

InvNTT row kernel:
  docs/gt_soa_layout_experiment/kernels/
    ntruplus768_invntt32_rowpack_soa_row_no_entry_no_end.S

InvNTT postmerge:
  docs/gt_soa_layout_experiment/kernels/
    ntruplus768_invntt32_rowpack_postmerge_branchfold.S
```

## Slothy Status

| Component | Current file(s) | Slothy status | Notes |
| --- | --- | --- | --- |
| Production Forward NTT32 | `asm/slothy/ntt32_symbolic.s`, `asm/slothy/my_32ntt.opt.s` | Slothy-generated scheduled artifact | Wired through `asm/my_ntt.s` for promoted GT production path. |
| Rowpack Forward NTT v2 | `asm/slothy/ntt32_v2_symbolic.s`, `asm/slothy/ntt32_8way.rowpack_v2.n1.alloc.s`, `asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s` | Slothy-generated RA/opt candidate | Opt-in rowpack Forward candidate; latest rowpack candidate uses `.opt.s`. |
| Production InvNTT | `asm/slothy/invntt_opt.s` | Slothy-scheduled production artifact | Included by `asm/inv_my_ntt.s`; production default remains here. |
| Production GT basemul/add | `asm/base_gt.opt.s` | Slothy-scheduled artifact | Promoted GT pointwise baseline. |
| Rowpack InvNTT32 original rowkernel | `kernels/ntruplus768_invntt32_rowpack_soa_row.sym.S`, `.alloc.S`, `.opt.S` | Slothy-generated symbolic/RA/opt set | Diagnostic baseline, no longer best rowpack candidate. |
| Rowpack InvNTT32 no-inred variant | `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.*` | Slothy-generated older variant | Historical/canonicalization experiment, not current candidate. |
| Rowpack InvNTT32 no-entry/no-end lazy rowkernel | `kernels/ntruplus768_invntt32_rowpack_soa_row_no_entry_no_end.S` | Slothy-derived, not a fresh independent Slothy design | Generated from the allocated rowkernel by `audit_rowpack_invntt.py --generate-no-entry-no-end`; current rowpack candidate. |
| Rowpack postmerge branchfold | `kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S` | Not Slothy | Hand-written AArch64 Neon ASM; current rowpack candidate. |
| Rowpack native basemul/add | `gt_test/test_gt_rowpack_soa_invntt32_fullpath.c` | Not Slothy | C/Neon intrinsic harness implementation, not standalone ASM. |
| Rowvec ABI probes | `gt_test/test_gt_rowvec_layout_contract.c`, `gt_test/bench_gt_basemul_soa.c` | Not Slothy | Diagnostic only; rowvec ABI is stopped by current evidence. |

## Current Commands

Correctness:

```sh
make test_gt_forward_rowpack_v2_asm
make test_gt_rowpack_no_entry_no_end_fullpath
make test_gt_rowpack_lazy_postmerge_asm_fullpath
```

Pi5 cycle comparison:

```sh
make bench_gt_rowpack_lazy_postmerge_asm_cycles_compare
make bench_gt_rowpack_lazy_asm_vs_kpqc_final
make bench_gt_rowpack_lazy_asm_fullchain_stage_compare
make bench_gt_rowpack_forward_v2_overhead_breakdown
make bench_gt_rowpack_forward_scatter_lower_bound
```

Focused InvNTT/postmerge isolation:

```sh
make bench_gt_rowpack_lazy_postmerge_asm_isolate_cycles
```

Production baseline:

```sh
make bench_ntt_pipeline_gt_opt_cycles
make bench_ntt_pipeline_add_gt_opt_cycles
```

## Cleanup / Ignore List

These are not part of the current rowpack candidate:

- `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.*`
  - Older canonical/no-inred rowkernel experiment.
- `gt_test/test_gt_rowpack_soa_oracle.c`
  - Layout oracle; useful for mapping, not current performance path.
- `gt_test/test_gt_rowvec_layout_contract.c`
  - Rowvec ABI contract; evidence says do not continue rowvec ABI now.
- `gt_test/bench_gt_basemul_soa.c`
  - Rowpack/rowvec basemul microbench; diagnostic only.
- `gt_test/analyze_gt_rowpack_basemul_output_ranges.c`
  - Range-analysis helper; diagnostic only.
- `docs/gt_soa_layout_experiment/rowpack-soa-invntt-plan.md`
  and `slothy-rowpack-invntt32-handoff.md`
  - Historical handoff/planning notes; use the dashboard and YAML contract for
    current decisions.
- `asm/inv_my_ntt_post_branchfold_a72.s`
  - Retained alternate A72-oriented wrapper, not current Pi5 default.
- Deleted `asm/inv_my_ntt_*` scratch variants visible in `git status`
  - Legacy wrappers/negative experiments already removed from the active path.

Do not delete the diagnostic files above unless the corresponding Makefile
targets are also retired.  They are not current implementation files, but they
still explain the evidence behind the current stop/continue decisions.
