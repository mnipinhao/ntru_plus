#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "gt_basemul_soa.h"
#include "gt_invntt_soa.h"
#include "gt_ntt_avx2.h"
#include "params.h"
#include "poly.h"

#ifndef BENCH_BUILD_FLAGS
#define BENCH_BUILD_FLAGS "unknown"
#endif

#ifndef BENCH_NINPUTS
#define BENCH_NINPUTS 64
#endif
#ifndef BENCH_NWARMUP
#define BENCH_NWARMUP 100
#endif
#ifndef BENCH_NITERATIONS
#define BENCH_NITERATIONS 1000
#endif
#ifndef BENCH_NTESTS
#define BENCH_NTESTS 101
#endif
#ifndef BENCH_PERF_ITERATIONS
#define BENCH_PERF_ITERATIONS 100000
#endif

_Static_assert((BENCH_NTESTS & 1) == 1, "BENCH_NTESTS must be odd");

void ntt_gt_rowbitrevlayout(int16_t out[NTRUPLUS_N],
                            const int16_t in[NTRUPLUS_N]);
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4],
             int16_t zeta);
extern const int16_t gt_rowbitrev_lambda[2][96];

typedef void (*bench_fn)(unsigned index);

struct operation {
  const char *name;
  bench_fn run;
};

static poly inputs_a[BENCH_NINPUTS];
static poly inputs_b[BENCH_NINPUTS];
static poly ntt_a[BENCH_NINPUTS];
static poly ntt_b[BENCH_NINPUTS];
static poly freq_out[BENCH_NINPUTS];
static poly outputs[BENCH_NINPUTS];
static int16_t gt_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_soa_products[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint32_t next_u32(uint32_t *state)
{
  uint32_t x = *state;

  x ^= x << 13;
  x ^= x >> 17;
  x ^= x << 5;
  *state = x;
  return x;
}

static void fill_poly(poly *out, uint32_t seed)
{
  unsigned i;
  uint32_t state = seed == 0 ? 1 : seed;

  for (i = 0; i < NTRUPLUS_N; i++) {
    out->coeffs[i] = (int16_t)((int)(next_u32(&state) % 3U) - 1);
  }
}

static int mod_q(int64_t value)
{
  int result = (int)(value % NTRUPLUS_Q);

  if (result < 0) {
    result += NTRUPLUS_Q;
  }
  return result;
}

static int16_t centered_mod_q(int64_t value)
{
  int result = mod_q(value);

  if (result > NTRUPLUS_Q / 2) {
    result -= NTRUPLUS_Q;
  }
  return (int16_t)result;
}

static int equal_poly_mod_q(const int16_t *a, const int16_t *b)
{
  unsigned i;

  for (i = 0; i < NTRUPLUS_N; i++) {
    if (mod_q((int)a[i] - b[i]) != 0) {
      fprintf(stderr, "mismatch at coefficient %u: got=%d want=%d\n",
              i, a[i], b[i]);
      return 0;
    }
  }
  return 1;
}

static void schoolbook_mul(poly *out, const poly *a, const poly *b)
{
  int64_t temporary[2 * NTRUPLUS_N - 1] = {0};
  int i;
  int j;

  for (i = 0; i < NTRUPLUS_N; i++) {
    for (j = 0; j < NTRUPLUS_N; j++) {
      temporary[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
    }
  }

  /* X^768 = X^384 - 1. */
  for (i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--) {
    const int64_t value = temporary[i];

    temporary[i - NTRUPLUS_N / 2] += value;
    temporary[i - NTRUPLUS_N] -= value;
  }

  for (i = 0; i < NTRUPLUS_N; i++) {
    out->coeffs[i] = centered_mod_q(temporary[i]);
  }
}

static uint64_t checksum_i16(const int16_t *values)
{
  uint64_t result = UINT64_C(0x6a09e667f3bcc909);
  unsigned i;

  for (i = 0; i < NTRUPLUS_N; i++) {
    result ^= (uint16_t)values[i];
    result *= UINT64_C(0x100000001b3);
    result ^= result >> 32;
  }
  return result;
}

static void prepare_inputs(void)
{
  unsigned i;

  for (i = 0; i < BENCH_NINPUTS; i++) {
    fill_poly(&inputs_a[i], UINT32_C(0x243f6a88) + i);
    fill_poly(&inputs_b[i], UINT32_C(0x85a308d3) + i);
    poly_ntt(&ntt_a[i], &inputs_a[i]);
    poly_ntt(&ntt_b[i], &inputs_b[i]);
    poly_basemul(&freq_out[i], &ntt_a[i], &ntt_b[i]);
    gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_asm_soa(gt_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_soa_products[i], gt_asm_soa_outputs[i],
                        gt_asm_soa_b[i]);
  }
}

static void gt_basemul_rowbitrev_reference(int16_t out[NTRUPLUS_N],
                                           const int16_t a[NTRUPLUS_N],
                                           const int16_t b[NTRUPLUS_N])
{
  unsigned branch;
  unsigned block;

  for (branch = 0; branch < 2; branch++) {
    for (block = 0; block < 96; block++) {
      const unsigned offset = 384U * branch + 4U * block;

      basemul(out + offset, a + offset, b + offset,
              gt_rowbitrev_lambda[branch][block]);
    }
  }
}

static int validate_all(void)
{
  poly got;
  poly want;
  poly frequency_a;
  poly frequency_b;
  poly frequency_product;
  int16_t gt_want[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_b_want[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_soa_want[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_product_want[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_product_soa_want[NTRUPLUS_N] __attribute__((aligned(32)));
  unsigned i;

  for (i = 0; i < 8; i++) {
    poly_ntt(&frequency_a, &inputs_a[i]);
    poly_invntt(&got, &frequency_a);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("production NTT round-trip failed\n", stderr);
      return 0;
    }

    schoolbook_mul(&want, &inputs_a[i], &inputs_b[i]);
    poly_ntt(&frequency_a, &inputs_a[i]);
    poly_ntt(&frequency_b, &inputs_b[i]);
    poly_basemul(&frequency_product, &frequency_a, &frequency_b);
    poly_invntt(&got, &frequency_product);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("production polynomial multiplication failed\n", stderr);
      return 0;
    }

    ntt_gt_rowbitrevlayout(gt_want, inputs_a[i].coeffs);
    gt_ntt_avx2(gt_outputs[i], inputs_a[i].coeffs);
    if (!equal_poly_mod_q(gt_outputs[i], gt_want)) {
      fputs("GT forward NTT differential failed\n", stderr);
      return 0;
    }

    gt_ntt_rowbitrev_to_soa(gt_soa_want, gt_want);
    gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[i], inputs_a[i].coeffs);
    if (!equal_poly_mod_q(gt_asm_soa_outputs[i], gt_soa_want)) {
      fputs("GT ASM SoA forward NTT differential failed\n", stderr);
      return 0;
    }

    ntt_gt_rowbitrevlayout(gt_b_want, inputs_b[i].coeffs);
    gt_ntt_avx2_asm_soa(gt_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_rowbitrev_reference(gt_product_want, gt_want, gt_b_want);
    gt_ntt_rowbitrev_to_soa(gt_product_soa_want, gt_product_want);
    gt_basemul_soa_avx2(gt_soa_products[i], gt_asm_soa_outputs[i],
                        gt_asm_soa_b[i]);
    if (!equal_poly_mod_q(gt_soa_products[i], gt_product_soa_want)) {
      fputs("GT SoA basemul differential failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2(got.coeffs, gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2(got.coeffs, gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA polynomial multiplication failed\n", stderr);
      return 0;
    }
  }
  puts("validation=passed");
  return 1;
}

static void target_ntt(unsigned index)
{
  poly_ntt(&outputs[index], &inputs_a[index]);
}

static void target_gt_ntt(unsigned index)
{
  gt_ntt_avx2(gt_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_asm_soa(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_basemul(unsigned index)
{
  poly_basemul(&freq_out[index], &ntt_a[index], &ntt_b[index]);
}

static void target_gt_basemul_soa(unsigned index)
{
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
}

static void target_gt_invntt_soa(unsigned index)
{
  gt_invntt_soa_avx2(outputs[index].coeffs, gt_asm_soa_outputs[index]);
}

static void target_invntt(unsigned index)
{
  poly_invntt(&outputs[index], &ntt_a[index]);
}

static void target_polymul(unsigned index)
{
  poly_ntt(&ntt_a[index], &inputs_a[index]);
  poly_ntt(&ntt_b[index], &inputs_b[index]);
  poly_basemul(&freq_out[index], &ntt_a[index], &ntt_b[index]);
  poly_invntt(&outputs[index], &freq_out[index]);
}

static void target_gt_polymul_soa(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
  gt_invntt_soa_avx2(outputs[index].coeffs, gt_soa_products[index]);
}

static const struct operation operations[] = {
  {"ntt", target_ntt},
  {"gt-ntt", target_gt_ntt},
  {"gt-ntt-asm-soa", target_gt_ntt_asm_soa},
  {"basemul", target_basemul},
  {"gt-basemul-soa", target_gt_basemul_soa},
  {"invntt", target_invntt},
  {"gt-invntt-soa", target_gt_invntt_soa},
  {"polymul", target_polymul},
  {"gt-polymul-soa", target_gt_polymul_soa},
};

static const struct operation *find_operation(const char *name)
{
  unsigned i;

  for (i = 0; i < sizeof(operations) / sizeof(operations[0]); i++) {
    if (strcmp(name, operations[i].name) == 0) {
      return &operations[i];
    }
  }
  return NULL;
}

static uint64_t start_tsc(void)
{
  _mm_lfence();
  return __rdtsc();
}

static uint64_t stop_tsc(void)
{
  unsigned auxiliary;
  const uint64_t value = __rdtscp(&auxiliary);

  _mm_lfence();
  return value;
}

static int compare_u64(const void *left, const void *right)
{
  const uint64_t a = *(const uint64_t *)left;
  const uint64_t b = *(const uint64_t *)right;

  return (a > b) - (a < b);
}

static void consume_outputs(const struct operation *operation)
{
  unsigned i;

  for (i = 0; i < BENCH_NINPUTS; i++) {
    if (operation->run == target_gt_ntt) {
      sink ^= checksum_i16(gt_outputs[i]);
    } else if (operation->run == target_gt_ntt_asm_soa) {
      sink ^= checksum_i16(gt_asm_soa_outputs[i]);
    } else if (operation->run == target_basemul) {
      sink ^= checksum_i16(freq_out[i].coeffs);
    } else if (operation->run == target_gt_basemul_soa) {
      sink ^= checksum_i16(gt_soa_products[i]);
    } else {
      sink ^= checksum_i16(outputs[i].coeffs);
    }
  }
}

static void run_tsc_benchmark(const struct operation *operation)
{
  uint64_t samples[BENCH_NTESTS];
  unsigned i;
  unsigned j;

  for (i = 0; i < BENCH_NWARMUP; i++) {
    operation->run(i % BENCH_NINPUTS);
  }

  for (i = 0; i < BENCH_NTESTS; i++) {
    const uint64_t start = start_tsc();

    for (j = 0; j < BENCH_NITERATIONS; j++) {
      operation->run(j % BENCH_NINPUTS);
    }
    samples[i] = stop_tsc() - start;
  }

  qsort(samples, BENCH_NTESTS, sizeof(samples[0]), compare_u64);
  consume_outputs(operation);
  printf("operation=%s tsc_median=%" PRIu64
         " tsc_p10=%" PRIu64 " tsc_p90=%" PRIu64
         " tsc_p99=%" PRIu64 " iterations=%d sink=%" PRIu64 "\n",
         operation->name,
         samples[BENCH_NTESTS / 2] / BENCH_NITERATIONS,
         samples[BENCH_NTESTS / 10] / BENCH_NITERATIONS,
         samples[(BENCH_NTESTS * 90) / 100] / BENCH_NITERATIONS,
         samples[(BENCH_NTESTS * 99) / 100] / BENCH_NITERATIONS,
         BENCH_NITERATIONS, sink);
}

static void run_perf_loop(const struct operation *operation)
{
  unsigned i;

  for (i = 0; i < BENCH_NWARMUP; i++) {
    operation->run(i % BENCH_NINPUTS);
  }
  for (i = 0; i < BENCH_PERF_ITERATIONS; i++) {
    operation->run(i % BENCH_NINPUTS);
  }
  consume_outputs(operation);
  printf("operation=%s perf_iterations=%d sink=%" PRIu64 "\n",
         operation->name, BENCH_PERF_ITERATIONS, sink);
}

static void print_build_metadata(void)
{
  printf("compiler=%s\n", __VERSION__);
  printf("build_flags=%s\n", BENCH_BUILD_FLAGS);
  printf("ninputs=%d warmup=%d iterations=%d tests=%d perf_iterations=%d\n",
         BENCH_NINPUTS, BENCH_NWARMUP, BENCH_NITERATIONS, BENCH_NTESTS,
         BENCH_PERF_ITERATIONS);
}

static void print_usage(const char *program)
{
  fprintf(stderr,
          "usage: %s --validate | "
          "<ntt|gt-ntt|gt-ntt-asm-soa|basemul|gt-basemul-soa|invntt|"
          "gt-invntt-soa|polymul|gt-polymul-soa> "
          "[--perf-loop]\n", program);
}

int main(int argc, char **argv)
{
  const struct operation *operation;

  prepare_inputs();
  print_build_metadata();
  if (argc == 2 && strcmp(argv[1], "--validate") == 0) {
    return validate_all() ? 0 : 1;
  }
  if (argc < 2 || argc > 3) {
    print_usage(argv[0]);
    return 2;
  }

  operation = find_operation(argv[1]);
  if (operation == NULL) {
    print_usage(argv[0]);
    return 2;
  }

  if (argc == 3) {
    if (strcmp(argv[2], "--perf-loop") != 0) {
      print_usage(argv[0]);
      return 2;
    }
    run_perf_loop(operation);
  } else {
    run_tsc_benchmark(operation);
  }
  return 0;
}
