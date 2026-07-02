# Forward NTT Slothy Sources

`asm/slothy/my_32ntt.opt.s` is the only retained NTT32 row kernel wired into
the production GT forward NTT.  The older rowpack, shadow-base, and forward
window experiment artifacts were removed from the active tree after they failed
to become production candidates.

`asm/my_ntt.s` is the production wrapper and now always calls the fused-scatter
`_ntt32_8way` row kernel.  The older row-buffer scatter fallback was removed
from the production file to keep the active path readable.

The generated `my_32ntt.opt.s` has a small boundary post-process: it defines
stack slots for Slothy spills and reloads `dst`, `row_base`, and the row's
initial `scatter_ptr` before each stage345 block.  Keep that in mind if you
regenerate the file from scratch.

## Forward Phase123 N1 Schedule

The first half of `asm/my_ntt.s` is the N1 Slothy-scheduled Phase123 path:

- symbolic source used to run Slothy: `asm/slothy/my_ntt_phase123_flat.sym.s`
- scheduled wrapper used by the default GT KEM builds:
  `asm/my_ntt_phase123_n1.s`
- scheduled region included by the wrapper:
  `asm/slothy/my_ntt_phase123.n1.opt.s`
- local driver used for the split-heuristic run:
  `asm/slothy/optimize_phase123_split.py`

`asm/my_ntt.s` directly includes the scheduled region.  The old
macro-expanded GAS `PHASE123_ITER` fallback and the Phase123 A/B/C experiment
selector were removed from the production file.

The default Makefile path uses:

```sh
GT_NTT_ASM = asm/my_ntt_phase123_n1.s asm/slothy/my_32ntt.opt.s
```

The flat symbolic file expands the eight iterations explicitly and then
optimizes each
`slothy_start_ntt_phase123_iterN:slothy_end_ntt_phase123_iterN` region with the
N1 target and split heuristic.

Rejected 2026-06-25 Phase123 A76 load-schedule experiments:

| variant | change | Slothy n1 per iter | Pi5 KEM result |
| --- | --- | ---: | --- |
| A | twist table `ldp` fixed-offset, one final `add x3,#384` | 161 instr / 40 cycles | parity: 923 / 893 / 745 |
| B | A + zip/DFT3 triad streaming | 161 instr / 40 cycles | parity/slight NTT noise: 924 / 893 / 744 |
| C | A + full triad streaming, pairs 0/2/4 then 1/3/5 | 165 instr / 41 cycles | slower: 926 / 895 / 745 |

Do not keep or promote these experiment artifacts.  The current production
Phase123 remains the baseline 160-instruction / 40-cycle N1 schedule, measured
on Pi5 at roughly KEYGEN 923, ENCAP 894, DECAP 744.

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

# Inverse NTT Files

The active inverse NTT path is intentionally narrow:

- `asm/inv_my_ntt.s` is the production wrapper.  It selects the Pi 5 validated
  directstage123 + Slothy stage45-reduce + post-row no-DFT3-reduce +
  branch-constant folded final merge path through assembler-time gates, then
  includes `asm/slothy/invntt_opt.production.s`.
- `asm/slothy/invntt_opt.production.s` is the current inverse implementation
  wired into production tests and benchmarks.  The older
  `asm/slothy/invntt_opt.s` remains as a legacy experiment superset.
- `asm/slothy/archive/invntt_rowstage45_post_prototypes.s` archives rowstage45
  and post prototypes that are not included by production wrappers.
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
