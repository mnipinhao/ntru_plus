#ifndef ROUND4C_LANE_NTT16_INTRINSIC_H
#define ROUND4C_LANE_NTT16_INTRINSIC_H

#include <stdint.h>

/* Benchmark-only Layout-B probes: one YMM lane axis is i16. */
void round4c_lane_ntt16_x1(int16_t out[16], const int16_t in[16]);
void round4c_lane_ntt16_x3(int16_t out[48], const int16_t in[48]);
void round4c_lane_ntt16_batch_x1(int16_t out[768], const int16_t in[768]);
void round4c_lane_ntt16_batch_x3(int16_t out[768], const int16_t in[768]);

#endif
