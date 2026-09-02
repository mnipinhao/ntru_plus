#ifndef GT864_FRISO2_H
#define GT864_FRISO2_H

#include <stdint.h>

#define GT864_FRISO2_COEFFICIENTS 864

/* FR-0 SoA -> the component basis (1,tau,tau^2), in the same slots. */
void gt864_friso2_normalize(int16_t out[GT864_FRISO2_COEFFICIENTS],
                            const int16_t in[GT864_FRISO2_COEFFICIENTS]);

/* Inverse basis map; this is an algebra oracle, not a proposed memory pass. */
void gt864_friso2_denormalize(int16_t out[GT864_FRISO2_COEFFICIENTS],
                              const int16_t in[GT864_FRISO2_COEFFICIENTS]);

void gt864_friso2_basemul(int16_t out[GT864_FRISO2_COEFFICIENTS],
                          const int16_t a[GT864_FRISO2_COEFFICIENTS],
                          const int16_t b[GT864_FRISO2_COEFFICIENTS]);

void gt864_friso2_basemul_add(int16_t out[GT864_FRISO2_COEFFICIENTS],
                              const int16_t a[GT864_FRISO2_COEFFICIENTS],
                              const int16_t b[GT864_FRISO2_COEFFICIENTS],
                              const int16_t c[GT864_FRISO2_COEFFICIENTS]);

#endif
