#ifndef GT864_P14_TOBYTES_H
#define GT864_P14_TOBYTES_H
#include <stdint.h>
void gt864_p14_tobytes_full_inner(uint8_t out[1296],const int16_t in[864]);
void gt864_p14_tobytes_small_inner(uint8_t out[1296],const int16_t in[864]);
void gt864_p14_tobytes_full_asm(uint8_t out[1296],const int16_t in[864]);
void gt864_p14_tobytes_small_asm(uint8_t out[1296],const int16_t in[864]);
#endif
