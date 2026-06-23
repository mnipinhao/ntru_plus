# NTT32 Slothy Sources

`ntt32_symbolic.s` is the source of truth for the 8-way parallel Forward CT
NTT32 used by `asm/my_ntt.s`.

The current symbolic kernel is specialized for the full `my_ntt.s` pipeline:

- input layout: `Q0..Q31 = [row_base + 16*i]`
- each vector lane is one independent Good-Thomas row branch
- input is the lazy Phase123 raw DFT3 row buffer, not arbitrary int16 data
- output is reduced to canonical range, split into low/high 64-bit halves, and
  scattered directly to the final `poly_ntt` output layout
- caller contract for the fused scatter form:
  `x0 = dst`, `x4 = row_base`, `x10 = dst + row_offset`

This version assumes the Slothy target model supports general
`str D..., [x]`, plus the concrete GPR pointer updates used by the branchless
scatter wrap.

Power-0 CT butterflies are optimized specially:

- stage 1 uses `t = high` directly, which is still within the current lazy
  range bound
- later power-0 butterflies reduce the high operand in place and omit the
  useless `mul by 1`; using raw `high` there would let the DC path exceed the
  int16 range

Suggested generated file names after running Slothy:

- `ntt32_8way.fused_scatter.alloc.s` for RA-only output
- `ntt32_8way.fused_scatter.opt.s` for scheduled output used by `asm/my_ntt.s`

The older `my_32ntt.opt.s` name is a previous generated output kept because the
current Makefile still wires it into `poly_ntt`.  Treat it as a disposable
Slothy artifact, not as the source of truth unless you intentionally overwrite
it with the fused-scatter version.

`asm/my_ntt.s` is currently wired for the fused-scatter `_ntt32_8way` by setting
the assembler-time `NTT32_FUSED_SCATTER` constant to `1`.  If you intentionally
test an older row-buffer `_ntt32_8way` artifact, switch that constant back to
`0`.

The generated `my_32ntt.opt.s` has a small boundary post-process: it defines
stack slots for Slothy spills and reloads `dst`, `row_base`, and the row's
initial `scatter_ptr` before each stage345 block.  Keep that in mind if you
regenerate the file from scratch.

## Forward Phase123 N1 Schedule

The first half of `asm/my_ntt.s`, from `slothy_start_ntt_phase123` to
`slothy_end_ntt_phase123`, has an N1 Slothy-scheduled variant:

- unscheduled source of truth: `asm/my_ntt.s`
- scheduled wrapper used by the default GT KEM builds:
  `asm/my_ntt_phase123_n1.s`
- scheduled region included by the wrapper:
  `asm/slothy/my_ntt_phase123.n1.opt.s`
- flat symbolic source used to run Slothy:
  `asm/slothy/my_ntt_phase123_flat.sym.s`
- local driver used for the split-heuristic run:
  `asm/slothy/optimize_phase123_split.py`

`asm/my_ntt.s` keeps the original macro-expanded Phase123 block behind the
default path.  Defining `MY_NTT_USE_PHASE123_N1` includes the scheduled region
instead; `asm/my_ntt_phase123_n1.s` is just that define plus an include of
`asm/my_ntt.s`.

The default Makefile path uses:

```sh
GT_NTT_ASM = asm/my_ntt_phase123_n1.s asm/slothy/my_32ntt.opt.s
```

To compare against the unscheduled Phase123 block without editing files:

```sh
make -B test_kem_gt_production_opt \
  GT_NTT_ASM='asm/my_ntt.s asm/slothy/my_32ntt.opt.s'
```

Slothy cannot directly parse the original `PHASE123_ITER` GAS macro because of
the `.if \pattern == ...` branch.  The flat symbolic file expands the eight
iterations explicitly and then optimizes each
`slothy_start_ntt_phase123_iterN:slothy_end_ntt_phase123_iterN` region with the
N1 target and split heuristic.

Rerun command:

```sh
SLOTHY_PATH=/path/to/slothy python3 optimize_phase123_split.py \
  --input my_ntt_phase123_flat.sym.s \
  --output my_ntt_phase123.n1.opt.s \
  --target n1 \
  --region slothy_start_ntt_phase123_iter0:slothy_end_ntt_phase123_iter0 \
  --region slothy_start_ntt_phase123_iter1:slothy_end_ntt_phase123_iter1 \
  --region slothy_start_ntt_phase123_iter2:slothy_end_ntt_phase123_iter2 \
  --region slothy_start_ntt_phase123_iter3:slothy_end_ntt_phase123_iter3 \
  --region slothy_start_ntt_phase123_iter4:slothy_end_ntt_phase123_iter4 \
  --region slothy_start_ntt_phase123_iter5:slothy_end_ntt_phase123_iter5 \
  --region slothy_start_ntt_phase123_iter6:slothy_end_ntt_phase123_iter6 \
  --region slothy_start_ntt_phase123_iter7:slothy_end_ntt_phase123_iter7 \
  --stalls 192
```

## NTT32 Rowpack Output v2

`ntt32_v2_symbolic.s` is an experimental symbolic source for the Forward NTT
rowpack-output path.  It keeps the same stage12 and stage345 arithmetic as
`ntt32_symbolic.s`, but changes the final stage345 output packing:

- each stage345 block reduces eight Q vectors;
- the eight vectors are transposed with `trn1/trn2`;
- branch/lane planes are stored as contiguous rowpack SoA Q vectors;
- output layout matches
  `rowpack_index(branch,row,lane,k32) = branch*384 + row*128 + lane*32 + k32`.

The caller ABI is intentionally still `_ntt32_8way(x0=dst, x4=row_base,
x10=dst+256*row)`, so this source can be generated and tested behind the same
`asm/my_ntt.s` row calls once a wrapper is added for the rowpack public
`poly_ntt` output convention.  It is not wired into production.

Run the portable contract gate before generating or testing a candidate:

```sh
make test_gt_forward_rowpack_output_contract
```

Suggested Slothy direction for Pi 5 / Cortex-A76-class testing is the
Neoverse-N1 model, not A72.  The stage345 v2 regions are medium sized, so use
RA-first/window optimization or split heuristics rather than treating the whole
NTT32 as one region.

Suggested generated file names:

- `ntt32_8way.rowpack_v2.n1.alloc.s`
- `ntt32_8way.rowpack_v2.n1.opt.s`

Current opt-in candidate:

- `ntt32_8way.rowpack_v2.n1.opt.s`

Correctness gates:

```sh
make test_gt_forward_rowpack_v2_asm
make test_gt_rowpack_soa_invntt32_fullpath_forward_v2
make test_gt_rowpack_soa_invntt32_fullpath_forward_v2_nativebasemul
```

Pi 5 cycle targets:

```sh
make bench_gt_rowpack_pipeline_forward_v2_nativebasemul_cycles_compare
```

# Inverse NTT Files

The active inverse NTT path is intentionally narrow:

- `asm/inv_my_ntt.s` is the production wrapper.  It selects the Pi 5 validated
  directstage123 + Slothy stage45-reduce + post-row no-DFT3-reduce +
  branch-constant folded final merge path through assembler-time gates, then
  includes `asm/slothy/invntt_opt.s`.
- `asm/slothy/invntt_opt.s` is the current inverse implementation wired into
  tests and benchmarks.
- `asm/slothy/invntt32_stage45_reduce_fused_clean.slothy.s` and
  `asm/slothy/invntt_post_fused_dstore_clean.slothy.s` are the retained clean
  Slothy sources for the promoted scheduled regions.
- `asm/inv_my_ntt_post_branchfold_a72.s` is an opt-in wrapper for the same
  mathematical path, but it uses an A72 Slothy schedule for the branchfold
  fused post stripe.  It is not production default until Pi 5 measurements
  show a clear win.
- `asm/slothy/invntt_post_branchfold_reduce_clean.slothy.s` and
  `asm/slothy/invntt_post_branchfold_reduce_a72.opt.s` are the clean and
  generated sources for that opt-in branchfold schedule.
- `asm/base_gt.opt.s` and `asm/inv_my_ntt.s` are the current Pi 5 promoted
  pair.  The current result summary and rerun commands live in
  `docs/slothy_pi5_bench_matrix.md`.

The old standalone `inv_my_ntt_*directstage123*.s`,
`inv_my_ntt_*stage45*.s`, `inv_my_ntt_*post_fused*.s`, fastscale, unreduced
branchfold, stage123-stripescratch, and negative `postmerge_folded` wrappers
were removed after promotion.  The duplicate branchfold wrapper was also
removed because `asm/inv_my_ntt.s` is now that exact path.  The retained
alternate wrapper is the A72 branchfold schedule.

Raspberry Pi 5 PERF medians motivating the promotion:

- previous no-DFT3-reduce production baseline: about 5379 cycles
- directstage123 only: about 5263 cycles
- directstage123 + post-fused Slothy: 5109 cycles
- directstage123 + stage45-reduce Slothy + post-fused Slothy: 5000 cycles
- previous promoted post no-DFT3-reduce path: 4562 cycles
- promoted branchfold-reduce path: 4044 cycles
- GT `ntt_mul_pipeline` with the no-DFT3-reduce inverse: 13671 cycles
- GT `ntt_basemul_add_pipeline` with the no-DFT3-reduce inverse: 17071 cycles
- GT `kem_dec` with the no-DFT3-reduce inverse: 35218 cycles
- removed no-DFT3-reduce + fastscale+reduce experiment: 4997 cycles
