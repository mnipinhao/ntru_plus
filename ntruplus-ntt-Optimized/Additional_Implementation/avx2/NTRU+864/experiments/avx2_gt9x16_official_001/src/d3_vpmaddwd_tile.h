#ifndef NTRUPLUS864_EXP001_D3_VPMADDWD_TILE_H
#define NTRUPLUS864_EXP001_D3_VPMADDWD_TILE_H

#include <stdint.h>

void ntruplus864_exp001_d3_tile_baseline(int16_t out[48],
                                         const int16_t a_packed[48],
                                         const int16_t b_packed[48],
                                         const int16_t zeta_qinv_and_zeta[32],
                                         int16_t scratch[96]);

void ntruplus864_exp001_d3_tile_vpmaddwd(int16_t out[48],
                                         const int16_t a_packed[48],
                                         const int16_t b_packed[48],
                                         const int16_t zeta_qinv_and_zeta[32],
                                         int16_t scratch_unused[96]);

#endif
