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
static int16_t gt_frontend_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_frontend_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_frontend_asm_soa_products[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_direct_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_direct_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_direct_interleaved_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_direct_interleaved_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_half_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_half_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_remapped_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_remapped_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_half_remapped_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_half_remapped_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_resident_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_resident_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_queued_store_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_queued_store_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_centered_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_identity_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_identity_centered_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_u2_identity_centered_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_u4_identity_centered_asm_soa_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_identity_centered_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_u2_identity_centered_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_u4_identity_centered_asm_soa_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_identity_native_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_u2_identity_native_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_u4_identity_native_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_u2_identity_native_fused_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_u2_identity_native_pipelined_fused_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_u2_fused_split_twist_native_pipelined_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_u2_high_first_native_pipelined_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_fixed_high_first_native_pipelined_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_wide_high_first_native_pipelined_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t
    gt_wide_fused_delayed_native_pipelined_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_wide_fused_delayed_row2q2_native_pipelined_outputs
    [BENCH_NINPUTS][NTRUPLUS_N] __attribute__((aligned(32)));
static int16_t gt_wide_fused_delayed_row2q2_native_lazy_outputs
    [BENCH_NINPUTS][NTRUPLUS_N] __attribute__((aligned(32)));
static int16_t gt_wide_fused_delayed_contiguous_twiddles_native_outputs
    [BENCH_NINPUTS][NTRUPLUS_N] __attribute__((aligned(32)));
static int16_t gt_wide_fused_partial_n0_native_pipelined_outputs
    [BENCH_NINPUTS][NTRUPLUS_N] __attribute__((aligned(32)));
static int16_t gt_u4_identity_native_fused_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
/* Shared by the paired native timing targets to fix output cache color. */
static int16_t gt_native_timed_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
/* Shared cache colors for centered/lazy native-consumer boundary timings. */
static int16_t gt_native_boundary_a[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_native_boundary_b[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_native_boundary_product[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_serial_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_interleaved_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_remapped_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_resident_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_queued_store_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_centered_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_centered_queued_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_stage345_native_centered_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_soa_products[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static gt_frontend_scratch gt_frontend_inputs[BENCH_NINPUTS];
static gt_frontend_scratch gt_frontend_outputs[BENCH_NINPUTS];
static gt_frontend_scratch gt_frontend_asm_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_stage12_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_stage12_asm_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_asm_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_identity_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_stage12_identity_row2q2_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_u2_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_u4_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_u2_identity_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_u4_identity_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_direct_outputs[BENCH_NINPUTS];
static gt_stage2_scratch gt_frontend_stage12_half_outputs[BENCH_NINPUTS];
static int16_t gt_invntt32_rows[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invntt32_rows_asm[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invdft3_rows[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invdft3_rows_asm[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invpost_rows[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invpost_outputs[BENCH_NINPUTS][NTRUPLUS_N]
    __attribute__((aligned(32)));
static int16_t gt_invpost_outputs_asm[BENCH_NINPUTS][NTRUPLUS_N]
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

static void native_centered_to_soa(int16_t out[NTRUPLUS_N],
                                   const int16_t in[NTRUPLUS_N])
{
  unsigned branch;
  unsigned coefficient;
  unsigned group;
  unsigned lane;

  for (group = 0; group < 4; group++) {
    for (branch = 0; branch < 2; branch++) {
      for (coefficient = 0; coefficient < 4; coefficient++) {
        for (lane = 0; lane < 16; lane++) {
          const unsigned k3 = lane / 8;
          const unsigned q_lane = lane % 8;
          const unsigned native_batch = 2 * group + branch;
          const unsigned soa_batch = 4 * k3 + group;

          out[64 * soa_batch + 16 * coefficient + 8 * branch + q_lane] =
              in[64 * native_batch + 16 * coefficient + lane];
        }
      }
    }
  }

  for (group = 0; group < 2; group++) {
    for (branch = 0; branch < 2; branch++) {
      for (coefficient = 0; coefficient < 4; coefficient++) {
        for (lane = 0; lane < 16; lane++) {
          const unsigned q_half = lane / 8;
          const unsigned q_lane = lane % 8;
          const unsigned native_batch = 8 + 2 * group + branch;
          const unsigned soa_batch = 8 + group + 2 * q_half;

          out[64 * soa_batch + 16 * coefficient + 8 * branch + q_lane] =
              in[64 * native_batch + 16 * coefficient + lane];
        }
      }
    }
  }
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
    gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_outputs[i],
                                 inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_b[i],
                                 inputs_b[i].coeffs);
    gt_ntt_avx2_frontend(&gt_frontend_inputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_asm(&gt_frontend_stage12_asm_outputs[i],
                                     inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_identity_asm(
        &gt_frontend_stage12_identity_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_stage12_identity_row2q2_asm(
        &gt_stage12_identity_row2q2_outputs[i], &gt_frontend_inputs[i]);
    gt_ntt_avx2_frontend_stage12_u2_asm(
        &gt_frontend_stage12_u2_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_u4_asm(
        &gt_frontend_stage12_u4_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_u2_identity_asm(
        &gt_frontend_stage12_u2_identity_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_u4_identity_asm(
        &gt_frontend_stage12_u4_identity_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_direct_asm(
        &gt_frontend_stage12_direct_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_half_asm(
        &gt_frontend_stage12_half_outputs[i], inputs_a[i].coeffs);
    gt_basemul_soa_avx2(gt_soa_products[i], gt_asm_soa_outputs[i],
                        gt_asm_soa_b[i]);
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
        gt_native_boundary_a[i], inputs_a[i].coeffs, 1);
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
        gt_native_boundary_b[i], inputs_b[i].coeffs, 0);
    gt_basemul_native_avx2(gt_native_boundary_product[i],
                           gt_native_boundary_a[i], gt_native_boundary_b[i]);
    gt_invntt_soa_ntt32_intrinsic(gt_invdft3_rows[i],
                                  gt_asm_soa_outputs[i]);
    memcpy(gt_invdft3_rows_asm[i], gt_invdft3_rows[i],
           sizeof(gt_invdft3_rows[i]));
    memcpy(gt_invpost_rows[i], gt_invdft3_rows[i],
           sizeof(gt_invpost_rows[i]));
    gt_invntt_soa_dft3_intrinsic(gt_invpost_rows[i]);
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
  int16_t gt_native_centered_soa[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_native_lazy_soa[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_native_product_soa[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_basemul_asm_product[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_native_basemul_asm_product[NTRUPLUS_N]
      __attribute__((aligned(32)));
  int16_t gt_direct_queued_a[NTRUPLUS_N] __attribute__((aligned(32)));
  int16_t gt_direct_queued_b[NTRUPLUS_N] __attribute__((aligned(32)));
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

    gt_ntt_avx2_frontend_asm(&gt_frontend_asm_outputs[i],
                             inputs_a[i].coeffs);
    if (memcmp(&gt_frontend_inputs[i], &gt_frontend_asm_outputs[i],
               sizeof(gt_frontend_inputs[i])) != 0) {
      fputs("GT frontend ASM exact boundary differential failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_stage12(&gt_stage12_outputs[i], &gt_frontend_inputs[i]);
    gt_ntt_avx2_stage12_asm(&gt_stage12_asm_outputs[i],
                            &gt_frontend_inputs[i]);
    gt_ntt_avx2_frontend_stage12_asm(&gt_frontend_stage12_asm_outputs[i],
                                     inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_direct_asm(
        &gt_frontend_stage12_direct_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_stage12_half_asm(
        &gt_frontend_stage12_half_outputs[i], inputs_a[i].coeffs);
    if (memcmp(&gt_stage12_outputs[i], &gt_stage12_asm_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0 ||
        memcmp(&gt_stage12_outputs[i], &gt_frontend_stage12_asm_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0 ||
        memcmp(&gt_stage12_outputs[i], &gt_frontend_stage12_u2_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0 ||
        memcmp(&gt_stage12_outputs[i], &gt_frontend_stage12_u4_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0 ||
        memcmp(&gt_stage12_outputs[i], &gt_frontend_stage12_direct_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0 ||
        memcmp(&gt_stage12_outputs[i], &gt_frontend_stage12_half_outputs[i],
               sizeof(gt_stage12_outputs[i])) != 0) {
      fputs("GT frontend/stage12 ASM exact boundary differential failed\n",
            stderr);
      return 0;
    }
    if (!equal_poly_mod_q(
            (const int16_t *)(const void *)&gt_frontend_stage12_identity_outputs[i],
            (const int16_t *)(const void *)&gt_stage12_outputs[i]) ||
        memcmp(&gt_frontend_stage12_identity_outputs[i],
               &gt_frontend_stage12_u2_identity_outputs[i],
               sizeof(gt_frontend_stage12_identity_outputs[i])) != 0 ||
        memcmp(&gt_frontend_stage12_identity_outputs[i],
               &gt_frontend_stage12_u4_identity_outputs[i],
               sizeof(gt_frontend_stage12_identity_outputs[i])) != 0 ||
        !equal_poly_mod_q(
            (const int16_t *)(const void *)&gt_stage12_identity_row2q2_outputs[i],
            (const int16_t *)(const void *)&gt_frontend_stage12_identity_outputs[i])) {
      fputs("GT identity stage12 modulo differential failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_stage345_soa_asm(gt_stage345_serial_outputs[i],
                                 &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_interleaved_asm(
        gt_stage345_interleaved_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_remapped_asm(
        gt_stage345_remapped_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_resident_asm(
        gt_stage345_resident_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_queued_store_asm(
        gt_stage345_queued_store_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_centered_asm(
        gt_stage345_centered_outputs[i], &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_soa_centered_queued_store_asm(
        gt_stage345_centered_queued_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    gt_ntt_avx2_stage345_native_centered_asm(
        gt_stage345_native_centered_outputs[i],
        &gt_frontend_stage12_asm_outputs[i]);
    if (memcmp(gt_stage345_serial_outputs[i],
               gt_stage345_interleaved_outputs[i],
               sizeof(gt_stage345_serial_outputs[i])) != 0 ||
        memcmp(gt_stage345_serial_outputs[i], gt_stage345_remapped_outputs[i],
               sizeof(gt_stage345_serial_outputs[i])) != 0 ||
        memcmp(gt_stage345_serial_outputs[i], gt_stage345_resident_outputs[i],
               sizeof(gt_stage345_serial_outputs[i])) != 0 ||
        memcmp(gt_stage345_serial_outputs[i],
               gt_stage345_queued_store_outputs[i],
               sizeof(gt_stage345_serial_outputs[i])) != 0) {
      fputs("GT stage345 candidate ASM exact differential failed\n", stderr);
      return 0;
    }
    if (!equal_poly_mod_q(gt_stage345_centered_outputs[i],
                          gt_stage345_serial_outputs[i]) ||
        memcmp(gt_stage345_centered_outputs[i],
               gt_stage345_centered_queued_outputs[i],
               sizeof(gt_stage345_centered_outputs[i])) != 0) {
      fputs("GT centered Stage345 differential failed\n", stderr);
      return 0;
    }
    for (unsigned j = 0; j < NTRUPLUS_N; j++) {
      if (gt_stage345_centered_outputs[i][j] < -3080 ||
          gt_stage345_centered_outputs[i][j] > 3079) {
        fputs("GT centered Stage345 range failed\n", stderr);
        return 0;
      }
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_stage345_native_centered_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_stage345_centered_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT native centered Stage345 mapping failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_outputs[i],
                                 inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_direct_asm_soa(gt_direct_asm_soa_outputs[i],
                                        inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
        gt_direct_interleaved_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
        gt_direct_queued_a, inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_half_asm_soa(gt_half_asm_soa_outputs[i],
                                      inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_remapped_asm_soa(gt_remapped_asm_soa_outputs[i],
                                          inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_half_remapped_asm_soa(
        gt_half_remapped_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_resident_asm_soa(gt_resident_asm_soa_outputs[i],
                                          inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_queued_store_asm_soa(
        gt_queued_store_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_centered_asm_soa(
        gt_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_identity_asm_soa(
        gt_identity_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_identity_centered_asm_soa(
        gt_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
        gt_u2_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
        gt_u4_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_identity_native_centered_asm(
        gt_identity_native_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u2_identity_native_centered_asm(
        gt_u2_identity_native_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u4_identity_native_centered_asm(
        gt_u4_identity_native_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_forward_u2_identity_native_centered_fused_asm(
        gt_u2_identity_native_fused_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm(
        gt_u2_identity_native_pipelined_fused_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm(
        gt_u2_fused_split_twist_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm(
        gt_u2_high_first_native_pipelined_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm(
        gt_fixed_high_first_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm(
        gt_wide_high_first_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm(
        gt_wide_fused_delayed_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
        gt_wide_fused_delayed_row2q2_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
        gt_wide_fused_delayed_row2q2_native_lazy_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm(
        gt_wide_fused_delayed_contiguous_twiddles_native_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm(
        gt_wide_fused_partial_n0_native_pipelined_outputs[i],
        inputs_a[i].coeffs);
    gt_ntt_avx2_forward_u4_identity_native_centered_fused_asm(
        gt_u4_identity_native_fused_outputs[i], inputs_a[i].coeffs);
    if (memcmp(gt_asm_soa_outputs[i], gt_frontend_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_direct_queued_a,
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_direct_interleaved_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_direct_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_half_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_remapped_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_half_remapped_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_resident_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_queued_store_asm_soa_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_asm_soa_outputs[i], gt_stage345_serial_outputs[i],
               sizeof(gt_asm_soa_outputs[i])) != 0) {
      fputs("GT frontend ASM SoA forward exact differential failed\n", stderr);
      return 0;
    }
    if (!equal_poly_mod_q(gt_centered_asm_soa_outputs[i],
                          gt_asm_soa_outputs[i]) ||
        !equal_poly_mod_q(gt_identity_asm_soa_outputs[i],
                          gt_asm_soa_outputs[i]) ||
        !equal_poly_mod_q(gt_identity_centered_asm_soa_outputs[i],
                          gt_asm_soa_outputs[i])) {
      fputs("GT reducer full-forward modulo differential failed\n", stderr);
      return 0;
    }
    if (memcmp(gt_u2_identity_centered_asm_soa_outputs[i],
               gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_identity_centered_asm_soa_outputs[i])) != 0 ||
        memcmp(gt_u4_identity_centered_asm_soa_outputs[i],
               gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_identity_centered_asm_soa_outputs[i])) != 0) {
      fputs("GT u2/u4 combined full-forward exact differential failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_identity_native_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT identity native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_u2_identity_native_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u2 identity native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_u4_identity_native_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u4 identity native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_u2_identity_native_fused_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u2 identity fused native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_u2_identity_native_pipelined_fused_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u2 identity pipelined fused native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_u2_fused_split_twist_native_pipelined_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT u2 fused split-twist native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_u2_high_first_native_pipelined_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u2 high-first native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_fixed_high_first_native_pipelined_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT fixed high-first native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_wide_high_first_native_pipelined_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT wide high-first native full-forward mapping failed\n", stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_wide_fused_delayed_native_pipelined_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT wide fused delayed native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_wide_fused_delayed_row2q2_native_pipelined_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT wide fused delayed row2q2 native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_wide_fused_delayed_row2q2_native_lazy_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT wide fused delayed row2q2 lazy-native mapping failed\n",
            stderr);
      return 0;
    }
    for (unsigned j = 0; j < NTRUPLUS_N; j++) {
      if (gt_wide_fused_delayed_row2q2_native_lazy_outputs[i][j] <
              -8 * (GT_NTT_Q - 1) ||
          gt_wide_fused_delayed_row2q2_native_lazy_outputs[i][j] >
              8 * (GT_NTT_Q - 1)) {
        fputs("GT lazy-native full-forward range failed\n", stderr);
        return 0;
      }
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_wide_fused_delayed_contiguous_twiddles_native_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT wide fused delayed contiguous-twiddle native mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(
        gt_product_soa_want,
        gt_wide_fused_partial_n0_native_pipelined_outputs[i]);
    if (!equal_poly_mod_q(gt_product_soa_want,
                          gt_identity_centered_asm_soa_outputs[i])) {
      fputs("GT wide fused partial-n0 native full-forward mapping failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(gt_product_soa_want,
                           gt_u4_identity_native_fused_outputs[i]);
    if (memcmp(gt_product_soa_want, gt_identity_centered_asm_soa_outputs[i],
               sizeof(gt_product_soa_want)) != 0) {
      fputs("GT u4 identity fused native full-forward mapping failed\n",
            stderr);
      return 0;
    }

    ntt_gt_rowbitrevlayout(gt_b_want, inputs_b[i].coeffs);
    gt_ntt_avx2_asm_soa(gt_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_rowbitrev_reference(gt_product_want, gt_want, gt_b_want);
    gt_ntt_rowbitrev_to_soa(gt_product_soa_want, gt_product_want);
    gt_basemul_soa_avx2(gt_soa_products[i], gt_asm_soa_outputs[i],
                        gt_asm_soa_b[i]);
    gt_basemul_soa_asm_avx2(gt_basemul_asm_product, gt_asm_soa_outputs[i],
                            gt_asm_soa_b[i]);
    if (!equal_poly_mod_q(gt_soa_products[i], gt_product_soa_want)) {
      fputs("GT SoA basemul differential failed\n", stderr);
      return 0;
    }
    if (memcmp(gt_basemul_asm_product, gt_soa_products[i],
               sizeof(gt_basemul_asm_product)) != 0) {
      fputs("GT SoA basemul ASM exact differential failed\n", stderr);
      return 0;
    }
    gt_basemul_soa_rminus1_asm_avx2(
        gt_basemul_asm_product, gt_asm_soa_outputs[i], gt_asm_soa_b[i]);
    gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
        got.coeffs, gt_basemul_asm_product);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA R^-1 basemul/inverse polynomial multiplication failed\n",
            stderr);
      return 0;
    }
    gt_basemul_soa_rminus1_c0lazy_asm_avx2(
        gt_basemul_asm_product, gt_asm_soa_outputs[i], gt_asm_soa_b[i]);
    gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
        got.coeffs, gt_basemul_asm_product);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA R^-1 c0-lazy polynomial multiplication failed\n",
            stderr);
      return 0;
    }

    /* Direct native-layout centered-by-lazy consumer, no layout conversion. */
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
        gt_native_boundary_a[i], inputs_a[i].coeffs);
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
        gt_native_boundary_b[i], inputs_b[i].coeffs);
    gt_basemul_native_avx2(gt_native_boundary_product[i],
                           gt_native_boundary_a[i], gt_native_boundary_b[i]);
    gt_basemul_native_asm_avx2(gt_native_basemul_asm_product,
                               gt_native_boundary_a[i],
                               gt_native_boundary_b[i]);
    if (memcmp(gt_native_basemul_asm_product, gt_native_boundary_product[i],
               sizeof(gt_native_basemul_asm_product)) != 0) {
      fputs("GT asymmetric native basemul ASM exact differential failed\n",
            stderr);
      return 0;
    }
    native_centered_to_soa(gt_native_centered_soa,
                           gt_native_boundary_a[i]);
    native_centered_to_soa(gt_native_lazy_soa, gt_native_boundary_b[i]);
    native_centered_to_soa(gt_native_product_soa,
                           gt_native_basemul_asm_product);
    gt_basemul_soa_avx2(gt_product_soa_want, gt_native_centered_soa,
                        gt_native_lazy_soa);
    if (!equal_poly_mod_q(gt_native_product_soa, gt_product_soa_want)) {
      fputs("GT asymmetric native basemul differential failed\n", stderr);
      return 0;
    }
    gt_invntt_soa_avx2_fused_asm(got.coeffs, gt_native_product_soa);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT asymmetric native boundary polymul failed\n", stderr);
      return 0;
    }
    gt_basemul_native_rminus1_asm_avx2(
        gt_native_basemul_asm_product, gt_native_boundary_a[i],
        gt_native_boundary_b[i]);
    native_centered_to_soa(gt_native_product_soa,
                           gt_native_basemul_asm_product);
    gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
        got.coeffs, gt_native_product_soa);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT asymmetric native R^-1 boundary polymul failed\n", stderr);
      return 0;
    }
    gt_basemul_native_rminus1_c0lazy_asm_avx2(
        gt_native_basemul_asm_product, gt_native_boundary_a[i],
        gt_native_boundary_b[i]);
    native_centered_to_soa(gt_native_product_soa,
                           gt_native_basemul_asm_product);
    gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
        got.coeffs, gt_native_product_soa);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT asymmetric native R^-1 c0-lazy boundary polymul failed\n",
            stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_b[i],
                                 inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_frontend_asm_soa_outputs[i],
                        gt_frontend_asm_soa_b[i]);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT frontend ASM fused polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
        gt_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
        gt_identity_centered_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_identity_centered_asm_soa_outputs[i],
                        gt_identity_centered_asm_soa_b[i]);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT identity/centered polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
        gt_u2_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
        gt_u2_identity_centered_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_u2_identity_centered_asm_soa_outputs[i],
                        gt_u2_identity_centered_asm_soa_b[i]);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT u2 combined polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
        gt_u4_identity_centered_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
        gt_u4_identity_centered_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_u4_identity_centered_asm_soa_outputs[i],
                        gt_u4_identity_centered_asm_soa_b[i]);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT u4 combined polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
        gt_direct_interleaved_asm_soa_outputs[i], inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
        gt_direct_interleaved_asm_soa_b[i], inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_direct_interleaved_asm_soa_outputs[i],
                        gt_direct_interleaved_asm_soa_b[i]);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT direct/interleaved ASM polynomial multiplication failed\n",
            stderr);
      return 0;
    }

    gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
        gt_direct_queued_a, inputs_a[i].coeffs);
    gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
        gt_direct_queued_b, inputs_b[i].coeffs);
    gt_basemul_soa_avx2(gt_frontend_asm_soa_products[i],
                        gt_direct_queued_a, gt_direct_queued_b);
    gt_invntt_soa_avx2_fused_asm(got.coeffs,
                                 gt_frontend_asm_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT direct/queued-store ASM polynomial multiplication failed\n",
            stderr);
      return 0;
    }

    gt_invntt_soa_avx2(got.coeffs, gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_hybrid(got.coeffs, gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA hybrid inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_dft3_hybrid(got.coeffs, gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA DFT3 hybrid inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_postprocess_hybrid(got.coeffs,
                                          gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA postprocess hybrid inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_fused_asm(got.coeffs, gt_asm_soa_outputs[i]);
    if (!equal_poly_mod_q(got.coeffs, inputs_a[i].coeffs)) {
      fputs("GT SoA fused ASM inverse round-trip failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_ntt32_intrinsic(gt_invntt32_rows[i],
                                   gt_asm_soa_outputs[i]);
    gt_invntt_soa_ntt32_asm(gt_invntt32_rows_asm[i],
                            gt_asm_soa_outputs[i]);
    if (memcmp(gt_invntt32_rows[i], gt_invntt32_rows_asm[i],
               sizeof(gt_invntt32_rows[i])) != 0) {
      fputs("GT inverse NTT32 ASM boundary differential failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_dft3_intrinsic(gt_invdft3_rows[i]);
    gt_invntt_soa_dft3_asm(gt_invdft3_rows_asm[i]);
    if (memcmp(gt_invdft3_rows[i], gt_invdft3_rows_asm[i],
               sizeof(gt_invdft3_rows[i])) != 0) {
      fputs("GT inverse DFT3 ASM boundary differential failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_postprocess_intrinsic(gt_invpost_outputs[i],
                                        gt_invpost_rows[i]);
    gt_invntt_soa_postprocess_asm(gt_invpost_outputs_asm[i],
                                  gt_invpost_rows[i]);
    if (memcmp(gt_invpost_outputs[i], gt_invpost_outputs_asm[i],
               sizeof(gt_invpost_outputs[i])) != 0) {
      fputs("GT inverse postprocess ASM boundary differential failed\n",
            stderr);
      return 0;
    }

    gt_invntt_soa_avx2(got.coeffs, gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_hybrid(got.coeffs, gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA hybrid polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_dft3_hybrid(got.coeffs, gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA DFT3 hybrid polynomial multiplication failed\n", stderr);
      return 0;
    }

    gt_invntt_soa_avx2_postprocess_hybrid(got.coeffs,
                                          gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA postprocess hybrid polynomial multiplication failed\n",
            stderr);
      return 0;
    }


    gt_invntt_soa_avx2_fused_asm(got.coeffs, gt_soa_products[i]);
    if (!equal_poly_mod_q(got.coeffs, want.coeffs)) {
      fputs("GT SoA fused ASM polynomial multiplication failed\n", stderr);
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

static void target_gt_frontend(unsigned index)
{
  gt_ntt_avx2_frontend(&gt_frontend_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_frontend_asm(unsigned index)
{
  gt_ntt_avx2_frontend_asm(&gt_frontend_asm_outputs[index],
                           inputs_a[index].coeffs);
}

static void target_gt_stage12(unsigned index)
{
  gt_ntt_avx2_stage12(&gt_stage12_outputs[index],
                      &gt_frontend_inputs[index]);
}

static void target_gt_stage12_asm(unsigned index)
{
  gt_ntt_avx2_stage12_asm(&gt_stage12_asm_outputs[index],
                          &gt_frontend_inputs[index]);
}

static void target_gt_stage12_identity_asm(unsigned index)
{
  gt_ntt_avx2_stage12_identity_asm(
      &gt_frontend_stage12_identity_outputs[index],
      &gt_frontend_inputs[index]);
}

static void target_gt_stage12_identity_row2q2_asm(unsigned index)
{
  gt_ntt_avx2_stage12_identity_row2q2_asm(
      &gt_stage12_identity_row2q2_outputs[index], &gt_frontend_inputs[index]);
}

static void target_gt_frontend_stage12_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_asm(
      &gt_frontend_stage12_asm_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_identity_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_identity_asm(
      &gt_frontend_stage12_identity_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_u2_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_u2_asm(
      &gt_frontend_stage12_u2_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_u4_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_u4_asm(
      &gt_frontend_stage12_u4_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_u2_identity_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_u2_identity_asm(
      &gt_frontend_stage12_u2_identity_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_u4_identity_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_u4_identity_asm(
      &gt_frontend_stage12_u4_identity_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_direct_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_direct_asm(
      &gt_frontend_stage12_direct_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_frontend_stage12_half_asm(unsigned index)
{
  gt_ntt_avx2_frontend_stage12_half_asm(
      &gt_frontend_stage12_half_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_stage345_serial_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_asm(
      gt_stage345_serial_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_interleaved_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_interleaved_asm(
      gt_stage345_interleaved_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_remapped_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_remapped_asm(
      gt_stage345_remapped_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_resident_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_resident_asm(
      gt_stage345_resident_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_queued_store_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_queued_store_asm(
      gt_stage345_queued_store_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_centered_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_centered_asm(
      gt_stage345_centered_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_centered_queued_asm(unsigned index)
{
  gt_ntt_avx2_stage345_soa_centered_queued_store_asm(
      gt_stage345_centered_queued_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_stage345_native_centered_asm(unsigned index)
{
  gt_ntt_avx2_stage345_native_centered_asm(
      gt_stage345_native_centered_outputs[index],
      &gt_frontend_stage12_asm_outputs[index]);
}

static void target_gt_ntt_frontend_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_outputs[index],
                               inputs_a[index].coeffs);
}

static void target_gt_ntt_direct_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_direct_asm_soa(gt_direct_asm_soa_outputs[index],
                                      inputs_a[index].coeffs);
}

static void target_gt_ntt_direct_interleaved_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
      gt_direct_interleaved_asm_soa_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_ntt_direct_queued_store_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
      gt_direct_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_half_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_half_asm_soa(gt_half_asm_soa_outputs[index],
                                    inputs_a[index].coeffs);
}

static void target_gt_ntt_remapped_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_remapped_asm_soa(gt_remapped_asm_soa_outputs[index],
                                        inputs_a[index].coeffs);
}

static void target_gt_ntt_half_remapped_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_half_remapped_asm_soa(
      gt_half_remapped_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_resident_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_resident_asm_soa(gt_resident_asm_soa_outputs[index],
                                        inputs_a[index].coeffs);
}

static void target_gt_ntt_queued_store_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_queued_store_asm_soa(
      gt_queued_store_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_centered_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_centered_asm_soa(
      gt_centered_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_centered_queued_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_centered_queued_store_asm_soa(
      gt_centered_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_identity_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_identity_asm_soa(
      gt_identity_asm_soa_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_identity_centered_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_identity_centered_asm_soa(
      gt_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_ntt_identity_centered_queued_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
      gt_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_identity_centered_queued_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
      gt_u2_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_ntt_u4_identity_centered_queued_asm_soa(unsigned index)
{
  gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
      gt_u4_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
}

static void target_gt_ntt_identity_native_centered_asm(unsigned index)
{
  gt_ntt_avx2_frontend_identity_native_centered_asm(
      gt_identity_native_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_identity_native_centered_asm(unsigned index)
{
  gt_ntt_avx2_frontend_u2_identity_native_centered_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u4_identity_native_centered_asm(unsigned index)
{
  gt_ntt_avx2_frontend_u4_identity_native_centered_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_identity_native_centered_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_u2_identity_native_centered_fused_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u4_identity_native_centered_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_u4_identity_native_centered_fused_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_identity_native_centered_pipelined_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_fused_split_twist_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_u2_high_first_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_fixed_high_first_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_wide_high_first_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_wide_fused_delayed_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void
target_gt_ntt_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void
target_gt_ntt_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void
target_gt_ntt_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
}

static void target_gt_ntt_wide_fused_partial_n0_native_centered_pipelined_asm(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm(
      gt_native_timed_outputs[index], inputs_a[index].coeffs);
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

static void target_gt_basemul_native_asymmetric(unsigned index)
{
  gt_basemul_native_avx2(gt_native_boundary_product[index],
                         gt_native_boundary_a[index],
                         gt_native_boundary_b[index]);
}

static void target_gt_basemul_soa_asm(unsigned index)
{
	gt_basemul_soa_asm_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
				gt_asm_soa_b[index]);
}

static void target_gt_basemul_soa_rminus1_asm(unsigned index)
{
  gt_basemul_soa_rminus1_asm_avx2(
      gt_soa_products[index], gt_asm_soa_outputs[index], gt_asm_soa_b[index]);
}

static void target_gt_basemul_soa_rminus1_c0lazy_asm(unsigned index)
{
  gt_basemul_soa_rminus1_c0lazy_asm_avx2(
      gt_soa_products[index], gt_asm_soa_outputs[index], gt_asm_soa_b[index]);
}

static void target_gt_basemul_native_asymmetric_asm(unsigned index)
{
  gt_basemul_native_asm_avx2(gt_native_boundary_product[index],
                             gt_native_boundary_a[index],
                             gt_native_boundary_b[index]);
}

static void target_gt_basemul_native_asymmetric_rminus1_asm(unsigned index)
{
  gt_basemul_native_rminus1_asm_avx2(
      gt_native_boundary_product[index], gt_native_boundary_a[index],
      gt_native_boundary_b[index]);
}

static void target_gt_basemul_native_asymmetric_rminus1_c0lazy_asm(
    unsigned index)
{
  gt_basemul_native_rminus1_c0lazy_asm_avx2(
      gt_native_boundary_product[index], gt_native_boundary_a[index],
      gt_native_boundary_b[index]);
}

/*
 * Forward-pair + basemul boundaries intentionally omit inverse layout work.
 * Both targets use the same native buffers; only B's terminal center differs.
 */
static void target_gt_native_forward2_basemul_centered_boundary(unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs);
  gt_basemul_native_avx2(gt_native_boundary_product[index],
                         gt_native_boundary_a[index],
                         gt_native_boundary_b[index]);
}

static void target_gt_native_forward2_basemul_asymmetric_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs);
  gt_basemul_native_avx2(gt_native_boundary_product[index],
                         gt_native_boundary_a[index],
                         gt_native_boundary_b[index]);
}

static void target_gt_native_forward2_basemul_runtime_centered_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs, 1);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs, 1);
  gt_basemul_native_avx2(gt_native_boundary_product[index],
                         gt_native_boundary_a[index],
                         gt_native_boundary_b[index]);
}

static void target_gt_native_forward2_basemul_runtime_asymmetric_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs, 1);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs, 0);
  gt_basemul_native_avx2(gt_native_boundary_product[index],
                         gt_native_boundary_a[index],
                         gt_native_boundary_b[index]);
}

static void target_gt_native_forward2_basemul_runtime_asymmetric_asm_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs, 1);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs, 0);
  gt_basemul_native_asm_avx2(gt_native_boundary_product[index],
                             gt_native_boundary_a[index],
                             gt_native_boundary_b[index]);
}

static void
target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_asm_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs, 1);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs, 0);
  gt_basemul_native_rminus1_asm_avx2(
      gt_native_boundary_product[index], gt_native_boundary_a[index],
      gt_native_boundary_b[index]);
}

static void
target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_c0lazy_asm_boundary(
    unsigned index)
{
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_a[index], inputs_a[index].coeffs, 1);
  gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm(
      gt_native_boundary_b[index], inputs_b[index].coeffs, 0);
  gt_basemul_native_rminus1_c0lazy_asm_avx2(
      gt_native_boundary_product[index], gt_native_boundary_a[index],
      gt_native_boundary_b[index]);
}

static void target_gt_invntt_soa(unsigned index)
{
  gt_invntt_soa_avx2(outputs[index].coeffs, gt_asm_soa_outputs[index]);
}

static void target_gt_invntt_soa_hybrid(unsigned index)
{
  gt_invntt_soa_avx2_hybrid(outputs[index].coeffs,
                            gt_asm_soa_outputs[index]);
}

static void target_gt_invntt_soa_dft3_hybrid(unsigned index)
{
  gt_invntt_soa_avx2_dft3_hybrid(outputs[index].coeffs,
                                 gt_asm_soa_outputs[index]);
}

static void target_gt_invntt_soa_postprocess_hybrid(unsigned index)
{
  gt_invntt_soa_avx2_postprocess_hybrid(outputs[index].coeffs,
                                        gt_asm_soa_outputs[index]);
}

static void target_gt_invntt_soa_fused_asm(unsigned index)
{
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_asm_soa_outputs[index]);
}

static void target_gt_invntt32_intrinsic(unsigned index)
{
  gt_invntt_soa_ntt32_intrinsic(gt_invntt32_rows[index],
                                gt_asm_soa_outputs[index]);
}

static void target_gt_invntt32_asm(unsigned index)
{
  gt_invntt_soa_ntt32_asm(gt_invntt32_rows_asm[index],
                          gt_asm_soa_outputs[index]);
}

static void target_gt_invdft3_intrinsic(unsigned index)
{
  gt_invntt_soa_dft3_intrinsic(gt_invdft3_rows[index]);
}

static void target_gt_invdft3_asm(unsigned index)
{
  gt_invntt_soa_dft3_asm(gt_invdft3_rows_asm[index]);
}

static void target_gt_invpost_intrinsic(unsigned index)
{
  gt_invntt_soa_postprocess_intrinsic(gt_invpost_outputs[index],
                                      gt_invpost_rows[index]);
}

static void target_gt_invpost_asm(unsigned index)
{
  gt_invntt_soa_postprocess_asm(gt_invpost_outputs_asm[index],
                                gt_invpost_rows[index]);
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

static void target_gt_polymul_soa_hybrid(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_hybrid(outputs[index].coeffs, gt_soa_products[index]);
}

static void target_gt_polymul_soa_dft3_hybrid(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_dft3_hybrid(outputs[index].coeffs,
                                 gt_soa_products[index]);
}

static void target_gt_polymul_soa_postprocess_hybrid(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_postprocess_hybrid(outputs[index].coeffs,
                                        gt_soa_products[index]);
}

static void target_gt_polymul_soa_basemul_asm_postprocess_hybrid(
    unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_asm_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                          gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_postprocess_hybrid(outputs[index].coeffs,
                                        gt_soa_products[index]);
}

static void target_gt_polymul_soa_rminus1_asm_postprocess_hybrid(
    unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_rminus1_asm_avx2(
      gt_soa_products[index], gt_asm_soa_outputs[index], gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
      outputs[index].coeffs, gt_soa_products[index]);
}

static void target_gt_polymul_soa_rminus1_c0lazy_asm_postprocess_hybrid(
    unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_rminus1_c0lazy_asm_avx2(
      gt_soa_products[index], gt_asm_soa_outputs[index], gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_rminus1_postprocess_hybrid(
      outputs[index].coeffs, gt_soa_products[index]);
}

static void target_gt_polymul_soa_fused_asm(unsigned index)
{
  gt_ntt_avx2_asm_soa(gt_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_asm_soa(gt_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_soa_products[index], gt_asm_soa_outputs[index],
                      gt_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_soa_products[index]);
}

static void target_gt_polymul_frontend_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_outputs[index],
                               inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_asm_soa(gt_frontend_asm_soa_b[index],
                               inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_frontend_asm_soa_outputs[index],
                      gt_frontend_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_identity_centered_queued_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
      gt_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_identity_centered_queued_store_asm_soa(
      gt_identity_centered_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_identity_centered_asm_soa_outputs[index],
                      gt_identity_centered_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_u2_identity_centered_queued_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
      gt_u2_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_u2_identity_centered_queued_store_asm_soa(
      gt_u2_identity_centered_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_u2_identity_centered_asm_soa_outputs[index],
                      gt_u2_identity_centered_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_u4_identity_centered_queued_fused_asm(
    unsigned index)
{
  gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
      gt_u4_identity_centered_asm_soa_outputs[index],
      inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_u4_identity_centered_queued_store_asm_soa(
      gt_u4_identity_centered_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_u4_identity_centered_asm_soa_outputs[index],
                      gt_u4_identity_centered_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_direct_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_direct_asm_soa(gt_direct_asm_soa_outputs[index],
                                      inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_direct_asm_soa(gt_direct_asm_soa_b[index],
                                      inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_direct_asm_soa_outputs[index],
                      gt_direct_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_direct_interleaved_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
      gt_direct_interleaved_asm_soa_outputs[index],
      inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
      gt_direct_interleaved_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_direct_interleaved_asm_soa_outputs[index],
                      gt_direct_interleaved_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_direct_queued_store_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
      gt_direct_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
      gt_direct_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_direct_asm_soa_outputs[index],
                      gt_direct_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_half_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_half_asm_soa(gt_half_asm_soa_outputs[index],
                                    inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_half_asm_soa(gt_half_asm_soa_b[index],
                                    inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_half_asm_soa_outputs[index],
                      gt_half_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_remapped_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_remapped_asm_soa(gt_remapped_asm_soa_outputs[index],
                                        inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_remapped_asm_soa(gt_remapped_asm_soa_b[index],
                                        inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_remapped_asm_soa_outputs[index],
                      gt_remapped_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_half_remapped_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_half_remapped_asm_soa(
      gt_half_remapped_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_half_remapped_asm_soa(
      gt_half_remapped_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_half_remapped_asm_soa_outputs[index],
                      gt_half_remapped_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_resident_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_resident_asm_soa(gt_resident_asm_soa_outputs[index],
                                        inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_resident_asm_soa(gt_resident_asm_soa_b[index],
                                        inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_resident_asm_soa_outputs[index],
                      gt_resident_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static void target_gt_polymul_queued_store_fused_asm(unsigned index)
{
  gt_ntt_avx2_frontend_queued_store_asm_soa(
      gt_queued_store_asm_soa_outputs[index], inputs_a[index].coeffs);
  gt_ntt_avx2_frontend_queued_store_asm_soa(
      gt_queued_store_asm_soa_b[index], inputs_b[index].coeffs);
  gt_basemul_soa_avx2(gt_frontend_asm_soa_products[index],
                      gt_queued_store_asm_soa_outputs[index],
                      gt_queued_store_asm_soa_b[index]);
  gt_invntt_soa_avx2_fused_asm(outputs[index].coeffs,
                               gt_frontend_asm_soa_products[index]);
}

static const struct operation operations[] = {
  {"ntt", target_ntt},
  {"gt-ntt", target_gt_ntt},
  {"gt-ntt-asm-soa", target_gt_ntt_asm_soa},
  {"gt-frontend", target_gt_frontend},
  {"gt-frontend-asm", target_gt_frontend_asm},
  {"gt-stage12", target_gt_stage12},
  {"gt-stage12-asm", target_gt_stage12_asm},
  {"gt-stage12-identity-asm", target_gt_stage12_identity_asm},
  {"gt-stage12-identity-row2q2-asm",
   target_gt_stage12_identity_row2q2_asm},
  {"gt-frontend-stage12-asm", target_gt_frontend_stage12_asm},
  {"gt-frontend-stage12-identity-asm",
   target_gt_frontend_stage12_identity_asm},
  {"gt-frontend-stage12-u2-asm", target_gt_frontend_stage12_u2_asm},
  {"gt-frontend-stage12-u4-asm", target_gt_frontend_stage12_u4_asm},
  {"gt-frontend-stage12-u2-identity-asm",
   target_gt_frontend_stage12_u2_identity_asm},
  {"gt-frontend-stage12-u4-identity-asm",
   target_gt_frontend_stage12_u4_identity_asm},
  {"gt-frontend-stage12-direct-asm", target_gt_frontend_stage12_direct_asm},
  {"gt-frontend-stage12-half-asm", target_gt_frontend_stage12_half_asm},
  {"gt-stage345-serial-asm", target_gt_stage345_serial_asm},
  {"gt-stage345-interleaved-asm", target_gt_stage345_interleaved_asm},
  {"gt-stage345-remapped-asm", target_gt_stage345_remapped_asm},
  {"gt-stage345-resident-asm", target_gt_stage345_resident_asm},
  {"gt-stage345-queued-store-asm", target_gt_stage345_queued_store_asm},
  {"gt-stage345-centered-asm", target_gt_stage345_centered_asm},
  {"gt-stage345-centered-queued-asm",
   target_gt_stage345_centered_queued_asm},
  {"gt-stage345-native-centered-asm",
   target_gt_stage345_native_centered_asm},
  {"gt-ntt-frontend-asm-soa", target_gt_ntt_frontend_asm_soa},
  {"gt-ntt-direct-asm-soa", target_gt_ntt_direct_asm_soa},
  {"gt-ntt-direct-interleaved-asm-soa",
   target_gt_ntt_direct_interleaved_asm_soa},
  {"gt-ntt-direct-queued-store-asm-soa",
   target_gt_ntt_direct_queued_store_asm_soa},
  {"gt-ntt-half-asm-soa", target_gt_ntt_half_asm_soa},
  {"gt-ntt-remapped-asm-soa", target_gt_ntt_remapped_asm_soa},
  {"gt-ntt-half-remapped-asm-soa", target_gt_ntt_half_remapped_asm_soa},
  {"gt-ntt-resident-asm-soa", target_gt_ntt_resident_asm_soa},
  {"gt-ntt-queued-store-asm-soa", target_gt_ntt_queued_store_asm_soa},
  {"gt-ntt-centered-asm-soa", target_gt_ntt_centered_asm_soa},
  {"gt-ntt-centered-queued-asm-soa",
   target_gt_ntt_centered_queued_asm_soa},
  {"gt-ntt-identity-asm-soa", target_gt_ntt_identity_asm_soa},
  {"gt-ntt-identity-centered-asm-soa",
   target_gt_ntt_identity_centered_asm_soa},
  {"gt-ntt-identity-centered-queued-asm-soa",
   target_gt_ntt_identity_centered_queued_asm_soa},
  {"gt-ntt-u2-identity-centered-queued-asm-soa",
   target_gt_ntt_u2_identity_centered_queued_asm_soa},
  {"gt-ntt-u4-identity-centered-queued-asm-soa",
   target_gt_ntt_u4_identity_centered_queued_asm_soa},
  {"gt-ntt-identity-native-centered-asm",
   target_gt_ntt_identity_native_centered_asm},
  {"gt-ntt-u2-identity-native-centered-asm",
   target_gt_ntt_u2_identity_native_centered_asm},
  {"gt-ntt-u4-identity-native-centered-asm",
   target_gt_ntt_u4_identity_native_centered_asm},
  {"gt-ntt-u2-identity-native-centered-fused-asm",
   target_gt_ntt_u2_identity_native_centered_fused_asm},
  {"gt-ntt-u2-identity-native-centered-pipelined-fused-asm",
   target_gt_ntt_u2_identity_native_centered_pipelined_fused_asm},
  {"gt-ntt-u2-fused-split-twist-native-centered-pipelined-asm",
   target_gt_ntt_u2_fused_split_twist_native_centered_pipelined_asm},
  {"gt-ntt-u2-high-first-native-centered-pipelined-asm",
   target_gt_ntt_u2_high_first_native_centered_pipelined_asm},
  {"gt-ntt-fixed-high-first-native-centered-pipelined-asm",
   target_gt_ntt_fixed_high_first_native_centered_pipelined_asm},
  {"gt-ntt-wide-high-first-native-centered-pipelined-asm",
   target_gt_ntt_wide_high_first_native_centered_pipelined_asm},
  {"gt-ntt-wide-fused-delayed-native-centered-pipelined-asm",
   target_gt_ntt_wide_fused_delayed_native_centered_pipelined_asm},
  {"gt-ntt-wide-fused-delayed-row2q2-native-centered-pipelined-asm",
   target_gt_ntt_wide_fused_delayed_row2q2_native_centered_pipelined_asm},
  {"gt-ntt-wide-fused-delayed-row2q2-native-lazy-pipelined-asm",
   target_gt_ntt_wide_fused_delayed_row2q2_native_lazy_pipelined_asm},
  {"gt-ntt-wide-fused-delayed-native-centered-contiguous-twiddles-pipelined-asm",
   target_gt_ntt_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm},
  {"gt-ntt-wide-fused-partial-n0-native-centered-pipelined-asm",
   target_gt_ntt_wide_fused_partial_n0_native_centered_pipelined_asm},
  {"gt-ntt-u4-identity-native-centered-fused-asm",
   target_gt_ntt_u4_identity_native_centered_fused_asm},
  {"basemul", target_basemul},
  {"gt-basemul-soa", target_gt_basemul_soa},
  {"gt-basemul-native-asymmetric", target_gt_basemul_native_asymmetric},
  {"gt-basemul-soa-asm", target_gt_basemul_soa_asm},
  {"gt-basemul-soa-rminus1-asm", target_gt_basemul_soa_rminus1_asm},
  {"gt-basemul-soa-rminus1-c0lazy-asm",
   target_gt_basemul_soa_rminus1_c0lazy_asm},
  {"gt-basemul-native-asymmetric-asm",
   target_gt_basemul_native_asymmetric_asm},
  {"gt-basemul-native-asymmetric-rminus1-asm",
   target_gt_basemul_native_asymmetric_rminus1_asm},
  {"gt-basemul-native-asymmetric-rminus1-c0lazy-asm",
   target_gt_basemul_native_asymmetric_rminus1_c0lazy_asm},
  {"gt-native-forward2-basemul-centered-boundary",
   target_gt_native_forward2_basemul_centered_boundary},
  {"gt-native-forward2-basemul-asymmetric-boundary",
   target_gt_native_forward2_basemul_asymmetric_boundary},
  {"gt-native-forward2-basemul-runtime-centered-boundary",
   target_gt_native_forward2_basemul_runtime_centered_boundary},
  {"gt-native-forward2-basemul-runtime-asymmetric-boundary",
   target_gt_native_forward2_basemul_runtime_asymmetric_boundary},
  {"gt-native-forward2-basemul-runtime-asymmetric-asm-boundary",
   target_gt_native_forward2_basemul_runtime_asymmetric_asm_boundary},
  {"gt-native-forward2-basemul-runtime-asymmetric-rminus1-asm-boundary",
   target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_asm_boundary},
  {"gt-native-forward2-basemul-runtime-asymmetric-rminus1-c0lazy-asm-boundary",
   target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_c0lazy_asm_boundary},
  {"invntt", target_invntt},
  {"gt-invntt32", target_gt_invntt32_intrinsic},
  {"gt-invntt32-asm", target_gt_invntt32_asm},
  {"gt-invdft3", target_gt_invdft3_intrinsic},
  {"gt-invdft3-asm", target_gt_invdft3_asm},
  {"gt-invpost", target_gt_invpost_intrinsic},
  {"gt-invpost-asm", target_gt_invpost_asm},
  {"gt-invntt-soa", target_gt_invntt_soa},
  {"gt-invntt-soa-hybrid", target_gt_invntt_soa_hybrid},
  {"gt-invntt-soa-dft3-hybrid", target_gt_invntt_soa_dft3_hybrid},
  {"gt-invntt-soa-postprocess-hybrid",
   target_gt_invntt_soa_postprocess_hybrid},
  {"gt-invntt-soa-fused-asm", target_gt_invntt_soa_fused_asm},
  {"polymul", target_polymul},
  {"gt-polymul-soa", target_gt_polymul_soa},
  {"gt-polymul-soa-hybrid", target_gt_polymul_soa_hybrid},
  {"gt-polymul-soa-dft3-hybrid", target_gt_polymul_soa_dft3_hybrid},
  {"gt-polymul-soa-postprocess-hybrid",
   target_gt_polymul_soa_postprocess_hybrid},
  {"gt-polymul-soa-basemul-asm-postprocess-hybrid",
   target_gt_polymul_soa_basemul_asm_postprocess_hybrid},
  {"gt-polymul-soa-rminus1-asm-postprocess-hybrid",
   target_gt_polymul_soa_rminus1_asm_postprocess_hybrid},
  {"gt-polymul-soa-rminus1-c0lazy-asm-postprocess-hybrid",
   target_gt_polymul_soa_rminus1_c0lazy_asm_postprocess_hybrid},
  {"gt-polymul-soa-fused-asm", target_gt_polymul_soa_fused_asm},
  {"gt-polymul-frontend-fused-asm",
   target_gt_polymul_frontend_fused_asm},
  {"gt-polymul-identity-centered-queued-fused-asm",
   target_gt_polymul_identity_centered_queued_fused_asm},
  {"gt-polymul-u2-identity-centered-queued-fused-asm",
   target_gt_polymul_u2_identity_centered_queued_fused_asm},
  {"gt-polymul-u4-identity-centered-queued-fused-asm",
   target_gt_polymul_u4_identity_centered_queued_fused_asm},
  {"gt-polymul-direct-fused-asm", target_gt_polymul_direct_fused_asm},
  {"gt-polymul-direct-interleaved-fused-asm",
   target_gt_polymul_direct_interleaved_fused_asm},
  {"gt-polymul-direct-queued-store-fused-asm",
   target_gt_polymul_direct_queued_store_fused_asm},
  {"gt-polymul-half-fused-asm", target_gt_polymul_half_fused_asm},
  {"gt-polymul-remapped-fused-asm", target_gt_polymul_remapped_fused_asm},
  {"gt-polymul-half-remapped-fused-asm",
   target_gt_polymul_half_remapped_fused_asm},
  {"gt-polymul-resident-fused-asm", target_gt_polymul_resident_fused_asm},
  {"gt-polymul-queued-store-fused-asm",
   target_gt_polymul_queued_store_fused_asm},
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
    } else if (operation->run == target_gt_ntt_frontend_asm_soa) {
      sink ^= checksum_i16(gt_frontend_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_direct_asm_soa) {
      sink ^= checksum_i16(gt_direct_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_direct_interleaved_asm_soa) {
      sink ^= checksum_i16(gt_direct_interleaved_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_direct_queued_store_asm_soa) {
      sink ^= checksum_i16(gt_direct_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_half_asm_soa) {
      sink ^= checksum_i16(gt_half_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_remapped_asm_soa) {
      sink ^= checksum_i16(gt_remapped_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_half_remapped_asm_soa) {
      sink ^= checksum_i16(gt_half_remapped_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_resident_asm_soa) {
      sink ^= checksum_i16(gt_resident_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_queued_store_asm_soa) {
      sink ^= checksum_i16(gt_queued_store_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_centered_asm_soa ||
               operation->run == target_gt_ntt_centered_queued_asm_soa) {
      sink ^= checksum_i16(gt_centered_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_identity_asm_soa) {
      sink ^= checksum_i16(gt_identity_asm_soa_outputs[i]);
    } else if (operation->run == target_gt_ntt_identity_centered_asm_soa ||
               operation->run ==
                   target_gt_ntt_identity_centered_queued_asm_soa) {
      sink ^= checksum_i16(gt_identity_centered_asm_soa_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_identity_centered_queued_asm_soa) {
      sink ^= checksum_i16(gt_u2_identity_centered_asm_soa_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u4_identity_centered_queued_asm_soa) {
      sink ^= checksum_i16(gt_u4_identity_centered_asm_soa_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_identity_native_centered_asm) {
      sink ^= checksum_i16(gt_identity_native_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_identity_native_centered_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u4_identity_native_centered_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_identity_native_centered_fused_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_identity_native_centered_pipelined_fused_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_fused_split_twist_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u2_high_first_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_fixed_high_first_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_high_first_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_fused_delayed_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_fused_delayed_row2q2_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_fused_delayed_row2q2_native_lazy_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_wide_fused_partial_n0_native_centered_pipelined_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run ==
               target_gt_ntt_u4_identity_native_centered_fused_asm) {
      sink ^= checksum_i16(gt_native_timed_outputs[i]);
    } else if (operation->run == target_gt_frontend) {
      sink ^= checksum_i16((const int16_t *)(const void *)&gt_frontend_outputs[i]);
    } else if (operation->run == target_gt_frontend_asm) {
      sink ^= checksum_i16(
          (const int16_t *)(const void *)&gt_frontend_asm_outputs[i]);
    } else if (operation->run == target_gt_stage12) {
      sink ^= checksum_i16((const int16_t *)(const void *)&gt_stage12_outputs[i]);
    } else if (operation->run == target_gt_stage12_asm) {
      sink ^= checksum_i16(
          (const int16_t *)(const void *)&gt_stage12_asm_outputs[i]);
    } else if (operation->run == target_gt_stage12_identity_asm ||
               operation->run == target_gt_frontend_stage12_identity_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_identity_outputs[i]);
    } else if (operation->run == target_gt_stage12_identity_row2q2_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_stage12_identity_row2q2_outputs[i]);
    } else if (operation->run == target_gt_frontend_stage12_u2_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_u2_outputs[i]);
    } else if (operation->run == target_gt_frontend_stage12_u4_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_u4_outputs[i]);
    } else if (operation->run ==
               target_gt_frontend_stage12_u2_identity_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_u2_identity_outputs[i]);
    } else if (operation->run ==
               target_gt_frontend_stage12_u4_identity_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_u4_identity_outputs[i]);
    } else if (operation->run == target_gt_frontend_stage12_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_asm_outputs[i]);
    } else if (operation->run == target_gt_frontend_stage12_direct_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_direct_outputs[i]);
    } else if (operation->run == target_gt_frontend_stage12_half_asm) {
      sink ^= checksum_i16((const int16_t *)(const void *)
                               &gt_frontend_stage12_half_outputs[i]);
    } else if (operation->run == target_gt_stage345_serial_asm) {
      sink ^= checksum_i16(gt_stage345_serial_outputs[i]);
    } else if (operation->run == target_gt_stage345_interleaved_asm) {
      sink ^= checksum_i16(gt_stage345_interleaved_outputs[i]);
    } else if (operation->run == target_gt_stage345_remapped_asm) {
      sink ^= checksum_i16(gt_stage345_remapped_outputs[i]);
    } else if (operation->run == target_gt_stage345_resident_asm) {
      sink ^= checksum_i16(gt_stage345_resident_outputs[i]);
    } else if (operation->run == target_gt_stage345_queued_store_asm) {
      sink ^= checksum_i16(gt_stage345_queued_store_outputs[i]);
    } else if (operation->run == target_gt_stage345_centered_asm) {
      sink ^= checksum_i16(gt_stage345_centered_outputs[i]);
    } else if (operation->run == target_gt_stage345_centered_queued_asm) {
      sink ^= checksum_i16(gt_stage345_centered_queued_outputs[i]);
    } else if (operation->run == target_gt_stage345_native_centered_asm) {
      sink ^= checksum_i16(gt_stage345_native_centered_outputs[i]);
    } else if (operation->run == target_basemul) {
      sink ^= checksum_i16(freq_out[i].coeffs);
    } else if (operation->run == target_gt_basemul_soa ||
               operation->run == target_gt_basemul_soa_asm ||
               operation->run == target_gt_basemul_soa_rminus1_asm ||
               operation->run == target_gt_basemul_soa_rminus1_c0lazy_asm) {
      sink ^= checksum_i16(gt_soa_products[i]);
    } else if (operation->run == target_gt_basemul_native_asymmetric ||
               operation->run == target_gt_basemul_native_asymmetric_asm ||
               operation->run ==
                   target_gt_basemul_native_asymmetric_rminus1_asm ||
               operation->run ==
                   target_gt_basemul_native_asymmetric_rminus1_c0lazy_asm ||
               operation->run ==
                   target_gt_native_forward2_basemul_centered_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_asymmetric_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_runtime_centered_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_runtime_asymmetric_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_runtime_asymmetric_asm_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_asm_boundary ||
               operation->run ==
                   target_gt_native_forward2_basemul_runtime_asymmetric_rminus1_c0lazy_asm_boundary) {
      sink ^= checksum_i16(gt_native_boundary_product[i]);
    } else if (operation->run == target_gt_invntt32_intrinsic) {
      sink ^= checksum_i16(gt_invntt32_rows[i]);
    } else if (operation->run == target_gt_invntt32_asm) {
      sink ^= checksum_i16(gt_invntt32_rows_asm[i]);
    } else if (operation->run == target_gt_invdft3_intrinsic) {
      sink ^= checksum_i16(gt_invdft3_rows[i]);
    } else if (operation->run == target_gt_invdft3_asm) {
      sink ^= checksum_i16(gt_invdft3_rows_asm[i]);
    } else if (operation->run == target_gt_invpost_intrinsic) {
      sink ^= checksum_i16(gt_invpost_outputs[i]);
    } else if (operation->run == target_gt_invpost_asm) {
      sink ^= checksum_i16(gt_invpost_outputs_asm[i]);
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
  unsigned i;

  fprintf(stderr, "usage: %s --validate | <operation> [--perf-loop]\n",
          program);
  fputs("operations:", stderr);
  for (i = 0; i < sizeof(operations) / sizeof(operations[0]); i++) {
    fprintf(stderr, " %s", operations[i].name);
  }
  fputc('\n', stderr);
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
