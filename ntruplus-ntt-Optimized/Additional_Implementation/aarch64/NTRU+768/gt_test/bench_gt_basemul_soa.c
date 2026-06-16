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
#error "bench_gt_basemul_soa requires AArch64 Neon"
#endif

#include <arm_neon.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_BRANCHES 2
#define GT_BRANCH_N (NTRUPLUS_N / GT_BRANCHES)
#define GT_BLOCKS_PER_BRANCH 96
#define GT_ROWS 3
#define GT_ROW_N 32
#define GT_QUARTIC_LANES 4
#define GT_VECTOR_LANES 8
#define GT_CHUNKS_PER_BRANCH (GT_BLOCKS_PER_BRANCH / GT_VECTOR_LANES)
#define GT_ROW_CHUNKS (GT_ROW_N / GT_VECTOR_LANES)

#define NTRUPLUS_R (-147)
#define NTRUPLUS_RSQ 867

#ifndef BENCH_ITERS
#define BENCH_ITERS 2000
#endif

#ifndef BENCH_WARMUP
#define BENCH_WARMUP 200
#endif

#ifndef BENCH_BATCH
#define BENCH_BATCH 64
#endif

typedef struct {
	int16_t coeffs[NTRUPLUS_N];
} soa_poly __attribute__((aligned(16)));

static const int16_t gt_base_consts[8] __attribute__((aligned(16))) = {
	3457, 19412, -12929, -147,
	-1393, -1571, -14891, 0,
};

static poly g_a_block;
static poly g_b_block;
static poly g_c_block;
static poly g_out_block;
static poly g_ref_block;
static poly g_soa_as_block;
static soa_poly g_a_soa;
static soa_poly g_b_soa;
static soa_poly g_c_soa;
static soa_poly g_out_soa;
static soa_poly g_a_rowpack;
static soa_poly g_b_rowpack;
static soa_poly g_c_rowpack;
static soa_poly g_out_rowpack;
static poly g_rowpack_as_block;
static soa_poly g_a_rowvec;
static soa_poly g_b_rowvec;
static soa_poly g_c_rowvec;
static soa_poly g_out_rowvec;
static poly g_rowvec_as_block;
static int16_t g_lambda_rowpack[GT_BRANCHES][GT_ROWS][GT_ROW_CHUNKS]
                                [GT_VECTOR_LANES] __attribute__((aligned(16)));
static volatile int16_t g_sink;

static int block_index(int branch, int physical_j, int lane)
{
	return branch * GT_BRANCH_N + GT_QUARTIC_LANES * physical_j + lane;
}

static int soa_index(int branch, int physical_j, int lane)
{
	const int chunk = physical_j / GT_VECTOR_LANES;
	const int vlane = physical_j % GT_VECTOR_LANES;

	return branch * GT_BRANCH_N +
	       chunk * (GT_QUARTIC_LANES * GT_VECTOR_LANES) +
	       lane * GT_VECTOR_LANES + vlane;
}

static int physical_j_from_row_k32(int row, int k32)
{
	return (GT_ROW_N * row + GT_ROWS * k32) % GT_BLOCKS_PER_BRANCH;
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

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static void fill_input(poly *a, uint32_t seed)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		a->coeffs[i] =
			(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
			          NTRUPLUS_Q);
	}
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

static void block_to_soa(soa_poly *soa, const poly *block)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_BLOCKS_PER_BRANCH;
		     physical_j++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				soa->coeffs[soa_index(branch, physical_j, lane)] =
					block->coeffs[block_index(branch, physical_j, lane)];
			}
		}
	}
}

static void soa_to_block(poly *block, const soa_poly *soa)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_BLOCKS_PER_BRANCH;
		     physical_j++)
		{
			for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
			{
				block->coeffs[block_index(branch, physical_j, lane)] =
					soa->coeffs[soa_index(branch, physical_j, lane)];
			}
		}
	}
}

static void block_to_rowpack(soa_poly *rowpack, const poly *block)
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
					rowpack->coeffs[rowpack_index(branch, row, lane, k32)] =
						block->coeffs[block_index(branch, physical_j, lane)];
				}
			}
		}
	}
}

static void rowpack_to_block(poly *block, const soa_poly *rowpack)
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
					block->coeffs[block_index(branch, physical_j, lane)] =
						rowpack->coeffs[rowpack_index(branch, row, lane, k32)];
				}
			}
		}
	}
}

static void block_to_rowvec(soa_poly *rowvec, const poly *block)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;

					rowvec->coeffs[rowvec_index(row, k32, blane)] =
						block->coeffs[block_index(branch, physical_j, lane)];
				}
			}
		}
	}
}

static void rowvec_to_block(poly *block, const soa_poly *rowvec)
{
	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int k32 = 0; k32 < GT_ROW_N; k32++)
		{
			const int physical_j = physical_j_from_row_k32(row, k32);

			for (int branch = 0; branch < GT_BRANCHES; branch++)
			{
				for (int lane = 0; lane < GT_QUARTIC_LANES; lane++)
				{
					const int blane = branch * GT_QUARTIC_LANES + lane;

					block->coeffs[block_index(branch, physical_j, lane)] =
						rowvec->coeffs[rowvec_index(row, k32, blane)];
				}
			}
		}
	}
}

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

static inline int16x8_t barrett_vec(int16x8_t x)
{
	int16x8_t t = vqdmulhq_n_s16(x, 19412);

	t = vrshrq_n_s16(t, 11);
	return vmlsq_n_s16(x, t, NTRUPLUS_Q);
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

static inline void transpose8x8_s16(int16x8_t v[GT_VECTOR_LANES])
{
	int16x8_t a0 = vzip1q_s16(v[0], v[1]);
	int16x8_t a1 = vzip2q_s16(v[0], v[1]);
	int16x8_t a2 = vzip1q_s16(v[2], v[3]);
	int16x8_t a3 = vzip2q_s16(v[2], v[3]);
	int16x8_t a4 = vzip1q_s16(v[4], v[5]);
	int16x8_t a5 = vzip2q_s16(v[4], v[5]);
	int16x8_t a6 = vzip1q_s16(v[6], v[7]);
	int16x8_t a7 = vzip2q_s16(v[6], v[7]);

	int32x4_t b0 = vzip1q_s32(vreinterpretq_s32_s16(a0),
	                          vreinterpretq_s32_s16(a2));
	int32x4_t b1 = vzip2q_s32(vreinterpretq_s32_s16(a0),
	                          vreinterpretq_s32_s16(a2));
	int32x4_t b2 = vzip1q_s32(vreinterpretq_s32_s16(a1),
	                          vreinterpretq_s32_s16(a3));
	int32x4_t b3 = vzip2q_s32(vreinterpretq_s32_s16(a1),
	                          vreinterpretq_s32_s16(a3));
	int32x4_t b4 = vzip1q_s32(vreinterpretq_s32_s16(a4),
	                          vreinterpretq_s32_s16(a6));
	int32x4_t b5 = vzip2q_s32(vreinterpretq_s32_s16(a4),
	                          vreinterpretq_s32_s16(a6));
	int32x4_t b6 = vzip1q_s32(vreinterpretq_s32_s16(a5),
	                          vreinterpretq_s32_s16(a7));
	int32x4_t b7 = vzip2q_s32(vreinterpretq_s32_s16(a5),
	                          vreinterpretq_s32_s16(a7));

	v[0] = vreinterpretq_s16_s64(vzip1q_s64(vreinterpretq_s64_s32(b0),
	                                        vreinterpretq_s64_s32(b4)));
	v[1] = vreinterpretq_s16_s64(vzip2q_s64(vreinterpretq_s64_s32(b0),
	                                        vreinterpretq_s64_s32(b4)));
	v[2] = vreinterpretq_s16_s64(vzip1q_s64(vreinterpretq_s64_s32(b1),
	                                        vreinterpretq_s64_s32(b5)));
	v[3] = vreinterpretq_s16_s64(vzip2q_s64(vreinterpretq_s64_s32(b1),
	                                        vreinterpretq_s64_s32(b5)));
	v[4] = vreinterpretq_s16_s64(vzip1q_s64(vreinterpretq_s64_s32(b2),
	                                        vreinterpretq_s64_s32(b6)));
	v[5] = vreinterpretq_s16_s64(vzip2q_s64(vreinterpretq_s64_s32(b2),
	                                        vreinterpretq_s64_s32(b6)));
	v[6] = vreinterpretq_s16_s64(vzip1q_s64(vreinterpretq_s64_s32(b3),
	                                        vreinterpretq_s64_s32(b7)));
	v[7] = vreinterpretq_s16_s64(vzip2q_s64(vreinterpretq_s64_s32(b3),
	                                        vreinterpretq_s64_s32(b7)));
}

static inline void rowvec_load_chunk(int16x8_t v[GT_VECTOR_LANES],
                                     const soa_poly *a, int row, int k32)
{
	for (int i = 0; i < GT_VECTOR_LANES; i++)
	{
		v[i] = vld1q_s16(&a->coeffs[rowvec_index(row, k32 + i, 0)]);
	}
}

static inline void rowvec_store_chunk(soa_poly *r,
                                      const int16x8_t v[GT_VECTOR_LANES],
                                      int row, int k32)
{
	for (int i = 0; i < GT_VECTOR_LANES; i++)
	{
		vst1q_s16(&r->coeffs[rowvec_index(row, k32 + i, 0)], v[i]);
	}
}

__attribute__((noinline))
static void poly_basemul_ld4_neon(poly *r, const poly *a, const poly *b)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int chunk = 0; chunk < GT_CHUNKS_PER_BRANCH; chunk++)
		{
			const int physical_j = chunk * GT_VECTOR_LANES;
			const int pos = block_index(branch, physical_j, 0);
			const int16x8_t zeta =
				vld1q_s16(&gt_rowbitrev_lambda[branch][physical_j]);
			const int16x8x4_t av = vld4q_s16(&a->coeffs[pos]);
			const int16x8x4_t bv = vld4q_s16(&b->coeffs[pos]);
			int16x8x4_t rv;

			basemul8(&rv.val[0], &rv.val[1], &rv.val[2], &rv.val[3],
			         av.val[0], av.val[1], av.val[2], av.val[3],
			         bv.val[0], bv.val[1], bv.val[2], bv.val[3],
			         zeta, con);
			vst4q_s16(&r->coeffs[pos], rv);
		}
	}
}

__attribute__((noinline))
static void poly_basemul_add_ld4_neon(poly *r, const poly *a, const poly *b,
                                      const poly *c)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int chunk = 0; chunk < GT_CHUNKS_PER_BRANCH; chunk++)
		{
			const int physical_j = chunk * GT_VECTOR_LANES;
			const int pos = block_index(branch, physical_j, 0);
			const int16x8_t zeta =
				vld1q_s16(&gt_rowbitrev_lambda[branch][physical_j]);
			const int16x8x4_t av = vld4q_s16(&a->coeffs[pos]);
			const int16x8x4_t bv = vld4q_s16(&b->coeffs[pos]);
			const int16x8x4_t cv = vld4q_s16(&c->coeffs[pos]);
			int16x8x4_t rv;

			basemul_add8(&rv.val[0], &rv.val[1], &rv.val[2], &rv.val[3],
			             av.val[0], av.val[1], av.val[2], av.val[3],
			             bv.val[0], bv.val[1], bv.val[2], bv.val[3],
			             cv.val[0], cv.val[1], cv.val[2], cv.val[3],
			             zeta, con);
			vst4q_s16(&r->coeffs[pos], rv);
		}
	}
}

__attribute__((noinline))
static void poly_basemul_soa_neon(soa_poly *r, const soa_poly *a,
                                  const soa_poly *b)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int chunk = 0; chunk < GT_CHUNKS_PER_BRANCH; chunk++)
		{
			const int physical_j = chunk * GT_VECTOR_LANES;
			const int pos = branch * GT_BRANCH_N +
			                chunk * (GT_QUARTIC_LANES * GT_VECTOR_LANES);
			const int16x8_t zeta =
				vld1q_s16(&gt_rowbitrev_lambda[branch][physical_j]);
			const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
			const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 8]);
			const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 16]);
			const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 24]);
			const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
			const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 8]);
			const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 16]);
			const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 24]);
			int16x8_t r0;
			int16x8_t r1;
			int16x8_t r2;
			int16x8_t r3;

			basemul8(&r0, &r1, &r2, &r3,
			         a0, a1, a2, a3,
			         b0, b1, b2, b3,
			         zeta, con);
			vst1q_s16(&r->coeffs[pos + 0], r0);
			vst1q_s16(&r->coeffs[pos + 8], r1);
			vst1q_s16(&r->coeffs[pos + 16], r2);
			vst1q_s16(&r->coeffs[pos + 24], r3);
		}
	}
}

__attribute__((noinline))
static void poly_basemul_add_soa_neon(soa_poly *r, const soa_poly *a,
                                      const soa_poly *b, const soa_poly *c)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int chunk = 0; chunk < GT_CHUNKS_PER_BRANCH; chunk++)
		{
			const int physical_j = chunk * GT_VECTOR_LANES;
			const int pos = branch * GT_BRANCH_N +
			                chunk * (GT_QUARTIC_LANES * GT_VECTOR_LANES);
			const int16x8_t zeta =
				vld1q_s16(&gt_rowbitrev_lambda[branch][physical_j]);
			const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
			const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 8]);
			const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 16]);
			const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 24]);
			const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
			const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 8]);
			const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 16]);
			const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 24]);
			const int16x8_t c0 = vld1q_s16(&c->coeffs[pos + 0]);
			const int16x8_t c1 = vld1q_s16(&c->coeffs[pos + 8]);
			const int16x8_t c2 = vld1q_s16(&c->coeffs[pos + 16]);
			const int16x8_t c3 = vld1q_s16(&c->coeffs[pos + 24]);
			int16x8_t r0;
			int16x8_t r1;
			int16x8_t r2;
			int16x8_t r3;

			basemul_add8(&r0, &r1, &r2, &r3,
			             a0, a1, a2, a3,
			             b0, b1, b2, b3,
			             c0, c1, c2, c3,
			             zeta, con);
			vst1q_s16(&r->coeffs[pos + 0], r0);
			vst1q_s16(&r->coeffs[pos + 8], r1);
			vst1q_s16(&r->coeffs[pos + 16], r2);
			vst1q_s16(&r->coeffs[pos + 24], r3);
		}
	}
}

__attribute__((noinline))
static void poly_basemul_rowpack_soa_neon(soa_poly *r, const soa_poly *a,
                                          const soa_poly *b)
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
				const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul8(&r0, &r1, &r2, &r3,
				         a0, a1, a2, a3,
				         b0, b1, b2, b3,
				         zeta, con);
				vst1q_s16(&r->coeffs[pos + 0], r0);
				vst1q_s16(&r->coeffs[pos + 32], r1);
				vst1q_s16(&r->coeffs[pos + 64], r2);
				vst1q_s16(&r->coeffs[pos + 96], r3);
			}
		}
	}
}

__attribute__((noinline))
static void poly_basemul_rowpack_soa_canonical_neon(soa_poly *r,
                                                    const soa_poly *a,
                                                    const soa_poly *b)
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
				const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul8(&r0, &r1, &r2, &r3,
				         a0, a1, a2, a3,
				         b0, b1, b2, b3,
				         zeta, con);
				r0 = barrett_vec(r0);
				r1 = barrett_vec(r1);
				r2 = barrett_vec(r2);
				r3 = barrett_vec(r3);
				vst1q_s16(&r->coeffs[pos + 0], r0);
				vst1q_s16(&r->coeffs[pos + 32], r1);
				vst1q_s16(&r->coeffs[pos + 64], r2);
				vst1q_s16(&r->coeffs[pos + 96], r3);
			}
		}
	}
}

__attribute__((noinline))
static void poly_basemul_add_rowpack_soa_neon(soa_poly *r,
                                              const soa_poly *a,
                                              const soa_poly *b,
                                              const soa_poly *c)
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
				const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 96]);
				const int16x8_t c0 = vld1q_s16(&c->coeffs[pos + 0]);
				const int16x8_t c1 = vld1q_s16(&c->coeffs[pos + 32]);
				const int16x8_t c2 = vld1q_s16(&c->coeffs[pos + 64]);
				const int16x8_t c3 = vld1q_s16(&c->coeffs[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul_add8(&r0, &r1, &r2, &r3,
				             a0, a1, a2, a3,
				             b0, b1, b2, b3,
				             c0, c1, c2, c3,
				             zeta, con);
				vst1q_s16(&r->coeffs[pos + 0], r0);
				vst1q_s16(&r->coeffs[pos + 32], r1);
				vst1q_s16(&r->coeffs[pos + 64], r2);
				vst1q_s16(&r->coeffs[pos + 96], r3);
			}
		}
	}
}

__attribute__((noinline))
static void poly_basemul_add_rowpack_soa_canonical_neon(soa_poly *r,
                                                        const soa_poly *a,
                                                        const soa_poly *b,
                                                        const soa_poly *c)
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
				const int16x8_t a0 = vld1q_s16(&a->coeffs[pos + 0]);
				const int16x8_t a1 = vld1q_s16(&a->coeffs[pos + 32]);
				const int16x8_t a2 = vld1q_s16(&a->coeffs[pos + 64]);
				const int16x8_t a3 = vld1q_s16(&a->coeffs[pos + 96]);
				const int16x8_t b0 = vld1q_s16(&b->coeffs[pos + 0]);
				const int16x8_t b1 = vld1q_s16(&b->coeffs[pos + 32]);
				const int16x8_t b2 = vld1q_s16(&b->coeffs[pos + 64]);
				const int16x8_t b3 = vld1q_s16(&b->coeffs[pos + 96]);
				const int16x8_t c0 = vld1q_s16(&c->coeffs[pos + 0]);
				const int16x8_t c1 = vld1q_s16(&c->coeffs[pos + 32]);
				const int16x8_t c2 = vld1q_s16(&c->coeffs[pos + 64]);
				const int16x8_t c3 = vld1q_s16(&c->coeffs[pos + 96]);
				int16x8_t r0;
				int16x8_t r1;
				int16x8_t r2;
				int16x8_t r3;

				basemul_add8(&r0, &r1, &r2, &r3,
				             a0, a1, a2, a3,
				             b0, b1, b2, b3,
				             c0, c1, c2, c3,
				             zeta, con);
				r0 = barrett_vec(r0);
				r1 = barrett_vec(r1);
				r2 = barrett_vec(r2);
				r3 = barrett_vec(r3);
				vst1q_s16(&r->coeffs[pos + 0], r0);
				vst1q_s16(&r->coeffs[pos + 32], r1);
				vst1q_s16(&r->coeffs[pos + 64], r2);
				vst1q_s16(&r->coeffs[pos + 96], r3);
			}
		}
	}
}

__attribute__((noinline))
static void poly_basemul_rowvec_transpose_neon(soa_poly *r, const soa_poly *a,
                                               const soa_poly *b)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int chunk = 0; chunk < GT_ROW_CHUNKS; chunk++)
		{
			const int k32 = chunk * GT_VECTOR_LANES;
			const int16x8_t zeta0 =
				vld1q_s16(&g_lambda_rowpack[0][row][chunk][0]);
			const int16x8_t zeta1 =
				vld1q_s16(&g_lambda_rowpack[1][row][chunk][0]);
			int16x8_t av[GT_VECTOR_LANES];
			int16x8_t bv[GT_VECTOR_LANES];
			int16x8_t rv[GT_VECTOR_LANES];

			rowvec_load_chunk(av, a, row, k32);
			rowvec_load_chunk(bv, b, row, k32);
			transpose8x8_s16(av);
			transpose8x8_s16(bv);

			basemul8(&rv[0], &rv[1], &rv[2], &rv[3],
			         av[0], av[1], av[2], av[3],
			         bv[0], bv[1], bv[2], bv[3],
			         zeta0, con);
			basemul8(&rv[4], &rv[5], &rv[6], &rv[7],
			         av[4], av[5], av[6], av[7],
			         bv[4], bv[5], bv[6], bv[7],
			         zeta1, con);

			transpose8x8_s16(rv);
			rowvec_store_chunk(r, rv, row, k32);
		}
	}
}

__attribute__((noinline))
static void poly_basemul_add_rowvec_transpose_neon(soa_poly *r,
                                                   const soa_poly *a,
                                                   const soa_poly *b,
                                                   const soa_poly *c)
{
	const int16x8_t con = vld1q_s16(gt_base_consts);

	for (int row = 0; row < GT_ROWS; row++)
	{
		for (int chunk = 0; chunk < GT_ROW_CHUNKS; chunk++)
		{
			const int k32 = chunk * GT_VECTOR_LANES;
			const int16x8_t zeta0 =
				vld1q_s16(&g_lambda_rowpack[0][row][chunk][0]);
			const int16x8_t zeta1 =
				vld1q_s16(&g_lambda_rowpack[1][row][chunk][0]);
			int16x8_t av[GT_VECTOR_LANES];
			int16x8_t bv[GT_VECTOR_LANES];
			int16x8_t cv[GT_VECTOR_LANES];
			int16x8_t rv[GT_VECTOR_LANES];

			rowvec_load_chunk(av, a, row, k32);
			rowvec_load_chunk(bv, b, row, k32);
			rowvec_load_chunk(cv, c, row, k32);
			transpose8x8_s16(av);
			transpose8x8_s16(bv);
			transpose8x8_s16(cv);

			basemul_add8(&rv[0], &rv[1], &rv[2], &rv[3],
			             av[0], av[1], av[2], av[3],
			             bv[0], bv[1], bv[2], bv[3],
			             cv[0], cv[1], cv[2], cv[3],
			             zeta0, con);
			basemul_add8(&rv[4], &rv[5], &rv[6], &rv[7],
			             av[4], av[5], av[6], av[7],
			             bv[4], bv[5], bv[6], bv[7],
			             cv[4], cv[5], cv[6], cv[7],
			             zeta1, con);

			transpose8x8_s16(rv);
			rowvec_store_chunk(r, rv, row, k32);
		}
	}
}

static void scalar_basemul_ref(poly *r, const poly *a, const poly *b)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_BLOCKS_PER_BRANCH;
		     physical_j++)
		{
			const int pos = block_index(branch, physical_j, 0);

			basemul(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
			        gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static void scalar_basemul_add_ref(poly *r, const poly *a, const poly *b,
                                   const poly *c)
{
	for (int branch = 0; branch < GT_BRANCHES; branch++)
	{
		for (int physical_j = 0; physical_j < GT_BLOCKS_PER_BRANCH;
		     physical_j++)
		{
			const int pos = block_index(branch, physical_j, 0);

			basemul_add(r->coeffs + pos,
			            a->coeffs + pos,
			            b->coeffs + pos,
			            c->coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]);
		}
	}
}

static int compare_poly(const char *label, const poly *got, const poly *want)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (!equal_modq(got->coeffs[i], want->coeffs[i]))
		{
			fprintf(stderr,
			        "%s mismatch at %d: got=%d want=%d\n",
			        label,
			        i,
			        got->coeffs[i],
			        want->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static int check_canonical_rowpack_range(const char *label, const soa_poly *a)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		if (a->coeffs[i] < -(NTRUPLUS_Q / 2) ||
		    a->coeffs[i] > NTRUPLUS_Q / 2)
		{
			fprintf(stderr,
			        "%s non-canonical at %d: got=%d\n",
			        label,
			        i,
			        a->coeffs[i]);
			return 0;
		}
	}

	return 1;
}

static int check_correctness(void)
{
	scalar_basemul_ref(&g_ref_block, &g_a_block, &g_b_block);
	poly_basemul_ld4_neon(&g_out_block, &g_a_block, &g_b_block);
	poly_basemul_soa_neon(&g_out_soa, &g_a_soa, &g_b_soa);
	poly_basemul_rowpack_soa_neon(&g_out_rowpack, &g_a_rowpack, &g_b_rowpack);
	poly_basemul_rowvec_transpose_neon(&g_out_rowvec, &g_a_rowvec,
	                                   &g_b_rowvec);
	soa_to_block(&g_soa_as_block, &g_out_soa);
	rowpack_to_block(&g_rowpack_as_block, &g_out_rowpack);
	rowvec_to_block(&g_rowvec_as_block, &g_out_rowvec);

	if (!compare_poly("ld4 basemul", &g_out_block, &g_ref_block) ||
	    !compare_poly("soa basemul", &g_soa_as_block, &g_ref_block) ||
	    !compare_poly("rowpack soa basemul", &g_rowpack_as_block,
	                  &g_ref_block) ||
	    !compare_poly("rowvec transpose basemul", &g_rowvec_as_block,
	                  &g_ref_block))
	{
		return 0;
	}

	poly_basemul_rowpack_soa_canonical_neon(&g_out_rowpack, &g_a_rowpack,
	                                        &g_b_rowpack);
	rowpack_to_block(&g_rowpack_as_block, &g_out_rowpack);

	if (!compare_poly("rowpack soa canonical basemul",
	                  &g_rowpack_as_block,
	                  &g_ref_block) ||
	    !check_canonical_rowpack_range("rowpack soa canonical basemul",
	                                   &g_out_rowpack))
	{
		return 0;
	}

	scalar_basemul_add_ref(&g_ref_block, &g_a_block, &g_b_block, &g_c_block);
	poly_basemul_add_ld4_neon(&g_out_block, &g_a_block, &g_b_block, &g_c_block);
	poly_basemul_add_soa_neon(&g_out_soa, &g_a_soa, &g_b_soa, &g_c_soa);
	poly_basemul_add_rowpack_soa_neon(&g_out_rowpack, &g_a_rowpack,
	                                  &g_b_rowpack, &g_c_rowpack);
	poly_basemul_add_rowvec_transpose_neon(&g_out_rowvec, &g_a_rowvec,
	                                       &g_b_rowvec, &g_c_rowvec);
	soa_to_block(&g_soa_as_block, &g_out_soa);
	rowpack_to_block(&g_rowpack_as_block, &g_out_rowpack);
	rowvec_to_block(&g_rowvec_as_block, &g_out_rowvec);

	if (!compare_poly("ld4 basemul_add", &g_out_block, &g_ref_block) ||
	    !compare_poly("soa basemul_add", &g_soa_as_block, &g_ref_block) ||
	    !compare_poly("rowpack soa basemul_add", &g_rowpack_as_block,
	                  &g_ref_block) ||
	    !compare_poly("rowvec transpose basemul_add", &g_rowvec_as_block,
	                  &g_ref_block))
	{
		return 0;
	}

	poly_basemul_add_rowpack_soa_canonical_neon(&g_out_rowpack,
	                                            &g_a_rowpack,
	                                            &g_b_rowpack,
	                                            &g_c_rowpack);
	rowpack_to_block(&g_rowpack_as_block, &g_out_rowpack);

	return compare_poly("rowpack soa canonical basemul_add",
	                    &g_rowpack_as_block,
	                    &g_ref_block) &&
	       check_canonical_rowpack_range("rowpack soa canonical basemul_add",
	                                    &g_out_rowpack);
}

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
		        "bench_gt_basemul_soa: perf_event_open(cycles) failed: %s\n",
		        strerror(errno));
		fprintf(stderr,
		        "bench_gt_basemul_soa: try lowering perf_event_paranoid or run "
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
		        "bench_gt_basemul_soa: read(cycles) failed: %s\n",
		        got < 0 ? strerror(errno) : "short read");
		return 0;
	}

	return cycles;
}

static uint64_t measure_counter_delta(void (*fn)(void), int batch)
{
	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
	    ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_ENABLE, 0) != 0)
	{
		fprintf(stderr,
		        "bench_gt_basemul_soa: enabling cycle counter failed: %s\n",
		        strerror(errno));
		return 0;
	}

	for (int j = 0; j < batch; j++)
	{
		fn();
	}

	if (ioctl(g_perf_cycles_fd, PERF_EVENT_IOC_DISABLE, 0) != 0)
	{
		fprintf(stderr,
		        "bench_gt_basemul_soa: disabling cycle counter failed: %s\n",
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

static uint64_t measure_counter_delta(void (*fn)(void), int batch)
{
	const uint64_t start = read_counter();
	uint64_t end;

	for (int j = 0; j < batch; j++)
	{
		fn();
	}

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

static void call_ld4_basemul(void)
{
	poly_basemul_ld4_neon(&g_out_block, &g_a_block, &g_b_block);
	g_sink ^= g_out_block.coeffs[0];
}

static void call_soa_basemul(void)
{
	poly_basemul_soa_neon(&g_out_soa, &g_a_soa, &g_b_soa);
	g_sink ^= g_out_soa.coeffs[0];
}

static void call_rowpack_basemul(void)
{
	poly_basemul_rowpack_soa_neon(&g_out_rowpack, &g_a_rowpack, &g_b_rowpack);
	g_sink ^= g_out_rowpack.coeffs[0];
}

static void call_rowvec_basemul(void)
{
	poly_basemul_rowvec_transpose_neon(&g_out_rowvec, &g_a_rowvec,
	                                   &g_b_rowvec);
	g_sink ^= g_out_rowvec.coeffs[0];
}

static void call_rowpack_canonical_basemul(void)
{
	poly_basemul_rowpack_soa_canonical_neon(&g_out_rowpack, &g_a_rowpack,
	                                        &g_b_rowpack);
	g_sink ^= g_out_rowpack.coeffs[0];
}

static void call_ld4_basemul_add(void)
{
	poly_basemul_add_ld4_neon(&g_out_block, &g_a_block, &g_b_block, &g_c_block);
	g_sink ^= g_out_block.coeffs[1];
}

static void call_soa_basemul_add(void)
{
	poly_basemul_add_soa_neon(&g_out_soa, &g_a_soa, &g_b_soa, &g_c_soa);
	g_sink ^= g_out_soa.coeffs[1];
}

static void call_rowpack_basemul_add(void)
{
	poly_basemul_add_rowpack_soa_neon(&g_out_rowpack, &g_a_rowpack,
	                                  &g_b_rowpack, &g_c_rowpack);
	g_sink ^= g_out_rowpack.coeffs[1];
}

static void call_rowvec_basemul_add(void)
{
	poly_basemul_add_rowvec_transpose_neon(&g_out_rowvec, &g_a_rowvec,
	                                       &g_b_rowvec, &g_c_rowvec);
	g_sink ^= g_out_rowvec.coeffs[1];
}

static void call_rowpack_canonical_basemul_add(void)
{
	poly_basemul_add_rowpack_soa_canonical_neon(&g_out_rowpack,
	                                            &g_a_rowpack,
	                                            &g_b_rowpack,
	                                            &g_c_rowpack);
	g_sink ^= g_out_rowpack.coeffs[1];
}

static void call_block_to_soa3(void)
{
	block_to_soa(&g_a_soa, &g_a_block);
	block_to_soa(&g_b_soa, &g_b_block);
	block_to_soa(&g_c_soa, &g_c_block);
	g_sink ^= g_a_soa.coeffs[2];
}

static void call_block_to_rowpack3(void)
{
	block_to_rowpack(&g_a_rowpack, &g_a_block);
	block_to_rowpack(&g_b_rowpack, &g_b_block);
	block_to_rowpack(&g_c_rowpack, &g_c_block);
	g_sink ^= g_a_rowpack.coeffs[2];
}

static void call_block_to_rowvec3(void)
{
	block_to_rowvec(&g_a_rowvec, &g_a_block);
	block_to_rowvec(&g_b_rowvec, &g_b_block);
	block_to_rowvec(&g_c_rowvec, &g_c_block);
	g_sink ^= g_a_rowvec.coeffs[2];
}

static void call_soa_to_block1(void)
{
	soa_to_block(&g_out_block, &g_out_soa);
	g_sink ^= g_out_block.coeffs[3];
}

static void call_rowpack_to_block1(void)
{
	rowpack_to_block(&g_out_block, &g_out_rowpack);
	g_sink ^= g_out_block.coeffs[3];
}

static void call_rowvec_to_block1(void)
{
	rowvec_to_block(&g_out_block, &g_out_rowvec);
	g_sink ^= g_out_block.coeffs[3];
}

static void run_bench(const char *label, void (*fn)(void))
{
	static uint64_t samples[BENCH_ITERS];
	uint64_t total = 0;
	const uint64_t wall_start = read_wall_ns();

	for (int i = 0; i < BENCH_WARMUP; i++)
	{
		fn();
	}

	for (int i = 0; i < BENCH_ITERS; i++)
	{
		samples[i] = measure_counter_delta(fn, BENCH_BATCH);
		total += samples[i];
	}

	const uint64_t wall_end = read_wall_ns();

	qsort(samples, BENCH_ITERS, sizeof(samples[0]), cmp_u64);

	printf("bench=%s iters=%d warmup=%d batch=%d cntfrq=%llu sink=%d\n",
	       label,
	       BENCH_ITERS,
	       BENCH_WARMUP,
	       BENCH_BATCH,
	       (unsigned long long)read_counter_freq(),
	       g_sink);
	printf("%s/call min=%.3f median=%.3f avg=%.3f p90=%.3f p99=%.3f\n",
	       BENCH_COUNTER_NAME,
	       (double)samples[0] / (double)BENCH_BATCH,
	       (double)samples[BENCH_ITERS / 2] / (double)BENCH_BATCH,
	       ((double)total / (double)BENCH_ITERS) / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 90) / 100] / (double)BENCH_BATCH,
	       (double)samples[(BENCH_ITERS * 99) / 100] / (double)BENCH_BATCH);
	printf("wall_ns/call avg=%.2f\n",
	       (double)(wall_end - wall_start) /
	           (double)((uint64_t)BENCH_ITERS * (uint64_t)BENCH_BATCH));
}

int main(void)
{
	fill_input(&g_a_block, 0x243f6a88u);
	fill_input(&g_b_block, 0x85a308d3u);
	fill_input(&g_c_block, 0x13198a2eu);
	init_lambda_rowpack();
	block_to_soa(&g_a_soa, &g_a_block);
	block_to_soa(&g_b_soa, &g_b_block);
	block_to_soa(&g_c_soa, &g_c_block);
	block_to_rowpack(&g_a_rowpack, &g_a_block);
	block_to_rowpack(&g_b_rowpack, &g_b_block);
	block_to_rowpack(&g_c_rowpack, &g_c_block);
	block_to_rowvec(&g_a_rowvec, &g_a_block);
	block_to_rowvec(&g_b_rowvec, &g_b_block);
	block_to_rowvec(&g_c_rowvec, &g_c_block);

	if (!check_correctness())
	{
		return 1;
	}

	if (!init_cycle_counter())
	{
		return 1;
	}

	run_bench("gt_basemul_ld4_intrinsic", call_ld4_basemul);
	run_bench("gt_basemul_soa_ld1_intrinsic", call_soa_basemul);
	run_bench("gt_basemul_rowpack_soa_ld1_intrinsic", call_rowpack_basemul);
	run_bench("gt_basemul_rowvec_transpose_intrinsic", call_rowvec_basemul);
	run_bench("gt_basemul_rowpack_soa_canonical_ld1_intrinsic",
	          call_rowpack_canonical_basemul);
	run_bench("gt_basemuladd_ld4_intrinsic", call_ld4_basemul_add);
	run_bench("gt_basemuladd_soa_ld1_intrinsic", call_soa_basemul_add);
	run_bench("gt_basemuladd_rowpack_soa_ld1_intrinsic",
	          call_rowpack_basemul_add);
	run_bench("gt_basemuladd_rowvec_transpose_intrinsic",
	          call_rowvec_basemul_add);
	run_bench("gt_basemuladd_rowpack_soa_canonical_ld1_intrinsic",
	          call_rowpack_canonical_basemul_add);
	run_bench("gt_block_to_soa_3_inputs", call_block_to_soa3);
	run_bench("gt_block_to_rowpack_3_inputs", call_block_to_rowpack3);
	run_bench("gt_block_to_rowvec_3_inputs", call_block_to_rowvec3);
	run_bench("gt_soa_to_block_1_output", call_soa_to_block1);
	run_bench("gt_rowpack_to_block_1_output", call_rowpack_to_block1);
	run_bench("gt_rowvec_to_block_1_output", call_rowvec_to_block1);

	close_cycle_counter();
	return 0;
}
