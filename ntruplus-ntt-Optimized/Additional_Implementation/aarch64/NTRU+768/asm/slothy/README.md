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

The older `my_32ntt.alloc.s` and `my_32ntt.opt.s` names are previous generated
outputs.  Treat them as disposable Slothy artifacts, not as the source of
truth unless you intentionally overwrite them with the fused-scatter version.

`asm/my_ntt.s` is currently wired for the fused-scatter `_ntt32_8way` by setting
the assembler-time `NTT32_FUSED_SCATTER` constant to `1`.  If you intentionally
test an older row-buffer `_ntt32_8way` artifact, switch that constant back to
`0`.

The generated `my_32ntt.opt.s` has a small boundary post-process: it defines
stack slots for Slothy spills and reloads `dst`, `row_base`, and the row's
initial `scatter_ptr` before each stage345 block.  Keep that in mind if you
regenerate the file from scratch.
