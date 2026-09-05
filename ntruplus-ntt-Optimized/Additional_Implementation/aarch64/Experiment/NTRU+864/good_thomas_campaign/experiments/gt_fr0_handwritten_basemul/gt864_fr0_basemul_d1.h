#ifndef GT864_FR0_BASEMUL_D1_H
#define GT864_FR0_BASEMUL_D1_H

#include <stdint.h>

#define GT864_FR0_BASEMUL_D1_COEFFICIENTS 864

void gt864_fr0_basemul_d1_neon(
    int16_t out[GT864_FR0_BASEMUL_D1_COEFFICIENTS],
    const int16_t a[GT864_FR0_BASEMUL_D1_COEFFICIENTS],
    const int16_t b[GT864_FR0_BASEMUL_D1_COEFFICIENTS]);

void gt864_fr0_basemul_add_d1_neon(
    int16_t out[GT864_FR0_BASEMUL_D1_COEFFICIENTS],
    const int16_t a[GT864_FR0_BASEMUL_D1_COEFFICIENTS],
    const int16_t b[GT864_FR0_BASEMUL_D1_COEFFICIENTS],
    const int16_t c[GT864_FR0_BASEMUL_D1_COEFFICIENTS]);

#endif
