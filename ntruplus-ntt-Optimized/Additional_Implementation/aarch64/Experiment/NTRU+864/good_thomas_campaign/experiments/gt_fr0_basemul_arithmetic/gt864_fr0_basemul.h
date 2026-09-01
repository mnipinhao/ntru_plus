#ifndef GT864_FR0_BASEMUL_H
#define GT864_FR0_BASEMUL_H

#include <stdint.h>

#define GT864_FR0_BASEMUL_COEFFICIENTS 864

void gt864_fr0_basemul_neon(
    int16_t out[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t a[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t b[GT864_FR0_BASEMUL_COEFFICIENTS]);

void gt864_fr0_basemul_add_neon(
    int16_t out[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t a[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t b[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t c[GT864_FR0_BASEMUL_COEFFICIENTS]);

#endif
