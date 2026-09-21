#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "params.h"
#include "poly.h"
#include "scale1-r-serializer-v2-asm.h"
#include "scale1_r_serializer_v2_hash_g.h"
#include "symmetric.h"
#include "wire-monotone-kem.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "bytes", "words", 0 };
const long long sizes[] = { NTRUPLUS_POLYBYTES, NTRUPLUS_N };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PMU_BANKS 4096
#define WS(base, i) ((base) + (i) * NTRUPLUS_N)
#define BS(base, i) ((base) + (i) * NTRUPLUS_POLYBYTES)
static poly *input_r, *input_m, *input_h, *official_r, *official_m, *official_out;
static poly *official_native_pmu, *official_output_pmu;
static int16_t *wire_output_pmu;
static int16_t *split, *wire_r, *wire_m, *wire_out;
static uint8_t *pk, *bytes, *hashes;
static long long cycles[TIMINGS + 1];
static volatile unsigned int reject_sink;
enum pmu_mode {
  PMU_BASELINE, PMU_OFFICIAL_FORWARD, PMU_OFFICIAL_NATIVE, PMU_GT_FORWARD, PMU_SERIALIZER,
  PMU_SERIALIZER_HASH, PMU_GT_TAIL, PMU_OFFICIAL_TAIL
};
static enum pmu_mode parse_pmu_mode(const char *name) {
  if (!strcmp(name,"baseline")) return PMU_BASELINE;
  if (!strcmp(name,"official_forward")) return PMU_OFFICIAL_FORWARD;
  if (!strcmp(name,"official_forward_preserve_input")) return PMU_OFFICIAL_FORWARD;
  if (!strcmp(name,"official_forward_native_inplace")) return PMU_OFFICIAL_NATIVE;
  if (!strcmp(name,"gt_forward")) return PMU_GT_FORWARD;
  if (!strcmp(name,"serializer_v2")) return PMU_SERIALIZER;
  if (!strcmp(name,"serializer_v2_hash_g")) return PMU_SERIALIZER_HASH;
  if (!strcmp(name,"gt_tail_decode_ma2_egress")) return PMU_GT_TAIL;
  if (!strcmp(name,"h4_exact_egress")) return PMU_GT_TAIL; /* legacy alias */
  if (!strcmp(name,"official_tail")) return PMU_OFFICIAL_TAIL;
  abort();
}

void preallocate(void) {}
void allocate(void) {
  input_r = (poly *)alignedcalloc(BANKS * sizeof *input_r);
  input_m = (poly *)alignedcalloc(BANKS * sizeof *input_m);
  input_h = (poly *)alignedcalloc(BANKS * sizeof *input_h);
  official_r = (poly *)alignedcalloc(BANKS * sizeof *official_r);
  official_m = (poly *)alignedcalloc(BANKS * sizeof *official_m);
  official_out = (poly *)alignedcalloc(BANKS * sizeof *official_out);
  official_native_pmu = (poly *)alignedcalloc(PMU_BANKS * sizeof *official_native_pmu);
  official_output_pmu = (poly *)alignedcalloc(PMU_BANKS * sizeof *official_output_pmu);
  wire_output_pmu = (int16_t *)alignedcalloc(PMU_BANKS * NTRUPLUS_N * sizeof *wire_output_pmu);
  split = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *split);
  wire_r = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_r);
  wire_m = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_m);
  wire_out = (int16_t *)alignedcalloc(BANKS * NTRUPLUS_N * sizeof *wire_out);
  pk = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  bytes = (uint8_t *)alignedcalloc(BANKS * NTRUPLUS_POLYBYTES);
  hashes = (uint8_t *)alignedcalloc(BANKS * (NTRUPLUS_N / 4));
  for (int i = 0; i < PMU_BANKS; ++i)
    for (int j = 0; j < NTRUPLUS_N; ++j)
      official_native_pmu[i].coeffs[j] =
          (int16_t)(((j * 619U + i * 17U + 11U) % 3U) - 1);
}
static uint8_t *hs(int i) { return hashes + i * (NTRUPLUS_N / 4); }
static void reset(void) {
  int i, j;
  for (i = 0; i < BANKS; ++i) {
    for (j = 0; j < NTRUPLUS_N; ++j) {
      input_r[i].coeffs[j] = (int16_t)(((j * 619U + i * 17U + 11U) % 3U) - 1);
      input_m[i].coeffs[j] = (int16_t)(((j * 433U + i * 23U + 7U) % 3U) - 1);
      input_h[i].coeffs[j] = (int16_t)((j * 991U + i * 29U + 47U) % NTRUPLUS_Q);
    }
    poly_tobytes(BS(pk,i), input_h+i);
  }
}
static void official_forward(poly *out, const poly *in) { *out = *in; poly_ntt(out); }
static void wire_forward(int16_t *out, const poly *in) {
  ntruplus1152_exp001_top_split_small(out, in->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(out);
}
static void prepare_states(void) {
  int i;
  for (i = 0; i < BANKS; ++i) {
    official_forward(official_r+i, input_r+i);
    official_forward(official_m+i, input_m+i);
    wire_forward(WS(wire_r,i), input_r+i);
    wire_forward(WS(wire_m,i), input_m+i);
  }
}
static int official_tail(uint8_t *out, poly *scratch, const uint8_t *public_key,
                         const poly *r, const poly *m) {
  poly h; int reject = poly_frombytes(&h, public_key);
  poly_basemul(scratch, &h, r); poly_add(scratch, scratch, m);
  poly_tobytes(out, scratch); return reject;
}
static void preflight(void) {
  uint8_t reference[NTRUPLUS_POLYBYTES], digest[NTRUPLUS_N/4];
  reset(); prepare_states();
  poly_tobytes(reference, official_r);
  ntruplus1152_exp001_scale1_r_serializer_v2(bytes, wire_r);
  if (memcmp(reference, bytes, sizeof reference)) abort();
  hash_g(digest, reference);
  ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(hashes, wire_r);
  if (memcmp(digest, hashes, sizeof digest)) abort();
  if (official_tail(reference, official_out, pk, official_r, official_m) ||
      ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
          bytes, pk, wire_r, wire_m, wire_out) ||
      memcmp(reference, bytes, sizeof reference)) abort();
}
#define RUN(label, preparation, statement) do {                         \
  preparation;                                                         \
  for (i = 0; i <= TIMINGS; ++i) { cycles[i] = cpucycles(); statement; } \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i+1] - cycles[i];   \
  printentry(-1, label "_cycles", cycles, TIMINGS);                    \
} while (0)
void measure(void) {
  int i, loop; preflight();
  const char *pmu = getenv("NTRUPLUS_COMPONENT_PMU");
  if (pmu) {
    enum pmu_mode mode = parse_pmu_mode(pmu);
    for (i = 0; i < 4096; ++i) {
      int k = i % BANKS;
      switch (mode) {
      case PMU_BASELINE: __asm__ volatile("" ::: "memory"); break;
      case PMU_OFFICIAL_FORWARD: official_forward(official_output_pmu+i,official_native_pmu+i); break;
      case PMU_OFFICIAL_NATIVE: poly_ntt(official_native_pmu+i); break;
      case PMU_GT_FORWARD: wire_forward(wire_output_pmu+i*NTRUPLUS_N,official_native_pmu+i); break;
      case PMU_SERIALIZER: ntruplus1152_exp001_scale1_r_serializer_v2(BS(bytes,k),WS(wire_r,k)); break;
      case PMU_SERIALIZER_HASH: ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(hs(k),WS(wire_r,k)); break;
      case PMU_GT_TAIL: reject_sink^=(unsigned)ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(BS(bytes,k),BS(pk,k),WS(wire_r,k),WS(wire_m,k),WS(wire_out,k)); break;
      case PMU_OFFICIAL_TAIL: reject_sink^=(unsigned)official_tail(BS(bytes,k),official_out+k,BS(pk,k),official_r+k,official_m+k); break;
      }
    }
    return;
  }
  for (loop = 0; loop < LOOPS; ++loop) {
    RUN("official_forward_native_inplace", reset(), poly_ntt(input_r+i));
    RUN("official_forward_preserve_input", reset(), official_forward(official_out+i, input_r+i));
    RUN("top_split", reset(), ntruplus1152_exp001_top_split_small(WS(split,i), input_r[i].coeffs));
    RUN("gt_forward_full", reset(),
        (ntruplus1152_exp001_top_split_small(WS(split,i), input_r[i].coeffs),
         ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(WS(split,i))));
    RUN("serializer_v2", (reset(),prepare_states()),
        ntruplus1152_exp001_scale1_r_serializer_v2(BS(bytes,i), WS(wire_r,i)));
    RUN("serializer_v2_hash_g", (reset(),prepare_states()),
        ntruplus1152_exp001_scale1_r_serializer_v2_hash_g(hs(i), WS(wire_r,i)));
    RUN("gt_tail_decode_ma2_egress", (reset(),prepare_states()),
        reject_sink ^= (unsigned)ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
            BS(bytes,i), BS(pk,i), WS(wire_r,i), WS(wire_m,i), WS(wire_out,i)));
    RUN("official_tail", (reset(),prepare_states()),
        reject_sink ^= (unsigned)official_tail(BS(bytes,i), official_out+i, BS(pk,i),
                                               official_r+i, official_m+i));
  }
}
