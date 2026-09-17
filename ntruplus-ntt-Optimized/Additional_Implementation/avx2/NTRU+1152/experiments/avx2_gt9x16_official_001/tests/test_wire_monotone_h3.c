#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 1152
#define BYTES 1728
#define Q 3457

void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(int16_t state[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[N]);
int ntruplus1152_exp001_encap_h_ingress_ma2_h3(int16_t out[N], const uint8_t pk[BYTES], const int16_t r[N], const int16_t m[N]);
int ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(int16_t out[N], const uint8_t pk[BYTES], const int16_t r[N], const int16_t m[N]);

static const uint16_t current_to_wire[N] = {
#include "wire-monotone-source-to-wire.inc"
};
static uint64_t state = UINT64_C(0x4833574952454d41);
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)(state >> 16); }
static int canon(int x) { x %= Q; return x < 0 ? x + Q : x; }
static void encode12(uint8_t out[BYTES], const uint16_t in[N]) {
  int i; memset(out, 0, BYTES);
  for (i = 0; i < N; ++i) {
    unsigned bit = 12U * (unsigned)i, byte = bit >> 3, shift = bit & 7U;
    uint32_t word = (uint32_t)in[i] << shift;
    out[byte] |= (uint8_t)word;
    if (byte + 1 < BYTES) out[byte + 1] |= (uint8_t)(word >> 8);
    if (byte + 2 < BYTES) out[byte + 2] |= (uint8_t)(word >> 16);
  }
}

int main(void) {
  _Alignas(32) int16_t rc[N], mc[N], rn[N], mn[N], rw[N], mw[N], on[N], ow[N];
  _Alignas(32) uint16_t h[N];
  _Alignas(32) uint8_t pk[BYTES];
  int trial, i;
  for (trial = 0; trial < 160; ++trial) {
    for (i = 0; i < N; ++i) {
      rc[i] = (int16_t)((int)(rnd() % 3) - 1);
      mc[i] = (int16_t)((int)(rnd() % 3) - 1);
      h[i] = (uint16_t)(rnd() % Q);
    }
    encode12(pk, h);
    ntruplus1152_exp001_top_split_small(rn, rc); memcpy(rw, rn, sizeof rn);
    ntruplus1152_exp001_top_split_small(mn, mc); memcpy(mw, mn, sizeof mn);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(rn);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(mn);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(rw);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(mw);
    for (i = 0; i < N; ++i)
      if (rn[i] != rw[current_to_wire[i]] || mn[i] != mw[current_to_wire[i]]) {
        fprintf(stderr, "wire H3 input mismatch trial=%d index=%d target=%u r=%d/%d m=%d/%d\n",
                trial, i, current_to_wire[i], rn[i], rw[current_to_wire[i]],
                mn[i], mw[current_to_wire[i]]); return 1;
      }
    if (ntruplus1152_exp001_encap_h_ingress_ma2_h3(on, pk, rn, mn) ||
        ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(ow, pk, rw, mw)) {
      fprintf(stderr, "valid decode rejected at trial %d\n", trial); return 1;
    }
    for (i = 0; i < N; ++i)
      if (canon(on[i]) != canon(ow[current_to_wire[i]])) {
        fprintf(stderr, "wire H3 mismatch trial=%d index=%d target=%u value=%d/%d\n",
                trial, i, current_to_wire[i], on[i], ow[current_to_wire[i]]); return 1;
      }
  }
  memset(pk, 0xff, sizeof pk);
  if (!ntruplus1152_exp001_encap_h_ingress_ma2_h3(on, pk, rn, mn) ||
      !ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(ow, pk, rw, mw)) {
    fputs("invalid decode accepted\n", stderr); return 1;
  }
  puts("wire-monotone H3: ok");
  return 0;
}
