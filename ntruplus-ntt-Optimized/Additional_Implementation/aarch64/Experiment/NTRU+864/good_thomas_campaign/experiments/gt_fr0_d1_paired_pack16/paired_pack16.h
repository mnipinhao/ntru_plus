#ifndef GT864_PAIRED_PACK16_H
#define GT864_PAIRED_PACK16_H

#include <stdint.h>

void gt864_pack8_ordered(uint8_t out[1296], const int16_t in[864]);
void gt864_pack16_ordered(uint8_t out[1296], const int16_t in[864]);

#endif
