#include <immintrin.h>

#include "gt9x16_shear.h"

#define LOAD_AND_SHEAR()                                                        \
  __m256i r0 = _mm256_loadu_si256((const __m256i *)input->values[0]);           \
  __m256i r1 = _mm256_loadu_si256((const __m256i *)input->values[1]);           \
  __m256i r2 = _mm256_loadu_si256((const __m256i *)input->values[2]);           \
  __m256i r3 = _mm256_loadu_si256((const __m256i *)input->values[3]);           \
  __m256i r4 = _mm256_loadu_si256((const __m256i *)input->values[4]);           \
  __m256i r5 = _mm256_loadu_si256((const __m256i *)input->values[5]);           \
  __m256i r6 = _mm256_loadu_si256((const __m256i *)input->values[6]);           \
  __m256i r7 = _mm256_loadu_si256((const __m256i *)input->values[7]);           \
  __m256i r8 = _mm256_loadu_si256((const __m256i *)input->values[8]);           \
  __m256i temporary;                                                            \
                                                                                \
  temporary = r0;                                                               \
  r0 = _mm256_blend_epi16(r0, r1, 0xAA);                                        \
  r1 = _mm256_blend_epi16(r1, r2, 0xAA);                                        \
  r2 = _mm256_blend_epi16(r2, r3, 0xAA);                                        \
  r3 = _mm256_blend_epi16(r3, r4, 0xAA);                                        \
  r4 = _mm256_blend_epi16(r4, r5, 0xAA);                                        \
  r5 = _mm256_blend_epi16(r5, r6, 0xAA);                                        \
  r6 = _mm256_blend_epi16(r6, r7, 0xAA);                                        \
  r7 = _mm256_blend_epi16(r7, r8, 0xAA);                                        \
  r8 = _mm256_blend_epi16(r8, temporary, 0xAA);                                 \
                                                                                \
  temporary = r0;                                                               \
  r0 = _mm256_blend_epi16(r0, r2, 0xCC);                                        \
  r2 = _mm256_blend_epi16(r2, r4, 0xCC);                                        \
  r4 = _mm256_blend_epi16(r4, r6, 0xCC);                                        \
  r6 = _mm256_blend_epi16(r6, r8, 0xCC);                                        \
  r8 = _mm256_blend_epi16(r8, r1, 0xCC);                                        \
  r1 = _mm256_blend_epi16(r1, r3, 0xCC);                                        \
  r3 = _mm256_blend_epi16(r3, r5, 0xCC);                                        \
  r5 = _mm256_blend_epi16(r5, r7, 0xCC);                                        \
  r7 = _mm256_blend_epi16(r7, temporary, 0xCC);                                 \
                                                                                \
  temporary = r0;                                                               \
  r0 = _mm256_blend_epi16(r0, r4, 0xF0);                                        \
  r4 = _mm256_blend_epi16(r4, r8, 0xF0);                                        \
  r8 = _mm256_blend_epi16(r8, r3, 0xF0);                                        \
  r3 = _mm256_blend_epi16(r3, r7, 0xF0);                                        \
  r7 = _mm256_blend_epi16(r7, r2, 0xF0);                                        \
  r2 = _mm256_blend_epi16(r2, r6, 0xF0);                                        \
  r6 = _mm256_blend_epi16(r6, r1, 0xF0);                                        \
  r1 = _mm256_blend_epi16(r1, r5, 0xF0);                                        \
  r5 = _mm256_blend_epi16(r5, temporary, 0xF0)

#define STORE_ROW(index, value)                                                  \
  _mm256_storeu_si256((__m256i *)output->values[index], value)

void ntruplus1152_exp001_gt9x16_shear_z(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  LOAD_AND_SHEAR();
  STORE_ROW(0, r0);
  STORE_ROW(1, r1);
  STORE_ROW(2, r2);
  STORE_ROW(3, r3);
  STORE_ROW(4, r4);
  STORE_ROW(5, r5);
  STORE_ROW(6, r6);
  STORE_ROW(7, r7);
  STORE_ROW(8, r8);
}

void ntruplus1152_exp001_gt9x16_shear_materialized(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input) {
  __m256i y0, y1, y2, y3, y4, y5, y6, y7, y8;
  LOAD_AND_SHEAR();
  y0 = _mm256_permute2x128_si256(r0, r8, 0x30);
  y1 = _mm256_permute2x128_si256(r1, r0, 0x30);
  y2 = _mm256_permute2x128_si256(r2, r1, 0x30);
  y3 = _mm256_permute2x128_si256(r3, r2, 0x30);
  y4 = _mm256_permute2x128_si256(r4, r3, 0x30);
  y5 = _mm256_permute2x128_si256(r5, r4, 0x30);
  y6 = _mm256_permute2x128_si256(r6, r5, 0x30);
  y7 = _mm256_permute2x128_si256(r7, r6, 0x30);
  y8 = _mm256_permute2x128_si256(r8, r7, 0x30);
  STORE_ROW(0, y0);
  STORE_ROW(1, y1);
  STORE_ROW(2, y2);
  STORE_ROW(3, y3);
  STORE_ROW(4, y4);
  STORE_ROW(5, y5);
  STORE_ROW(6, y6);
  STORE_ROW(7, y7);
  STORE_ROW(8, y8);
}

#define STAGE8_ROW(index, current, previous) do {                               \
  __m128i a = _mm256_castsi256_si128(current);                                  \
  __m128i b = _mm256_extracti128_si256(previous, 1);                            \
  __m128i z = _mm_set1_epi16(zeta[index]);                                      \
  __m128i zq = _mm_set1_epi16(zeta_qinv[index]);                                \
  __m128i q = _mm_set1_epi16(3457);                                             \
  __m128i low_product = _mm_mullo_epi16(b, zq);                                 \
  __m128i high_product = _mm_mulhi_epi16(b, z);                                 \
  __m128i correction = _mm_mulhi_epi16(low_product, q);                         \
  __m128i t = _mm_sub_epi16(high_product, correction);                          \
  __m128i plus = _mm_add_epi16(a, t);                                           \
  __m128i minus = _mm_sub_epi16(a, t);                                          \
  __m256i combined = _mm256_castsi128_si256(plus);                              \
  combined = _mm256_inserti128_si256(combined, minus, 1);                       \
  STORE_ROW(index, combined);                                                   \
} while (0)

void ntruplus1152_exp001_gt9x16_shear_stage8(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input,
    const int16_t zeta[9],
    const int16_t zeta_qinv[9]) {
  LOAD_AND_SHEAR();
  STAGE8_ROW(0, r0, r8);
  STAGE8_ROW(1, r1, r0);
  STAGE8_ROW(2, r2, r1);
  STAGE8_ROW(3, r3, r2);
  STAGE8_ROW(4, r4, r3);
  STAGE8_ROW(5, r5, r4);
  STAGE8_ROW(6, r6, r5);
  STAGE8_ROW(7, r7, r6);
  STAGE8_ROW(8, r8, r7);
}

static inline __m256i __attribute__((always_inline)) montgomery_multiply_vector(
    __m256i value, __m256i zeta, __m256i zeta_qinv, __m256i q) {
  __m256i low_product = _mm256_mullo_epi16(value, zeta_qinv);
  __m256i high_product = _mm256_mulhi_epi16(value, zeta);
  __m256i correction = _mm256_mulhi_epi16(low_product, q);
  return _mm256_sub_epi16(high_product, correction);
}

void ntruplus1152_exp001_gt9x16_ntt16_finish_row(
    int16_t output[16], const int16_t input[16],
    const ntruplus1152_exp001_ntt16_row_tables *tables) {
  const __m256i q = _mm256_set1_epi16(3457);
  const __m256i even_words = _mm256_setr_epi8(
      0, 1, 0, 1, 4, 5, 4, 5, 8, 9, 8, 9, 12, 13, 12, 13,
      0, 1, 0, 1, 4, 5, 4, 5, 8, 9, 8, 9, 12, 13, 12, 13);
  const __m256i odd_words = _mm256_setr_epi8(
      2, 3, 2, 3, 6, 7, 6, 7, 10, 11, 10, 11, 14, 15, 14, 15,
      2, 3, 2, 3, 6, 7, 6, 7, 10, 11, 10, 11, 14, 15, 14, 15);
  __m256i value = _mm256_loadu_si256((const __m256i *)input);
  __m256i a, b, t, plus, minus, zeta, zeta_qinv;

  a = _mm256_shuffle_epi32(value, _MM_SHUFFLE(1, 0, 1, 0));
  b = _mm256_shuffle_epi32(value, _MM_SHUFFLE(3, 2, 3, 2));
  zeta = _mm256_setr_epi16(
      tables->zeta4[0], tables->zeta4[0], tables->zeta4[0], tables->zeta4[0], tables->zeta4[0], tables->zeta4[0], tables->zeta4[0], tables->zeta4[0],
      tables->zeta4[1], tables->zeta4[1], tables->zeta4[1], tables->zeta4[1], tables->zeta4[1], tables->zeta4[1], tables->zeta4[1], tables->zeta4[1]);
  zeta_qinv = _mm256_setr_epi16(
      tables->qinv4[0], tables->qinv4[0], tables->qinv4[0], tables->qinv4[0], tables->qinv4[0], tables->qinv4[0], tables->qinv4[0], tables->qinv4[0],
      tables->qinv4[1], tables->qinv4[1], tables->qinv4[1], tables->qinv4[1], tables->qinv4[1], tables->qinv4[1], tables->qinv4[1], tables->qinv4[1]);
  t = montgomery_multiply_vector(b, zeta, zeta_qinv, q);
  plus = _mm256_add_epi16(a, t);
  minus = _mm256_sub_epi16(a, t);
  value = _mm256_blend_epi32(plus, minus, 0xCC);

  a = _mm256_shuffle_epi32(value, _MM_SHUFFLE(2, 2, 0, 0));
  b = _mm256_shuffle_epi32(value, _MM_SHUFFLE(3, 3, 1, 1));
  zeta = _mm256_setr_epi16(
      tables->zeta2[0], tables->zeta2[0], tables->zeta2[0], tables->zeta2[0], tables->zeta2[1], tables->zeta2[1], tables->zeta2[1], tables->zeta2[1],
      tables->zeta2[2], tables->zeta2[2], tables->zeta2[2], tables->zeta2[2], tables->zeta2[3], tables->zeta2[3], tables->zeta2[3], tables->zeta2[3]);
  zeta_qinv = _mm256_setr_epi16(
      tables->qinv2[0], tables->qinv2[0], tables->qinv2[0], tables->qinv2[0], tables->qinv2[1], tables->qinv2[1], tables->qinv2[1], tables->qinv2[1],
      tables->qinv2[2], tables->qinv2[2], tables->qinv2[2], tables->qinv2[2], tables->qinv2[3], tables->qinv2[3], tables->qinv2[3], tables->qinv2[3]);
  t = montgomery_multiply_vector(b, zeta, zeta_qinv, q);
  plus = _mm256_add_epi16(a, t);
  minus = _mm256_sub_epi16(a, t);
  value = _mm256_blend_epi32(plus, minus, 0xAA);

  a = _mm256_shuffle_epi8(value, even_words);
  b = _mm256_shuffle_epi8(value, odd_words);
  zeta = _mm256_setr_epi16(
      tables->zeta1[0], tables->zeta1[0], tables->zeta1[1], tables->zeta1[1], tables->zeta1[2], tables->zeta1[2], tables->zeta1[3], tables->zeta1[3],
      tables->zeta1[4], tables->zeta1[4], tables->zeta1[5], tables->zeta1[5], tables->zeta1[6], tables->zeta1[6], tables->zeta1[7], tables->zeta1[7]);
  zeta_qinv = _mm256_setr_epi16(
      tables->qinv1[0], tables->qinv1[0], tables->qinv1[1], tables->qinv1[1], tables->qinv1[2], tables->qinv1[2], tables->qinv1[3], tables->qinv1[3],
      tables->qinv1[4], tables->qinv1[4], tables->qinv1[5], tables->qinv1[5], tables->qinv1[6], tables->qinv1[6], tables->qinv1[7], tables->qinv1[7]);
  t = montgomery_multiply_vector(b, zeta, zeta_qinv, q);
  plus = _mm256_add_epi16(a, t);
  minus = _mm256_sub_epi16(a, t);
  value = _mm256_blend_epi16(plus, minus, 0xAA);
  _mm256_storeu_si256((__m256i *)output, value);
}
