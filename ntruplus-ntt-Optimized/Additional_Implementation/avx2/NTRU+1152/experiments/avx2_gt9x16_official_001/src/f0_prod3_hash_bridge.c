#include <immintrin.h>

#include "f0-ma0-adapter.h"
#include "f0_prod3_hash_bridge.h"

static inline __m256i remove_scale4(__m256i value) {
  const __m256i q = _mm256_set1_epi16(3457);
  const __m256i inv4_montgomery = _mm256_set1_epi16(-901);
  const __m256i inv4_montgomery_qinv = _mm256_set1_epi16(16379);
  __m256i low = _mm256_mullo_epi16(value, inv4_montgomery_qinv);
  __m256i high = _mm256_mulhi_epi16(value, inv4_montgomery);
  return _mm256_sub_epi16(high, _mm256_mulhi_epi16(low, q));
}

void ntruplus1152_exp001_prod3_hash_bytes(
    uint8_t output[NTRUPLUS_POLYBYTES],
    const int16_t input_planes[NTRUPLUS_N], poly *generic_scratch,
    poly *official_scratch) {
  int vector;

  ntruplus1152_exp001_f0_ma2_planes_to_generic(generic_scratch->coeffs,
                                                input_planes);
  ntruplus1152_exp001_f0_ma0_to_official(official_scratch->coeffs,
                                          generic_scratch->coeffs);
  for (vector = 0; vector < NTRUPLUS_N / 16; ++vector) {
    __m256i value = _mm256_load_si256(
        (const __m256i *)(const void *)official_scratch->coeffs + vector);
    value = remove_scale4(value);
    _mm256_store_si256((__m256i *)(void *)official_scratch->coeffs + vector,
                       value);
  }
  poly_tobytes(output, official_scratch);
}
