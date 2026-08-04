#ifndef ROUND4C_TRANSPOSE_INTRINSIC_H
#define ROUND4C_TRANSPOSE_INTRINSIC_H

#include <stdint.h>

void round4c_vertical_to_soa(int16_t out[768], const int16_t in[768]);
void round4c_soa_to_vertical(int16_t out[768], const int16_t in[768]);

#endif
