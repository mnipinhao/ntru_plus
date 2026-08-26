#include "f0-prod2-ma2-asm.h"
#include "f0_forward_for_ma2.h"
#include "gt9x16_forward.h"

void __attribute__((aligned(32)))
ntruplus1152_exp001_f0_forward_for_ma2_p2b(
    int16_t output_planes[NTRUPLUS1152_EXP001_F0_N],
    const int16_t input[NTRUPLUS1152_EXP001_F0_N]) {
  _Alignas(32) int16_t split[NTRUPLUS1152_EXP001_F0_N];
  unsigned int branch, terminal_pair;

  ntruplus1152_exp001_top_split_small(split, input);
  for (branch = 0; branch < 2; ++branch)
    for (terminal_pair = 0; terminal_pair < 2; ++terminal_pair)
      ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(
          output_planes, split, branch, terminal_pair);
}
