# Gate 13 Forward v4 Transform-DAG Search

Status: `complete_bounded_search_no_asm_candidate`

This gate is a tagged-index model.  It emits YAML/Markdown only; it
does not generate `.S`, `.opt.s`, Slothy input, or benchmark binaries.

## Reference DAG

- NTT32 size: `32`
- stages: `stage1, stage2, stage3, stage4, stage5`
- stage distances: `[16, 8, 4, 2, 1]`
- current stage12 boundary: `k32-major scratch vectors`
- rowpack output blocks: `4` blocks of `8` k32 values

## Cost Model

- current tail: `24 permutes/block`
- recoverable window: `209.969 cycles/NTT`
- continue gate: `>= 150.0 cycles/NTT`
- strong gate: `>= 200.0 cycles/NTT`

## Candidate Matrix

| candidate | total permutes/block | expected saved cycles/NTT | proof | status |
| --- | ---: | ---: | --- | --- |
| A_current_ct_stage12_k32_major | 24 | +0.000 | `proved_by_existing_gates` | `no_headroom` |
| B_layout_moved_before_stage345 | 72 | -419.938 | `structural_only` | `reject_static_model` |
| C_layout_moved_into_stage12_one_level | 24 | +0.000 | `structural_only` | `no_headroom` |
| D_six_step_4x8_or_8x4_decomposition | 48 | -209.969 | `requires_twiddle_factorization_proof` | `reject_static_model` |
| E_rowpack_from_entry_horizontal_ntt32 | 80 | -489.928 | `structural_only` | `reject_static_model` |
| F_algebraic_absorb_one_mixing_level | 16 | +69.990 | `not_found_in_bounded_search` | `below_gate_and_unproved` |
| G_algebraic_absorb_two_mixing_levels | 8 | +139.979 | `not_found_in_bounded_search` | `below_gate_and_unproved` |
| H_algebraic_absorb_three_mixing_levels | 0 | +209.969 | `not_found_in_bounded_search` | `blocked_pending_transform_proof` |
| I_non_radix2_new_decomposition | unknown | unknown | `research_only` | `unquantified_research` |

## Decision

Best proved candidate: `A_current_ct_stage12_k32_major` with `0.0` cycles/NTT expected recovery.

Best unproved candidate: `H_algebraic_absorb_three_mixing_levels` with `209.969` cycles/NTT expected recovery.

The bounded tagged-index search found no proved transform DAG with at least 150 cycles/NTT expected recovery.  The only modeled class with strong enough headroom is full algebraic absorption of all three rowpack mixing levels, and no concrete tagged transform or twiddle remap was found for it.

Forward v4 ASM remains blocked.  If this line continues, the next
artifact should be a numeric tagged-index transform oracle for
`H_algebraic_absorb_three_mixing_levels` using the actual NTRU+768
Forward NTT tables, not assembly.
