/*
 * Paired PMU harness for GT forward NTT U01v3 G1 full-path variants.
 *
 * A = production poly_ntt
 * B = U01v3 G1 full poly_ntt
 * C = U01v3 G1 plus S2 high-half umov+str
 * D = G1 with Slothy-scheduled Stage345 block1/2/3 reduction tails
 * E = D plus the audited S2 high-half umov+str transformation
 */
#if !defined(__linux__)
#error "bench_u01v3_g1_fullpath_pmu requires Linux perf_event_open"
#endif

#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

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
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 10000
#endif
#ifndef NWARMUP
#define NWARMUP 200
#endif
#ifndef NINPUTS
#define NINPUTS 64
#endif
#ifndef NVALID_ORACLE
#define NVALID_ORACLE 1024
#endif

#ifndef WRAPPER_A
#define WRAPPER_A "ntruplus/asm/gt/poly_ntt.s"
#endif
#ifndef WRAPPER_B
#define WRAPPER_B "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1.S"
#endif
#ifndef WRAPPER_C
#define WRAPPER_C "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_s2.S"
#endif
#ifndef WRAPPER_D
#define WRAPPER_D "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_r123.S"
#endif
#ifndef WRAPPER_E
#define WRAPPER_E "ntruplus/asm/gt/experiment/poly_ntt_u01v3_g1_r123_s2.S"
#endif

#define VARIANT_COUNT 5
#define ORDER_COUNT 5
#define PMU_EVENT_COUNT 2

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

void poly_ntt_u01v3_g1(poly *r, const poly *a);
void poly_ntt_u01v3_g1_s2(poly *r, const poly *a);
void poly_ntt_u01v3_g1_r123(poly *r, const poly *a);
void poly_ntt_u01v3_g1_r123_s2(poly *r, const poly *a);

typedef void (*ntt_fn)(poly *r, const poly *a);

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
  const char *id;
  const char *name;
  const char *symbol;
  const char *wrapper_path;
  ntt_fn fn;
};

struct order
{
  const char *name;
  uint8_t index[VARIANT_COUNT];
};

static poly g_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_oracle[NINPUTS] __attribute__((aligned(64)));
static poly g_out __attribute__((aligned(64)));
static volatile uint64_t g_sink;
static uint32_t g_rng_state = 0x12345678u;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1},
};
static int g_leader_fd = -1;

static const struct variant g_variants[VARIANT_COUNT] = {
    {"A", "production", "poly_ntt", WRAPPER_A, poly_ntt},
    {"B", "u01v3_g1_fullpath",
     "poly_ntt_u01v3_g1", WRAPPER_B,
     poly_ntt_u01v3_g1},
    {"C", "u01v3_g1_s2_fullpath",
     "poly_ntt_u01v3_g1_s2", WRAPPER_C,
     poly_ntt_u01v3_g1_s2},
    {"D", "u01v3_g1_r123_reduction_slothy",
     "poly_ntt_u01v3_g1_r123", WRAPPER_D,
     poly_ntt_u01v3_g1_r123},
    {"E", "u01v3_g1_r123_s2",
     "poly_ntt_u01v3_g1_r123_s2", WRAPPER_E,
     poly_ntt_u01v3_g1_r123_s2},
};

static const struct order g_orders[ORDER_COUNT] = {
    {"ABCDE", {0, 1, 2, 3, 4}},
    {"BCDEA", {1, 2, 3, 4, 0}},
    {"CDEAB", {2, 3, 4, 0, 1}},
    {"DEABC", {3, 4, 0, 1, 2}},
    {"EABCD", {4, 0, 1, 2, 3}},
};

static struct counts g_samples[ORDER_COUNT][VARIANT_COUNT][NTESTS];

static uint32_t next_u32(void)
{
  g_rng_state = g_rng_state * 1664525u + 1013904223u;
  return g_rng_state;
}

static void fill_input(poly *a, size_t slot)
{
  const int bound = 3 * (NTRUPLUS_Q - 1);

  for (size_t i = 0; i < NTRUPLUS_N; i++)
  {
    switch (slot % 5)
    {
    case 0:
      a->coeffs[i] = 0;
      break;
    case 1:
      a->coeffs[i] = (int16_t)((int)i % 9);
      break;
    case 2:
      a->coeffs[i] = (int16_t)(NTRUPLUS_Q - 1 - ((int)i % 23));
      break;
    case 3:
      a->coeffs[i] = (int16_t)(bound - ((int)i % 47));
      break;
    default:
      a->coeffs[i] =
          (int16_t)((int)(next_u32() % (uint32_t)(2 * bound + 1)) - bound);
      break;
    }
  }
}

static uint64_t checksum_poly(const poly *a)
{
  uint64_t acc = 0x9e3779b97f4a7c15ULL;

  for (size_t i = 0; i < NTRUPLUS_N; i++)
  {
    acc ^= (uint16_t)a->coeffs[i];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static int poly_exact_mismatches(const poly *a, const poly *b)
{
  int mismatches = 0;

  for (size_t i = 0; i < NTRUPLUS_N; i++)
    mismatches += a->coeffs[i] != b->coeffs[i];
  return mismatches;
}

static void prepare_inputs(void)
{
  for (size_t slot = 0; slot < NINPUTS; slot++)
  {
    fill_input(&g_inputs[slot], slot);
    poly_ntt(&g_oracle[slot], &g_inputs[slot]);
  }
}

static int run_correctness_after_each_call(void)
{
  int total_mismatches = 0;

  for (size_t call_idx = 0; call_idx < NVALID_ORACLE; call_idx++)
  {
    const size_t slot = call_idx % NINPUTS;

    for (size_t variant_idx = 0; variant_idx < VARIANT_COUNT; variant_idx++)
    {
      int mismatches;

      g_variants[variant_idx].fn(&g_out, &g_inputs[slot]);
      mismatches = poly_exact_mismatches(&g_out, &g_oracle[slot]);
      if (mismatches != 0 && total_mismatches < 16)
      {
        printf("correctness_error,variant=%s,call=%zu,slot=%zu,"
               "mismatches=%d\n",
               g_variants[variant_idx].id, call_idx, slot, mismatches);
      }
      total_mismatches += mismatches;
    }
  }

  printf("correctness,after_each_call=1,valid_calls=%d,total_mismatches=%d\n",
         NVALID_ORACLE * VARIANT_COUNT, total_mismatches);
  return total_mismatches;
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

static NOINLINE struct counts measure_once(const struct variant *variant)
{
  uint64_t values[PMU_EVENT_COUNT + 1] = {0};

  ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (size_t i = 0; i < NITERATIONS; i++)
  {
    const size_t slot = i % NINPUTS;

    variant->fn(&g_out, &g_inputs[slot]);
    g_sink ^= (uint16_t)g_out.coeffs[(i * 13u + (size_t)variant->id[0]) %
                                     NTRUPLUS_N];
  }
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
  const uint64_t av = *(const uint64_t *)a;
  const uint64_t bv = *(const uint64_t *)b;

  return (av > bv) - (av < bv);
}

static int cmp_i64(const void *a, const void *b)
{
  const int64_t av = *(const int64_t *)a;
  const int64_t bv = *(const int64_t *)b;

  return (av > bv) - (av < bv);
}

static void warmup_order(const struct order *order)
{
  for (size_t i = 0; i < NWARMUP; i++)
  {
    const size_t slot = i % NINPUTS;

    for (size_t pos = 0; pos < VARIANT_COUNT; pos++)
    {
      const struct variant *variant = &g_variants[order->index[pos]];

      variant->fn(&g_out, &g_inputs[slot]);
      g_sink ^= (uint16_t)g_out.coeffs[(i + pos) % NTRUPLUS_N];
    }
  }
}

static uintptr_t address_from_ntt_fn(ntt_fn fn)
{
  uintptr_t value = 0;
  const size_t n = sizeof(fn) < sizeof(value) ? sizeof(fn) : sizeof(value);

  memcpy(&value, &fn, n);
  return value;
}

static void print_address_metadata(const char *kind, const char *name,
                                   uintptr_t value)
{
  printf("layout_runtime,%s=%s,address=0x%" PRIxPTR ",addr_mod32=%" PRIuPTR
         ",addr_mod64=%" PRIuPTR "\n",
         kind, name, value, value & 31u, value & 63u);
}

static void print_object_pointer_metadata(const char *kind, const char *name,
                                          const void *ptr)
{
  const uintptr_t value = (uintptr_t)ptr;

  printf("layout_runtime,%s=%s,address=%p,addr_mod32=%" PRIuPTR
         ",addr_mod64=%" PRIuPTR "\n",
         kind, name, ptr, value & 31u, value & 63u);
}

static void print_layout_metadata(void)
{
  printf("metadata,measurement_boundary=poly_ntt_only\n");
  printf("metadata,pmu_compare_overhead_included=0\n");
  printf("metadata,same_input_buffers=1,same_output_buffer=1\n");
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d,"
         "orders=ABCDE/BCDEA/CDEAB/DEABC/EABCD\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  bench_print_gt_production_config();

  for (size_t i = 0; i < VARIANT_COUNT; i++)
  {
    print_address_metadata("variant", g_variants[i].id,
                           address_from_ntt_fn(g_variants[i].fn));
    printf("layout_runtime,variant=%s,name=%s,symbol=%s,wrapper=%s\n",
           g_variants[i].id, g_variants[i].name, g_variants[i].symbol,
           g_variants[i].wrapper_path);
  }

  printf("metadata,A_wrapper=production_include_plus_bl_ntt32_rows\n");
  printf("metadata,B_wrapper=monolithic_g1_stack_local_scratch\n");
  printf("metadata,C_wrapper=monolithic_g1_s2_stack_local_scratch\n");
  printf("metadata,D_wrapper=monolithic_g1_r123_stack_local_scratch\n");
  printf("metadata,E_wrapper=monolithic_g1_r123_s2_stack_local_scratch\n");
  print_object_pointer_metadata("buffer", "inputs", (const void *)g_inputs);
  print_object_pointer_metadata("buffer", "oracle", (const void *)g_oracle);
  print_object_pointer_metadata("buffer", "out", (const void *)&g_out);
}

static void summarize_variant_order(size_t order_idx, size_t variant_idx)
{
  uint64_t cycles[NTESTS];
  uint64_t instructions[NTESTS];

  for (size_t t = 0; t < NTESTS; t++)
  {
    cycles[t] = g_samples[order_idx][variant_idx][t].cycles;
    instructions[t] = g_samples[order_idx][variant_idx][t].instructions;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), cmp_u64);
  qsort(instructions, NTESTS, sizeof(instructions[0]), cmp_u64);
  printf("summary,scope=order,order=%s,variant=%s,cycles_min=%" PRIu64
         ",cycles_median=%" PRIu64 ",cycles_max=%" PRIu64
         ",instructions_min=%" PRIu64 ",instructions_median=%" PRIu64
         ",instructions_max=%" PRIu64 ",cpi_median=%.6f\n",
         g_orders[order_idx].name, g_variants[variant_idx].id, cycles[0],
         cycles[NTESTS / 2], cycles[NTESTS - 1], instructions[0],
         instructions[NTESTS / 2], instructions[NTESTS - 1],
         (double)cycles[NTESTS / 2] / (double)instructions[NTESTS / 2]);
}

static void summarize_variant_overall(size_t variant_idx)
{
  enum
  {
    TOTAL = ORDER_COUNT * NTESTS
  };
  uint64_t cycles[TOTAL];
  uint64_t instructions[TOTAL];
  size_t out_idx = 0;

  for (size_t order_idx = 0; order_idx < ORDER_COUNT; order_idx++)
    for (size_t t = 0; t < NTESTS; t++)
    {
      cycles[out_idx] = g_samples[order_idx][variant_idx][t].cycles;
      instructions[out_idx] =
          g_samples[order_idx][variant_idx][t].instructions;
      out_idx++;
    }

  qsort(cycles, TOTAL, sizeof(cycles[0]), cmp_u64);
  qsort(instructions, TOTAL, sizeof(instructions[0]), cmp_u64);
  printf("summary,scope=overall,variant=%s,name=%s,cycles_min=%" PRIu64
         ",cycles_median=%" PRIu64 ",cycles_max=%" PRIu64
         ",instructions_min=%" PRIu64 ",instructions_median=%" PRIu64
         ",instructions_max=%" PRIu64 ",cpi_median=%.6f,samples=%d\n",
         g_variants[variant_idx].id, g_variants[variant_idx].name, cycles[0],
         cycles[TOTAL / 2], cycles[TOTAL - 1], instructions[0],
         instructions[TOTAL / 2], instructions[TOTAL - 1],
         (double)cycles[TOTAL / 2] / (double)instructions[TOTAL / 2], TOTAL);
}

static void summarize_delta_order(size_t order_idx, size_t lhs_idx,
                                  size_t rhs_idx)
{
  int64_t cycles[NTESTS];
  int64_t instructions[NTESTS];
  uint64_t rhs_cycles[NTESTS];

  for (size_t t = 0; t < NTESTS; t++)
  {
    cycles[t] = (int64_t)g_samples[order_idx][lhs_idx][t].cycles -
                (int64_t)g_samples[order_idx][rhs_idx][t].cycles;
    instructions[t] =
        (int64_t)g_samples[order_idx][lhs_idx][t].instructions -
        (int64_t)g_samples[order_idx][rhs_idx][t].instructions;
    rhs_cycles[t] = g_samples[order_idx][rhs_idx][t].cycles;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), cmp_i64);
  qsort(instructions, NTESTS, sizeof(instructions[0]), cmp_i64);
  qsort(rhs_cycles, NTESTS, sizeof(rhs_cycles[0]), cmp_u64);
  printf("delta,scope=order,order=%s,pair=%s-%s,cycles_min=%" PRId64
         ",cycles_median=%" PRId64 ",cycles_max=%" PRId64
         ",instructions_median=%" PRId64 ",cycles_median_percent=%.4f\n",
         g_orders[order_idx].name, g_variants[lhs_idx].id,
         g_variants[rhs_idx].id, cycles[0], cycles[NTESTS / 2],
         cycles[NTESTS - 1], instructions[NTESTS / 2],
         100.0 * (double)cycles[NTESTS / 2] /
             (double)rhs_cycles[NTESTS / 2]);
}

static void summarize_delta_overall(size_t lhs_idx, size_t rhs_idx)
{
  enum
  {
    TOTAL = ORDER_COUNT * NTESTS
  };
  int64_t cycles[TOTAL];
  int64_t instructions[TOTAL];
  uint64_t rhs_cycles[TOTAL];
  size_t out_idx = 0;

  for (size_t order_idx = 0; order_idx < ORDER_COUNT; order_idx++)
    for (size_t t = 0; t < NTESTS; t++)
    {
      cycles[out_idx] = (int64_t)g_samples[order_idx][lhs_idx][t].cycles -
                        (int64_t)g_samples[order_idx][rhs_idx][t].cycles;
      instructions[out_idx] =
          (int64_t)g_samples[order_idx][lhs_idx][t].instructions -
          (int64_t)g_samples[order_idx][rhs_idx][t].instructions;
      rhs_cycles[out_idx] = g_samples[order_idx][rhs_idx][t].cycles;
      out_idx++;
    }

  qsort(cycles, TOTAL, sizeof(cycles[0]), cmp_i64);
  qsort(instructions, TOTAL, sizeof(instructions[0]), cmp_i64);
  qsort(rhs_cycles, TOTAL, sizeof(rhs_cycles[0]), cmp_u64);
  printf("delta,scope=overall,pair=%s-%s,cycles_min=%" PRId64
         ",cycles_median=%" PRId64 ",cycles_max=%" PRId64
         ",instructions_median=%" PRId64 ",cycles_median_percent=%.4f,"
         "samples=%d\n",
         g_variants[lhs_idx].id, g_variants[rhs_idx].id, cycles[0],
         cycles[TOTAL / 2], cycles[TOTAL - 1], instructions[TOTAL / 2],
         100.0 * (double)cycles[TOTAL / 2] /
             (double)rhs_cycles[TOTAL / 2],
         TOTAL);
}

static void run_pmu(void)
{
  setup_perf_events();

  for (size_t order_idx = 0; order_idx < ORDER_COUNT; order_idx++)
  {
    const struct order *order = &g_orders[order_idx];

    warmup_order(order);
    for (size_t t = 0; t < NTESTS; t++)
    {
      for (size_t pos = 0; pos < VARIANT_COUNT; pos++)
      {
        const size_t variant_idx = order->index[pos];
        struct counts counts = measure_once(&g_variants[variant_idx]);

        g_samples[order_idx][variant_idx][t].cycles =
            counts.cycles / NITERATIONS;
        g_samples[order_idx][variant_idx][t].instructions =
            counts.instructions / NITERATIONS;
      }
    }
  }

  for (size_t order_idx = 0; order_idx < ORDER_COUNT; order_idx++)
    for (size_t variant_idx = 0; variant_idx < VARIANT_COUNT; variant_idx++)
      summarize_variant_order(order_idx, variant_idx);

  for (size_t variant_idx = 0; variant_idx < VARIANT_COUNT; variant_idx++)
    summarize_variant_overall(variant_idx);

  for (size_t order_idx = 0; order_idx < ORDER_COUNT; order_idx++)
  {
    summarize_delta_order(order_idx, 2, 1);
    summarize_delta_order(order_idx, 2, 0);
    summarize_delta_order(order_idx, 1, 0);
    summarize_delta_order(order_idx, 3, 1);
    summarize_delta_order(order_idx, 4, 2);
    summarize_delta_order(order_idx, 4, 3);
    summarize_delta_order(order_idx, 3, 0);
    summarize_delta_order(order_idx, 4, 0);
  }
  summarize_delta_overall(2, 1);
  summarize_delta_overall(2, 0);
  summarize_delta_overall(1, 0);
  summarize_delta_overall(3, 1);
  summarize_delta_overall(4, 2);
  summarize_delta_overall(4, 3);
  summarize_delta_overall(3, 0);
  summarize_delta_overall(4, 0);

  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  prepare_inputs();
  print_layout_metadata();

  if (run_correctness_after_each_call() != 0)
    return 1;

  run_pmu();
  return 0;
}
