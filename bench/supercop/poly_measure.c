#include <stdint.h>
#include <stdlib.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "ntruplus_bench.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "publickeybytes", "secretkeybytes", 0 };
const long long sizes[] = { crypto_kem_PUBLICKEYBYTES, crypto_kem_SECRETKEYBYTES };

static poly *small_a, *small_b, *general_a, *general_b, *transformed_a;
static poly *transformed_b, *output;

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
  for (i = 0; i < NTRUPLUS_N; ++i) {
    small_a->coeffs[i] = (int16_t)((i % 3) - 1);
    small_b->coeffs[i] = (int16_t)(((i * 5) % 3) - 1);
    general_a->coeffs[i] = (int16_t)(((i * 1009 + 17) % 3457) - 1728);
    general_b->coeffs[i] = (int16_t)(((i * 1597 + 29) % 3457) - 1728);
  }
  ntruplus_bench_forward(transformed_a, general_a);
  ntruplus_bench_forward(transformed_b, general_b);
}

#define TIMINGS 32
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
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_ENTRY("forward_small_cycles", ntruplus_bench_forward(output, small_a));
    MEASURE_ENTRY("forward_general_cycles", ntruplus_bench_forward(output, general_a));
    MEASURE_ENTRY("basemul_cycles", ntruplus_bench_basemul(output, transformed_a, transformed_b));
    MEASURE_ENTRY("inverse_cycles", ntruplus_bench_inverse(output, transformed_a));
    MEASURE_ENTRY("baseinv_cycles", (void)ntruplus_bench_baseinv(output, transformed_a));
    MEASURE_ENTRY("poly_mul_small_cycles", ntruplus_bench_mul(output, small_a, small_b));
    MEASURE_ENTRY("poly_mul_general_cycles", ntruplus_bench_mul(output, general_a, general_b));
  }
}
