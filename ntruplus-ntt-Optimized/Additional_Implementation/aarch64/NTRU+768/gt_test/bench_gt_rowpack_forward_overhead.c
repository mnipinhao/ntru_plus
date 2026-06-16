#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if !defined(__aarch64__)
#error "bench_gt_rowpack_forward_overhead requires AArch64 Neon"
#endif

#include <arm_neon.h>

#if defined(ROWPACK_USE_PERF_CYCLES) || defined(BENCH_USE_PERF_CYCLES)
#if !defined(__linux__)
#error "ROWPACK_USE_PERF_CYCLES requires Linux perf_event_open"
#endif
#include <errno.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#endif

#include "params.h"

#ifndef BENCH_ITERS
#define BENCH_ITERS 1000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 100
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

#define GT_BRANCHES 2
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VEC_LANES 8

typedef void (*bench_fn)(uint64_t calls);

static int16_t g_stage_rows[GT_ROWS][GT_ROW_N][GT_VEC_LANES]
    __attribute__((aligned(16)));
static int16_t g_store_planes[GT_ROWS][GT_ROW_N / 8][GT_VEC_LANES][GT_VEC_LANES]
    __attribute__((aligned(16)));
static int16_t g_rowpack[NTRUPLUS_N] __attribute__((aligned(16)));
static int16_t g_rowpack_ref[NTRUPLUS_N] __attribute__((aligned(16)));
static int16_t g_block[NTRUPLUS_N] __attribute__((aligned(16)));
static int16_t g_transpose_sink[GT_VEC_LANES] __attribute__((aligned(16)));
static volatile uint64_t g_sink;

#if defined(ROWPACK_USE_PERF_CYCLES) || defined(BENCH_USE_PERF_CYCLES)
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
		        "bench_gt_rowpack_forward_overhead: "
		        "perf_event_open(cycles) failed: %s\n",
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
		        "bench_gt_rowpack_forward_overhead: read(cycles) failed: %s\n",
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
		        "bench_gt_rowpack_forward_overhead: "
		        "enabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	target(calls);
	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0) != 0)
	{
		fprintf(stderr,
		        "bench_gt_rowpack_forward_overhead: "
		        "disabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	return read_perf_cycles();
}

static inline uint64_t read_counter_freq(void)
{
	return 0;
}

#define FORWARD_COUNTER_NAME "cycles"
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

#define FORWARD_COUNTER_NAME "cntvct_ticks"
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

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * 384 + row * 128 + lane * 32 + k32;
}

static int block_index(int branch, int physical_j, int lane)
{
	return branch * 384 + 4 * physical_j + lane;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (32 * row + 3 * k32) % 96;
}

static void fill_inputs(void)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int lane = 0; lane < GT_VEC_LANES; lane++)
			{
				const int v = 1000 * row + 10 * k32 + lane;

				g_stage_rows[row][k32][lane] = (int16_t)v;
			}
		}
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			for (int plane = 0; plane < GT_VEC_LANES; plane++)
			{
				for (int k = 0; k < 8; k++)
				{
					g_store_planes[row][block][plane][k] =
					    g_stage_rows[row][8 * block + k][plane];
				}
			}
		}
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		g_block[i] = (int16_t)(i - 384);
		g_rowpack[i] = 0;
		g_rowpack_ref[i] = 0;
	}
	for (int i = 0; i < GT_VEC_LANES; i++)
	{
		g_transpose_sink[i] = 0;
	}
}

static void consume_outputs(void)
{
	uint64_t acc = g_sink;

	for (int i = 0; i < NTRUPLUS_N; i += 31)
	{
		acc = acc * 1315423911u + (uint16_t)g_rowpack[i];
	}
	for (int i = 0; i < GT_VEC_LANES; i++)
	{
		acc = acc * 1315423911u + (uint16_t)g_transpose_sink[i];
	}
	g_sink = acc;
}

static void rowpack_scatter_scalar_ref(int16_t dst[NTRUPLUS_N])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int vec_lane = branch * GT_QUARTIC_LANES + lane;

					dst[rowpack_index(branch, row, lane, k32)] =
					    g_stage_rows[row][k32][vec_lane];
				}
			}
		}
	}
}

static void gt_block_to_rowpack_scalar(int16_t dst[NTRUPLUS_N],
                                       const int16_t src[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					const int physical_j = physical_j_from_row_k32(row, k32);

					dst[rowpack_index(branch, row, lane, k32)] =
					    src[block_index(branch, physical_j, lane)];
				}
			}
		}
	}
}

static void transpose8x8_s16(int16x8_t q0, int16x8_t q1, int16x8_t q2,
                             int16x8_t q3, int16x8_t q4, int16x8_t q5,
                             int16x8_t q6, int16x8_t q7,
                             int16x8_t out[GT_VEC_LANES])
{
	const int16x8x2_t t01 = vtrnq_s16(q0, q1);
	const int16x8x2_t t23 = vtrnq_s16(q2, q3);
	const int16x8x2_t t45 = vtrnq_s16(q4, q5);
	const int16x8x2_t t67 = vtrnq_s16(q6, q7);

	const int32x4x2_t u02_0 =
	    vtrnq_s32(vreinterpretq_s32_s16(t01.val[0]),
	              vreinterpretq_s32_s16(t23.val[0]));
	const int32x4x2_t u02_1 =
	    vtrnq_s32(vreinterpretq_s32_s16(t01.val[1]),
	              vreinterpretq_s32_s16(t23.val[1]));
	const int32x4x2_t u46_0 =
	    vtrnq_s32(vreinterpretq_s32_s16(t45.val[0]),
	              vreinterpretq_s32_s16(t67.val[0]));
	const int32x4x2_t u46_1 =
	    vtrnq_s32(vreinterpretq_s32_s16(t45.val[1]),
	              vreinterpretq_s32_s16(t67.val[1]));

	const int16x8_t a0 = vreinterpretq_s16_s32(u02_0.val[0]);
	const int16x8_t a1 = vreinterpretq_s16_s32(u02_1.val[0]);
	const int16x8_t a2 = vreinterpretq_s16_s32(u02_0.val[1]);
	const int16x8_t a3 = vreinterpretq_s16_s32(u02_1.val[1]);
	const int16x8_t b0 = vreinterpretq_s16_s32(u46_0.val[0]);
	const int16x8_t b1 = vreinterpretq_s16_s32(u46_1.val[0]);
	const int16x8_t b2 = vreinterpretq_s16_s32(u46_0.val[1]);
	const int16x8_t b3 = vreinterpretq_s16_s32(u46_1.val[1]);

	out[0] = vcombine_s16(vget_low_s16(a0), vget_low_s16(b0));
	out[1] = vcombine_s16(vget_low_s16(a1), vget_low_s16(b1));
	out[2] = vcombine_s16(vget_low_s16(a2), vget_low_s16(b2));
	out[3] = vcombine_s16(vget_low_s16(a3), vget_low_s16(b3));
	out[4] = vcombine_s16(vget_high_s16(a0), vget_high_s16(b0));
	out[5] = vcombine_s16(vget_high_s16(a1), vget_high_s16(b1));
	out[6] = vcombine_s16(vget_high_s16(a2), vget_high_s16(b2));
	out[7] = vcombine_s16(vget_high_s16(a3), vget_high_s16(b3));
}

__attribute__((noinline)) static void rowpack_scatter_block_neon(
	int16_t dst[NTRUPLUS_N], int16_t row_base[GT_ROW_N][GT_VEC_LANES],
	int row, int block)
{
	int16x8_t out[GT_VEC_LANES];
	const int k = 8 * block;

	transpose8x8_s16(vld1q_s16(row_base[k + 0]),
	                 vld1q_s16(row_base[k + 1]),
	                 vld1q_s16(row_base[k + 2]),
	                 vld1q_s16(row_base[k + 3]),
	                 vld1q_s16(row_base[k + 4]),
	                 vld1q_s16(row_base[k + 5]),
	                 vld1q_s16(row_base[k + 6]),
	                 vld1q_s16(row_base[k + 7]),
	                 out);

	for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
	{
		vst1q_s16(&dst[rowpack_index(0, row, lane, k)], out[lane]);
		vst1q_s16(&dst[rowpack_index(1, row, lane, k)],
		          out[GT_QUARTIC_LANES + lane]);
	}
}

__attribute__((noinline)) static void rowpack_scatter_all_neon(
	int16_t dst[NTRUPLUS_N],
	int16_t rows[GT_ROWS][GT_ROW_N][GT_VEC_LANES])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			rowpack_scatter_block_neon(dst, rows[row], row, block);
		}
	}
}

#define STORE_Q_LANES(Q, I)                                                    \
	do                                                                     \
	{                                                                      \
		vst1q_lane_s16(&b0_l0[(I)], (Q), 0);                            \
		vst1q_lane_s16(&b0_l1[(I)], (Q), 1);                            \
		vst1q_lane_s16(&b0_l2[(I)], (Q), 2);                            \
		vst1q_lane_s16(&b0_l3[(I)], (Q), 3);                            \
		vst1q_lane_s16(&b1_l0[(I)], (Q), 4);                            \
		vst1q_lane_s16(&b1_l1[(I)], (Q), 5);                            \
		vst1q_lane_s16(&b1_l2[(I)], (Q), 6);                            \
		vst1q_lane_s16(&b1_l3[(I)], (Q), 7);                            \
	} while (0)

__attribute__((noinline)) static void rowpack_lane_store_block_neon(
	int16_t dst[NTRUPLUS_N], int16_t row_base[GT_ROW_N][GT_VEC_LANES],
	int row, int block)
{
	const int k = 8 * block;
	int16_t *b0_l0 = &dst[rowpack_index(0, row, 0, k)];
	int16_t *b0_l1 = &dst[rowpack_index(0, row, 1, k)];
	int16_t *b0_l2 = &dst[rowpack_index(0, row, 2, k)];
	int16_t *b0_l3 = &dst[rowpack_index(0, row, 3, k)];
	int16_t *b1_l0 = &dst[rowpack_index(1, row, 0, k)];
	int16_t *b1_l1 = &dst[rowpack_index(1, row, 1, k)];
	int16_t *b1_l2 = &dst[rowpack_index(1, row, 2, k)];
	int16_t *b1_l3 = &dst[rowpack_index(1, row, 3, k)];

	const int16x8_t q0 = vld1q_s16(row_base[k + 0]);
	const int16x8_t q1 = vld1q_s16(row_base[k + 1]);
	const int16x8_t q2 = vld1q_s16(row_base[k + 2]);
	const int16x8_t q3 = vld1q_s16(row_base[k + 3]);
	const int16x8_t q4 = vld1q_s16(row_base[k + 4]);
	const int16x8_t q5 = vld1q_s16(row_base[k + 5]);
	const int16x8_t q6 = vld1q_s16(row_base[k + 6]);
	const int16x8_t q7 = vld1q_s16(row_base[k + 7]);

	STORE_Q_LANES(q0, 0);
	STORE_Q_LANES(q1, 1);
	STORE_Q_LANES(q2, 2);
	STORE_Q_LANES(q3, 3);
	STORE_Q_LANES(q4, 4);
	STORE_Q_LANES(q5, 5);
	STORE_Q_LANES(q6, 6);
	STORE_Q_LANES(q7, 7);
}

#undef STORE_Q_LANES

__attribute__((noinline)) static void rowpack_lane_store_all_neon(
	int16_t dst[NTRUPLUS_N],
	int16_t rows[GT_ROWS][GT_ROW_N][GT_VEC_LANES])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			rowpack_lane_store_block_neon(dst, rows[row], row, block);
		}
	}
}

__attribute__((noinline)) static void rowpack_store_ready_all_neon(
	int16_t dst[NTRUPLUS_N],
	int16_t planes[GT_ROWS][GT_ROW_N / 8][GT_VEC_LANES][GT_VEC_LANES])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			const int k = 8 * block;

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				vst1q_s16(&dst[rowpack_index(0, row, lane, k)],
				          vld1q_s16(planes[row][block][lane]));
				vst1q_s16(&dst[rowpack_index(1, row, lane, k)],
				          vld1q_s16(planes[row][block]
				                          [GT_QUARTIC_LANES + lane]));
			}
		}
	}
}

__attribute__((noinline)) static void rowpack_zero_store_all_neon(
	int16_t dst[NTRUPLUS_N])
{
	const int16x8_t z0 = vdupq_n_s16(0);
	const int16x8_t z1 = vdupq_n_s16(1);
	const int16x8_t z2 = vdupq_n_s16(2);
	const int16x8_t z3 = vdupq_n_s16(3);
	const int16x8_t z4 = vdupq_n_s16(4);
	const int16x8_t z5 = vdupq_n_s16(5);
	const int16x8_t z6 = vdupq_n_s16(6);
	const int16x8_t z7 = vdupq_n_s16(7);

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			const int k = 8 * block;

			vst1q_s16(&dst[rowpack_index(0, row, 0, k)], z0);
			vst1q_s16(&dst[rowpack_index(0, row, 1, k)], z1);
			vst1q_s16(&dst[rowpack_index(0, row, 2, k)], z2);
			vst1q_s16(&dst[rowpack_index(0, row, 3, k)], z3);
			vst1q_s16(&dst[rowpack_index(1, row, 0, k)], z4);
			vst1q_s16(&dst[rowpack_index(1, row, 1, k)], z5);
			vst1q_s16(&dst[rowpack_index(1, row, 2, k)], z6);
			vst1q_s16(&dst[rowpack_index(1, row, 3, k)], z7);
		}
	}
}

__attribute__((noinline)) static void rowpack_transpose_all_no_store(
	int16_t rows[GT_ROWS][GT_ROW_N][GT_VEC_LANES])
{
	int16x8_t acc = vdupq_n_s16(0);

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int block = 0; block < GT_ROW_N / 8; block++)
		{
			int16x8_t out[GT_VEC_LANES];
			const int k = 8 * block;

			transpose8x8_s16(vld1q_s16(rows[row][k + 0]),
			                 vld1q_s16(rows[row][k + 1]),
			                 vld1q_s16(rows[row][k + 2]),
			                 vld1q_s16(rows[row][k + 3]),
			                 vld1q_s16(rows[row][k + 4]),
			                 vld1q_s16(rows[row][k + 5]),
			                 vld1q_s16(rows[row][k + 6]),
			                 vld1q_s16(rows[row][k + 7]),
			                 out);
			for (int lane = 0; lane < GT_VEC_LANES; lane++)
			{
				acc = veorq_s16(acc, out[lane]);
			}
		}
	}

	vst1q_s16(g_transpose_sink, acc);
}

__attribute__((noinline)) static void target_rowpack_scatter_only(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		rowpack_scatter_all_neon(g_rowpack, g_stage_rows);
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_rowpack_lane_store_candidate(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		rowpack_lane_store_all_neon(g_rowpack, g_stage_rows);
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_rowpack_store_ready(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		rowpack_store_ready_all_neon(g_rowpack, g_store_planes);
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_rowpack_zero_store(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		rowpack_zero_store_all_neon(g_rowpack);
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_rowpack_transpose_no_store(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		rowpack_transpose_all_no_store(g_stage_rows);
		__asm__ volatile("" ::: "memory");
	}
}

__attribute__((noinline)) static void target_gt_to_rowpack_scalar(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		__asm__ volatile("" ::: "memory");
		gt_block_to_rowpack_scalar(g_rowpack, g_block);
		__asm__ volatile("" ::: "memory");
	}
}

static int check_helpers(void)
{
	rowpack_scatter_scalar_ref(g_rowpack_ref);
	rowpack_scatter_all_neon(g_rowpack, g_stage_rows);
	if (memcmp(g_rowpack, g_rowpack_ref, sizeof(g_rowpack)) != 0)
	{
		fprintf(stderr, "rowpack scatter Neon probe mismatch\n");
		return 0;
	}

	memset(g_rowpack, 0, sizeof(g_rowpack));
	rowpack_lane_store_all_neon(g_rowpack, g_stage_rows);
	if (memcmp(g_rowpack, g_rowpack_ref, sizeof(g_rowpack)) != 0)
	{
		fprintf(stderr, "rowpack lane-store candidate mismatch\n");
		return 0;
	}

	memset(g_rowpack, 0, sizeof(g_rowpack));
	rowpack_store_ready_all_neon(g_rowpack, g_store_planes);
	if (memcmp(g_rowpack, g_rowpack_ref, sizeof(g_rowpack)) != 0)
	{
		fprintf(stderr, "rowpack store-ready probe mismatch\n");
		return 0;
	}

	memset(g_rowpack, 0, sizeof(g_rowpack));
	memset(g_rowpack_ref, 0, sizeof(g_rowpack_ref));
	gt_block_to_rowpack_scalar(g_rowpack, g_block);
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					const int physical_j =
					    physical_j_from_row_k32(row, k32);
					const int want =
					    g_block[block_index(branch, physical_j, lane)];
					const int got =
					    g_rowpack[rowpack_index(branch, row, lane, k32)];

					if (got != want)
					{
						fprintf(stderr,
						        "gt->rowpack conversion mismatch at "
						        "branch=%d row=%d lane=%d k32=%d\n",
						        branch, row, lane, k32);
						return 0;
					}
				}
			}
		}
	}

	return 1;
}

static void run_measure(const char *metric, bench_fn target)
{
	static uint64_t samples[BENCH_ITERS];
	uint64_t wall_start;
	uint64_t wall_end;
	int trim_lo;
	int trim_hi;
	long double trimmed_total = 0.0;

	target(BENCH_WARMUP);
	consume_outputs();

	wall_start = read_wall_ns();
	for (int i = 0; i < BENCH_ITERS; i++)
	{
		samples[i] = measure_counter_delta(target, BENCH_BATCH);
	}
	wall_end = read_wall_ns();
	consume_outputs();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);
	trim_lo = BENCH_ITERS / 100;
	trim_hi = BENCH_ITERS - trim_lo;
	if (trim_hi <= trim_lo)
	{
		trim_lo = 0;
		trim_hi = BENCH_ITERS;
	}
	for (int i = trim_lo; i < trim_hi; i++)
	{
		trimmed_total += (long double)samples[i];
	}

	printf("%s_%s/call min=%.3f median=%.3f trimmed_avg=%.3f "
	       "p90=%.3f p99=%.3f max=%.3f\n",
	       metric,
	       FORWARD_COUNTER_NAME,
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       (double)(trimmed_total / (long double)(trim_hi - trim_lo) /
	                (long double)BENCH_BATCH),
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS - 1] / (double)BENCH_BATCH);
	printf("%s_wall_ns/call avg=%.2f\n",
	       metric,
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));
}

int main(void)
{
	fill_inputs();
	if (!check_helpers())
	{
		return 1;
	}
	if (!init_cycle_counter())
	{
		return 1;
	}

	printf("bench=gt_rowpack_forward_v2_overhead_probes "
	       "iters=%d warmup=%d batch=%d counter=%s cntfrq=%llu "
	       "correctness=ok\n",
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       FORWARD_COUNTER_NAME,
	       (unsigned long long)read_counter_freq());

	run_measure("rowpack_forward_scatter_only", target_rowpack_scatter_only);
	run_measure("rowpack_forward_lane_store_candidate",
	            target_rowpack_lane_store_candidate);
	run_measure("rowpack_forward_store_ready", target_rowpack_store_ready);
	run_measure("rowpack_forward_zero_store", target_rowpack_zero_store);
	run_measure("rowpack_forward_transpose_no_store",
	            target_rowpack_transpose_no_store);
	run_measure("gt_to_rowpack_scalar_convert", target_gt_to_rowpack_scalar);

	close_cycle_counter();
	printf("sink=%llu\n", (unsigned long long)g_sink);
	return 0;
}
