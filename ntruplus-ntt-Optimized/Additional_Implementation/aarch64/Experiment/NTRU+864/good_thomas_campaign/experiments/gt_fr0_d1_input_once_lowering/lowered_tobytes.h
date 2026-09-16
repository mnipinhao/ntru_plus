#ifndef GT864_INPUT_ONCE_LOWERED_TOBYTES_H
#define GT864_INPUT_ONCE_LOWERED_TOBYTES_H

#include <stdint.h>

void gt864_fr0_input_once_l1_tobytes(uint8_t out[1296],
                                     const int16_t fr0[864]);
void gt864_fr0_input_once_l12_tobytes(uint8_t out[1296],
                                      const int16_t fr0[864]);

#endif
