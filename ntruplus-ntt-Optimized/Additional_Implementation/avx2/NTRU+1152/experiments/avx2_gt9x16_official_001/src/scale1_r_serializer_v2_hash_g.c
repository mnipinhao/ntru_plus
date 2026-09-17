#ifndef _DEFAULT_SOURCE
#define _DEFAULT_SOURCE
#endif
#include <stdint.h>
#include "fips202.h"
#include "params.h"
#include "scale1-r-serializer-v2-asm.h"
#include "util.h"

void ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(
    uint8_t out[NTRUPLUS_N / 4], const int16_t state[NTRUPLUS_N]) {
  _Alignas(32) uint8_t stage[1 + NTRUPLUS_POLYBYTES];
  stage[0] = 0x01;
  ntruplus1152_exp001_scale1_r_serializer_v2(stage + 1, state);
  shake256(out, NTRUPLUS_N / 4, stage, sizeof stage);
  secure_clear(stage, sizeof stage);
}
