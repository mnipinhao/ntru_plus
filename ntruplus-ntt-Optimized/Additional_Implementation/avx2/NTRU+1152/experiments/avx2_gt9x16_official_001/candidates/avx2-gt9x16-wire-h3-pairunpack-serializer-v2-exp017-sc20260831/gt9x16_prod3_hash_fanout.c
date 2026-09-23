#include "f0_prod3_hash_bridge.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full_price.h"
#include "gt9x16_prod3_hash_fanout.h"

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_hash_fanout_o0(poly *official_state) {
  poly_ntt(official_state);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_hash_fanout_o1(
    uint8_t hash_bytes[NTRUPLUS_POLYBYTES], poly *official_state) {
  poly_ntt(official_state);
  poly_tobytes(hash_bytes, official_state);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_hash_fanout_c0(
    int16_t planes[NTRUPLUS_N], const poly *coefficient_input) {
  ntruplus1152_exp001_top_split_small(planes, coefficient_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(planes);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_hash_fanout_c1(
    uint8_t hash_bytes[NTRUPLUS_POLYBYTES], int16_t planes[NTRUPLUS_N],
    const poly *coefficient_input, poly *generic_scratch,
    poly *official_scratch) {
  ntruplus1152_exp001_top_split_small(planes, coefficient_input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_price(planes);
  ntruplus1152_exp001_prod3_hash_bytes(
      hash_bytes, planes, generic_scratch, official_scratch);
}
