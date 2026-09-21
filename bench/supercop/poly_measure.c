#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "ntruplus_bench.h"
#include "symmetric.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "publickeybytes", "secretkeybytes", 0 };
const long long sizes[] = { crypto_kem_PUBLICKEYBYTES, crypto_kem_SECRETKEYBYTES };

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PMU_BANKS 4096

static poly *small_a, *small_b, *general_a, *general_b, *transformed_a;
static poly *transformed_b, *output;
static poly *small_native, *general_native, *small_native_pmu, *general_native_pmu;
static poly *forward_output_pmu;
static uint8_t *encoded, *cbd_input, *message, *sotp_mask, *hash_input;
static uint8_t *hash_output, *decoded_message;
static volatile unsigned int reject_sink;
enum pmu_mode {
  PMU_BASELINE, PMU_FORWARD_SMALL, PMU_FORWARD_SMALL_NATIVE,
  PMU_FORWARD_GENERAL, PMU_FORWARD_GENERAL_NATIVE, PMU_BASEMUL,
  PMU_BASEMUL_SCALE, PMU_INVERSE, PMU_BASEINV, PMU_FROMBYTES, PMU_TOBYTES,
  PMU_CBD1, PMU_CREPMOD3, PMU_ADD, PMU_SUB, PMU_SOTP_ENCODE,
  PMU_SOTP_DECODE, PMU_HASH_F, PMU_HASH_G, PMU_HASH_H,
  PMU_MUL_SMALL, PMU_MUL_GENERAL
};
static enum pmu_mode parse_pmu_mode(const char *name) {
#define PMU_NAME(text, value) if (!strcmp(name, text)) return value
  PMU_NAME("baseline", PMU_BASELINE);
  PMU_NAME("forward_small", PMU_FORWARD_SMALL);
  PMU_NAME("forward_small_preserve_input", PMU_FORWARD_SMALL);
  PMU_NAME("forward_small_native_inplace", PMU_FORWARD_SMALL_NATIVE);
  PMU_NAME("forward_general", PMU_FORWARD_GENERAL);
  PMU_NAME("forward_general_preserve_input_unqualified", PMU_FORWARD_GENERAL);
  PMU_NAME("forward_general_native_inplace_unqualified", PMU_FORWARD_GENERAL_NATIVE);
  PMU_NAME("basemul", PMU_BASEMUL);
  PMU_NAME("basemul_scale", PMU_BASEMUL_SCALE);
  PMU_NAME("inverse", PMU_INVERSE);
  PMU_NAME("baseinv", PMU_BASEINV);
  PMU_NAME("poly_frombytes", PMU_FROMBYTES);
  PMU_NAME("poly_tobytes", PMU_TOBYTES);
  PMU_NAME("cbd1", PMU_CBD1);
  PMU_NAME("crepmod3", PMU_CREPMOD3);
  PMU_NAME("poly_add", PMU_ADD);
  PMU_NAME("poly_sub", PMU_SUB);
  PMU_NAME("sotp_encode", PMU_SOTP_ENCODE);
  PMU_NAME("sotp_decode", PMU_SOTP_DECODE);
  PMU_NAME("hash_f", PMU_HASH_F);
  PMU_NAME("hash_g", PMU_HASH_G);
  PMU_NAME("hash_h", PMU_HASH_H);
  PMU_NAME("poly_mul_small", PMU_MUL_SMALL);
  PMU_NAME("poly_mul_general", PMU_MUL_GENERAL);
#undef PMU_NAME
  abort();
}

void preallocate(void) {}

void allocate(void) {
  int i;
  small_a = (poly *)alignedcalloc(sizeof(poly));
  small_b = (poly *)alignedcalloc(sizeof(poly));
  general_a = (poly *)alignedcalloc(sizeof(poly));
  general_b = (poly *)alignedcalloc(sizeof(poly));
  transformed_a = (poly *)alignedcalloc(sizeof(poly));
  transformed_b = (poly *)alignedcalloc(sizeof(poly));
  output = (poly *)alignedcalloc(sizeof(poly));
  small_native = (poly *)alignedcalloc(BANKS * sizeof(poly));
  general_native = (poly *)alignedcalloc(BANKS * sizeof(poly));
  small_native_pmu = (poly *)alignedcalloc(PMU_BANKS * sizeof(poly));
  general_native_pmu = (poly *)alignedcalloc(PMU_BANKS * sizeof(poly));
  forward_output_pmu = (poly *)alignedcalloc(PMU_BANKS * sizeof(poly));
  encoded = (uint8_t *)alignedcalloc(NTRUPLUS_POLYBYTES);
  cbd_input = (uint8_t *)alignedcalloc(NTRUPLUS_N / 4);
  message = (uint8_t *)alignedcalloc(NTRUPLUS_N / 8);
  sotp_mask = (uint8_t *)alignedcalloc(NTRUPLUS_N / 4);
  hash_input = (uint8_t *)alignedcalloc(NTRUPLUS_POLYBYTES);
  hash_output = (uint8_t *)alignedcalloc(HASH_H_OUTBYTES);
  decoded_message = (uint8_t *)alignedcalloc(NTRUPLUS_N / 8);
  for (i = 0; i < NTRUPLUS_N; ++i) {
    small_a->coeffs[i] = (int16_t)((i % 3) - 1);
    small_b->coeffs[i] = (int16_t)(((i * 5) % 3) - 1);
    general_a->coeffs[i] = (int16_t)(((i * 1009 + 17) % 3457) - 1728);
    general_b->coeffs[i] = (int16_t)(((i * 1597 + 29) % 3457) - 1728);
  }
  for (i = 0; i < BANKS; ++i) {
    small_native[i] = *small_a;
    general_native[i] = *general_a;
  }
  for (i = 0; i < PMU_BANKS; ++i) {
    small_native_pmu[i] = *small_a;
    general_native_pmu[i] = *general_a;
  }
  ntruplus_bench_forward(transformed_a, general_a);
  ntruplus_bench_forward(transformed_b, general_b);
  ntruplus_bench_tobytes(encoded, general_a);
  for (i = 0; i < NTRUPLUS_N / 4; ++i)
    cbd_input[i] = sotp_mask[i] = (uint8_t)(i * 73 + 19);
  for (i = 0; i < NTRUPLUS_N / 8; ++i)
    message[i] = (uint8_t)(i * 29 + 7);
  for (i = 0; i < NTRUPLUS_POLYBYTES; ++i)
    hash_input[i] = (uint8_t)(i * 41 + 13);
}

static long long cycles[TIMINGS + 1];

#define MEASURE_ENTRY(label, statement) do {                       \
  for (i = 0; i <= TIMINGS; ++i) {                                 \
    cycles[i] = cpucycles();                                       \
    statement;                                                     \
  }                                                               \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                           \
} while (0)

void measure(void) {
  int i, loop;
  const char *pmu = getenv("NTRUPLUS_COMPONENT_PMU");
  if (pmu) {
    enum pmu_mode mode = parse_pmu_mode(pmu);
    for (i = 0; i < 4096; ++i) {
      switch (mode) {
      case PMU_BASELINE: __asm__ volatile("" ::: "memory"); break;
      case PMU_FORWARD_SMALL: ntruplus_bench_forward(forward_output_pmu+i, small_native_pmu+i); break;
      case PMU_FORWARD_SMALL_NATIVE: ntruplus_bench_forward_inplace(small_native_pmu+i); break;
      case PMU_FORWARD_GENERAL: ntruplus_bench_forward(forward_output_pmu+i, general_native_pmu+i); break;
      case PMU_FORWARD_GENERAL_NATIVE: ntruplus_bench_forward_inplace(general_native_pmu+i); break;
      case PMU_BASEMUL: ntruplus_bench_basemul_unscaled(output, transformed_a, transformed_b); break;
      case PMU_BASEMUL_SCALE: ntruplus_bench_basemul(output, transformed_a, transformed_b); break;
      case PMU_INVERSE: ntruplus_bench_inverse(output, transformed_a); break;
      case PMU_BASEINV: (void)ntruplus_bench_baseinv(output, transformed_a); break;
      case PMU_FROMBYTES: (void)ntruplus_bench_frombytes(output, encoded); break;
      case PMU_TOBYTES: ntruplus_bench_tobytes(encoded, general_a); break;
      case PMU_CBD1: ntruplus_bench_cbd1(output, cbd_input); break;
      case PMU_CREPMOD3: ntruplus_bench_crepmod3(output, general_a); break;
      case PMU_ADD: ntruplus_bench_add(output, general_a, general_b); break;
      case PMU_SUB: ntruplus_bench_sub(output, general_a, general_b); break;
      case PMU_SOTP_ENCODE: ntruplus_bench_sotp_encode(output, message, sotp_mask); break;
      case PMU_SOTP_DECODE: reject_sink ^= (unsigned)ntruplus_bench_sotp_decode(decoded_message, small_a, sotp_mask); break;
      case PMU_HASH_F: ntruplus_bench_hash_f(hash_output, hash_input); break;
      case PMU_HASH_G: ntruplus_bench_hash_g(hash_output, hash_input); break;
      case PMU_HASH_H: ntruplus_bench_hash_h(hash_output, hash_input); break;
      case PMU_MUL_SMALL: ntruplus_bench_mul(output, small_a, small_b); break;
      case PMU_MUL_GENERAL: ntruplus_bench_mul(output, general_a, general_b); break;
      }
    }
    return;
  }
  for (loop = 0; loop < LOOPS; ++loop) {
    for (i = 0; i < BANKS; ++i) {
      small_native[i] = *small_a;
      general_native[i] = *general_a;
    }
    MEASURE_ENTRY("forward_small_native_inplace_cycles", ntruplus_bench_forward_inplace(small_native+i));
    MEASURE_ENTRY("forward_small_preserve_input_cycles", ntruplus_bench_forward(output, small_a));
    MEASURE_ENTRY("forward_general_native_inplace_unqualified_cycles", ntruplus_bench_forward_inplace(general_native+i));
    MEASURE_ENTRY("forward_general_preserve_input_unqualified_cycles", ntruplus_bench_forward(output, general_a));
    MEASURE_ENTRY("basemul_cycles", ntruplus_bench_basemul_unscaled(output, transformed_a, transformed_b));
    MEASURE_ENTRY("basemul_scale_cycles", ntruplus_bench_basemul(output, transformed_a, transformed_b));
    MEASURE_ENTRY("inverse_cycles", ntruplus_bench_inverse(output, transformed_a));
    MEASURE_ENTRY("baseinv_cycles", (void)ntruplus_bench_baseinv(output, transformed_a));
    MEASURE_ENTRY("poly_frombytes_cycles", (void)ntruplus_bench_frombytes(output, encoded));
    MEASURE_ENTRY("poly_tobytes_cycles", ntruplus_bench_tobytes(encoded, general_a));
    MEASURE_ENTRY("cbd1_cycles", ntruplus_bench_cbd1(output, cbd_input));
    MEASURE_ENTRY("crepmod3_cycles", ntruplus_bench_crepmod3(output, general_a));
    MEASURE_ENTRY("poly_add_cycles", ntruplus_bench_add(output, general_a, general_b));
    MEASURE_ENTRY("poly_sub_cycles", ntruplus_bench_sub(output, general_a, general_b));
    MEASURE_ENTRY("sotp_encode_cycles", ntruplus_bench_sotp_encode(output, message, sotp_mask));
    MEASURE_ENTRY("sotp_decode_cycles", reject_sink ^= (unsigned)ntruplus_bench_sotp_decode(decoded_message, small_a, sotp_mask));
    MEASURE_ENTRY("hash_f_cycles", ntruplus_bench_hash_f(hash_output, hash_input));
    MEASURE_ENTRY("hash_g_cycles", ntruplus_bench_hash_g(hash_output, hash_input));
    MEASURE_ENTRY("hash_h_cycles", ntruplus_bench_hash_h(hash_output, hash_input));
    MEASURE_ENTRY("poly_mul_small_cycles", ntruplus_bench_mul(output, small_a, small_b));
    MEASURE_ENTRY("poly_mul_general_cycles", ntruplus_bench_mul(output, general_a, general_b));
  }
}
