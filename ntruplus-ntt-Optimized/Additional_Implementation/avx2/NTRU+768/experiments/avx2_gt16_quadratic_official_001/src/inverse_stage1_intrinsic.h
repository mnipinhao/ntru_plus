#ifndef ROUND4C_INVERSE_STAGE1_INTRINSIC_H
#define ROUND4C_INVERSE_STAGE1_INTRINSIC_H

#include <stdint.h>

void round4c_inverse_stage1_i0(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_stage1_i1(int16_t out[768], const int16_t quadratic[768]);
void round4c_qbm_inverse_stage1_fused_asm(int16_t out[768],
                                          const int16_t a[768],
                                          const int16_t b[768]);
void round4c_qbm_inverse_stage1_fused(int16_t out[768],
                                      const int16_t a[768],
                                      const int16_t b[768]);
void round4c_inverse_ntt16_layers_asm(int16_t values[768]);
void round4c_inverse_ntt16_layers_reference(int16_t values[768]);
void round4c_inverse_stage1_asm(int16_t out[768],
                                const int16_t quadratic[768]);
void round4c_inverse_stage1_wide_asm(int16_t out[768],
                                     const int16_t quadratic[768]);
void round4c_inverse_finish_asm(int16_t out[768], int16_t rows[768]);
void round4c_inverse_full_asm(int16_t out[768],
                              const int16_t quadratic[768]);
void round4c_inverse_full_wide_asm(int16_t out[768],
                                   const int16_t quadratic[768]);
void round4c_inverse_full_wide_hybrid(int16_t out[768],
                                      const int16_t quadratic[768]);
void round4c_inverse_ntt16_i0(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_ntt16_i1(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_full_i0(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_full_i1(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_full_i0_ntt16_asm(int16_t out[768],
                                       const int16_t quadratic[768]);
void round4c_inverse_full_i0_finish_asm(int16_t out[768],
                                        const int16_t quadratic[768]);
void round4c_qbm_inverse_full_fused(int16_t out[768], const int16_t a[768],
                                    const int16_t b[768]);

#endif
