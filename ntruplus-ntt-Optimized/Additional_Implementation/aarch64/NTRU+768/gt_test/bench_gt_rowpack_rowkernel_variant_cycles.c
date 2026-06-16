#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(BENCH_USE_PERF_CYCLES)
#if !defined(__linux__)
#error "BENCH_USE_PERF_CYCLES requires Linux perf_event_open"
#endif
#include <errno.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#endif

#if !defined(__aarch64__)
#error "bench_gt_rowpack_rowkernel_variant_cycles requires AArch64"
#endif

#include "params.h"

#define GT_BRANCHES 2
#define GT_ROWS 3
#define GT_QUARTIC_LANES 4
#define GT_ROW_WORDS 32
#define GT_ROW_KERNEL_CALLS (GT_BRANCHES * GT_ROWS * GT_QUARTIC_LANES)

#ifndef BENCH_ROWKERNEL_CALLS
#define BENCH_ROWKERNEL_CALLS GT_ROW_KERNEL_CALLS
#endif

#if BENCH_ROWKERNEL_CALLS < 1 || BENCH_ROWKERNEL_CALLS > GT_ROW_KERNEL_CALLS
#error "BENCH_ROWKERNEL_CALLS must be in 1..24"
#endif

#ifndef BENCH_ITERS
#define BENCH_ITERS 1000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 100
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

#ifndef BENCH_LABEL
#define BENCH_LABEL "rowpack_rowkernel_variant"
#endif

void ntruplus768_invntt32_rowpack_soa_row(int16_t *row_plane,
                                          const int16_t *consts);
extern const int16_t ntruplus768_invntt32_rowpack_soa_row_consts[];

typedef void (*bench_fn)(uint64_t calls);

static int16_t g_rows[GT_ROW_KERNEL_CALLS][GT_ROW_WORDS]
	__attribute__((aligned(16)));
static volatile uint64_t g_sink;

#if defined(BENCH_USE_PERF_CYCLES)
static int g_perf_cycles_fd = -1;

static long perf_event_open(struct perf_event_attr *hw_event,
                            pid_t pid, int cpu, int group_fd,
                            unsigned long flags)
{
	return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

static int init_cycle_counter(void)
{
	struct perf_event_attr pe;

	memset(&pe, 0, sizeof(pe));
	pe.type = PERF_TYPE_HARDWARE;
	pe.size = sizeof(pe);
	pe.config = PERF_COUNT_HW_CPU_CYCLES;
	pe.disabled = 1;
	pe.exclude_kernel = 1;
	pe.exclude_hv = 1;

	g_perf_cycles_fd = (int)perf_event_open(&pe, 0, -1, -1, 0);
	if (g_perf_cycles_fd < 0)
	{
		fprintf(stderr,
		        "rowkernel variant bench: perf_event_open(cycles) failed: %s\n",
		        strerror(errno));
		return 0;
	}
	return 1;
}

static void close_cycle_counter(void)
{
	if (g_perf_cycles_fd >= 0)
	{
		close(g_perf_cycles_fd);
		g_perf_cycles_fd = -1;
	}
}

static uint64_t read_perf_cycles(void)
{
	uint64_t cycles = 0;
	const ssize_t got = read(g_perf_cycles_fd, &cycles, sizeof(cycles));

	if (got != (ssize_t)sizeof(cycles))
	{
		fprintf(stderr,
		        "rowkernel variant bench: read(cycles) failed: %s\n",
		        got < 0 ? strerror(errno) : "short read");
		return 0;
	}
	return cycles;
}

static uint64_t measure_counter_delta(bench_fn target, uint64_t calls)
{
	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
	    ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_ENABLE, 0) != 0)
	{
		fprintf(stderr,
		        "rowkernel variant bench: enabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	target(calls);
	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0) != 0)
	{
		fprintf(stderr,
		        "rowkernel variant bench: disabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	return read_perf_cycles();
}

static inline uint64_t read_counter_freq(void)
{
	return 0;
}

#define BENCH_COUNTER_NAME "cycles"

#else
static inline uint64_t read_counter(void)
{
	uint64_t t;

	__asm__ volatile(
	    "isb\n\t"
	    "mrs %0, cntvct_el0\n\t"
	    "isb"
	    : "=r"(t)
	    :
	    : "memory");
	return t;
}

static inline uint64_t read_counter_freq(void)
{
	uint64_t t;

	__asm__ volatile("mrs %0, cntfrq_el0" : "=r"(t));
	return t;
}

static uint64_t measure_counter_delta(bench_fn target, uint64_t calls)
{
	const uint64_t start = read_counter();
	uint64_t end;

	target(calls);
	end = read_counter();
	return end >= start ? end - start : 0;
}

static int init_cycle_counter(void)
{
	return 1;
}

static void close_cycle_counter(void)
{
}

#define BENCH_COUNTER_NAME "cntvct_ticks"
#endif

static uint64_t read_wall_ns(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

static int cmp_u64(const void *a, const void *b)
{
	const uint64_t aa = *(const uint64_t *)a;
	const uint64_t bb = *(const uint64_t *)b;

	return (aa > bb) - (aa < bb);
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void init_rows(void)
{
	uint32_t seed = 0x243f6a88u;

	for (int row = 0; row < GT_ROW_KERNEL_CALLS; row++)
	{
		for (int i = 0; i < GT_ROW_WORDS; i++)
		{
			g_rows[row][i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
		}
	}
}

static uint64_t checksum_rows(void)
{
	uint64_t acc = 0x6a09e667f3bcc909ULL;

	for (int row = 0; row < GT_ROW_KERNEL_CALLS; row++)
	{
		for (int i = 0; i < GT_ROW_WORDS; i++)
		{
			acc ^= (uint16_t)g_rows[row][i];
			acc *= 0x100000001b3ULL;
			acc ^= acc >> 32;
		}
	}

	return acc;
}

__attribute__((noinline)) static void target_rowkernels(uint64_t calls)
{
	for (uint64_t c = 0; c < calls; c++)
	{
		for (int row = 0; row < BENCH_ROWKERNEL_CALLS; row++)
		{
			ntruplus768_invntt32_rowpack_soa_row(
				g_rows[row],
				ntruplus768_invntt32_rowpack_soa_row_consts);
		}
	}
}

static void run_measure(void)
{
	static uint64_t samples[BENCH_ITERS];
	uint64_t wall_start;
	uint64_t wall_end;
	long double total = 0.0;

	target_rowkernels(BENCH_WARMUP);
	g_sink ^= checksum_rows();

	wall_start = read_wall_ns();
	for (int i = 0; i < BENCH_ITERS; i++)
	{
		samples[i] = measure_counter_delta(target_rowkernels, BENCH_BATCH);
		total += (long double)samples[i];
	}
	wall_end = read_wall_ns();
	g_sink ^= checksum_rows();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);

	printf("bench=%s iters=%d warmup=%d batch=%d counter=%s cntfrq=%llu sink=%llu\n",
	       BENCH_LABEL,
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       BENCH_COUNTER_NAME,
	       (unsigned long long)read_counter_freq(),
	       (unsigned long long)g_sink);
	printf("rowkernel_calls=%d\n", BENCH_ROWKERNEL_CALLS);
	printf("rowkernels%d_%s/call min=%.3f median=%.3f avg=%.3f p90=%.3f p99=%.3f max=%.3f\n",
	       BENCH_ROWKERNEL_CALLS,
	       BENCH_COUNTER_NAME,
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       (double)(total / (long double)BENCH_ITERS /
	                (long double)BENCH_BATCH),
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS - 1] / (double)BENCH_BATCH);
	printf("rowkernel1_%s/call median=%.3f\n",
	       BENCH_COUNTER_NAME,
	       ((double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH) /
	           (double)BENCH_ROWKERNEL_CALLS);
	printf("wall_ns/call avg=%.2f\n",
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));
}

int main(void)
{
	init_rows();
	if (!init_cycle_counter())
	{
		return 1;
	}
	run_measure();
	close_cycle_counter();
	return 0;
}
