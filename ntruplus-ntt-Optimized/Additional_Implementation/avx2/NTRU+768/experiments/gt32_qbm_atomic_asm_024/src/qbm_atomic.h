#ifndef GT32_QBM_ATOMIC_024_H
#define GT32_QBM_ATOMIC_024_H

#include <stdint.h>

typedef void (*qbm_asm_fn)(int16_t *, const int16_t *, const int16_t *,
                           const int16_t (*)[16], const int16_t (*)[16]);

void qbm_selected_control_asm(int16_t out[768], const int16_t a[768],
                              const int16_t b[768],
                              const int16_t weight_mont[48][16],
                              const int16_t weight_qinv[48][16]);
void qbm_atomic_expanded_asm(int16_t out[768], const int16_t a[768],
                            const int16_t b[768],
                            const int16_t weight_mont[48][16],
                            const int16_t weight_qinv[48][16]);

#endif
