# Gate 12 Forward v4 Topology Model

Status: `complete_static_model_no_asm_candidate`

This gate models whether a larger Forward v4 arithmetic topology rewrite
has enough headroom to justify ASM.  It does not generate `.S`, `.opt.s`,
or Slothy artifacts.

## Cost Model

- current rowpack output tail: `24 permutes/block`
- current scatter/transpose-only: `319.328 cycles/NTT`
- store-ready lower bound: `109.359 cycles/NTT`
- recoverable window: `209.969 cycles/NTT`
- estimated cycles per removed permute: `2.187`
- continue gate: `>= 150.0 cycles/NTT`
- strong gate: `>= 200.0 cycles/NTT`

## Candidate Matrix

| candidate | total permutes/block | expected cycles saved/NTT | status | interpretation |
| --- | ---: | ---: | --- | --- |
| A_current_v2_k32_major | 24 | +0.000 | `no_headroom` | Current rowpack v2 topology. |
| B_pretranspose_then_horizontal_stage345 | 72 | -419.938 | `reject_static_model` | Transpose each 8-k32 block into rowpack plane vectors before stage345, then run stages 3/4/5 as horizontal lane butterflies inside each plane. |
| C_absorb_one_mixing_stage_into_stage12 | 24 | +0.000 | `no_headroom` | Try to form a partially rowpack-friendly 2-way grouping at the stage12 boundary, reducing the final transpose by one stage. |
| D_absorb_two_mixing_stages_into_stage12 | 24 | +0.000 | `no_headroom` | Try to form a 4-way rowpack-friendly grouping at the stage12 boundary, leaving one final transpose stage. |
| E_rowpack_from_entry_horizontal_ntt32 | 80 | -489.928 | `reject_static_model` | Keep rowpack plane vectors from the NTT32 entry and run all five 32-point stages horizontally inside lanes. |
| F_new_forward_decomposition_rowpack_native | unknown | unknown | `research_only_no_static_cycle_claim` | Change the mathematical/vectorization decomposition earlier than stage12 so lane mixing is algebraically absorbed into the transform, not implemented as an added transpose network. |

## Concrete Rejections

- `A_current_v2_k32_major`: baseline. Modeled total lane mixing is `24` permutes/block.
- `B_pretranspose_then_horizontal_stage345`: very high; replaces cheap vector-wise butterflies with horizontal lane work. Modeled total lane mixing is `72` permutes/block.
- `C_absorb_one_mixing_stage_into_stage12`: medium; moves one transpose stage into stage12 without reducing total cost. Modeled total lane mixing is `24` permutes/block.
- `D_absorb_two_mixing_stages_into_stage12`: high; moves two transpose stages into stage12 without reducing total cost. Modeled total lane mixing is `24` permutes/block.
- `E_rowpack_from_entry_horizontal_ntt32`: very high; destroys the current vector-wise butterfly advantage. Modeled total lane mixing is `80` permutes/block.

## Open Research Path

`F_new_forward_decomposition_rowpack_native` is the only class left
that could plausibly beat the 24-permute/block barrier, but this
model cannot assign it cycle credit yet.  It changes the transform
decomposition earlier than stage12, so the next artifact must be a
tagged-index transform DAG with twiddle remap and range proof.  ASM
or Slothy remains blocked until that DAG predicts at least
`150 cycles/NTT` recoverable.

## Decision

No concrete topology in this model predicts at least 150 cycles/NTT recoverable.  The concrete variants either tie the 24-permute/block barrier, move it earlier, or replace it with more horizontal butterfly permutation work.

Next gate if continuing: `build a tagged-index Forward v4 transform-DAG search, not ASM`.
