#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(ROWPACK_TMVP_BASEMUL) || defined(ROWPACK_TMVP_BASEMUL_ASM)
#include "gt_tmvp_quartic_tmvp_experimental.h"
#endif

#if defined(ROWPACK_FORWARD_NTT_ASM)
#include "poly.h"
#endif

#if defined(ROWPACK_USE_PERF_CYCLES)
#if !defined(__linux__)
#error "ROWPACK_USE_PERF_CYCLES requires Linux perf_event_open"
#endif
#include <errno.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#endif

#if !defined(__aarch64__)
#error "test_gt_rowpack_soa_invntt32_fullpath requires AArch64 Neon"
#endif

#if defined(ROWPACK_NATIVE_BASEMUL) || defined(ROWPACK_NATIVE_POSTMERGE)
#if defined(ROWPACK_NATIVE_BASEMUL) && defined(ROWPACK_CANONICAL_BASEMUL)
#error "ROWPACK_NATIVE_BASEMUL currently supports only fused normalization ABI"
#endif
#include <arm_neon.h>
#endif

#if defined(ROWPACK_TMVP_BASEMUL) && !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C)
#error "ROWPACK_TMVP_BASEMUL requires GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_C"
#endif

#if defined(ROWPACK_TMVP_BASEMUL_ASM) && !defined(GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM)
#error "ROWPACK_TMVP_BASEMUL_ASM requires GT_TMVP_ENABLE_QUARTIC_TMVP_EXPERIMENTAL_ASM"
#endif

#if defined(ROWPACK_TMVP_BASEMUL) && defined(ROWPACK_TMVP_BASEMUL_ASM)
#error "ROWPACK_TMVP_BASEMUL and ROWPACK_TMVP_BASEMUL_ASM are mutually exclusive"
#endif

#if (defined(ROWPACK_TMVP_BASEMUL) || defined(ROWPACK_TMVP_BASEMUL_ASM)) && \
	defined(ROWPACK_NATIVE_BASEMUL)
#error "ROWPACK TMVP basemul and ROWPACK_NATIVE_BASEMUL are mutually exclusive"
#endif

#if (defined(ROWPACK_TMVP_BASEMUL) || defined(ROWPACK_TMVP_BASEMUL_ASM)) && \
	defined(ROWPACK_CANONICAL_BASEMUL)
#error "ROWPACK TMVP basemul uses the production basemul bounded-output ABI"
#endif

#if defined(ROWPACK_INVNTT_AUDIT_SYMBOLS)
#define ROWPACK_AUDIT_NOINLINE __attribute__((noinline, used))
#else
#define ROWPACK_AUDIT_NOINLINE
#endif

#define NTRUPLUS_NTT_REFERENCE_TEST
#include "../ntt.c"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8
#define GT_ROW_CHUNKS (GT_ROW_N / GT_VECTOR_LANES)
#define RANDOM_TESTS 16

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
#define BENCH_LABEL "gt_rowpack_pipeline"
#endif

void ntruplus768_invntt32_rowpack_soa_row(int16_t *row_plane,
                                          const int16_t *consts);
extern const int16_t ntruplus768_invntt32_rowpack_soa_row_consts[];

#if defined(ROWPACK_CANONICAL_BASEMUL)
static void canonicalize_quartic(int16_t r[GT_QUARTIC_LANES]);
#endif
static int centered_modq(int64_t a);

#if defined(ROWPACK_NATIVE_POSTMERGE_ASM)
void ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
	int16_t *r, const int16_t *work, const int16_t *low_mont,
	const int16_t *high_mont);
#if defined(ROWPACK_NATIVE_POSTMERGE_BOUNDED_ASM)
void ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded_asm(
	int16_t *r, const int16_t *work, const int16_t *low_mont,
	const int16_t *high_mont);
#endif
#endif

#if defined(ROWPACK_NATIVE_BASEMUL) || defined(ROWPACK_NATIVE_POSTMERGE)
static const int16_t gt_base_consts[8] __attribute__((aligned(16))) = {
	3457, 19412, -12929, -147,
	-1393, -1571, -14891, 0,
};

static int16_t g_lambda_rowpack[GT_BRANCHES][GT_ROWS][GT_ROW_CHUNKS]
                                [GT_VECTOR_LANES] __attribute__((aligned(16)));
#endif

static int block_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_QUARTIC_LANES * physical_j + lane;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % (GT_ROWS * GT_ROW_N);
}

static int row_from_physical_j(int physical_j)
{
	return (2 * (physical_j % GT_ROWS)) % GT_ROWS;
}

static int k32_from_physical_j(int physical_j)
{
	const int row = row_from_physical_j(physical_j);

	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		if (physical_j_from_row_k32(row, k32) == physical_j)
		{
			return k32;
		}
	}

	return -1;
}

static int rowpack_index(int branch, int row, int lane, int k32)
{
	return branch * GT_BRANCH_N +
	       row * (GT_QUARTIC_LANES * GT_ROW_N) +
	       lane * GT_ROW_N + k32;
}

static int rowvec_index(int row, int k32, int blane)
{
	return row * (GT_ROW_N * GT_VECTOR_LANES) +
	       k32 * GT_VECTOR_LANES + blane;
}

static void block_to_rowpack(int16_t rowpack[NTRUPLUS_N],
                             const int16_t block[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int row = row_from_physical_j(physical_j);
			const int k32 = k32_from_physical_j(physical_j);

			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				rowpack[rowpack_index(branch, row, lane, k32)] =
					block[block_index(branch, physical_j, lane)];
			}
		}
	}
}

static void rowpack_to_block(int16_t block[NTRUPLUS_N],
                             const int16_t rowpack[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					block[block_index(branch, physical_j, lane)] =
						rowpack[rowpack_index(branch, row, lane, k32)];
				}
			}
		}
	}
}

static void rowpack_rows_to_rowvec(int16_t rowvec[NTRUPLUS_N],
                                   const int16_t rowpack[NTRUPLUS_N])
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;

					rowvec[rowvec_index(row, k32, blane)] =
						rowpack[rowpack_index(branch, row, lane, k32)];
				}
			}
		}
	}
}

#if defined(ROWPACK_NATIVE_BASEMUL) || defined(ROWPACK_NATIVE_POSTMERGE)
static void init_lambda_rowpack(void)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int chunk = 0; chunk < GT_ROW_CHUNKS; chunk++)
			{
				for (int vlane = 0; vlane < GT_VECTOR_LANES; vlane++)
				{
					const int k32 = chunk * GT_VECTOR_LANES + vlane;
					const int physical_j =
						physical_j_from_row_k32(row, k32);

					g_lambda_rowpack[branch][row][chunk][vlane] =
						gt_rowbitrev_lambda[branch][physical_j];
				}
			}
		}
	}
}

static inline int16x8_t montgomery_reduce_i32(int32x4_t lo, int32x4_t hi,
                                              int16x8_t con)
{
	int16x8_t t = vuzp1q_s16(vreinterpretq_s16_s32(lo),
	                         vreinterpretq_s16_s32(hi));

	t = vmulq_laneq_s16(t, con, 2);
	lo = vmlal_lane_s16(lo, vget_low_s16(t), vget_low_s16(con), 0);
	hi = vmlal_high_lane_s16(hi, t, vget_low_s16(con), 0);

	return vuzp2q_s16(vreinterpretq_s16_s32(lo),
	                  vreinterpretq_s16_s32(hi));
}

static inline int16x8_t fqmul_vec(int16x8_t x, int16x8_t y, int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(x), vget_low_s16(y));
	int32x4_t hi = vmull_high_s16(x, y);

	return montgomery_reduce_i32(lo, hi, con);
}

static inline int16x8_t reduce_mul2(int16x8_t a, int16x8_t b,
                                    int16x8_t c, int16x8_t d,
                                    int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(a), vget_low_s16(b));
	int32x4_t hi = vmull_high_s16(a, b);

	lo = vmlal_s16(lo, vget_low_s16(c), vget_low_s16(d));
	hi = vmlal_high_s16(hi, c, d);

	return montgomery_reduce_i32(lo, hi, con);
}

static inline int16x8_t reduce_mul3(int16x8_t a, int16x8_t b,
                                    int16x8_t c, int16x8_t d,
                                    int16x8_t e, int16x8_t f,
                                    int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(a), vget_low_s16(b));
	int32x4_t hi = vmull_high_s16(a, b);

	lo = vmlal_s16(lo, vget_low_s16(c), vget_low_s16(d));
	hi = vmlal_high_s16(hi, c, d);
	lo = vmlal_s16(lo, vget_low_s16(e), vget_low_s16(f));
	hi = vmlal_high_s16(hi, e, f);

	return montgomery_reduce_i32(lo, hi, con);
}

static inline int16x8_t reduce_mul4(int16x8_t a, int16x8_t b,
                                    int16x8_t c, int16x8_t d,
                                    int16x8_t e, int16x8_t f,
                                    int16x8_t g, int16x8_t h,
                                    int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(a), vget_low_s16(b));
	int32x4_t hi = vmull_high_s16(a, b);

	lo = vmlal_s16(lo, vget_low_s16(c), vget_low_s16(d));
	hi = vmlal_high_s16(hi, c, d);
	lo = vmlal_s16(lo, vget_low_s16(e), vget_low_s16(f));
	hi = vmlal_high_s16(hi, e, f);
	lo = vmlal_s16(lo, vget_low_s16(g), vget_low_s16(h));
	hi = vmlal_high_s16(hi, g, h);

	return montgomery_reduce_i32(lo, hi, con);
}

static inline int16x8_t reduce_mul_scalar_add(int16x8_t a, int16_t b,
                                              int16x8_t c, int16_t d,
                                              int16x8_t con)
{
	int32x4_t lo = vmull_n_s16(vget_low_s16(a), b);
	int32x4_t hi = vmull_high_n_s16(a, b);

	lo = vmlal_n_s16(lo, vget_low_s16(c), d);
	hi = vmlal_high_n_s16(hi, c, d);

	return montgomery_reduce_i32(lo, hi, con);
}

static inline void basemul8_prefinal(int16x8_t *r0, int16x8_t *r1,
                                     int16x8_t *r2, int16x8_t *r3,
                                     int16x8_t a0, int16x8_t a1,
                                     int16x8_t a2, int16x8_t a3,
                                     int16x8_t b0, int16x8_t b1,
                                     int16x8_t b2, int16x8_t b3,
                                     int16x8_t zeta, int16x8_t con)
{
	int16x8_t t0 = reduce_mul3(a1, b3, a2, b2, a3, b1, con);
	int16x8_t t1 = reduce_mul2(a2, b3, a3, b2, con);
	int16x8_t t2 = fqmul_vec(a3, b3, con);

	*r0 = reduce_mul2(t0, zeta, a0, b0, con);
	*r1 = reduce_mul3(t1, zeta, a0, b1, a1, b0, con);
	*r2 = reduce_mul4(t2, zeta, a0, b2, a1, b1, a2, b0, con);
	*r3 = reduce_mul4(a0, b3, a1, b2, a2, b1, a3, b0, con);
}

static inline void basemul8(int16x8_t *r0, int16x8_t *r1, int16x8_t *r2,
                            int16x8_t *r3, int16x8_t a0, int16x8_t a1,
                            int16x8_t a2, int16x8_t a3, int16x8_t b0,
                            int16x8_t b1, int16x8_t b2, int16x8_t b3,
                            int16x8_t zeta, int16x8_t con)
{
	const int16x8_t rsq = vdupq_n_s16(NTRUPLUS_RSQ);

	basemul8_prefinal(r0, r1, r2, r3,
	                  a0, a1, a2, a3,
	                  b0, b1, b2, b3,
	                  zeta, con);

	*r0 = fqmul_vec(*r0, rsq, con);
	*r1 = fqmul_vec(*r1, rsq, con);
	*r2 = fqmul_vec(*r2, rsq, con);
	*r3 = fqmul_vec(*r3, rsq, con);
}

static inline void basemul_add8(int16x8_t *r0, int16x8_t *r1, int16x8_t *r2,
                                int16x8_t *r3, int16x8_t a0, int16x8_t a1,
                                int16x8_t a2, int16x8_t a3, int16x8_t b0,
                                int16x8_t b1, int16x8_t b2, int16x8_t b3,
                                int16x8_t c0, int16x8_t c1, int16x8_t c2,
                                int16x8_t c3, int16x8_t zeta, int16x8_t con)
{
	int16x8_t t0;
	int16x8_t t1;
	int16x8_t t2;
	int16x8_t t3;

	basemul8_prefinal(&t0, &t1, &t2, &t3,
	                  a0, a1, a2, a3,
	                  b0, b1, b2, b3,
	                  zeta, con);

	*r0 = reduce_mul_scalar_add(c0, NTRUPLUS_R, t0, NTRUPLUS_RSQ, con);
	*r1 = reduce_mul_scalar_add(c1, NTRUPLUS_R, t1, NTRUPLUS_RSQ, con);
	*r2 = reduce_mul_scalar_add(c2, NTRUPLUS_R, t2, NTRUPLUS_RSQ, con);
	*r3 = reduce_mul_scalar_add(c3, NTRUPLUS_R, t3, NTRUPLUS_RSQ, con);
}

static void basemul_rowpack_neon(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N])
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int chunk = 0; chunk < GT_ROW_CHUNKS; chunk++)
			{
				const int k32 = chunk * GT_VECTOR_LANES;
				const int pos = rowpack_index(branch, row, 0, k32);
				const int16x8_t zeta =
					vld1q_s16(&g_lambda_rowpack[branch][row][chunk][0]);
				const int16x8_t a0 = vld1q_s16(&a[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul8(&r0, &r1, &r2, &r3,
				         a0, a1, a2, a3,
				         b0, b1, b2, b3,
				         zeta, con);
				vst1q_s16(&r[pos + 0], r0);
				vst1q_s16(&r[pos + 32], r1);
				vst1q_s16(&r[pos + 64], r2);
				vst1q_s16(&r[pos + 96], r3);
			}
		}
	}
}

static void basemul_add_rowpack_neon(int16_t r[NTRUPLUS_N],
                                     const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N],
                                     const int16_t c[NTRUPLUS_N])
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int chunk = 0; chunk < GT_ROW_CHUNKS; chunk++)
			{
				const int k32 = chunk * GT_VECTOR_LANES;
				const int pos = rowpack_index(branch, row, 0, k32);
				const int16x8_t zeta =
					vld1q_s16(&g_lambda_rowpack[branch][row][chunk][0]);
				const int16x8_t a0 = vld1q_s16(&a[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b[pos + 96]);
				const int16x8_t c0 = vld1q_s16(&c[pos + 0]);
				const int16x8_t c1 = vld1q_s16(&c[pos + 32]);
				const int16x8_t c2 = vld1q_s16(&c[pos + 64]);
				const int16x8_t c3 = vld1q_s16(&c[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul_add8(&r0, &r1, &r2, &r3,
				             a0, a1, a2, a3,
				             b0, b1, b2, b3,
				             c0, c1, c2, c3,
				             zeta, con);
				vst1q_s16(&r[pos + 0], r0);
				vst1q_s16(&r[pos + 32], r1);
				vst1q_s16(&r[pos + 64], r2);
				vst1q_s16(&r[pos + 96], r3);
			}
		}
	}
}
#endif

static void ntt_gt_rowpack_soa_layout(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N])
{
	int16_t work[NTRUPLUS_N];
	int16_t t1;

	for (int i = 0; i < NTRUPLUS_N / 2; i++)
	{
		t1 = fqmul(NTRUPLUS_ZETA_TOP_SPLIT, a[i + NTRUPLUS_N / 2]);

		work[i + NTRUPLUS_N / 2] = a[i] + a[i + NTRUPLUS_N / 2] - t1;
		work[i] = a[i] + t1;
	}

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *twist =
			branch == 0 ? twist_branch0 : twist_branch1;

		for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				work[branch_start + GT_QUARTIC_LANES * i + lane] =
					fqmul(work[branch_start + GT_QUARTIC_LANES * i + lane],
					      twist[i]);
			}
		}

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t in[GT_ROWS * GT_ROW_N];
			int16_t out[GT_ROWS * GT_ROW_N];

			for (int i = 0; i < GT_ROWS * GT_ROW_N; i++)
			{
				in[i] =
					work[branch_start + GT_QUARTIC_LANES * i + lane];
			}

			ntt96_goodthomas(out, in);

			for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
			     physical_j++)
			{
				const int row = row_from_physical_j(physical_j);
				const int k32 = k32_from_physical_j(physical_j);

				r[rowpack_index(branch, row, lane, k32)] = out[physical_j];
			}
		}
	}
}

static void ntt_gt_rowpack_soa_active(int16_t r[NTRUPLUS_N],
                                      const int16_t a[NTRUPLUS_N])
{
#if defined(ROWPACK_FORWARD_NTT_ASM)
	poly in;
	poly out;

	memcpy(in.coeffs, a, sizeof(in.coeffs));
	poly_ntt(&out, &in);
	memcpy(r, out.coeffs, sizeof(out.coeffs));
#else
	ntt_gt_rowpack_soa_layout(r, a);
#endif
}

static void basemul_block_scalar(int16_t r[NTRUPLUS_N],
                                 const int16_t a[NTRUPLUS_N],
                                 const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int pos = block_index(branch, physical_j, 0);

			basemul(&r[pos], &a[pos], &b[pos],
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static void basemul_add_block_scalar(int16_t r[NTRUPLUS_N],
                                     const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N],
                                     const int16_t c[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_ROWS * GT_ROW_N;
		     physical_j++)
		{
			const int pos = block_index(branch, physical_j, 0);

			basemul_add(&r[pos], &a[pos], &b[pos], &c[pos],
			            gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static void basemul_rowpack_scalar(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					aa[lane] = a[rowpack_index(branch, row, lane, k32)];
					bb[lane] = b[rowpack_index(branch, row, lane, k32)];
				}

				basemul(rr, aa, bb, gt_rowbitrev_lambda[branch][physical_j]);

#if defined(ROWPACK_CANONICAL_BASEMUL)
				canonicalize_quartic(rr);
#endif

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					r[rowpack_index(branch, row, lane, k32)] = rr[lane];
				}
			}
		}
	}
}

static void basemul_add_rowpack_scalar(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				int16_t aa[GT_QUARTIC_LANES];
				int16_t bb[GT_QUARTIC_LANES];
				int16_t cc[GT_QUARTIC_LANES];
				int16_t rr[GT_QUARTIC_LANES];
				const int physical_j = physical_j_from_row_k32(row, k32);

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					aa[lane] = a[rowpack_index(branch, row, lane, k32)];
					bb[lane] = b[rowpack_index(branch, row, lane, k32)];
					cc[lane] = c[rowpack_index(branch, row, lane, k32)];
				}

				basemul_add(rr, aa, bb, cc,
				            gt_rowbitrev_lambda[branch][physical_j]);

#if defined(ROWPACK_CANONICAL_BASEMUL)
				canonicalize_quartic(rr);
#endif

				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					r[rowpack_index(branch, row, lane, k32)] = rr[lane];
				}
			}
		}
	}
}

static void basemul_rowpack_active(int16_t r[NTRUPLUS_N],
                                   const int16_t a[NTRUPLUS_N],
                                   const int16_t b[NTRUPLUS_N])
{
#if defined(ROWPACK_TMVP_BASEMUL_ASM)
	const int status = gt_tmvp_quartic_tmvp_experimental_asm_fast(r, a, b);

	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "rowpack TMVP ASM basemul returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		abort();
	}
#elif defined(ROWPACK_TMVP_BASEMUL)
	const int status = gt_tmvp_quartic_tmvp_experimental_c(r, a, b);

	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "rowpack TMVP basemul returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		abort();
	}
#elif defined(ROWPACK_NATIVE_BASEMUL)
	basemul_rowpack_neon(r, a, b);
#else
	basemul_rowpack_scalar(r, a, b);
#endif
}

static void basemul_add_rowpack_active(int16_t r[NTRUPLUS_N],
                                       const int16_t a[NTRUPLUS_N],
                                       const int16_t b[NTRUPLUS_N],
                                       const int16_t c[NTRUPLUS_N])
{
#if defined(ROWPACK_TMVP_BASEMUL_ASM)
	const int status = gt_tmvp_quartic_tmvp_add_experimental_asm_fast(r, a, b, c);

	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "rowpack TMVP ASM basemul_add returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		abort();
	}
#elif defined(ROWPACK_TMVP_BASEMUL)
	const int status = gt_tmvp_quartic_tmvp_add_experimental_c(r, a, b, c);

	if (status != GT_TMVP_QUARTIC_TMVP_EXPERIMENTAL_OK)
	{
		fprintf(stderr, "rowpack TMVP basemul_add returned %s\n",
		        gt_tmvp_quartic_tmvp_experimental_status_name(status));
		abort();
	}
#elif defined(ROWPACK_NATIVE_BASEMUL)
	basemul_add_rowpack_neon(r, a, b, c);
#else
	basemul_add_rowpack_scalar(r, a, b, c);
#endif
}

#if defined(ROWPACK_NATIVE_POSTMERGE)
static int16_t g_postfold_low_mont[GT_ROWS * GT_ROW_N][GT_VECTOR_LANES]
                                  __attribute__((aligned(16)));
static int16_t g_postfold_high_mont[GT_ROWS * GT_ROW_N][GT_VECTOR_LANES]
                                   __attribute__((aligned(16)));
static int g_postfold_consts_ready;

static inline int16x8_t barrett_reduce_vec(int16x8_t a)
{
	const int16x8_t q = vdupq_n_s16(NTRUPLUS_Q);
	const int16x8_t v = vdupq_n_s16(19412);
	int16x8_t t = vqdmulhq_s16(a, v);

	t = vrshrq_n_s16(t, 11);
	return vmlsq_s16(a, t, q);
}

static int normal_from_mont_centered(int16_t a)
{
	return centered_modq(montgomery_reduce(a));
}

static int16_t mont_from_normal_centered(int normal)
{
	return (int16_t)centered_modq(fqmul((int16_t)centered_modq(normal),
	                                    NTRUPLUS_RSQ));
}

static void init_rowpack_postfold_consts(void)
{
	const int z = normal_from_mont_centered(NTRUPLUS_ZMINUSZ5INV);
	const int inv192 = normal_from_mont_centered(NTRUPLUS_NINV);
	const int inv96 = normal_from_mont_centered(NTRUPLUS_2NINV);

	if (g_postfold_consts_ready)
	{
		return;
	}

	for (int n = 0; n < GT_ROWS * GT_ROW_N; n++)
	{
		const int f0 = normal_from_mont_centered(untwist_branch0[n]);
		const int f1 = normal_from_mont_centered(untwist_branch1[n]);
		const int low0 = centered_modq((int64_t)f0 * (1 - z) * inv192);
		const int low1 = centered_modq((int64_t)f1 * (1 + z) * inv192);
		const int high0 = centered_modq((int64_t)f0 * z * inv96);
		const int high1 = centered_modq(-(int64_t)f1 * z * inv96);

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			g_postfold_low_mont[n][lane] =
				mont_from_normal_centered(low0);
			g_postfold_low_mont[n][GT_QUARTIC_LANES + lane] =
				mont_from_normal_centered(low1);
			g_postfold_high_mont[n][lane] =
				mont_from_normal_centered(high0);
			g_postfold_high_mont[n][GT_QUARTIC_LANES + lane] =
				mont_from_normal_centered(high1);
		}
	}

	g_postfold_consts_ready = 1;
}

static inline int16x8_t rowpack_load_branchlane_vec(
	const int16_t work[NTRUPLUS_N], int row, int k32)
{
	int16x8_t v = vdupq_n_s16(0);

	v = vsetq_lane_s16(work[rowpack_index(0, row, 0, k32)], v, 0);
	v = vsetq_lane_s16(work[rowpack_index(0, row, 1, k32)], v, 1);
	v = vsetq_lane_s16(work[rowpack_index(0, row, 2, k32)], v, 2);
	v = vsetq_lane_s16(work[rowpack_index(0, row, 3, k32)], v, 3);
	v = vsetq_lane_s16(work[rowpack_index(1, row, 0, k32)], v, 4);
	v = vsetq_lane_s16(work[rowpack_index(1, row, 1, k32)], v, 5);
	v = vsetq_lane_s16(work[rowpack_index(1, row, 2, k32)], v, 6);
	v = vsetq_lane_s16(work[rowpack_index(1, row, 3, k32)], v, 7);
	return v;
}

static inline int16x8_t trn1q_s16_s64(int16x8_t a, int16x8_t b)
{
	return vreinterpretq_s16_s64(
		vtrn1q_s64(vreinterpretq_s64_s16(a),
		           vreinterpretq_s64_s16(b)));
}

static inline int16x8_t trn2q_s16_s64(int16x8_t a, int16x8_t b)
{
	return vreinterpretq_s16_s64(
		vtrn2q_s64(vreinterpretq_s64_s16(a),
		           vreinterpretq_s64_s16(b)));
}

static inline int16x8_t trn1q_s16_s32(int16x8_t a, int16x8_t b)
{
	return vreinterpretq_s16_s32(
		vtrn1q_s32(vreinterpretq_s32_s16(a),
		           vreinterpretq_s32_s16(b)));
}

static inline int16x8_t trn2q_s16_s32(int16x8_t a, int16x8_t b)
{
	return vreinterpretq_s16_s32(
		vtrn2q_s32(vreinterpretq_s32_s16(a),
		           vreinterpretq_s32_s16(b)));
}

static inline void transpose8x8_s16(int16x8_t out[GT_VECTOR_LANES],
                                    int16x8_t r0, int16x8_t r1,
                                    int16x8_t r2, int16x8_t r3,
                                    int16x8_t r4, int16x8_t r5,
                                    int16x8_t r6, int16x8_t r7)
{
	const int16x8_t t0 = vtrn1q_s16(r0, r1);
	const int16x8_t t1 = vtrn2q_s16(r0, r1);
	const int16x8_t t2 = vtrn1q_s16(r2, r3);
	const int16x8_t t3 = vtrn2q_s16(r2, r3);
	const int16x8_t t4 = vtrn1q_s16(r4, r5);
	const int16x8_t t5 = vtrn2q_s16(r4, r5);
	const int16x8_t t6 = vtrn1q_s16(r6, r7);
	const int16x8_t t7 = vtrn2q_s16(r6, r7);
	const int16x8_t u0 = trn1q_s16_s32(t0, t2);
	const int16x8_t u1 = trn2q_s16_s32(t0, t2);
	const int16x8_t u2 = trn1q_s16_s32(t1, t3);
	const int16x8_t u3 = trn2q_s16_s32(t1, t3);
	const int16x8_t u4 = trn1q_s16_s32(t4, t6);
	const int16x8_t u5 = trn2q_s16_s32(t4, t6);
	const int16x8_t u6 = trn1q_s16_s32(t5, t7);
	const int16x8_t u7 = trn2q_s16_s32(t5, t7);

	out[0] = trn1q_s16_s64(u0, u4);
	out[4] = trn2q_s16_s64(u0, u4);
	out[2] = trn1q_s16_s64(u1, u5);
	out[6] = trn2q_s16_s64(u1, u5);
	out[1] = trn1q_s16_s64(u2, u6);
	out[5] = trn2q_s16_s64(u2, u6);
	out[3] = trn1q_s16_s64(u3, u7);
	out[7] = trn2q_s16_s64(u3, u7);
}

static inline void rowpack_load_branchlane_vec_chunk8(
	int16x8_t out[GT_VECTOR_LANES], const int16_t work[NTRUPLUS_N],
	int row, int kbase)
{
	const int16x8_t b0_l0 =
		vld1q_s16(&work[rowpack_index(0, row, 0, kbase)]);
	const int16x8_t b0_l1 =
		vld1q_s16(&work[rowpack_index(0, row, 1, kbase)]);
	const int16x8_t b0_l2 =
		vld1q_s16(&work[rowpack_index(0, row, 2, kbase)]);
	const int16x8_t b0_l3 =
		vld1q_s16(&work[rowpack_index(0, row, 3, kbase)]);
	const int16x8_t b1_l0 =
		vld1q_s16(&work[rowpack_index(1, row, 0, kbase)]);
	const int16x8_t b1_l1 =
		vld1q_s16(&work[rowpack_index(1, row, 1, kbase)]);
	const int16x8_t b1_l2 =
		vld1q_s16(&work[rowpack_index(1, row, 2, kbase)]);
	const int16x8_t b1_l3 =
		vld1q_s16(&work[rowpack_index(1, row, 3, kbase)]);

	transpose8x8_s16(out, b0_l0, b0_l1, b0_l2, b0_l3,
	                 b1_l0, b1_l1, b1_l2, b1_l3);
}

static inline int16x8_t rowvec_load_branchlane_vec(
	const int16_t work[NTRUPLUS_N], int row, int k32)
{
	return vld1q_s16(&work[rowvec_index(row, k32, 0)]);
}

static inline void rowpack_store_branchfold_vec(
	int16_t r[NTRUPLUS_N], int n, int16x8_t x, int16x8_t con)
{
	const int pos = GT_QUARTIC_LANES * n;
	const int16x8_t low_consts = vld1q_s16(g_postfold_low_mont[n]);
	const int16x8_t high_consts = vld1q_s16(g_postfold_high_mont[n]);
#if !defined(ROWPACK_NATIVE_POSTMERGE_SEPARATE_BRANCHES)
	const int16x8_t x_rot = vextq_s16(x, x, GT_QUARTIC_LANES);
	const int16x8_t low_consts_rot =
		vextq_s16(low_consts, low_consts, GT_QUARTIC_LANES);
	const int16x8_t high_consts_rot =
		vextq_s16(high_consts, high_consts, GT_QUARTIC_LANES);
	const int16x8_t low =
		reduce_mul2(x, low_consts, x_rot, low_consts_rot, con);
	const int16x8_t high =
		reduce_mul2(x, high_consts, x_rot, high_consts_rot, con);
#else
	int16x8_t low = fqmul_vec(x, low_consts, con);
	int16x8_t high = fqmul_vec(x, high_consts, con);

	low = vaddq_s16(low, vextq_s16(low, low, GT_QUARTIC_LANES));
	high = vaddq_s16(high, vextq_s16(high, high, GT_QUARTIC_LANES));
	low = barrett_reduce_vec(low);
	high = barrett_reduce_vec(high);
#endif

	vst1_s16(&r[pos], vget_low_s16(low));
	vst1_s16(&r[GT_BRANCH_N + pos], vget_low_s16(high));
}

static inline int gt96_next_stride33(int n)
{
	n += 33;
	if (n >= GT_ROWS * GT_ROW_N)
	{
		n -= GT_ROWS * GT_ROW_N;
	}
	return n;
}

ROWPACK_AUDIT_NOINLINE static void invntt_rowpack_postmerge_branchfold_neon(
	int16_t r[NTRUPLUS_N], const int16_t work[NTRUPLUS_N])
{
#if defined(ROWPACK_NATIVE_POSTMERGE_ASM)
#if defined(ROWPACK_NATIVE_POSTMERGE_BOUNDED_ASM)
	ntruplus768_invntt32_rowpack_postmerge_branchfold_bounded_asm(
		r, work, &g_postfold_low_mont[0][0],
		&g_postfold_high_mont[0][0]);
#else
	ntruplus768_invntt32_rowpack_postmerge_branchfold_asm(
		r, work, &g_postfold_low_mont[0][0],
		&g_postfold_high_mont[0][0]);
#endif
#else
	const int16x8_t con = vld1q_s16(gt_base_consts);
	const int16x8_t omega3 = vdupq_n_s16(GT96_OMEGA3);
	int n0 = 0;
	int n1 = 64;
	int n2 = 32;

#if !defined(ROWPACK_NATIVE_POSTMERGE_SCALAR_GATHER)
	for (int kbase = 0; kbase < GT_ROW_N; kbase += GT_VECTOR_LANES)
	{
		int16x8_t y0v[GT_VECTOR_LANES];
		int16x8_t y1v[GT_VECTOR_LANES];
		int16x8_t y2v[GT_VECTOR_LANES];

		rowpack_load_branchlane_vec_chunk8(y0v, work, 0, kbase);
		rowpack_load_branchlane_vec_chunk8(y1v, work, 1, kbase);
		rowpack_load_branchlane_vec_chunk8(y2v, work, 2, kbase);

		for (int lane = 0; lane < GT_VECTOR_LANES; lane++)
		{
			const int16x8_t y0 = y0v[lane];
			const int16x8_t y1 = y1v[lane];
			const int16x8_t y2 = y2v[lane];
			const int16x8_t d = vsubq_s16(y2, y1);
			const int16x8_t t = fqmul_vec(d, omega3, con);
			const int16x8_t x0 = vaddq_s16(vaddq_s16(y0, y1), y2);
			const int16x8_t x1 = vaddq_s16(vsubq_s16(y0, y1), t);
			const int16x8_t x2 = vsubq_s16(vsubq_s16(y0, y2), t);

			rowpack_store_branchfold_vec(r, n0, x0, con);
			rowpack_store_branchfold_vec(r, n1, x1, con);
			rowpack_store_branchfold_vec(r, n2, x2, con);
			n0 = gt96_next_stride33(n0);
			n1 = gt96_next_stride33(n1);
			n2 = gt96_next_stride33(n2);
		}
	}
#else
	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		const int16x8_t y0 =
			rowpack_load_branchlane_vec(work, 0, k32);
		const int16x8_t y1 =
			rowpack_load_branchlane_vec(work, 1, k32);
		const int16x8_t y2 =
			rowpack_load_branchlane_vec(work, 2, k32);
		const int16x8_t d = vsubq_s16(y2, y1);
		const int16x8_t t = fqmul_vec(d, omega3, con);
		const int16x8_t x0 = vaddq_s16(vaddq_s16(y0, y1), y2);
		const int16x8_t x1 = vaddq_s16(vsubq_s16(y0, y1), t);
		const int16x8_t x2 = vsubq_s16(vsubq_s16(y0, y2), t);

		rowpack_store_branchfold_vec(r, n0, x0, con);
		rowpack_store_branchfold_vec(r, n1, x1, con);
		rowpack_store_branchfold_vec(r, n2, x2, con);
		n0 = gt96_next_stride33(n0);
		n1 = gt96_next_stride33(n1);
		n2 = gt96_next_stride33(n2);
	}
#endif
#endif
}

ROWPACK_AUDIT_NOINLINE static void invntt_rowvec_postmerge_branchfold_neon(
	int16_t r[NTRUPLUS_N], const int16_t work[NTRUPLUS_N])
{
	const int16x8_t con = vld1q_s16(gt_base_consts);
	const int16x8_t omega3 = vdupq_n_s16(GT96_OMEGA3);
	int n0 = 0;
	int n1 = 64;
	int n2 = 32;

	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		const int16x8_t y0 =
			rowvec_load_branchlane_vec(work, 0, k32);
		const int16x8_t y1 =
			rowvec_load_branchlane_vec(work, 1, k32);
		const int16x8_t y2 =
			rowvec_load_branchlane_vec(work, 2, k32);
		const int16x8_t d = vsubq_s16(y2, y1);
		const int16x8_t t = fqmul_vec(d, omega3, con);
		const int16x8_t x0 = vaddq_s16(vaddq_s16(y0, y1), y2);
		const int16x8_t x1 = vaddq_s16(vsubq_s16(y0, y1), t);
		const int16x8_t x2 = vsubq_s16(vsubq_s16(y0, y2), t);

		rowpack_store_branchfold_vec(r, n0, x0, con);
		rowpack_store_branchfold_vec(r, n1, x1, con);
		rowpack_store_branchfold_vec(r, n2, x2, con);
		n0 = gt96_next_stride33(n0);
		n1 = gt96_next_stride33(n1);
		n2 = gt96_next_stride33(n2);
	}
}

#if defined(ROWPACK_INVNTT_STAGE_SPLIT)
static void invntt_postmerge_chunked_transpose_only(
	int16_t scratch[NTRUPLUS_N], const int16_t work[NTRUPLUS_N])
{
	int off = 0;

	for (int kbase = 0; kbase < GT_ROW_N; kbase += GT_VECTOR_LANES)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			int16x8_t y[GT_VECTOR_LANES];

			rowpack_load_branchlane_vec_chunk8(y, work, row, kbase);
			for (int lane = 0; lane < GT_VECTOR_LANES; lane++)
			{
				vst1q_s16(&scratch[off], y[lane]);
				off += GT_VECTOR_LANES;
			}
		}
	}
}

static void invntt_postmerge_rowvec_load_only(
	int16_t scratch[NTRUPLUS_N], const int16_t work[NTRUPLUS_N])
{
	int off = 0;

	for (int k32 = 0; k32 < GT_ROW_N; k32++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			const int16x8_t y =
				rowvec_load_branchlane_vec(work, row, k32);

			vst1q_s16(&scratch[off], y);
			off += GT_VECTOR_LANES;
		}
	}
}
#endif
#endif

static void invntt_rowpack_apply_rowkernels(int16_t work[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int row = 0; row < GT_ROWS; row++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				ntruplus768_invntt32_rowpack_soa_row(
					&work[rowpack_index(branch, row, lane, 0)],
					ntruplus768_invntt32_rowpack_soa_row_consts);
			}
		}
	}
}

static void invntt_rowpack_branch_combine(
	int16_t r[NTRUPLUS_N], const int16_t branches[NTRUPLUS_N])
{
	for (int i = 0; i < GT_BRANCH_N; i++)
	{
		const int16_t t1 = branches[i] + branches[i + GT_BRANCH_N];
		const int16_t t2 =
			fqmul(NTRUPLUS_ZMINUSZ5INV,
			      branches[i] - branches[i + GT_BRANCH_N]);

		r[i] = fqmul(NTRUPLUS_NINV, t1 - t2);
		r[i + GT_BRANCH_N] = fqmul(NTRUPLUS_2NINV, t2);
	}
}

#if defined(ROWPACK_INVNTT_ISOLATE)
static void invntt_rowpack_postmerge_gather_mat(
	int16_t mat[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N],
	const int16_t work[NTRUPLUS_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			for (int row = 0; row < GT_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					mat[branch][lane][row][k32] =
						work[rowpack_index(branch, row, lane, k32)];
				}
			}
		}
	}
}

static void invntt_rowpack_postmerge_dft3_mat(
	int16_t mat[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				dft3_inverse(&mat[branch][lane][0][k32],
				             &mat[branch][lane][1][k32],
				             &mat[branch][lane][2][k32]);
			}
		}
	}
}

static void invntt_rowpack_postmerge_untwist_scatter(
	int16_t branches[NTRUPLUS_N],
	int16_t mat[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N])
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			for (int n3 = 0; n3 < GT_ROWS; n3++)
			{
				for (int n32 = 0; n32 < GT_ROW_N; n32++)
				{
					const int n = (64 * n3 + 33 * n32) %
					              (GT_ROWS * GT_ROW_N);

					branches[branch_start + GT_QUARTIC_LANES * n + lane] =
						fqmul(mat[branch][lane][n3][n32], untwist[n]);
				}
			}
		}
	}
}

static void invntt_rowpack_postmerge_staged_from_rows(
	int16_t r[NTRUPLUS_N],
	const int16_t work[NTRUPLUS_N],
	int16_t mat[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N],
	int16_t branches[NTRUPLUS_N])
{
	invntt_rowpack_postmerge_gather_mat(mat, work);
	invntt_rowpack_postmerge_dft3_mat(mat);
	invntt_rowpack_postmerge_untwist_scatter(branches, mat);
	invntt_rowpack_branch_combine(r, branches);
}
#endif

static void invntt_rowpack_postmerge_from_rows(
	int16_t r[NTRUPLUS_N], const int16_t work[NTRUPLUS_N])
{
	int16_t branches[NTRUPLUS_N];

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BRANCH_N;
		const int16_t *untwist =
			branch == 0 ? untwist_branch0 : untwist_branch1;

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			int16_t mat[GT_ROWS][GT_ROW_N];

			for (int row = 0; row < GT_ROWS; row++)
			{
				for (int k32 = 0; k32 < GT_ROW_N; k32++)
				{
					mat[row][k32] =
						work[rowpack_index(branch, row, lane, k32)];
				}
			}

			for (int k32 = 0; k32 < GT_ROW_N; k32++)
			{
				dft3_inverse(&mat[0][k32], &mat[1][k32], &mat[2][k32]);
			}

			for (int n3 = 0; n3 < GT_ROWS; n3++)
			{
				for (int n32 = 0; n32 < GT_ROW_N; n32++)
				{
					const int n = (64 * n3 + 33 * n32) %
					              (GT_ROWS * GT_ROW_N);

					branches[branch_start + GT_QUARTIC_LANES * n + lane] =
						fqmul(mat[n3][n32], untwist[n]);
				}
			}
		}
	}

	invntt_rowpack_branch_combine(r, branches);
}

static void invntt_gt_rowpack_soa_rowkernel_inplace(
	int16_t r[NTRUPLUS_N], int16_t work[NTRUPLUS_N])
{
	invntt_rowpack_apply_rowkernels(work);
#if defined(ROWPACK_NATIVE_POSTMERGE)
	invntt_rowpack_postmerge_branchfold_neon(r, work);
#else
	invntt_rowpack_postmerge_from_rows(r, work);
#endif
}

static void invntt_gt_rowpack_soa_rowkernel(
	int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N])
{
	int16_t work[NTRUPLUS_N];

	memcpy(work, a, sizeof(work));
	invntt_gt_rowpack_soa_rowkernel_inplace(r, work);
}

static int modq(int64_t a)
{
	int r = (int)(a % NTRUPLUS_Q);

	if (r < 0)
	{
		r += NTRUPLUS_Q;
	}

	return r;
}

static int equal_modq(int16_t a, int16_t b)
{
	return modq((int)a - (int)b) == 0;
}

static int centered_modq(int64_t a)
{
	int r = modq(a);

	if (r > NTRUPLUS_Q / 2)
	{
		r -= NTRUPLUS_Q;
	}

	return r;
}

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_pattern(int16_t a[NTRUPLUS_N], unsigned pattern,
                         uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		switch (pattern)
		{
		case 0:
			a[i] = 0;
			break;
		case 1:
			a[i] = 1;
			break;
		case 2:
			a[i] = (i & 1) ? -1 : 1;
			break;
		case 3:
			a[i] = (i & 1) ? -(NTRUPLUS_Q / 2) : (NTRUPLUS_Q / 2);
			break;
		default:
			a[i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
			break;
		}
	}
}

static void schoolbook_mul_reference(int16_t r[NTRUPLUS_N],
                                     const int16_t a[NTRUPLUS_N],
                                     const int16_t b[NTRUPLUS_N])
{
	int64_t tmp[2 * NTRUPLUS_N - 1];

	memset(tmp, 0, sizeof(tmp));

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		for (int j = 0; j < NTRUPLUS_N; j++)
		{
			tmp[i + j] += (int64_t)a[i] * b[j];
		}
	}

	for (int i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
	{
		const int64_t c = tmp[i];

		tmp[i - NTRUPLUS_N / 2] += c;
		tmp[i - NTRUPLUS_N] -= c;
	}

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		r[i] = (int16_t)centered_modq(tmp[i]);
	}
}

static int compare_modq(const char *label, const int16_t got[NTRUPLUS_N],
                        const int16_t want[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got[i], want[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d\n",
			        label,
			        i,
			        got[i],
			        want[i]);
			return 0;
		}
	}

	return 1;
}

#if defined(ROWPACK_CHECK_FINAL_BOUNDED)
static int check_final_bounded_range(const char *label,
                                     const int16_t a[NTRUPLUS_N])
{
	int min = 32767;
	int max = -32768;
	int max_abs = 0;
	const int bound = NTRUPLUS_Q - 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		const int v = a[i];
		const int abs_v = v < 0 ? -v : v;

		if (v < min)
		{
			min = v;
		}
		if (v > max)
		{
			max = v;
		}
		if (abs_v > max_abs)
		{
			max_abs = abs_v;
		}
	}

	printf("%s final_range min=%d max=%d max_abs=%d bound=%d\n",
	       label, min, max, max_abs, bound);
	if (max_abs > bound)
	{
		fprintf(stderr,
		        "%s final output exceeded Montgomery output bound: max_abs=%d bound=%d\n",
		        label, max_abs, bound);
		return 0;
	}

	return 1;
}
#endif

#if defined(ROWPACK_CANONICAL_BASEMUL)
static void canonicalize_quartic(int16_t r[GT_QUARTIC_LANES])
{
	for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
	{
		r[lane] = barrett_reduce(r[lane]);
	}
}

static int check_rowpack_canonical_range(const char *label,
                                         const int16_t a[NTRUPLUS_N])
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (a[i] < -NTRUPLUS_Q / 2 || a[i] > NTRUPLUS_Q / 2)
		{
			fprintf(stderr,
			        "%s noncanonical at %d: %d\n",
			        label,
			        i,
			        a[i]);
			return 0;
		}
	}

	return 1;
}
#endif

static int check_forward_rowpack_direct(unsigned pattern, uint32_t seed)
{
	int16_t natural[NTRUPLUS_N];
	int16_t gt_block[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];

	fill_pattern(natural, pattern, seed);
	ntt_gt_rowbitrevlayout(gt_block, natural);
	block_to_rowpack(want, gt_block);
	ntt_gt_rowpack_soa_active(got, natural);

#if defined(ROWPACK_FORWARD_NTT_ASM)
	return compare_modq("ASM direct rowpack forward", got, want);
#else
	return compare_modq("direct rowpack forward", got, want);
#endif
}

static int check_rowpack_basemul_layout(uint32_t seed)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t a_block[NTRUPLUS_N];
	int16_t b_block[NTRUPLUS_N];
	int16_t c_block[NTRUPLUS_N];
	int16_t got_rowpack[NTRUPLUS_N];
	int16_t got_block[NTRUPLUS_N];
	int16_t want_block[NTRUPLUS_N];

	fill_pattern(a, 4, 0x6a09e667u + seed);
	fill_pattern(b, 4, 0xbb67ae85u + seed);
	fill_pattern(c, 4, 0x3c6ef372u + seed);

	ntt_gt_rowbitrevlayout(a_block, a);
	ntt_gt_rowbitrevlayout(b_block, b);
	ntt_gt_rowbitrevlayout(c_block, c);

	block_to_rowpack(a, a_block);
	block_to_rowpack(b, b_block);
	block_to_rowpack(c, c_block);

	basemul_rowpack_active(got_rowpack, a, b);
#if defined(ROWPACK_CANONICAL_BASEMUL)
	if (!check_rowpack_canonical_range("rowpack basemul canonical range",
	                                   got_rowpack))
	{
		return 0;
	}
#endif
	rowpack_to_block(got_block, got_rowpack);
	basemul_block_scalar(want_block, a_block, b_block);

	if (!compare_modq("rowpack basemul layout", got_block, want_block))
	{
		int16_t aa[GT_QUARTIC_LANES];
		int16_t bb[GT_QUARTIC_LANES];
		int16_t rr[GT_QUARTIC_LANES];
		int16_t ww[GT_QUARTIC_LANES];
		const int row = row_from_physical_j(0);
		const int k32 = k32_from_physical_j(0);

		for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
		{
			aa[lane] = a[rowpack_index(0, row, lane, k32)];
			bb[lane] = b[rowpack_index(0, row, lane, k32)];
			rr[lane] = got_rowpack[rowpack_index(0, row, lane, k32)];
		}
		basemul(ww, &a_block[0], &b_block[0], gt_rowbitrev_lambda[0][0]);

		fprintf(stderr,
		        "rowpack basemul block0 detail: a_block=[%d,%d,%d,%d] b_block=[%d,%d,%d,%d] rowpack_a=[%d,%d,%d,%d] rowpack_b=[%d,%d,%d,%d] rowpack_r=[%d,%d,%d,%d] want_block=[%d,%d,%d,%d] direct_want=[%d,%d,%d,%d] lambda=%d\n",
		        a_block[0], a_block[1], a_block[2], a_block[3],
		        b_block[0], b_block[1], b_block[2], b_block[3],
		        aa[0], aa[1], aa[2], aa[3],
		        bb[0], bb[1], bb[2], bb[3],
		        rr[0], rr[1], rr[2], rr[3],
		        want_block[0], want_block[1], want_block[2], want_block[3],
		        ww[0], ww[1], ww[2], ww[3],
		        gt_rowbitrev_lambda[0][0]);
		return 0;
	}

	basemul_add_rowpack_active(got_rowpack, a, b, c);
#if defined(ROWPACK_CANONICAL_BASEMUL)
	if (!check_rowpack_canonical_range("rowpack basemul_add canonical range",
	                                   got_rowpack))
	{
		return 0;
	}
#endif
	rowpack_to_block(got_block, got_rowpack);
	basemul_add_block_scalar(want_block, a_block, b_block, c_block);

	return compare_modq("rowpack basemul_add layout", got_block, want_block);
}

static int check_one(unsigned pattern, uint32_t seed, const char *label)
{
	int16_t natural[NTRUPLUS_N];
	int16_t gt_block[NTRUPLUS_N];
	int16_t rowpack[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];

	fill_pattern(natural, pattern, seed);
	ntt_gt_rowbitrevlayout(gt_block, natural);
	block_to_rowpack(rowpack, gt_block);
	invntt_gt_rowpack_soa_rowkernel(got, rowpack);
	invntt_gt_rowbitrevlayout_exact(want, gt_block);

	return compare_modq(label, got, want) &&
	       compare_modq("rowpack rowkernel roundtrip", got, natural);
}

static int check_product_roundtrip(uint32_t seed)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int16_t ntt_a[NTRUPLUS_N];
	int16_t ntt_b[NTRUPLUS_N];
	int16_t ntt_c[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];

	fill_pattern(a, 4, 0x3c6ef372u + seed);
	fill_pattern(b, 4, 0xa54ff53au + seed);

	schoolbook_mul_reference(want, a, b);
	ntt_gt_rowpack_soa_active(ntt_a, a);
	ntt_gt_rowpack_soa_active(ntt_b, b);
	basemul_rowpack_active(ntt_c, ntt_a, ntt_b);
#if defined(ROWPACK_CANONICAL_BASEMUL)
	if (!check_rowpack_canonical_range("rowpack product canonical range",
	                                   ntt_c))
	{
		return 0;
	}
#endif
	invntt_gt_rowpack_soa_rowkernel(got, ntt_c);

	if (!compare_modq("rowpack direct product roundtrip",
	                  got, want))
	{
		return 0;
	}
#if defined(ROWPACK_CHECK_FINAL_BOUNDED)
	if (!check_final_bounded_range("rowpack direct product roundtrip", got))
	{
		return 0;
	}
#endif
	return 1;
}

static int check_product_add_roundtrip(uint32_t seed)
{
	int16_t a[NTRUPLUS_N];
	int16_t b[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t want[NTRUPLUS_N];
	int16_t ntt_a[NTRUPLUS_N];
	int16_t ntt_b[NTRUPLUS_N];
	int16_t ntt_c[NTRUPLUS_N];
	int16_t ntt_out[NTRUPLUS_N];
	int16_t got[NTRUPLUS_N];

	fill_pattern(a, 4, 0x5be0cd19u + seed);
	fill_pattern(b, 4, 0x137e2179u + seed);
	fill_pattern(c, 4, 0x9966cc41u + seed);

	schoolbook_mul_reference(want, a, b);
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		want[i] = (int16_t)centered_modq((int64_t)want[i] + c[i]);
	}

	ntt_gt_rowpack_soa_active(ntt_a, a);
	ntt_gt_rowpack_soa_active(ntt_b, b);
	ntt_gt_rowpack_soa_active(ntt_c, c);
	basemul_add_rowpack_active(ntt_out, ntt_a, ntt_b, ntt_c);
#if defined(ROWPACK_CANONICAL_BASEMUL)
	if (!check_rowpack_canonical_range("rowpack product-add canonical range",
	                                   ntt_out))
	{
		return 0;
	}
#endif
	invntt_gt_rowpack_soa_rowkernel(got, ntt_out);

	if (!compare_modq("rowpack direct product-add roundtrip",
	                  got, want))
	{
		return 0;
	}
#if defined(ROWPACK_CHECK_FINAL_BOUNDED)
	if (!check_final_bounded_range("rowpack direct product-add roundtrip", got))
	{
		return 0;
	}
#endif
	return 1;
}

#if defined(ROWPACK_PIPELINE_BENCH)
typedef void (*bench_fn)(uint64_t calls);

static int16_t g_a[NTRUPLUS_N];
static int16_t g_b[NTRUPLUS_N];
#if defined(BENCH_OP_ADD)
static int16_t g_c[NTRUPLUS_N];
#endif
static int16_t g_ntt_a[NTRUPLUS_N];
static int16_t g_ntt_b[NTRUPLUS_N];
#if defined(BENCH_OP_ADD)
static int16_t g_ntt_c[NTRUPLUS_N];
#endif
static int16_t g_freq_out[NTRUPLUS_N];
static int16_t g_out[NTRUPLUS_N];
static int16_t g_invntt_work[NTRUPLUS_N];
static int16_t g_invntt_rows[NTRUPLUS_N];
#if defined(ROWPACK_INVNTT_ISOLATE)
static int16_t g_invntt_postmerge_mat
	[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N];
static int16_t g_invntt_postmerge_dft
	[GT_BRANCHES][GT_QUARTIC_LANES][GT_ROWS][GT_ROW_N];
static int16_t g_invntt_branches[NTRUPLUS_N];
static int16_t g_invntt_staged_out[NTRUPLUS_N];
#if defined(ROWPACK_NATIVE_POSTMERGE)
static int16_t g_invntt_rows_rowvec[NTRUPLUS_N];
static int16_t g_invntt_rowvec_out[NTRUPLUS_N];
#if defined(ROWPACK_INVNTT_STAGE_SPLIT)
static int16_t g_invntt_stage_scratch[NTRUPLUS_N];
#endif
#endif
#endif
static volatile uint64_t g_sink;

#if defined(ROWPACK_USE_PERF_CYCLES)
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
		        "rowpack bench: perf_event_open(cycles) failed: %s\n",
		        strerror(errno));
		fprintf(stderr,
		        "rowpack bench: try lowering perf_event_paranoid or run "
		        "with appropriate perf permissions.\n");
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
		        "rowpack bench: read(cycles) failed: %s\n",
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
		        "rowpack bench: enabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	target(calls);
	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0) != 0)
	{
		fprintf(stderr,
		        "rowpack bench: disabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}
	return read_perf_cycles();
}

static inline uint64_t read_counter_freq(void)
{
	return 0;
}

#define ROWPACK_COUNTER_NAME "cycles"

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

#define ROWPACK_COUNTER_NAME "cntvct_ticks"
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

static inline void bench_compiler_memory_barrier(void)
{
	__asm__ volatile("" ::: "memory");
}

static uint64_t checksum_coeffs(const int16_t a[NTRUPLUS_N])
{
	uint64_t acc = 0x6a09e667f3bcc909ULL;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		acc ^= (uint16_t)a[i];
		acc *= 0x100000001b3ULL;
		acc ^= acc >> 32;
	}

	return acc;
}

static void consume_outputs(void)
{
	g_sink = (g_sink << 5) ^ (g_sink >> 7) ^
	         checksum_coeffs(g_out) ^ checksum_coeffs(g_freq_out) ^
	         checksum_coeffs(g_invntt_work) ^
	         checksum_coeffs(g_invntt_rows)
#if defined(ROWPACK_INVNTT_ISOLATE)
	         ^ checksum_coeffs((const int16_t *)g_invntt_postmerge_mat) ^
	         checksum_coeffs((const int16_t *)g_invntt_postmerge_dft) ^
	         checksum_coeffs(g_invntt_branches) ^
	         checksum_coeffs(g_invntt_staged_out)
#if defined(ROWPACK_NATIVE_POSTMERGE)
	         ^ checksum_coeffs(g_invntt_rows_rowvec) ^
	         checksum_coeffs(g_invntt_rowvec_out)
#if defined(ROWPACK_INVNTT_STAGE_SPLIT)
	         ^ checksum_coeffs(g_invntt_stage_scratch)
#endif
#endif
#endif
	         ^ 0x9e3779b97f4a7c15ULL;
}

static void rowpack_forward_inputs(void)
{
	ntt_gt_rowpack_soa_active(g_ntt_a, g_a);
	ntt_gt_rowpack_soa_active(g_ntt_b, g_b);
#if defined(BENCH_OP_ADD)
	ntt_gt_rowpack_soa_active(g_ntt_c, g_c);
#endif
}

static void rowpack_basemul_step(void)
{
#if defined(BENCH_OP_ADD)
	basemul_add_rowpack_active(g_freq_out, g_ntt_a, g_ntt_b, g_ntt_c);
#else
	basemul_rowpack_active(g_freq_out, g_ntt_a, g_ntt_b);
#endif
}

static void rowpack_invntt_step(void)
{
#if defined(ROWPACK_PIPELINE_INVNTT_INPLACE)
	invntt_gt_rowpack_soa_rowkernel_inplace(g_out, g_freq_out);
#else
	invntt_gt_rowpack_soa_rowkernel(g_out, g_freq_out);
#endif
}

static void rowpack_pipeline_once(void)
{
	rowpack_forward_inputs();
	rowpack_basemul_step();
	rowpack_invntt_step();
}

static int check_bench_pipeline(void)
{
	int16_t want[NTRUPLUS_N];

	schoolbook_mul_reference(want, g_a, g_b);
#if defined(BENCH_OP_ADD)
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		want[i] = (int16_t)centered_modq((int64_t)want[i] + g_c[i]);
	}
#endif

	rowpack_pipeline_once();
#if defined(ROWPACK_INVNTT_ISOLATE)
	rowpack_basemul_step();
	memcpy(g_invntt_rows, g_freq_out, sizeof(g_invntt_rows));
	invntt_rowpack_apply_rowkernels(g_invntt_rows);
#if defined(ROWPACK_NATIVE_POSTMERGE_ASM)
	invntt_rowpack_postmerge_branchfold_neon(g_invntt_staged_out,
	                                         g_invntt_rows);
	if (!compare_modq("rowpack native postmerge bench pipeline",
	                  g_invntt_staged_out, want))
	{
		return 0;
	}
#else
	invntt_rowpack_postmerge_staged_from_rows(
		g_invntt_staged_out, g_invntt_rows, g_invntt_postmerge_mat,
		g_invntt_branches);
	if (!compare_modq("rowpack staged invntt bench pipeline",
	                  g_invntt_staged_out, want))
	{
		return 0;
	}
#if defined(ROWPACK_NATIVE_POSTMERGE)
	rowpack_rows_to_rowvec(g_invntt_rows_rowvec, g_invntt_rows);
	invntt_rowvec_postmerge_branchfold_neon(g_invntt_rowvec_out,
	                                        g_invntt_rows_rowvec);
	if (!compare_modq("rowvec native postmerge bench pipeline",
	                  g_invntt_rowvec_out, want))
	{
		return 0;
	}
#endif
#endif
#endif
#if defined(ROWPACK_CANONICAL_BASEMUL)
	if (!check_rowpack_canonical_range("bench rowpack canonical range",
	                                   g_freq_out))
	{
		return 0;
	}
#endif

	if (!compare_modq("rowpack bench pipeline", g_out, want))
	{
		return 0;
	}
#if defined(ROWPACK_CHECK_FINAL_BOUNDED)
	if (!check_final_bounded_range("rowpack bench pipeline", g_out))
	{
		return 0;
	}
#endif
	return 1;
}

static void setup_bench_inputs(void)
{
	fill_pattern(g_a, 4, 0x243f6a88u);
	fill_pattern(g_b, 4, 0x85a308d3u);
#if defined(BENCH_OP_ADD)
	fill_pattern(g_c, 4, 0x13198a2eu);
#endif
	rowpack_forward_inputs();
	rowpack_basemul_step();
	memcpy(g_invntt_rows, g_freq_out, sizeof(g_invntt_rows));
	invntt_rowpack_apply_rowkernels(g_invntt_rows);
#if defined(ROWPACK_INVNTT_ISOLATE) && defined(ROWPACK_NATIVE_POSTMERGE) && \
	!defined(ROWPACK_NATIVE_POSTMERGE_ASM)
	rowpack_rows_to_rowvec(g_invntt_rows_rowvec, g_invntt_rows);
	invntt_rowvec_postmerge_branchfold_neon(g_invntt_rowvec_out,
	                                        g_invntt_rows_rowvec);
#endif
	memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
#if defined(ROWPACK_INVNTT_ISOLATE) && !defined(ROWPACK_NATIVE_POSTMERGE_ASM)
	invntt_rowpack_postmerge_gather_mat(g_invntt_postmerge_mat,
	                                    g_invntt_rows);
	memcpy(g_invntt_postmerge_dft, g_invntt_postmerge_mat,
	       sizeof(g_invntt_postmerge_dft));
	invntt_rowpack_postmerge_dft3_mat(g_invntt_postmerge_dft);
	invntt_rowpack_postmerge_untwist_scatter(g_invntt_branches,
	                                         g_invntt_postmerge_dft);
#endif
	rowpack_invntt_step();
}

__attribute__((noinline)) static void target_ntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		ntt_gt_rowpack_soa_active(g_ntt_a, g_a);
	}
}

__attribute__((noinline)) static void target_basemul(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		rowpack_basemul_step();
	}
}

__attribute__((noinline)) static void target_invntt(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
#if defined(ROWPACK_PIPELINE_INVNTT_INPLACE)
		memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
		invntt_gt_rowpack_soa_rowkernel_inplace(g_out, g_invntt_work);
#else
		rowpack_invntt_step();
#endif
	}
}

#if defined(ROWPACK_INVNTT_ISOLATE)
__attribute__((noinline)) static void target_invntt_copy(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
	}
}

__attribute__((noinline)) static void target_invntt_rowkernels_with_copy(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
		invntt_rowpack_apply_rowkernels(g_invntt_work);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_from_rows(g_out, g_invntt_rows);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_gather(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_gather_mat(g_invntt_postmerge_mat,
		                                    g_invntt_rows);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_dft3(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_dft3_mat(g_invntt_postmerge_mat);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_untwist_scatter(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_untwist_scatter(g_invntt_branches,
		                                         g_invntt_postmerge_dft);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_branch_combine(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_branch_combine(g_out, g_invntt_branches);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_staged(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_staged_from_rows(
			g_out, g_invntt_rows, g_invntt_postmerge_mat,
			g_invntt_branches);
	}
}

__attribute__((noinline)) static void target_invntt_staged(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
		invntt_rowpack_apply_rowkernels(g_invntt_work);
		invntt_rowpack_postmerge_staged_from_rows(
			g_invntt_staged_out, g_invntt_work, g_invntt_postmerge_mat,
			g_invntt_branches);
	}
}

#if defined(ROWPACK_NATIVE_POSTMERGE)
#if defined(ROWPACK_INVNTT_STAGE_SPLIT)
__attribute__((noinline)) static void target_invntt_postmerge_chunked_transpose_only(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		bench_compiler_memory_barrier();
		invntt_postmerge_chunked_transpose_only(g_invntt_stage_scratch,
		                                        g_invntt_rows);
		bench_compiler_memory_barrier();
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_rowvec_load_only(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		bench_compiler_memory_barrier();
		invntt_postmerge_rowvec_load_only(g_invntt_stage_scratch,
		                                  g_invntt_rows_rowvec);
		bench_compiler_memory_barrier();
	}
}
#endif

__attribute__((noinline)) static void target_invntt_rows_to_rowvec(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		bench_compiler_memory_barrier();
		rowpack_rows_to_rowvec(g_invntt_rows_rowvec, g_invntt_rows);
		bench_compiler_memory_barrier();
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_native(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowpack_postmerge_branchfold_neon(g_out, g_invntt_rows);
	}
}

__attribute__((noinline)) static void target_invntt_postmerge_rowvec_native(
	uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		invntt_rowvec_postmerge_branchfold_neon(g_invntt_rowvec_out,
		                                        g_invntt_rows_rowvec);
	}
}

__attribute__((noinline)) static void target_invntt_native(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		memcpy(g_invntt_work, g_freq_out, sizeof(g_invntt_work));
		invntt_rowpack_apply_rowkernels(g_invntt_work);
		invntt_rowpack_postmerge_branchfold_neon(g_invntt_staged_out,
		                                         g_invntt_work);
	}
}
#endif
#endif

__attribute__((noinline)) static void target_pipeline(uint64_t calls)
{
	for (uint64_t i = 0; i < calls; i++)
	{
		rowpack_pipeline_once();
	}
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
	       ROWPACK_COUNTER_NAME,
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

#endif

#if !defined(ROWPACK_PIPELINE_BENCH)
int main(void)
{
#if defined(ROWPACK_NATIVE_BASEMUL)
	init_lambda_rowpack();
#endif
#if defined(ROWPACK_NATIVE_POSTMERGE)
	init_rowpack_postfold_consts();
#endif
	for (unsigned pattern = 0; pattern < 5; pattern++)
	{
		if (!check_forward_rowpack_direct(pattern, 0x243f6a88u + pattern))
		{
			return 1;
		}

		if (!check_one(pattern, 0x12345678u + pattern,
		               "rowpack rowkernel pattern"))
		{
			return 1;
		}
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		if (!check_forward_rowpack_direct(4, 0x85a308d3u + (uint32_t)t))
		{
			return 1;
		}

		if (!check_one(4, 0x9e3779b9u + (uint32_t)t,
		               "rowpack rowkernel random"))
		{
			return 1;
		}

		if (!check_rowpack_basemul_layout((uint32_t)t) ||
		    !check_product_roundtrip((uint32_t)t) ||
		    !check_product_add_roundtrip((uint32_t)t))
		{
			return 1;
		}
	}

	printf("GT rowpack SoA InvNTT32 rowkernel full path: ok\n");
	return 0;
}
#else
int main(void)
{
#if defined(ROWPACK_NATIVE_BASEMUL)
	init_lambda_rowpack();
#endif
#if defined(ROWPACK_NATIVE_POSTMERGE)
	init_rowpack_postfold_consts();
#endif
	setup_bench_inputs();
	if (!check_bench_pipeline())
	{
		return 1;
	}
	if (!init_cycle_counter())
	{
		return 1;
	}

	printf("bench=%s op=%s canonical_basemul=%d native_basemul=%d "
	       "iters=%d warmup=%d batch=%d counter=%s cntfrq=%llu "
	       "correctness=ok\n",
	       BENCH_LABEL,
#if defined(BENCH_OP_ADD)
	       "basemul_add",
#else
	       "basemul",
#endif
#if defined(ROWPACK_CANONICAL_BASEMUL)
	       1,
#else
	       0,
#endif
#if defined(ROWPACK_NATIVE_BASEMUL)
	       1,
#else
	       0,
#endif
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       ROWPACK_COUNTER_NAME,
	       (unsigned long long)read_counter_freq());

	run_measure("rowpack_poly_ntt", target_ntt);
#if defined(BENCH_OP_ADD)
	run_measure("rowpack_poly_basemul_add", target_basemul);
#else
	run_measure("rowpack_poly_basemul", target_basemul);
#endif
#if defined(ROWPACK_INVNTT_ISOLATE)
	run_measure("rowpack_poly_invntt_copy", target_invntt_copy);
	run_measure("rowpack_poly_invntt_rowkernels_with_copy",
	            target_invntt_rowkernels_with_copy);
#if !defined(ROWPACK_NATIVE_POSTMERGE_ASM)
	run_measure("rowpack_poly_invntt_postmerge_gather",
	            target_invntt_postmerge_gather);
	run_measure("rowpack_poly_invntt_postmerge_dft3",
	            target_invntt_postmerge_dft3);
	run_measure("rowpack_poly_invntt_postmerge_untwist_scatter",
	            target_invntt_postmerge_untwist_scatter);
	run_measure("rowpack_poly_invntt_postmerge_branch_combine",
	            target_invntt_postmerge_branch_combine);
	run_measure("rowpack_poly_invntt_postmerge_staged",
	            target_invntt_postmerge_staged);
	run_measure("rowpack_poly_invntt_postmerge", target_invntt_postmerge);
	run_measure("rowpack_poly_invntt_staged", target_invntt_staged);
#endif
#if defined(ROWPACK_NATIVE_POSTMERGE)
#if !defined(ROWPACK_NATIVE_POSTMERGE_ASM)
#if defined(ROWPACK_INVNTT_STAGE_SPLIT)
	run_measure("rowpack_poly_invntt_postmerge_chunked_transpose_only",
	            target_invntt_postmerge_chunked_transpose_only);
	run_measure("rowpack_poly_invntt_postmerge_rowvec_load_only",
	            target_invntt_postmerge_rowvec_load_only);
#endif
	run_measure("rowpack_poly_invntt_rows_to_rowvec",
	            target_invntt_rows_to_rowvec);
	run_measure("rowpack_poly_invntt_postmerge_rowvec_native",
	            target_invntt_postmerge_rowvec_native);
#endif
	run_measure("rowpack_poly_invntt_postmerge_native",
	            target_invntt_postmerge_native);
	run_measure("rowpack_poly_invntt_native", target_invntt_native);
#endif
#endif
	run_measure("rowpack_poly_invntt", target_invntt);
#if defined(BENCH_OP_ADD)
	run_measure("rowpack_ntt_basemul_add_pipeline", target_pipeline);
#else
	run_measure("rowpack_ntt_mul_pipeline", target_pipeline);
#endif

	printf("sink=%llu\n", (unsigned long long)g_sink);
	close_cycle_counter();
	return 0;
}
#endif
