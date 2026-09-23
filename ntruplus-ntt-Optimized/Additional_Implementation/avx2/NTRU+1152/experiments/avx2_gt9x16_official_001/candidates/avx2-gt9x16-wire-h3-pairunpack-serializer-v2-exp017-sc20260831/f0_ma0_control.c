#include <immintrin.h>
#include <stdint.h>

#include "f0-ma0-adapter.h"
#include "f0_ma0_control.h"

void poly_basemul(int16_t *, const int16_t *, const int16_t *);
void poly_add(int16_t *, const int16_t *, const int16_t *);
void poly_tobytes(uint8_t *, const int16_t *);

static inline __m256i center(__m256i value) {
  const __m256i q = _mm256_set1_epi16(3457);
  const __m256i half_q = _mm256_set1_epi16(1728);
  const __m256i negative_half_q = _mm256_set1_epi16(-1728);
  __m256i quotient = _mm256_mulhrs_epi16(value, _mm256_set1_epi16(9));
  value = _mm256_sub_epi16(value, _mm256_mullo_epi16(quotient, q));
  value = _mm256_sub_epi16(value,
      _mm256_and_si256(_mm256_cmpgt_epi16(value, half_q), q));
  value = _mm256_add_epi16(value,
      _mm256_and_si256(_mm256_cmpgt_epi16(negative_half_q, value), q));
  return value;
}

static inline __m256i montgomery_const(__m256i value, int16_t factor,
                                       int16_t factor_qinv) {
  const __m256i q = _mm256_set1_epi16(3457);
  const __m256i f = _mm256_set1_epi16(factor);
  __m256i low = _mm256_mullo_epi16(value, _mm256_set1_epi16(factor_qinv));
  __m256i high = _mm256_mulhi_epi16(value, f);
  return _mm256_sub_epi16(high, _mm256_mulhi_epi16(low, q));
}

void ntruplus1152_exp001_f0_ma0_control(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t scratch[3456]) {
  int16_t *r_official = scratch;
  int16_t *m_official = scratch + 1152;
  int16_t *product = scratch + 2304;
  int vector;
  ntruplus1152_exp001_f0_ma0_to_official(r_official, r_f0);
  ntruplus1152_exp001_f0_ma0_to_official(m_official, m_f0);
  for (vector = 0; vector < 72; ++vector) {
    __m256i r = _mm256_load_si256((const __m256i *)r_official + vector);
    __m256i m = _mm256_load_si256((const __m256i *)m_official + vector);
    _mm256_store_si256((__m256i *)r_official + vector, center(r));
    _mm256_store_si256((__m256i *)m_official + vector, center(m));
  }
  poly_basemul(product, h_official, r_official);
  poly_add(product, product, m_official);
  for (vector = 0; vector < 72; ++vector) {
    __m256i value = _mm256_load_si256((const __m256i *)product + vector);
    value = montgomery_const(value, -901, 16379);
    _mm256_store_si256((__m256i *)product + vector, center(value));
  }
  poly_tobytes(output, product);
}
