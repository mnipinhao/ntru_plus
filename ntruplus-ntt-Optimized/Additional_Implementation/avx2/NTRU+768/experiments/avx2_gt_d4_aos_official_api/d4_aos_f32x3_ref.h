#ifndef D4_AOS_F32X3_REF_H
#define D4_AOS_F32X3_REF_H

#include "d4_aos_ref.h"

typedef struct {
    int16_t lane[768];
} d4aos_f32x3_state __attribute__((aligned(32)));

_Static_assert(sizeof(d4aos_f32x3_state) == 1536, "F32X3 state size");
_Static_assert(_Alignof(d4aos_f32x3_state) >= 32, "F32X3 state alignment");

void d4aos_f32x3_ref_forward(
    d4aos_ntt_poly *out,
    const d4aos_coeff_poly *in);
void d4aos_f32x3_ref_inverse(
    d4aos_coeff_poly *out,
    const d4aos_ntt_poly *in);
void d4aos_f32x3_ref_inverse_checkpoint_stage0(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_stage0_avx2(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_stage0_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);

/* Test-only canonical R^0 checkpoints after inverse CT layers L0, L1 and L2. */
void d4aos_f32x3_ref_inverse_ntt32_checkpoints(
    d4aos_f32x3_state *after_l0,
    d4aos_f32x3_state *after_l1,
    d4aos_f32x3_state *after_l2,
    d4aos_f32x3_state *after_l3,
    d4aos_f32x3_state *after_l4,
    const d4aos_f32x3_state *in);

/* Release L0-L2 pass.  Input/output must be 32-byte aligned and non-overlapping. */
void gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);

/* Debug-build entry point; absent unless D4AOS_F32X3_ASM_CHECKPOINTS is enabled. */
void gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm(
    d4aos_f32x3_state *after_l0,
    d4aos_f32x3_state *after_l1,
    d4aos_f32x3_state *after_l2,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_ct_merged_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_ct_merged_yang_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *in);
void gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm(
    d4aos_f32x3_state *after_l3,
    d4aos_f32x3_state *after_l4,
    const d4aos_f32x3_state *after_l2);
void d4aos_f32x3_ref_inverse_dft3_barrett(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *post_l4);
void gt_d4aos_f32x3_idft3_barrett_probe_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *post_l4);
void gt_d4aos_f32x3_yang_idft3_probe_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *native_input);
void gt_d4aos_f32x3_yang_compact_idft3_probe_asm(
    d4aos_f32x3_state *out,
    const d4aos_f32x3_state *native_input);
void d4aos_f32x3_ref_inverse_terminal(
    d4aos_coeff_poly *out,
    const d4aos_f32x3_state *post_dft3);
void gt_d4aos_f32x3_yang_invntt_avx2_asm(
    d4aos_coeff_poly *out,
    const d4aos_f32x3_state *native_input);
void gt_d4aos_f32x3_yang_compact_invntt_avx2_asm(
    d4aos_coeff_poly *out,
    const d4aos_f32x3_state *native_input);

#endif
