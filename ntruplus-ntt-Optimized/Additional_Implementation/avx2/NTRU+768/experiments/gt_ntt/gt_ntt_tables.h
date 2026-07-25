#ifndef NTRUPLUS_GT_NTT_TABLES_H
#define NTRUPLUS_GT_NTT_TABLES_H

#include <stdint.h>

extern const int16_t gt_twist[2][96];
extern const int16_t gt_omega32[32];
extern const uint16_t gt_frontend_input_byte_offset[16][6];
extern const int16_t gt_frontend_twist_qinv_factor[16][3][32];
extern const int16_t gt_frontend_fused_split_twist_qinv_factor[16][3][64];

#endif
