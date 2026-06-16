# Rowpack InvNTT32 Slothy Handoff

Scope: symbolic source and driver draft for one native rowpack SoA InvNTT32 row
micro-kernel.  Slothy has now produced Neoverse-N1 `.alloc.S` and `.opt.S`
outputs, but they are not integrated into production InvNTT.

## Artifacts

- `rowpack-invntt32-kernel-contract.yml`
- `kernels/ntruplus768_invntt32_rowpack_soa_row.sym.S`
- `kernels/ntruplus768_invntt32_rowpack_soa_row.alloc.S`
- `kernels/ntruplus768_invntt32_rowpack_soa_row.opt.S`
- `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.sym.S`
- `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.alloc.S`
- `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S`
- `optimize_ntruplus768_invntt32_rowpack_soa_row.py`

The symbolic source implements:

- four fixed row-plane loads for `k32 = 0..31`;
- row-input Barrett normalization for all four loaded row vectors;
- stage 1 distance-1 in-vector butterflies;
- stage 2 distance-2 in-vector butterflies;
- stage 3 distance-4 in-vector butterflies;
- stage 4 and 5 cross-vector butterflies;
- row-end Barrett reduction;
- four fixed row-plane stores.

`bit` is used as the non-destructive-mask form of the `vbsl` selection in the
C model.  This preserves the shared mask constants while keeping the same
masked-select dataflow.

## Slothy Workflow

Use RA-first, then window optimization.  The successful local run used the
Slothy venv because the system Python did not have `unicorn` installed:

```sh
cd ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768
/Users/chenpinhao/slothy/venv/bin/python docs/gt_soa_layout_experiment/optimize_ntruplus768_invntt32_rowpack_soa_row.py --target neoverse-n1
```

Expected generated files:

- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.alloc.S`
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.opt.S`

If Slothy rejects `bit`, `rev32`, `rev64`, or symbolic vector-scalar lane
forms, add target-model support for those real AArch64 Neon instructions rather
than changing the instruction selection.

Current run status:

- RA-only output: 162 instructions, expected cycles 41, selfcheck OK.
- Scheduled output: 162 instructions, expected cycles 40.
- LLVM selftest was disabled because local LLVM tools were not found.
- The driver carries local parser compatibility for `rev32`, `rev64`, and
  `bit`.
- The generated `.S` files include Mach-O aliases and Apple guards for local
  assembler tests.

No-entry-normalization variant status:

- Symbolic source:
  `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.sym.S`.
- RA-only output:
  `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.alloc.S`.
- RA-only output is 150 instructions, expected cycles 38, selfcheck OK.
- Scheduled output:
  `kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S`.
- Scheduled output is 150 instructions, expected cycles 37, selfcheck OK.
- A larger-window run was too slow locally.  The reproducible successful run
  used smaller windows:

```sh
/Users/chenpinhao/slothy/venv/bin/python docs/gt_soa_layout_experiment/optimize_ntruplus768_invntt32_rowpack_soa_row.py --target neoverse-n1 --source kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.sym.S --alloc-output kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.alloc.S --output kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.opt.S --window-only --split-factor 16 --split-stepsize 0.0625 --split-repeat 1 --timeout 20 --retry-timeout 20
```

- The variant has the same ABI symbol as the fused kernel and is valid only
  when the caller uses the canonical rowpack basemul/add output convention.

## Validation After Slothy

1. Compare `.sym.S` to `.alloc.S`; the RA-only pass should preserve instruction
   order while replacing symbolic registers.
2. Compare `.alloc.S` to `.opt.S`; only the scheduling pass should reorder.
3. Inspect ABI use: `x0`, `x1`, `sp`, and reserved `x18-x30`.
4. Wire generated output into a row-kernel harness before touching production
   `asm/slothy/invntt_opt.s`.
5. Run:

```sh
make test_gt_rowpack_soa_oracle
make test_invntt32_rowpack_kernel_model
make test_invntt32_rowpack_slothy_opt
make test_gt_rowpack_soa_invntt32_fullpath
make test_gt_rowpack_soa_invntt32_fullpath_canonical
make analyze_gt_rowpack_basemul_output_ranges
make bench_gt_basemul_soa
./build/bench_gt_basemul_soa
make bench_gt_rowpack_pipeline_compare
make bench_gt_rowpack_pipeline_add_compare
```

Local validation completed:

- `make test_invntt32_rowpack_slothy_opt`
- `make test_invntt32_rowpack_slothy_opt ROWPACK_INVNTT32_SLOTHY_OPT_ASM=docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.alloc.S`
- `make test_gt_rowpack_soa_invntt32_fullpath`
- `make test_gt_rowpack_soa_invntt32_fullpath ROWPACK_INVNTT32_SLOTHY_OPT_ASM=docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row.alloc.S`
- `make test_gt_rowpack_soa_invntt32_fullpath_canonical`
- `make test_gt_rowpack_soa_invntt32_fullpath_canonical ROWPACK_INVNTT32_NOINRED_ASM=docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_noinred.alloc.S`
- `make analyze_gt_rowpack_basemul_output_ranges`
- `make test_gt_rowpack_soa_oracle test_invntt32_rowpack_kernel_model bench_gt_basemul_soa_run`
- `make bench_gt_rowpack_pipeline_compare bench_gt_rowpack_pipeline_add_compare`

`test_gt_rowpack_soa_invntt32_fullpath` now also proves direct rowpack Forward
NTT output, rowpack basemul/add layout, and product/product-add roundtrips.  The
product roundtrips call the generated row kernel directly; row-input Barrett
normalization is fused into the row kernel entry.

`rowpack-basemul-output-range-proof.md` documents the alternative
no-entry-normalization convention.  Current raw basemul/add output is not
canonical enough for that variant; the analyzer records `r[1] = -1737` as a
deterministic counterexample.  A no-entry-normalization row kernel needs a
canonical basemul/add output ABI that stores each lane in `[-1728, 1728]`.
`test_gt_rowpack_soa_invntt32_fullpath_canonical` now proves that ABI through
rowpack product and product-add full-path roundtrips using the no-entry
RA-only row kernel.

Promotion to production InvNTT still needs production caller layout and a
Forward-NTT-output-layout plan.  Do not promote this row kernel in isolation.
