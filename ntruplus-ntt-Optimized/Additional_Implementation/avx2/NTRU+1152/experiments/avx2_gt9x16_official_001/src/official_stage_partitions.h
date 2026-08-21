#ifndef NTRUPLUS1152_EXP001_OFFICIAL_STAGE_PARTITIONS_H
#define NTRUPLUS1152_EXP001_OFFICIAL_STAGE_PARTITIONS_H

#include <stdint.h>

#define NTRUPLUS1152_EXP001_OFFICIAL_N 1152

/* Diagnostic-only functions extracted from the pinned Official ntt.s. */
void ntruplus1152_exp001_official_t0(
    int16_t value[NTRUPLUS1152_EXP001_OFFICIAL_N]);
void ntruplus1152_exp001_official_t3x3(
    int16_t value[NTRUPLUS1152_EXP001_OFFICIAL_N]);
void ntruplus1152_exp001_official_t2x4(
    int16_t value[NTRUPLUS1152_EXP001_OFFICIAL_N]);

#endif
