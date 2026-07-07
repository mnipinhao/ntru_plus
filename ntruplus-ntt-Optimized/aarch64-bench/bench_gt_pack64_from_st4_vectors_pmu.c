/*
 * Benchmark-only pack64 microkernel model for base_gt direct-byte work.
 *
 * Contract:
 *   two st4-shaped base_gt output batches, each holding 32 coefficients as
 *   out0..out3 SoA quartic vectors, are normalized and packed into the same
 *   96 bytes that poly_tobytes would emit for those 64 coefficients.
 *
 * This target is intentionally not wired into decap/keygen.
 */
#if !defined(__linux__)
#error "bench_gt_pack64_from_st4_vectors_pmu requires Linux perf_event_open"
#endif

#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <arm_neon.h>
#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "bench_build_config.h"
#include "params.h"
#include "poly.h"

#ifndef NTESTS
#define NTESTS 31
#endif
#ifndef NITERATIONS
#define NITERATIONS 5000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif
#ifndef NINPUTS
#define NINPUTS 256
#endif
#ifndef NVALID_ORACLE
#define NVALID_ORACLE 4096
#endif

#define PACK64_COEFFS 64
#define PACK64_BYTES 96
#define ST4_VECTOR_COUNT 8
#define ST4_LANES 8
#define PMU_EVENT_COUNT 2

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

typedef void (*bench_target_fn)(size_t idx);

struct st4_pair
{
  int16_t v[ST4_VECTOR_COUNT][ST4_LANES];
} __attribute__((aligned(64)));

struct counts
{
  uint64_t cycles;
  uint64_t instructions;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
};

struct variant
{
  const char *name;
  bench_target_fn target;
};

static struct st4_pair g_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_poly_inputs[NINPUTS] __attribute__((aligned(64)));
static uint8_t g_candidate[NINPUTS][PACK64_BYTES] __attribute__((aligned(64)));
static uint8_t g_reference[NINPUTS][PACK64_BYTES] __attribute__((aligned(64)));
static uint8_t g_out[PACK64_BYTES] __attribute__((aligned(64)));
static uint8_t g_polybytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t g_sink;
static uint64_t g_rng_state = 1;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1},
};
static int g_leader_fd = -1;

static uint32_t deterministic_u32(void)
{
  g_rng_state = g_rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (uint32_t)(g_rng_state >> 32);
}

static int16_t random_range_i16(int16_t lo, int16_t hi)
{
  const uint32_t span = (uint32_t)(hi - lo + 1);
  return (int16_t)(lo + (int16_t)(deterministic_u32() % span));
}

static size_t vector_index_for_coeff(size_t coeff)
{
  return (coeff / 32) * 4 + (coeff % 4);
}

static size_t lane_index_for_coeff(size_t coeff)
{
  return (coeff % 32) / 4;
}

static void st4_set_coeff(struct st4_pair *p, size_t coeff, int16_t value)
{
  p->v[vector_index_for_coeff(coeff)][lane_index_for_coeff(coeff)] = value;
}

static int16_t st4_get_coeff(const struct st4_pair *p, size_t coeff)
{
  return p->v[vector_index_for_coeff(coeff)][lane_index_for_coeff(coeff)];
}

static void st4_to_poly_prefix(poly *out, const struct st4_pair *p)
{
  memset(out, 0, sizeof(*out));
  for (size_t i = 0; i < PACK64_COEFFS; i++)
    out->coeffs[i] = st4_get_coeff(p, i);
}

static void reference_pack64_poly_tobytes(uint8_t out[PACK64_BYTES],
                                          const struct st4_pair *p)
{
  poly tmp;
  uint8_t bytes[NTRUPLUS_POLYBYTES];

  st4_to_poly_prefix(&tmp, p);
  poly_tobytes(bytes, &tmp);
  memcpy(out, bytes, PACK64_BYTES);
}

static uint16x8_t normalize_to_tobytes_rep(int16x8_t x)
{
  const int16x8_t q = vdupq_n_s16(NTRUPLUS_Q);
  const int16x8_t mask = vshrq_n_s16(x, 15);
  return vreinterpretq_u16_s16(vaddq_s16(x, vandq_s16(mask, q)));
}

static void pack8_contiguous_vectors(uint8_t out[PACK64_BYTES],
                                     int16x8_t c0, int16x8_t c1,
                                     int16x8_t c2, int16x8_t c3,
                                     int16x8_t c4, int16x8_t c5,
                                     int16x8_t c6, int16x8_t c7)
{
  const uint16x8_t n0 = normalize_to_tobytes_rep(c0);
  const uint16x8_t n1 = normalize_to_tobytes_rep(c1);
  const uint16x8_t n2 = normalize_to_tobytes_rep(c2);
  const uint16x8_t n3 = normalize_to_tobytes_rep(c3);
  const uint16x8_t n4 = normalize_to_tobytes_rep(c4);
  const uint16x8_t n5 = normalize_to_tobytes_rep(c5);
  const uint16x8_t n6 = normalize_to_tobytes_rep(c6);
  const uint16x8_t n7 = normalize_to_tobytes_rep(c7);

  const uint16x8_t p12 = veorq_u16(n0, vshlq_n_u16(n1, 12));
  const uint16x8_t p13 = veorq_u16(vshrq_n_u16(n1, 4),
                                   vshlq_n_u16(n2, 8));
  const uint16x8_t p14 = veorq_u16(vshrq_n_u16(n2, 8),
                                   vshlq_n_u16(n3, 4));
  const uint16x8_t p15 = veorq_u16(n4, vshlq_n_u16(n5, 12));
  const uint16x8_t p16 = veorq_u16(vshrq_n_u16(n5, 4),
                                   vshlq_n_u16(n6, 8));
  const uint16x8_t p17 = veorq_u16(vshrq_n_u16(n6, 8),
                                   vshlq_n_u16(n7, 4));

  const uint16x8_t p18 = vtrn1q_u16(p12, p13);
  const uint16x8_t p19 = vtrn1q_u16(p14, p15);
  const uint16x8_t p20 = vtrn1q_u16(p16, p17);
  const uint16x8_t p21 = vtrn2q_u16(p12, p13);
  const uint16x8_t p22 = vtrn2q_u16(p14, p15);
  const uint16x8_t p23 = vtrn2q_u16(p16, p17);

  const uint32x4_t p24 =
      vtrn1q_u32(vreinterpretq_u32_u16(p18), vreinterpretq_u32_u16(p19));
  const uint32x4_t p25 =
      vtrn1q_u32(vreinterpretq_u32_u16(p20), vreinterpretq_u32_u16(p21));
  const uint32x4_t p26 =
      vtrn1q_u32(vreinterpretq_u32_u16(p22), vreinterpretq_u32_u16(p23));
  const uint32x4_t p27 =
      vtrn2q_u32(vreinterpretq_u32_u16(p18), vreinterpretq_u32_u16(p19));
  const uint32x4_t p28 =
      vtrn2q_u32(vreinterpretq_u32_u16(p20), vreinterpretq_u32_u16(p21));
  const uint32x4_t p29 =
      vtrn2q_u32(vreinterpretq_u32_u16(p22), vreinterpretq_u32_u16(p23));

  const uint64x2_t o0 =
      vtrn1q_u64(vreinterpretq_u64_u32(p24), vreinterpretq_u64_u32(p25));
  const uint64x2_t o1 =
      vtrn1q_u64(vreinterpretq_u64_u32(p26), vreinterpretq_u64_u32(p27));
  const uint64x2_t o2 =
      vtrn1q_u64(vreinterpretq_u64_u32(p28), vreinterpretq_u64_u32(p29));
  const uint64x2_t o3 =
      vtrn2q_u64(vreinterpretq_u64_u32(p24), vreinterpretq_u64_u32(p25));
  const uint64x2_t o4 =
      vtrn2q_u64(vreinterpretq_u64_u32(p26), vreinterpretq_u64_u32(p27));
  const uint64x2_t o5 =
      vtrn2q_u64(vreinterpretq_u64_u32(p28), vreinterpretq_u64_u32(p29));

  vst1q_u16((uint16_t *)(void *)(out + 0),
            vreinterpretq_u16_u64(o0));
  vst1q_u16((uint16_t *)(void *)(out + 16),
            vreinterpretq_u16_u64(o1));
  vst1q_u16((uint16_t *)(void *)(out + 32),
            vreinterpretq_u16_u64(o2));
  vst1q_u16((uint16_t *)(void *)(out + 48),
            vreinterpretq_u16_u64(o3));
  vst1q_u16((uint16_t *)(void *)(out + 64),
            vreinterpretq_u16_u64(o4));
  vst1q_u16((uint16_t *)(void *)(out + 80),
            vreinterpretq_u16_u64(o5));
}

static void gt_pack64_from_st4_vectors_neon(uint8_t out[PACK64_BYTES],
                                            const struct st4_pair *p)
{
  const int16x8_t o0a = vld1q_s16(p->v[0]);
  const int16x8_t o1a = vld1q_s16(p->v[1]);
  const int16x8_t o2a = vld1q_s16(p->v[2]);
  const int16x8_t o3a = vld1q_s16(p->v[3]);
  const int16x8_t o0b = vld1q_s16(p->v[4]);
  const int16x8_t o1b = vld1q_s16(p->v[5]);
  const int16x8_t o2b = vld1q_s16(p->v[6]);
  const int16x8_t o3b = vld1q_s16(p->v[7]);

  const int16x8_t a01lo = vzip1q_s16(o0a, o1a);
  const int16x8_t a01hi = vzip2q_s16(o0a, o1a);
  const int16x8_t a23lo = vzip1q_s16(o2a, o3a);
  const int16x8_t a23hi = vzip2q_s16(o2a, o3a);
  const int16x8_t b01lo = vzip1q_s16(o0b, o1b);
  const int16x8_t b01hi = vzip2q_s16(o0b, o1b);
  const int16x8_t b23lo = vzip1q_s16(o2b, o3b);
  const int16x8_t b23hi = vzip2q_s16(o2b, o3b);

  const int16x8_t c0 =
      vreinterpretq_s16_s32(vzip1q_s32(vreinterpretq_s32_s16(a01lo),
                                       vreinterpretq_s32_s16(a23lo)));
  const int16x8_t c1 =
      vreinterpretq_s16_s32(vzip2q_s32(vreinterpretq_s32_s16(a01lo),
                                       vreinterpretq_s32_s16(a23lo)));
  const int16x8_t c2 =
      vreinterpretq_s16_s32(vzip1q_s32(vreinterpretq_s32_s16(a01hi),
                                       vreinterpretq_s32_s16(a23hi)));
  const int16x8_t c3 =
      vreinterpretq_s16_s32(vzip2q_s32(vreinterpretq_s32_s16(a01hi),
                                       vreinterpretq_s32_s16(a23hi)));
  const int16x8_t c4 =
      vreinterpretq_s16_s32(vzip1q_s32(vreinterpretq_s32_s16(b01lo),
                                       vreinterpretq_s32_s16(b23lo)));
  const int16x8_t c5 =
      vreinterpretq_s16_s32(vzip2q_s32(vreinterpretq_s32_s16(b01lo),
                                       vreinterpretq_s32_s16(b23lo)));
  const int16x8_t c6 =
      vreinterpretq_s16_s32(vzip1q_s32(vreinterpretq_s32_s16(b01hi),
                                       vreinterpretq_s32_s16(b23hi)));
  const int16x8_t c7 =
      vreinterpretq_s16_s32(vzip2q_s32(vreinterpretq_s32_s16(b01hi),
                                       vreinterpretq_s32_s16(b23hi)));

  pack8_contiguous_vectors(out, c0, c1, c2, c3, c4, c5, c6, c7);
}

static void fill_case_pattern(struct st4_pair *p, size_t case_id)
{
  memset(p, 0, sizeof(*p));

  for (size_t i = 0; i < PACK64_COEFFS; i++)
  {
    int16_t value;

    switch (case_id)
    {
    case 0:
      value = 0;
      break;
    case 1:
      value = NTRUPLUS_Q - 1;
      break;
    case 2:
      value = -1;
      break;
    case 3:
      value = (i & 1) ? -1728 : 1728;
      break;
    case 4:
      value = (int16_t)((int)(i * 37) % NTRUPLUS_Q);
      break;
    case 5:
      value = (i % 3 == 0) ? -3456 : (int16_t)(NTRUPLUS_Q - 1);
      break;
    default:
      value = random_range_i16(-1728, 1728);
      break;
    }

    st4_set_coeff(p, i, value);
  }
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
  {
    fill_case_pattern(&g_inputs[i], i < 6 ? i : 6);
    st4_to_poly_prefix(&g_poly_inputs[i], &g_inputs[i]);
    reference_pack64_poly_tobytes(g_reference[i], &g_inputs[i]);
    gt_pack64_from_st4_vectors_neon(g_candidate[i], &g_inputs[i]);
  }
}

static int byte_mismatches(const uint8_t *a, const uint8_t *b, size_t n)
{
  int mismatches = 0;

  for (size_t i = 0; i < n; i++)
    mismatches += a[i] != b[i];
  return mismatches;
}

static int run_correctness(void)
{
  int neon_vs_poly_tobytes = 0;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    struct st4_pair p;
    uint8_t ref[PACK64_BYTES];
    uint8_t neon[PACK64_BYTES];

    fill_case_pattern(&p, i < 6 ? i : 6);
    reference_pack64_poly_tobytes(ref, &p);
    gt_pack64_from_st4_vectors_neon(neon, &p);

    neon_vs_poly_tobytes += byte_mismatches(ref, neon, PACK64_BYTES);
  }

  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("pack64_neon_mismatches=%d\n", neon_vs_poly_tobytes);
  printf("pack64_mismatches=%d\n", neon_vs_poly_tobytes);
  printf("pack64_from_st4_vectors_correctness,total_mismatches=%d\n",
         neon_vs_poly_tobytes);
  return neon_vs_poly_tobytes;
}

static NOINLINE void target_pack64_neon_candidate(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  gt_pack64_from_st4_vectors_neon(g_out, &g_inputs[input_idx]);
  g_sink ^= g_out[(idx + 13) % PACK64_BYTES];
}

static NOINLINE void target_poly_tobytes_full_context(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_polybytes, &g_poly_inputs[input_idx]);
  g_sink ^= g_polybytes[(idx + 29) % PACK64_BYTES];
}

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static void setup_perf_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof(attr));
    attr.type = g_events[i].type;
    attr.size = sizeof(attr);
    attr.config = g_events[i].config;
    attr.disabled = i == 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;

    g_events[i].fd = perf_event_open_wrap(&attr, 0, -1, g_leader_fd, 0);
    if (g_events[i].fd < 0)
    {
      fprintf(stderr, "perf_event_open(%s): %s\n", g_events[i].name,
              strerror(errno));
      exit(1);
    }
    if (i == 0)
      g_leader_fd = g_events[i].fd;
  }
}

static void close_perf_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    if (g_events[i].fd >= 0)
      close(g_events[i].fd);
    g_events[i].fd = -1;
  }
  g_leader_fd = -1;
}

static struct counts measure_once(bench_target_fn fn)
{
  uint64_t values[PMU_EVENT_COUNT + 1] = {0};

  ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (size_t i = 0; i < NITERATIONS; i++)
    fn(i);
  ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);

  if (read(g_leader_fd, values, sizeof(values)) != (ssize_t)sizeof(values))
  {
    perror("read perf group");
    exit(1);
  }

  return (struct counts){values[1], values[2]};
}

static int cmp_u64(const void *a, const void *b)
{
  uint64_t av = *(const uint64_t *)a;
  uint64_t bv = *(const uint64_t *)b;

  return (av > bv) - (av < bv);
}

static void run_one_variant(const struct variant *variant)
{
  uint64_t cycles[NTESTS];
  uint64_t instructions[NTESTS];
  uint64_t p25;
  uint64_t p50;
  uint64_t p75;

  for (size_t i = 0; i < NWARMUP; i++)
    variant->target(i);

  for (size_t t = 0; t < NTESTS; t++)
  {
    const struct counts c = measure_once(variant->target);

    cycles[t] = c.cycles / NITERATIONS;
    instructions[t] = c.instructions / NITERATIONS;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), cmp_u64);
  qsort(instructions, NTESTS, sizeof(instructions[0]), cmp_u64);
  p25 = cycles[NTESTS / 4];
  p50 = cycles[NTESTS / 2];
  p75 = cycles[(3 * NTESTS) / 4];

  printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
         ",cycles_max=%" PRIu64 ",cycles_iqr=%" PRIu64
         ",instr_p50=%" PRIu64 "\n",
         variant->name, p50, cycles[0], cycles[NTESTS - 1], p75 - p25,
         instructions[NTESTS / 2]);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"pack64_neon_candidate", target_pack64_neon_candidate},
      {"poly_tobytes_full_context", target_poly_tobytes_full_context},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  bench_print_gt_production_config();
  printf("pack64_context,poly_tobytes_full_context_packs_coeffs=%d\n",
         NTRUPLUS_N);
  printf("pack64_context,pack64_candidate_packs_coeffs=%d\n", PACK64_COEFFS);

  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    run_one_variant(&variants[i]);

  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  prepare_inputs();
  if (run_correctness() != 0)
    return 1;

  run_pmu();
  return 0;
}
