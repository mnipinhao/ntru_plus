#ifndef GT864_P9_TOBYTES_H
#define GT864_P9_TOBYTES_H

#include <stdint.h>

void gt864_p9_input_once_full_inner(uint8_t out[1296],
                                    const int16_t fr0[864]);
void gt864_p9_input_once_small_inner(uint8_t out[1296],
                                     const int16_t fr0[864]);
void gt864_p9_tobytes_full_asm(uint8_t out[1296], const int16_t fr0[864]);
void gt864_p9_tobytes_small_asm(uint8_t out[1296], const int16_t fr0[864]);

#endif
