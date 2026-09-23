#include <string.h>

#include "f0_forward_for_ma2.h"
#include "gt9x16_forward.h"
#include "gt9x16_ntt16_asm.h"

void __attribute__((aligned(32))) ntruplus1152_exp001_f0_forward_for_ma2(
    int16_t output[NTRUPLUS1152_EXP001_F0_N],
    const int16_t input[NTRUPLUS1152_EXP001_F0_N]) {
  _Alignas(32) int16_t split[NTRUPLUS1152_EXP001_F0_N];
  _Alignas(32) ntruplus1152_exp001_gt_persistent_pair pair_input;
  _Alignas(32) ntruplus1152_exp001_gt_persistent_pair pair_output;
  _Alignas(32) ntruplus1152_exp001_gt_rows coefficient_input;
  int branch, terminal_pair;

  ntruplus1152_exp001_top_split_small(split, input);
  for (branch = 0; branch < 2; ++branch) {
    for (terminal_pair = 0; terminal_pair < 2; ++terminal_pair) {
      int coefficient_stream, row, stream;
      for (coefficient_stream = 0; coefficient_stream < 2;
           ++coefficient_stream) {
        int coefficient = 2 * terminal_pair + coefficient_stream;
        ntruplus1152_exp001_top_split_to_gt_adapter(
            &coefficient_input, split, branch, coefficient);
        for (row = 0; row < 9; ++row)
          memcpy(pair_input.state[row][coefficient_stream],
                 coefficient_input.values[row], 32);
      }

      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(
          &pair_output, &pair_input);

      for (row = 0; row < 9; ++row)
        for (stream = 0; stream < 2; ++stream) {
          int vector = ((((branch * 9 + row) * 2 + terminal_pair) * 2) +
                        stream);
          memcpy(output + 16 * vector, pair_output.state[row][stream], 32);
        }
    }
  }
}
