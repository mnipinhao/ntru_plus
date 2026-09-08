#ifndef GT864_NATIVE_ASM_EXPERIMENT_API_H
#define GT864_NATIVE_ASM_EXPERIMENT_API_H
#include <stdint.h>
/* All functions are default-off experiments. Exact in-place alias is allowed.
 * Partial overlap is forbidden. Zeta pointers cover all 36 * 8 int16 values. */
int gt864_baseinv_asm(int16_t out[864], const int16_t in[864], const int16_t *zR);
void gt864_basemul_rinv_asm(int16_t out[864], const int16_t a[864],
                          const int16_t b[864], const int16_t *zR);
void gt864_inverse_rinv_asm(int16_t out[864], const int16_t in[864],
    const int16_t *twist, const int16_t *stage,
    const int16_t *main_scale, const int16_t *tail_scale);
#endif
