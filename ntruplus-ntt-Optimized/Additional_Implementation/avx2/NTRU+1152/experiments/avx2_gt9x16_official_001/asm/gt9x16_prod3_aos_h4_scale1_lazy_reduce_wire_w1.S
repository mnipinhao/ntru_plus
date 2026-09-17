/* One-row NTT9-to-NTT16 wavefront; frozen scale-1 wire ABI. */
#define PROD3_FULL_ONLY 1
#define PROD3_NATURAL_Q 1
#define PROD3_WIRE_MONOTONE 1
#define PROD3_T0_BETA 1
#define PROD3_SCALE1 1
#define PROD3_LAZY_R2_REDUCTIONS 1
#define PROD3_WAVEFRONT_W1 1
#define ntruplus1152_exp001_gt9x16_prod3_aos_full \
        ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce_w1
.include "generated/d1-wire-monotone-absorption.inc"
#include "gt9x16_prod3_aos_branch0.S"
