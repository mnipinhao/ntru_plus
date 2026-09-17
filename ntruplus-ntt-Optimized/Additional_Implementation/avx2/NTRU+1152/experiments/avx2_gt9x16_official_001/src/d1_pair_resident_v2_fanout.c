#include <stdint.h>

#include "poly.h"
#include "symmetric.h"

void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(
    int16_t *);
void ntruplus1152_exp001_scale1_r_serializer_v2(uint8_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r(int16_t *, uint8_t *);

/*
 * Both sides start at the coefficient-domain CBD1 r input and stop after the
 * exact same scale-1 wire state, hash_g output, and SOTP message polynomial.
 * The only timed difference is whether Serializer V2 reloads the materialized
 * Forward output or consumes the final D1 pairs while they are still live.
 */
void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_scale1_r_fanout_control(
    uint8_t hash_state[NTRUPLUS_POLYBYTES], poly *m,
    int16_t r_state[NTRUPLUS_N], const poly *r_coefficient,
    const uint8_t msg[NTRUPLUS_N / 8]) {
  ntruplus1152_exp001_top_split_small(r_state, r_coefficient->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(
      r_state);
  ntruplus1152_exp001_scale1_r_serializer_v2(hash_state, r_state);
  hash_g(hash_state, hash_state);
  poly_sotp_encode(m, msg, hash_state);
}

void __attribute__((noinline, aligned(32)))
ntruplus1152_exp001_scale1_r_fanout_candidate(
    uint8_t hash_state[NTRUPLUS_POLYBYTES], poly *m,
    int16_t r_state[NTRUPLUS_N], const poly *r_coefficient,
    const uint8_t msg[NTRUPLUS_N / 8]) {
  ntruplus1152_exp001_top_split_small(r_state, r_coefficient->coeffs);
  ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r(r_state, hash_state);
  hash_g(hash_state, hash_state);
  poly_sotp_encode(m, msg, hash_state);
}
