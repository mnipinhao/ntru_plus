#ifndef ROUND4C_FORWARD_INTRINSIC_H
#define ROUND4C_FORWARD_INTRINSIC_H

#include <stdint.h>

enum { ROUND4C_FORWARD_WORDS = 768 };

/* Stage-selectable quartic boundaries used only by the benchmark harness. */
void round4c_forward_frontend_intrinsic(int16_t out[768],
                                        const int16_t in[768]);
void round4c_forward_dft3_intrinsic(int16_t out[768],
                                    const int16_t in[768], int center_output);
void round4c_forward_ntt16_intrinsic(int16_t values[768]);
void round4c_forward_ntt16_asm(int16_t values[768]);

/* Complete producers.  Output is the Round 4C quadratic terminal layout. */
void round4c_forward_f0_materialized(int16_t out[768], const int16_t in[768]);
void round4c_forward_f0_fused(int16_t out[768], const int16_t in[768]);
void round4c_forward_f1_materialized(int16_t out[768], const int16_t in[768]);
void round4c_forward_f1_fused(int16_t out[768], const int16_t in[768]);
void round4c_forward_f1_hybrid_asm(int16_t out[768], const int16_t in[768]);
void round4c_forward_f1_full_asm(int16_t out[768], const int16_t in[768]);

#endif
