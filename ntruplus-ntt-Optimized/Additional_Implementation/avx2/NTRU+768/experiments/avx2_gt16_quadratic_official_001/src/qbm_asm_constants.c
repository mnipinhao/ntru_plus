#include <stdint.h>

#include "quadratic-constants.h"

const int16_t *const round4c_weight_mont_asm = &round4c_weight_mont[0][0];
const int16_t *const round4c_weight_qinv_asm = &round4c_weight_qinv[0][0];
const int16_t *const round4c_merge_mont_asm = &round4c_merge_mont[0][0];
const int16_t *const round4c_merge_qinv_asm = &round4c_merge_qinv[0][0];
const int16_t *const round4c_inv16_twiddle_mont_asm =
    &round4c_inv16_twiddle_mont[0];
const int16_t *const round4c_inv16_twiddle_qinv_asm =
    &round4c_inv16_twiddle_qinv[0];
const int16_t *const round4c_inv48_postweight_mont_asm =
    &round4c_inv48_postweight_mont[0][0];
const int16_t *const round4c_inv48_postweight_qinv_asm =
    &round4c_inv48_postweight_qinv[0][0];
const int16_t *const round4c_inv3_omega_mont_asm =
    &round4c_inv3_omega_mont;
const int16_t *const round4c_inv3_omega_qinv_asm =
    &round4c_inv3_omega_qinv;
const int16_t *const round4c_inv_beta_vector_mont_asm =
    &round4c_inv_beta_vector_mont[0];
const int16_t *const round4c_inv_beta_vector_qinv_asm =
    &round4c_inv_beta_vector_qinv[0];
const int16_t *const round4c_final_merge_mont_asm =
    &round4c_final_merge_mont[0];
const int16_t *const round4c_final_merge_qinv_asm =
    &round4c_final_merge_qinv[0];
const uint16_t *const round4c_inverse_natural_byte_offsets_asm =
    &round4c_inverse_natural_byte_offsets[0];
