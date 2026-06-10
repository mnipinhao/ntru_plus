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

# Inverse NTT Files

The active inverse NTT path is intentionally narrow:

- `asm/inv_my_ntt.s` is the production wrapper.  It selects the Pi 5 validated
  directstage123 + Slothy stage45-reduce + Slothy post-row path through
  assembler-time gates, then includes `asm/slothy/invntt_opt.s`.
- `asm/inv_my_ntt_rowlazy_baseline.s` is the pre-promotion rowlazy baseline
  wrapper for regression and benchmark comparison.
- `asm/slothy/invntt_opt.s` is the current inverse implementation wired into
  tests and benchmarks.
- `asm/slothy/invntt32_stage45_reduce_fused_clean.slothy.s` and
  `asm/slothy/invntt_post_fused_dstore_clean.slothy.s` are the retained clean
  Slothy sources for the promoted scheduled regions.

The old standalone `inv_my_ntt_*directstage123*.s`,
`inv_my_ntt_*stage45*.s`, `inv_my_ntt_*post_fused*.s`, and negative
`postmerge_folded` wrappers were removed after promotion.  The only retained
alternate wrapper is the rowlazy baseline above.

Raspberry Pi 5 PERF medians motivating the promotion:

- previous rowlazy/default GT `invntt`: about 5379 cycles
- directstage123 only: about 5263 cycles
- directstage123 + post-fused Slothy: 5109 cycles
- directstage123 + stage45-reduce Slothy + post-fused Slothy: 5000 cycles
- GT `ntt_mul_pipeline` with the promoted inverse: 13671 cycles
- GT `ntt_basemul_add_pipeline` with the promoted inverse: 17071 cycles
- GT `kem_dec` with the promoted inverse: 35218 cycles
