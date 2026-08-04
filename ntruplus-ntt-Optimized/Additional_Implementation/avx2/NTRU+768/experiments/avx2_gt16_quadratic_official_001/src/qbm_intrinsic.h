#ifndef ROUND4C_QBM_INTRINSIC_H
#define ROUND4C_QBM_INTRINSIC_H

#include <stdint.h>

enum { ROUND4C_WORDS = 768 };

void round4c_split_intrinsic(int16_t out[ROUND4C_WORDS],
                             const int16_t in[ROUND4C_WORDS]);
void round4c_qbm_vector_intrinsic(int16_t out[ROUND4C_WORDS],
                                  const int16_t a[ROUND4C_WORDS],
                                  const int16_t b[ROUND4C_WORDS]);
void round4c_qbm_interleaved4_intrinsic(int16_t out[ROUND4C_WORDS],
                                        const int16_t a[ROUND4C_WORDS],
                                        const int16_t b[ROUND4C_WORDS]);
void round4c_qbm_interleaved8_intrinsic(int16_t out[ROUND4C_WORDS],
                                        const int16_t a[ROUND4C_WORDS],
                                        const int16_t b[ROUND4C_WORDS]);
void round4c_merge2_intrinsic(int16_t out[ROUND4C_WORDS],
                              const int16_t in[ROUND4C_WORDS]);

#endif
