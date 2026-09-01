#ifndef GT864_FR0_INVERSE_H
#define GT864_FR0_INVERSE_H

#include <stdint.h>

#define GT864_FR0_COEFFICIENTS 864
#define GT864_INVERSE_P8_MAIN 768
#define GT864_INVERSE_P8_PADDED 896

/* Pass 1: FR-0 SoA leaves -> inverse-NTT9 P8+tail boundary. */
void gt864_fr0_inverse_ntt9_neon(
    int16_t out[GT864_INVERSE_P8_PADDED],
    const int16_t in[GT864_FR0_COEFFICIENTS]);

/* Pass 2: inverse NTT16, alpha/beta recombination, natural coefficients. */
void gt864_fr0_inverse_finish_neon(
    int16_t out[GT864_FR0_COEFFICIENTS],
    const int16_t in[GT864_INVERSE_P8_PADDED]);

#endif
