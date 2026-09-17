#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 1152
#define BYTES 1728
#define Q 3457

void ntruplus1152_exp001_top_split_small(int16_t *, const int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
int ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(int16_t *, const uint8_t *, const int16_t *, const int16_t *);
int ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire_pairunpack(int16_t *, const uint8_t *, const int16_t *, const int16_t *);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(uint8_t *, const uint8_t *, const int16_t *, const int16_t *, int16_t *);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire_pairunpack(uint8_t *, const uint8_t *, const int16_t *, const int16_t *, int16_t *);

static uint64_t rng = UINT64_C(0x483350414952554e);
static uint32_t rnd(void) {
  rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
  return (uint32_t)(rng >> 16);
}

static void encode12(uint8_t out[BYTES], const uint16_t in[N]) {
  memset(out, 0, BYTES);
  for (unsigned i = 0; i < N; ++i) {
    unsigned bit = 12U * i, byte = bit >> 3, shift = bit & 7U;
    uint32_t word = (uint32_t)in[i] << shift;
    out[byte] |= (uint8_t)word;
    if (byte + 1 < BYTES) out[byte + 1] |= (uint8_t)(word >> 8);
    if (byte + 2 < BYTES) out[byte + 2] |= (uint8_t)(word >> 16);
  }
}

int main(void) {
  _Alignas(32) int16_t rc[N], mc[N], r[N], m[N], a[N], b[N], sa[N], sb[N];
  _Alignas(32) uint16_t h[N];
  _Alignas(32) uint8_t pk[BYTES], ca[BYTES], cb[BYTES];

  for (int trial = 0; trial < 1003; ++trial) {
    for (int i = 0; i < N; ++i) {
      rc[i] = (int16_t)((int)(rnd() % 3) - 1);
      mc[i] = (int16_t)((int)(rnd() % 3) - 1);
      h[i] = (uint16_t)(rnd() % Q);
    }
    encode12(pk, h);
    ntruplus1152_exp001_top_split_small(r, rc);
    ntruplus1152_exp001_top_split_small(m, mc);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(r);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(m);

    if (ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(a, pk, r, m) ||
        ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire_pairunpack(b, pk, r, m) ||
        memcmp(a, b, sizeof a)) {
      fprintf(stderr, "H3 pair-unpack mismatch at trial %d\n", trial);
      return 1;
    }
    if (ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(ca, pk, r, m, sa) ||
        ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire_pairunpack(cb, pk, r, m, sb) ||
        memcmp(ca, cb, sizeof ca)) {
      fprintf(stderr, "H4 pair-unpack mismatch at trial %d\n", trial);
      return 1;
    }
  }

  memset(pk, 0xff, sizeof pk);
  if (!ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire(a, pk, r, m) ||
      !ntruplus1152_exp001_encap_h_ingress_ma2_h3_wire_pairunpack(b, pk, r, m) ||
      !ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(ca, pk, r, m, sa) ||
      !ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire_pairunpack(cb, pk, r, m, sb)) {
    fputs("pair-unpack invalid-PK differential failed\n", stderr);
    return 1;
  }
  puts("H3/H4 pair-unpack: ok");
  return 0;
}
