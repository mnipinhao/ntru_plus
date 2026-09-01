#ifndef GT864_FORWARD_COMPOSE_H
#define GT864_FORWARD_COMPOSE_H

#include <stdint.h>

#define GT864_FORWARD_P8_COEFFICIENTS 896
#define GT864_FORWARD_OUTPUT_COEFFICIENTS 864

/* Readable schedule oracle for the future fused assembly block. */
void gt864_forward_compose_barrett(
    int16_t out[GT864_FORWARD_OUTPUT_COEFFICIENTS],
    const int16_t p8[GT864_FORWARD_P8_COEFFICIENTS]);

#endif
