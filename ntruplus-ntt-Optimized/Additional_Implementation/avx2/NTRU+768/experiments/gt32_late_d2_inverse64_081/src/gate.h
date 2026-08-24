#ifndef GT32_LATE_D2_INVERSE64_081_GATE_H
#define GT32_LATE_D2_INVERSE64_081_GATE_H
#include <stdint.h>

#define GATE_WORDS 128

void late_soa_basemul_i2_fused_asm(int16_t *, const int16_t *, const int16_t *);
void hwa16_inverse_v2_asm(int16_t *, const int16_t *);
void d2_inverse64_qbm_asm(int16_t *, const int16_t *, const int16_t *);
void d2_inverse64_naturalize_asm(int16_t *, const int16_t *);
void d2_inverse64_inv_asm(int16_t *, const int16_t *);
void inverse32_normalize_asm(int16_t *, const int16_t *);
void late_d2_redeposit_i01_asm(int16_t *, const int16_t *);
void control_inverse_cross3_asm(int16_t *, const int16_t *);
void hwa_to_tile4_asm(int16_t *, const int16_t *);

#endif
