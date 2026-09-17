#ifndef NTRUPLUS768_AVX2_CLEAN_BASEMUL_H
#define NTRUPLUS768_AVX2_CLEAN_BASEMUL_H

#include <stdint.h>

#include "ntt.h"

#define GT_SOA_BATCHES 12
#define GT_SOA_LANES 16

/* P-layout tables consumed by the selected J1 BaseInv and F0xJ1 BaseMul. */
extern const int16_t gt_native_lambda[GT_SOA_BATCHES][GT_SOA_LANES];
extern const int16_t gt_native_lambda_qinv[GT_SOA_BATCHES][GT_SOA_LANES];

#endif
