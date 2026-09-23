#include <immintrin.h>

#include "gt9x16_forward.h"
#include "gt9x16-full-forward-tables.h"

static int16_t montgomery_reduce(int32_t value) {
  int16_t low = (int16_t)value * 12929;
  return (int16_t)((value - (int32_t)low * 3457) >> 16);
}

void ntruplus1152_exp001_top_split_small(
    int16_t output[NTRUPLUS1152_EXP001_N],
    const int16_t input[NTRUPLUS1152_EXP001_N]) {
  const __m256i zeta = _mm256_set1_epi16(-722);
  int index;
  for (index = 0; index < 576; index += 16) {
    __m256i low = _mm256_loadu_si256((const __m256i *)(input + index));
    __m256i high = _mm256_loadu_si256((const __m256i *)(input + index + 576));
    __m256i product = _mm256_mullo_epi16(high, zeta);
    __m256i first = _mm256_add_epi16(low, product);
    __m256i second = _mm256_sub_epi16(_mm256_add_epi16(low, high), product);
    _mm256_storeu_si256((__m256i *)(output + index), first);
    _mm256_storeu_si256((__m256i *)(output + index + 576), second);
  }
}

void ntruplus1152_exp001_top_split_to_gt_adapter(
    ntruplus1152_exp001_gt_rows *output,
    const int16_t split[NTRUPLUS1152_EXP001_N], int branch, int coefficient) {
  const int16_t *twist = branch == 0 ? ntruplus1152_exp001_twist_branch0
                                     : ntruplus1152_exp001_twist_branch1;
  int lane, row;
  for (row = 0; row < 9; ++row) {
    int h_row = (5 * row) % 9;
    for (lane = 0; lane < 16; ++lane) {
      int component = 16 * h_row + lane;
      int split_index = branch * 576 + 4 * component + coefficient;
      output->values[row][lane] = montgomery_reduce(
          (int32_t)split[split_index] * twist[component]);
    }
  }
}
