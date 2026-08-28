/* H4 scale-1 producer plus the proved inter-layer Barrett mask 79. */
#define PROD3_FULL_ONLY 1
#define PROD3_NATURAL_Q 1
#define PROD3_T0_BETA 1
#define PROD3_SCALE1 1
#define PROD3_LAZY_R2_REDUCTIONS 1
#define ntruplus1152_exp001_gt9x16_prod3_aos_full \
        ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce
#include "gt9x16_prod3_aos_branch0.S"
